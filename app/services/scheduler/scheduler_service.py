from datetime import datetime, timedelta
from datetime import timedelta

from zoneinfo import ZoneInfo

from app.extensions import db
from app.models.cita import Cita, EstadoCita
from app.services.notificacion_service import NotificacionService


class SchedulerService:

    @staticmethod
    def enviar_recordatorios():

        ahora = datetime.now(ZoneInfo("America/Lima"))

        citas = (
            Cita.query
            .filter(
                Cita.estado.in_([
                    EstadoCita.PENDIENTE_PAGO,
                    EstadoCita.REPROGRAMADA,
                    EstadoCita.RESERVADA,
                    EstadoCita.CONFIRMADA
                ]),
                Cita.fecha_inicio >= ahora
            )
            .all()
        )

        cambios = False

        for cita in citas:

            fecha_hora = cita.fecha_inicio_lima

            if not fecha_hora:
                continue

            restante = fecha_hora - ahora

            # ya pasó la cita
            if restante.total_seconds() < 0:
                continue

            # ------------------ 24 HORAS ------------------

            if (
                timedelta(hours=23, minutes=55)
                <= restante
                <= timedelta(hours=24, minutes=5)
                and not cita.recordatorio_24h
            ):

                if NotificacionService.enviar_recordatorio_24hrs(cita):

                    cita.recordatorio_24h = True
                    cambios = True

            # ------------------ 12 HORAS Inhabilitado ------------------

            #elif (
            #    timedelta(hours=11, minutes=55)
            #    <= restante
            #    <= timedelta(hours=12, minutes=5)
            #    and not cita.recordatorio_12h
            #):

            #    if NotificacionService.enviar_recordatorio_12hrs(cita):

            #        cita.recordatorio_12h = True
            #        cambios = True

            # ------------------ 1 HORA ------------------

            elif (
                timedelta(minutes=55)
                <= restante
                <= timedelta(hours=1, minutes=5)
                and not cita.recordatorio_1h
            ):

                if NotificacionService.enviar_recordatorio_1hr(cita):

                    cita.recordatorio_1h = True
                    cambios = True
        

        if cambios:
            db.session.commit()