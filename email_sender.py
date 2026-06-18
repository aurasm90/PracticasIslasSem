import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from config import EMAIL_REMITENTE, EMAIL_DESTINO, ASUNTO, SMTP_SERVER, SMTP_PORT

load_dotenv()


def crear_cuerpo_email(licitaciones_json):
    cuerpo = "Se han detectado nuevas licitaciones:\n\n"

    for licitacion in licitaciones_json:
        cuerpo += f"""
Expediente: {licitacion["expediente"]}
Objeto: {licitacion["objeto"]}
Fecha: {licitacion["fecha"]}
URL: {licitacion["url"]}
-------------------------
"""

    return cuerpo


def enviar_email_json(licitaciones_json):
    password = os.getenv("EMAIL_PASSWORD")

    mensaje = EmailMessage()
    mensaje["From"] = EMAIL_REMITENTE
    mensaje["To"] = EMAIL_DESTINO
    mensaje["Subject"] = ASUNTO

    mensaje.set_content(crear_cuerpo_email(licitaciones_json))

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(EMAIL_REMITENTE, password)
        smtp.send_message(mensaje)

    print("Email enviado correctamente")


licitaciones_prueba = [
    {
        "expediente": "123/2026",
        "objeto": "Servicio de limpieza",
        "fecha": "18/06/2026",
        "url": "https://ejemplo.com"
    }
]



enviar_email_json(licitaciones_prueba)
