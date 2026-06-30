"""
Módulo de envío de email con las licitaciones nuevas detectadas.

Flujo principal:
    1. Recibe la lista de licitaciones nuevas desde el módulo json_parser
    2. Genera un email en formato HTML con las licitaciones en formato compacto,
       mostrando expediente, objeto, órgano, CIF, tipo, importe, fecha y enlace
    3. Envía el email al destinatario configurado en config.py
       usando las credenciales del archivo .env

Configuración necesaria en .env:
    - EMAIL_PASSWORD: contraseña de la cuenta de envío

Configuración necesaria en config.py:
    - EMAIL_REMITENTE, EMAIL_DESTINO, ASUNTO, SMTP_SERVER, SMTP_PORT
"""

import os
import smtplib
from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv
from src.logger_config import logger
from src.config import (
    BASE_DIR,
    EMAIL_REMITENTE,
    EMAIL_DESTINO,
    ASUNTO,
    SMTP_SERVER,
    SMTP_PORT,
)

env_path = BASE_DIR / ".env"
load_dotenv("/home/adminlicitaciones/PracticasIslasSem/.env")


def acortar_texto(texto, limite=120):
    """
    Acorta textos largos para que el email no sea demasiado extenso.
    """
    if not texto:
        return ""

    if len(texto) <= limite:
        return texto

    return texto[:limite] + "..."


def crear_cuerpo_email_html(licitaciones_json):
    """
    Crea el cuerpo del email en formato HTML.
    Las licitaciones se muestran en formato compacto.
    """

    filas = ""

    for licitacion in licitaciones_json:
        expediente = licitacion.get("expediente", "")
        organo = licitacion.get("organo", "")
        tipo = licitacion.get("tipo", "")
        cif = licitacion.get("cif", "")
        objeto = acortar_texto(licitacion.get("objeto", ""))
        importe = licitacion.get("importe", "")
        fecha = licitacion.get("fecha", "")
        url = licitacion.get("url", "#")

        if importe and "€" not in importe:
            importe += " €"

        filas += f"""
        <tr>
            <td style="padding:12px; border-bottom:1px solid #e0e0e0;">
                <strong style="color:#0d47a1;">{expediente}</strong><br>

                <span style="color:#333333;">
                    {objeto}
                </span><br>

                <span style="font-size:12px; color:#666666;">
                    {organo} | CIF: {cif} | {tipo} 
                    <strong style="color:#198754;">
                        {importe}
                    </strong>
                    | {fecha}
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
    Envía por email la lista de licitaciones recibidas.
    """

    password = os.getenv("EMAIL_PASSWORD")
    logger.info(f"Password cargada: {bool(password)}")
    
    if not password:
        logger.error("EMAIL_PASSWORD no cargado desde .env")
        return

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

    logger.info("Email enviado correctamente")


if __name__ == "__main__":
    licitaciones_prueba = [
        {
            "organo": "Aena Dirección del Aeropuerto de Fuerteventura",
            "expediente": "FUE-50/2026",
            "cif": "A86212420",
            "tipo": "Suministros",
            "objeto": "Cerramiento de puertas antirretorno norte para mejorar el acceso y seguridad del aeropuerto",
            "estado": "Publicada",
            "importe": "5.752,00",
            "fecha": "18/06/2026",
            "url": "https://ejemplo.com/licitacion/123"
        }
    ]

    enviar_email_json(licitaciones_prueba)
