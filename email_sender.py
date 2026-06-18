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

# Datos de prueba para probar el correo
licitaciones_prueba = [
    {
        "numero": "FUE-55/2026",
        "organo": "Ayuntamiento de ejemplo",
        "tipo": "Servicios",
        "objeto": "Mantenimiento edificios",
        "estado": "Publicada",
        "importe": "10.000",
        "fecha_publicacion": "17/06/2026",
        "url": "https://contrataciondelestado.es",
    },
    {
        "numero": "FUE-56/2026",
        "organo": "Otro ayuntamiento",
        "tipo": "Obras",
        "objeto": "Reforma parque municipal",
        "estado": "Publicada",
        "importe": "50.000",
        "fecha_publicacion": "17/06/2026",
        "url": "https://contrataciondelestado.es",
    },
]
