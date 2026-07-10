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
    
    @staticmethod
    def enviar_recordatorio_24hrs(cita):

        mensaje = f"""
🌸 *Centro de belleza JI - Lashista-Pigmentadora

Hola *{cita.cliente_nombre}*.

Te recordamos que tienes una reserva.

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
"""

        return WhatsAppService.enviar(
            cita.cliente_telefono,
            mensaje
        )

    @staticmethod
    def enviar_recordatorio_12hrs(cita):

        mensaje = f"""
🌸 * Hola *{cita.cliente_nombre}*.

Recordatorio, Tu cita será hoy.

━━━━━━━━━━━━━━

🕒 Hora:
{cita.fecha_inicio_lima.strftime('%H:%M')}

💇 Servicio:
{cita.servicio.nombre}

👩 Profesional:
{cita.profesional.nombres}

━━━━━━━━━━━━━━

Nos vemos pronto..
"""

        return WhatsAppService.enviar(
            cita.cliente_telefono,
            mensaje
        )

    @staticmethod
    def enviar_recordatorio_1hr(cita):

        mensaje = f"""
🌸 * Hola *{cita.cliente_nombre}*.

Falta aproximadamente 1 hora para tu cita.

━━━━━━━━━━━━━━
💇 Servicio:
{cita.servicio.nombre}

👩 Profesional:
{cita.profesional.nombres}

━━━━━━━━━━━━━━

Te esperamos.
"""

        return WhatsAppService.enviar(
            cita.cliente_telefono,
            mensaje
        )
