import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from config import (
    EMAIL_REMITENTE,
    EMAIL_DESTINO,
    ASUNTO,
    SMTP_SERVER,
    SMTP_PORT
)

# Carga la contraseña del correo desde el archivo .env
load_dotenv()


def acortar_texto(texto, limite=120):
    """
    Acorta textos largos para que el email no sea demasiado extenso.
    """
    if len(texto) <= limite:
        return texto

    return texto[:limite] + "..."


def crear_cuerpo_email_html(licitaciones_json):
    """
    Crea el cuerpo del email en formato HTML.
    Cada licitación se muestra de forma compacta.
    """

    filas = ""

    for licitacion in licitaciones_json:
        expediente = licitacion.get("expediente", "")
        organo = licitacion.get("organo", "")
        tipo = licitacion.get("tipo", "")
        objeto = acortar_texto(licitacion.get("objeto", ""))
        importe = licitacion.get("importe", "")
        fecha = licitacion.get("fecha", "")
        url = licitacion.get("url", "#")

        filas += f"""
        <tr>
            <td style="padding:12px; border-bottom:1px solid #e0e0e0;">
                <strong style="color:#0d47a1;">{expediente}</strong><br>
                <span style="color:#333333;">{objeto}</span><br>
                <span style="font-size:12px; color:#666666;">
                    {organo} | {tipo} | {importe} | {fecha}
                </span>
            </td>

            <td style="padding:12px; border-bottom:1px solid #e0e0e0; text-align:right;">
                <a href="{url}"
                   style="
                        background-color:#0d47a1;
                        color:white;
                        padding:8px 12px;
                        text-decoration:none;
                        border-radius:5px;
                        font-size:13px;
                        font-weight:bold;
                   ">
                    Ver
                </a>
            </td>
        </tr>
        """

    cuerpo_html = f"""
    <html>
    <body style="
        font-family: Arial, sans-serif;
        background-color:#f4f6f8;
        padding:25px;
    ">

        <div style="
            max-width:900px;
            margin:auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                background:#0d47a1;
                color:white;
                padding:25px;
            ">
                <h1 style="margin:0;">
                    Nuevas licitaciones detectadas
                </h1>

                <p style="margin-top:10px; opacity:0.9;">
                    Se han encontrado {len(licitaciones_json)} licitaciones nuevas.
                </p>
            </div>

            <div style="padding:25px;">
                <table style="
                    width:100%;
                    border-collapse:collapse;
                    background:white;
                ">
                    {filas}
                </table>

                <p style="
                    font-size:12px;
                    color:#777777;
                    margin-top:25px;
                ">
                    Correo generado automáticamente por el sistema de seguimiento de licitaciones.
                </p>
            </div>

        </div>

    </body>
    </html>
    """

    return cuerpo_html


def enviar_email_json(licitaciones_json):
    """
    Envía por email la lista de licitaciones recibidas en formato JSON.
    """

    password = os.getenv("EMAIL_PASSWORD")

    mensaje = EmailMessage()
    mensaje["From"] = EMAIL_REMITENTE
    mensaje["To"] = EMAIL_DESTINO
    mensaje["Subject"] = ASUNTO

    mensaje.add_alternative(
        crear_cuerpo_email_html(licitaciones_json),
        subtype="html"
    )

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(EMAIL_REMITENTE, password)
        smtp.send_message(mensaje)

    print("Email enviado correctamente")


if __name__ == "__main__":
    licitaciones_prueba = [
        {
            "organo": "Aena Dirección del Aeropuerto de Fuerteventura",
            "expediente": "FUE-50/2026",
            "tipo": "Suministros",
            "objeto": "Cerramiento de puertas antirretorno norte para mejorar el acceso y seguridad del aeropuerto",
            "estado": "Publicada",
            "importe": "5.752,00 €",
            "fecha": "18/06/2026",
            "url": "https://ejemplo.com/licitacion/123"
        }
    ]

    enviar_email_json(licitaciones_prueba)