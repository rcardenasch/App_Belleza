from urllib.parse import quote
import requests
from flask import current_app


class WhatsAppService:


    @staticmethod
    def enviar(numero, mensaje):

        url = (
            f"{current_app.config['EVOLUTION_URL']}"
            f"/message/sendText/"
            f"{current_app.config['EVOLUTION_INSTANCE']}"
        )

        headers = {

            "apikey":
            current_app.config["EVOLUTION_TOKEN"]

        }

        def normalizar_numero(numero):
            numero = numero.replace("+", "").replace(" ", "")

            if numero.startswith("9"):
                numero = "51" + numero

            return numero
        
        payload = {

            "number": normalizar_numero(numero),

            "text": mensaje

        }


        try:
            r = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=(5,60)
            )

            print(r.text)

            return r.ok

        except requests.exceptions.RequestException as e:
            print("Error Evolution API:", e)
            return False



# metodo sin usar evolution api, solo genera el link de whatsapp para abrirlo en el navegador    
def generar_link_whatsapp(
        telefono,
        mensaje
    ):
        mensaje = quote(mensaje)

        if telefono:
            return f"https://wa.me/{telefono}?text={mensaje}"

        return f"https://wa.me/?text={mensaje}"

    