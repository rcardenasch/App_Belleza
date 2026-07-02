from urllib.parse import quote

def generar_link_whatsapp(
        telefono,
        mensaje
):
    mensaje = quote(mensaje)

    if telefono:
        return f"https://wa.me/{telefono}?text={mensaje}"

    return f"https://wa.me/?text={mensaje}"
