import json


def enviar_email_json(licitaciones_json):
    print("Preparando email con licitaciones nuevas...\n")

    cuerpo = "Se han detectado nuevas licitaciones:\n\n"

    for licitacion in licitaciones_json:
        cuerpo += f"""
Expediente: {licitacion["expediente"]}
Objeto: {licitacion["objeto"]}
Fecha: {licitacion["fecha"]}
URL: {licitacion["url"]}
-------------------------
"""

    print(cuerpo)


licitaciones_prueba = [
    {
        "expediente": "123/2026",
        "objeto": "Servicio de limpieza",
        "fecha": "18/06/2026",
        "url": "https://ejemplo.com/licitacion/123"
    },
    {
        "expediente": "124/2026",
        "objeto": "Mantenimiento de jardines",
        "fecha": "18/06/2026",
        "url": "https://ejemplo.com/licitacion/124"
    }
]



enviar_email_json(licitaciones_prueba)
