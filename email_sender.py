def enviar_email(licitaciones):

    print("Módulo de email funcionando")

    if not licitaciones:
        print("No hay licitaciones nuevas")
        return

    print("Licitaciones recibidas:")

    for licitacion in licitaciones:
        print(licitacion)


licitaciones_prueba = [
    {
        "expediente": "123/2026",
        "objeto": "Servicio de limpieza",
        "fecha": "17/06/2026",
        "url": "https://ejemplo.com"
    }
]

enviar_email(licitaciones_prueba)