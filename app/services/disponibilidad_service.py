from models import Cita,EstadoCita

class DisponibilidadService:

    @staticmethod
    def existe_cruce(
        profesional_id,
        inicio,
        fin,
        cita_id=None
    ):

        query = Cita.query.filter(
            Cita.profesional_id ==
            profesional_id,

            Cita.estado.in_([
                EstadoCita.CONFIRMADA,
                EstadoCita.PENDIENTE_PAGO,
                EstadoCita.REPROGRAMADA
            ]),

            Cita.fecha_inicio < fin,
            Cita.fecha_fin > inicio
        )

        if cita_id:
            query = query.filter(
                Cita.id != cita_id
            )

        return query.first() is not None