from .scheduler import scheduler
from .tareas import enviar_recordatorios


def iniciar_scheduler():

    scheduler.add_job(
        enviar_recordatorios,
        trigger="interval",
        minutes=5,
        id="recordatorios",
        replace_existing=True
    )

    scheduler.start()
