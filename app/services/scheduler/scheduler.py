from apscheduler.schedulers.background import BackgroundScheduler

from app.services.scheduler.scheduler_service import SchedulerService

scheduler = BackgroundScheduler(
    timezone="America/Lima"
)


def iniciar_scheduler(app):

    def ejecutar():

        with app.app_context():

            SchedulerService.enviar_recordatorios()

    scheduler.add_job(
        func=ejecutar,
        trigger="interval",
        minutes=5,
        id="recordatorios",
        replace_existing=True,
    )

    scheduler.start()

    print("✓ Scheduler iniciado")