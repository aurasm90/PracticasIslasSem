"""
Módulo de gestión de la memoria del programa.

Flujo principal:
    1. Carga las licitaciones de hoy desde datos/licitaciones_hoy.json,
       generado por el módulo de scraping
    2. Carga el histórico de licitaciones ya enviadas desde
       datos/expedientes_vistos.json
    3. Compara por ID para detectar licitaciones nuevas
    4. Guarda las nuevas en datos/licitaciones_nuevas.json para enviar por email
    5. Actualiza el histórico añadiendo los datos completos de las nuevas
       licitaciones para que no se vuelvan a enviar al día siguiente

Archivos usados:
    - datos/licitaciones_hoy.json: licitaciones encontradas en la ejecución actual
    - datos/expedientes_vistos.json: histórico acumulado de licitaciones ya enviadas
    - datos/licitaciones_nuevas.json: licitaciones nuevas a enviar por email
"""

import json
from pathlib import Path
from src.config import (
    ARCHIVO_HOY,
    ARCHIVO_VISTOS,
    ARCHIVO_NUEVAS,
    CLAVE_ID,
)


def cargar_json(ruta):
    """
    Carga un archivo JSON y devuelve su contenido.
    Si el archivo no existe o está corrupto, devuelve una lista vacía.
    """

    ruta = Path(ruta)
    if not ruta.exists():
        return []

    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        print(f"Aviso: '{ruta}' no es un JSON válido. Se usará una lista vacía.")
        return []


def guardar_json(datos, ruta):
    """
    Guarda datos en formato JSON.
    Crea la carpeta si no existe.
    """
    ruta = Path(ruta)

    # crea carpeta si no existe
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # escribe JSON
    ruta.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def obtener_ids_vistos(expedientes_vistos):
    """
    Obtiene un conjunto con los IDs ya enviados.
    """

    ids_vistos = set()

    for licitacion in expedientes_vistos:
        id_licitacion = licitacion.get(CLAVE_ID)

        if id_licitacion:
            ids_vistos.add(id_licitacion)

    return ids_vistos


def filtrar_nuevas(licitaciones_hoy, ids_vistos):
    """
    Devuelve solo las licitaciones de hoy cuyo ID no esté en el histórico.
    """
    nuevas = []

    for licitacion in licitaciones_hoy:
        id_licitacion = licitacion.get(CLAVE_ID)

        if not id_licitacion:
            continue

        if id_licitacion not in ids_vistos:
            nuevas.append(licitacion)

    return nuevas


def actualizar_expedientes_vistos(expedientes_vistos, licitaciones_nuevas):
    """
    Añade al histórico las licitaciones nuevas completas.

    Antes solo se guardaba el ID, pero ahora se guarda el diccionario completo
    de cada licitación para mantener un histórico con todos sus datos.
    """
    ids_vistos = obtener_ids_vistos(expedientes_vistos)

    for licitacion in licitaciones_nuevas:
        id_licitacion = licitacion.get(CLAVE_ID)

        if id_licitacion and id_licitacion not in ids_vistos:
            expedientes_vistos.append(licitacion)
            ids_vistos.add(id_licitacion)

    return expedientes_vistos


def procesar_licitaciones():
    """
    Flujo completo del JSON parser:

    1. Carga las licitaciones de hoy desde licitaciones_hoy.json (generado por el scraping).
    2. Carga el histórico expedientes_vistos.json.
    3. Compara por ID para detectar licitaciones nuevas.
    4. Guarda las nuevas en licitaciones_nuevas.json.
    5. Actualiza expedientes_vistos.json añadiendo las licitaciones completas.
    6. Devuelve las licitaciones nuevas para enviarlas por email.
    """

    # 1. Cargar licitaciones de hoy generadas por el scraping
    licitaciones_hoy = cargar_json(ARCHIVO_HOY)
    if not licitaciones_hoy:
        print("No hay licitaciones de hoy para procesar.")
        return []

    # 2. Cargar histórico
    expedientes_vistos = cargar_json(ARCHIVO_VISTOS)
    ids_vistos = obtener_ids_vistos(expedientes_vistos)

    # 3. Filtrar nuevas
    licitaciones_nuevas = filtrar_nuevas(licitaciones_hoy, ids_vistos)

    # 4. Guardar nuevas para el email
    guardar_json(licitaciones_nuevas, ARCHIVO_NUEVAS)

    # 5. Actualizar histórico
    if licitaciones_nuevas:
        expedientes_vistos = actualizar_expedientes_vistos(
            expedientes_vistos,
            licitaciones_nuevas
        )
        guardar_json(expedientes_vistos, ARCHIVO_VISTOS)
        print(f"{len(licitaciones_nuevas)} licitaciones nuevas guardadas.")
    else:
        print("No hay licitaciones nuevas.")

    return licitaciones_nuevas


if __name__ == "__main__":
    # licitaciones_prueba = [
    #     {
    #         "id": "ABC123",
    #         "expediente": "EXP-2024-001",
    #         "cif": "P3803700H",
    #         "organo": "Órgano de ejemplo",
    #         "objeto": "Objeto de ejemplo",
    #         "tipo": "Servicios",
    #         "estado": "Publicada",
    #         "importe": "10.000,00 €",
    #         "fecha": "19/06/2026",
    #         "url": "https://contrataciondelestado.es/",
    #     }
    # ]

    procesar_licitaciones()
