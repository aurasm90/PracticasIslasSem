import os
import smtplib
import sys
from email.message import EmailMessage
from dotenv import load_dotenv
from pathlib import Path

# FORMA CORRECTA - DESDE MAIN.py no funciona el metodo que teniamos: Buscar .env desde la raíz del proyecto
# Esto funciona tanto desde main.py como desde email_sender.py directamente
# Esto permite importar src.config desde cualquier lugar
sys.path.append(str(Path(__file__).parent.parent))
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from src.config import EMAIL_REMITENTE, EMAIL_DESTINO, ASUNTO, SMTP_SERVER, SMTP_PORT

def crear_cuerpo_email_html(licitaciones_json):

    tarjetas = ""

    for licitacion in licitaciones_json:

        estado = licitacion["estado"].lower()

        if "public" in estado:
            color_estado = "#28a745"
        elif "resuelta" in estado:
            color_estado = "#6c757d"
        elif "cancel" in estado:
            color_estado = "#dc3545"
        else:
            color_estado = "#fd7e14"

        tarjetas += f"""
        <div style="
            border:1px solid #dfe3e8;
            border-radius:12px;
            padding:20px;
            margin-bottom:20px;
            background-color:#ffffff;
            box-shadow:0 2px 6px rgba(0,0,0,0.05);
        ">

            <div style="
                background:#0d47a1;
                color:white;
                padding:12px;
                border-radius:8px;
                font-size:18px;
                font-weight:bold;
                margin-bottom:15px;
            ">
                Expediente: {licitacion["expediente"]}
            </div>

            <p><strong>Órgano:</strong> {licitacion["organo"]}</p>

            <p><strong>Objeto:</strong> {licitacion["objeto"]}</p>

            <p><strong>Tipo de contrato:</strong> {licitacion["tipo"]}</p>

            <p>
                <strong>Estado:</strong>
                <span style="
                    color:{color_estado};
                    font-weight:bold;
                ">
                    {licitacion["estado"]}
                </span>
            </p>

            <p>
                <strong>Importe:</strong>
                <span style="
                    color:#0d47a1;
                    font-weight:bold;
                ">
                    {licitacion["importe"]}
                </span>
            </p>

            <p><strong>Fecha:</strong> {licitacion["fecha"]}</p>

            <br>

            <a href="{licitacion["url"]}"
               style="
                    display:inline-block;
                    background-color:#0d47a1;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:6px;
                    font-weight:bold;
               ">
                Ver licitación
            </a>

        </div>
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

                <p style="
                    margin-top:10px;
                    opacity:0.9;
                ">
                    Se han encontrado nuevas licitaciones pendientes de revisión.
                </p>
            </div>

            <div style="padding:25px;">

                {tarjetas}

                <hr style="
                    border:none;
                    border-top:1px solid #e0e0e0;
                ">

                <p style="
                    font-size:12px;
                    color:#777777;
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

    password = os.getenv("EMAIL_PASSWORD")

    if not password:
        print("ERROR: No se encontró EMAIL_PASSWORD en .env")
        return

    if not licitaciones_json:
        print("No hay licitaciones para enviar")
        return

    # Convertir lista de destinatarios a string para el header
    destinatarios_str = ", ".join(EMAIL_DESTINO)

    mensaje = EmailMessage()
    mensaje["From"] = EMAIL_REMITENTE
    mensaje["To"] = destinatarios_str
    mensaje["Subject"] = ASUNTO

    mensaje.add_alternative(
        crear_cuerpo_email_html(licitaciones_json),
        subtype="html"
    )

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_REMITENTE, password)
            smtp.send_message(mensaje)
        print("Email enviado correctamente")
    except Exception as e:
        print(f"Error al enviar email: {e}")


if __name__ == "__main__":
    licitaciones_prueba = [
        {
            "organo": "Aena Dirección del Aeropuerto de Fuerteventura",
            "expediente": "FUE-50/2026",
            "tipo": "Suministros",
            "objeto": "Cerramiento de puertas antirretorno norte",
            "estado": "Publicada",
            "importe": "5.752,00 €",
            "fecha": "18/06/2026",
            "url": "https://ejemplo.com/licitacion/123"
        }
    ]

    enviar_email_json(licitaciones_prueba)
