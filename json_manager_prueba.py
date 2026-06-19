# FUNCIONES RELACIONADAS A LOS DATOS EN JSON
import json
import os

ARCHIVO_JSON = "expedientes_nuevos.json"


# DATOS EJEMPLO PARA PROBAR Y HACER LAS FUNCIONES NECESARIAS PARA GUARDAR EN JSON
licitaciones_prueba = [
    {
        "id": "ABC123",
        "numero": "FUE-50/2026",
        "organo": "Aena Dirección del Aeropuerto de Fuerteventura",
        "objeto": "Cerramiento de puertas antirretorno norte",
        "tipo": "Suministros",
        "estado": "Publicada",
        "importe": "5.752,00",
        "fecha": "18/06/2026",
        "url": "https://contrataciondelestado.es",
    },
    {
        "id": "DEF456",
        "numero": "LPA-35/2026",
        "organo": "Ayuntamiento de Santa Cruz de Tenerife",
        "objeto": "Mantenimiento de parques y jardines",
        "tipo": "Servicios",
        "estado": "Publicada",
        "importe": "10.000,00",
        "fecha": "18/06/2026",
        "url": "https://contrataciondelestado.es",
    },
]

# EJEMPLO FUNCIONES NECESARIAS PARA MANEJAR LOS DATOS JSON:
# cargar_vistos()
#   --> Lee el JSON
#   --> Devuelve lista de IDs ya vistos

# guardar_vistos(nuevas)
#   --> Recibe lista de licitaciones nuevas
#   --> Guarda sus IDs en el JSON

# filtrar_nuevos(licitaciones)
#   --> Recibe lista de licitaciones
#   --> Devuelve solo las que no están en el JSON
