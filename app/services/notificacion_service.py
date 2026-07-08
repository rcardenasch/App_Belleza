from flask import current_app

from app.services.whatsapp_service import WhatsAppService


class NotificacionService:

    @staticmethod
    def reserva_confirmada(cita):

        mensaje = f"""
🌸 *Centro de belleza JI - Lashista-Pigmentadora*

Hola *{cita.cliente_nombre}*.

Tu reserva fue registrada correctamente.

━━━━━━━━━━━━━━
💇 Servicio:
{cita.servicio.nombre}

👩 Profesional:
{cita.profesional.nombres}

📅 Fecha:
{cita.fecha_inicio_lima.strftime('%d/%m/%Y')}

🕒 Hora:
{cita.fecha_inicio_lima.strftime('%H:%M')}

━━━━━━━━━━━━━━
Te esperamos.

Muchas gracias por confiar en nosotros. En breve nos estaremos poniendo en contacto.
"""

        return WhatsAppService.enviar(

            cita.cliente_telefono,

            mensaje

        )
    
    @staticmethod
    def aviso_administrador(cita):

        mensaje = f"""
📢 *Nueva reserva registrada*

👤 Cliente:
{cita.cliente_nombre}
📱 Teléfono:
{cita.cliente_telefono}
💇 Servicio:
{cita.servicio.nombre}
👩 Profesional:
{cita.profesional.nombres}
📅 Fecha:
{cita.fecha_inicio_lima.strftime('%d/%m/%Y')}
🕒 Hora:
{cita.fecha_inicio_lima.strftime('%H:%M')}
📝 Observación:
{cita.observacion or 'Ninguna'}
"""
        return WhatsAppService.enviar(
            current_app.config["WHATSAPP_ADMIN"],
            mensaje
        )
