from datetime import datetime, timedelta

from app import db
from app.models.cita import Cita,EstadoCita

from app.services.notificacion_service import (
    NotificacionService
)


def enviar_recordatorios():

    ahora = datetime.now()

    citas = Cita.query.filter(
        Cita.estado.in_([EstadoCita.PENDIENTE_PAGO,EstadoCita.REPROGRAMADA,EstadoCita.RESERVADA,EstadoCita.CONFIRMADA])
    ).all()

    for cita in citas:

        diferencia = cita.fecha_inicio_lima - ahora

        horas = diferencia.total_seconds() / 3600

        if 23.8 <= horas <= 24.2:
            NotificacionService.enviar_recordatorio_24hrs(cita,24)

        #-- Inhabilitado temporalmente
        #elif 11.8 <= horas <= 12.2:
        #    NotificacionService.enviar_recordatorio_12hrs(cita,12)

        elif 0.8 <= horas <= 1.2:
            NotificacionService.enviar_recordatorio_1hr(cita,1)
