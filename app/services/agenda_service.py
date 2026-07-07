from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import and_

from app.models.cita import Cita, EstadoCita
from app.models.bloqueo import BloqueoAgenda
from app.models.disponibilidad import DisponibilidadSemanal
from app.models.profesional import Profesional
from app.models.servicio import Servicio

LIMA_TZ = ZoneInfo("America/Lima")
UTC = ZoneInfo("UTC")

class AgendaService:

    @staticmethod
    def validar_disponibilidad(
        profesional_id: int,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        cita_id: int | None = None
    ) -> tuple[bool, str | None]:
        """
        Valida si un rango de tiempo está disponible para un profesional.
        Recibe las fechas preferiblemente con tzinfo (o asume UTC si no tienen).
        """
        # Asegurar objetos aware en UTC para comparaciones internas consistentes
        if fecha_inicio.tzinfo is None:
            fecha_inicio = fecha_inicio.replace(tzinfo=UTC)
        if fecha_fin.tzinfo is None:
            fecha_fin = fecha_fin.replace(tzinfo=UTC)

        # Convertir a hora local (Lima) para validar contra el horario laboral
        inicio_lima = fecha_inicio.astimezone(LIMA_TZ)
        fin_lima = fecha_fin.astimezone(LIMA_TZ)

        # -----------------------------------------
        # 1. Validar horario laboral y Profesional activo
        # -----------------------------------------
        # .weekday() de Python: Lunes=0, Domingo=6. ISO es Lunes=1, Domingo=7.
        dia_semana_python = inicio_lima.isoweekday()

        disponibilidades = DisponibilidadSemanal.query.filter_by(
            profesional_id=profesional_id,
            activo=True,
            dia_semana=dia_semana_python
        ).all()

        if not disponibilidades:
            return False, "El profesional no tiene horarios configurados o no atiende ese día."

        # Verificar si encaja en alguna de las franjas del día (soporta turnos partidos)
        hora_inicio_local = inicio_lima.time()
        hora_fin_local = fin_lima.time()
        
        en_horario = False
        for d in disponibilidades:
            if d.hora_inicio <= hora_inicio_local and hora_fin_local <= d.hora_fin:
                en_horario = True
                break

        if not en_horario:
            return False, "La hora está fuera del horario laboral del profesional."

        # Convertir a datetime naive en UTC para comparar con la Base de Datos si se guarda en UTC
        # Si tu BD guarda datetimes con zona horaria, remueve el .replace(tzinfo=None)
        inicio_db = fecha_inicio.astimezone(UTC).replace(tzinfo=None)
        fin_db = fecha_fin.astimezone(UTC).replace(tzinfo=None)

        # -----------------------------------------
        # 2. Bloqueos
        # -----------------------------------------
        bloqueo = BloqueoAgenda.query.filter(
            BloqueoAgenda.profesional_id == profesional_id,
            BloqueoAgenda.fecha_inicio < fin_db,
            BloqueoAgenda.fecha_fin > inicio_db
        ).first()

        if bloqueo:
            return False, "El profesional tiene un bloqueo para ese horario."

        # -----------------------------------------
        # 3. Cruce con citas
        # -----------------------------------------
        consulta = Cita.query.filter(
            Cita.profesional_id == profesional_id,
            Cita.estado.notin_([EstadoCita.CANCELADA, EstadoCita.NO_ASISTIO]),
            Cita.fecha_inicio < fin_db,
            Cita.fecha_fin > inicio_db
        )

        if cita_id:
            consulta = consulta.filter(Cita.id != cita_id)

        if consulta.first():
            return False, "El horario ya se encuentra reservado."

        return True, None
    
    @staticmethod
    def obtener_horarios_disponibles(
        profesional_id: int,
        servicio_id: int,
        fecha_str: str
    ) -> list[str]:

        if not profesional_id or not servicio_id or not fecha_str:
            return []

        profesional = Profesional.query.get(profesional_id)
        servicio = Servicio.query.get(servicio_id)

        if not profesional or not servicio:
            return []

        try:
            fecha_local = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return []

        ahora_lima = datetime.now(LIMA_TZ)

        if fecha_local < ahora_lima.date():
            return []

        # Corregido: .weekday() para emparejar con el estándar de validar_disponibilidad
        dia_semana = fecha_local.isoweekday()

        disponibilidades = DisponibilidadSemanal.query.filter_by(
            profesional_id=profesional.id,
            dia_semana=dia_semana,
            activo=True
        ).all()

        if not disponibilidades:
            return []

        duracion = servicio.duracion_minutos or 60
        horarios = []

        for disp in disponibilidades:
            actual_local = datetime.combine(fecha_local, disp.hora_inicio, tzinfo=LIMA_TZ)
            fin_jornada_local = datetime.combine(fecha_local, disp.hora_fin, tzinfo=LIMA_TZ)
            intervalo = disp.duracion_promedio_minutos or 30

            while actual_local + timedelta(minutes=duracion) <= fin_jornada_local:
                # Validar que no sea una hora del pasado si es el día de hoy
                if actual_local >= ahora_lima:
                    inicio_utc = actual_local.astimezone(UTC)
                    fin_utc = (actual_local + timedelta(minutes=duracion)).astimezone(UTC)

                    ok, _ = AgendaService.validar_disponibilidad(
                        profesional.id,
                        inicio_utc,
                        fin_utc
                    )

                    if ok:
                        horarios.append(actual_local.strftime("%H:%M"))

                actual_local += timedelta(minutes=intervalo)

        return sorted(list(set(horarios)))
    
    @staticmethod
    def generar_agenda_profesional(
        profesional_id: int,
        fecha_str: str,
        servicio_id: int | None = None
    ) -> list[dict]:

    
        profesional = Profesional.query.get_or_404(profesional_id)

        try:
            fecha = datetime.strptime(
                fecha_str,
                "%Y-%m-%d"
            ).date()
            
        except ValueError:
            return []

        # Si no envían servicio usamos el primero asignado
        if servicio_id is None:
            if profesional.servicios:
                servicio = profesional.servicios[0]
            else:

                return []
        else:
            servicio = Servicio.query.get(servicio_id)

            if not servicio:

                return []

        duracion = servicio.duracion_minutos or 60
        
        # CORRECCIÓN CRÍTICA: Cambiado .isoweekday() por .weekday() 
        # para que coincida exactamente con la lógica de validar_disponibilidad
        dia_semana = fecha.isoweekday()


        agenda = []
        disponibilidades = profesional.disponibilidades

        for d in profesional.disponibilidades:
            
            print(
                "ID:", d.id,
                "Dia:", d.dia_semana,
                "Activo:", d.activo,
                "Inicio:", d.hora_inicio,
                "Fin:", d.hora_fin
            )

        for disp in disponibilidades:

            # CORRECCIÓN CRÍTICA: Validar usando el estándar .weekday() y que la disponibilidad esté activa
            if disp.dia_semana != dia_semana or not getattr(disp, 'activo', True):
                    continue

            # Generar tiempos correctos usando tzinfo para evitar desvíos horarios
            actual = datetime.combine(
                fecha,
                disp.hora_inicio,
                tzinfo=LIMA_TZ
            )

            fin = datetime.combine(
                fecha,
                disp.hora_fin,
                tzinfo=LIMA_TZ
            )

            intervalo = disp.duracion_promedio_minutos or 30

            while actual + timedelta(minutes=duracion) <= fin:

                hora = actual.strftime("%H:%M")

                # Conversión limpia y segura a UTC para pasar al validador
                inicio_utc = actual.astimezone(UTC)
                termino_utc = (actual + timedelta(minutes=duracion)).astimezone(UTC)

                ok, motivo = AgendaService.validar_disponibilidad(
                    profesional.id,
                    inicio_utc,
                    termino_utc
                )

                estado = "available"

                if not ok:
                    motivo_str = str(motivo).lower()

                    if "bloque" in motivo_str:
                        estado = "blocked"

                    elif "reserv" in motivo_str:
                        estado = "booked"

                    elif "atiende" in motivo_str:
                        estado = "outside"

                    else:
                        estado = "error"

                agenda.append({
                    "hora": hora,
                    "estado": estado,
                    "motivo": motivo if not ok else ""
                })

                actual += timedelta(
                    minutes=intervalo
                )

        # OPTIMIZACIÓN: Eliminar duplicados si hay cruces de horarios 
        # priorizando los estados ocupados o bloqueados

        prioridad = {
        "booked": 4,
        "blocked": 3,
        "outside": 2,
        "error": 1,
        "available": 0
        }

        agenda_unica = {}

        for slot in agenda:
            h = slot["hora"]

            if (
                h not in agenda_unica or
                prioridad[slot["estado"]] > prioridad[agenda_unica[h]["estado"]]
            ):
                agenda_unica[h] = slot

        print(agenda_unica)  # Depuración: Verificar la agenda generada antes de ordenar

        return sorted(agenda_unica.values(), key=lambda x: x["hora"])
