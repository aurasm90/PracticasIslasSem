# GESTIÓN DE LA MEMORIA DEL PROGRAMA
# Este módulo compara las licitaciones encontradas hoy con el histórico
# de expedientes ya enviados por email.
#
# Archivos usados:
# - datos/licitaciones_hoy.json: contiene todas las licitaciones encontradas hoy.
# - datos/expedientes_vistos.json: histórico acumulado de IDs ya enviados.
# - datos/licitaciones_nuevas.json: licitaciones nuevas detectadas en la ejecución actual.

import json
import os

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
    if not os.path.exists(ruta):
        return []

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, ValueError):
        print(f"Aviso: '{ruta}' no es un JSON válido. Se usará una lista vacía.")
        return []


def guardar_json(datos, ruta):
    """
    Guarda datos en formato JSON.
    Crea la carpeta si no existe.
    """
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def obtener_ids_vistos(expedientes_vistos):
    """
    Obtiene un conjunto con los IDs ya enviados.

    El archivo expedientes_vistos.json puede contener:
    - una lista de strings: ["ID1", "ID2"]
    - o una lista de diccionarios: [{"id": "ID1"}, {"id": "ID2"}]

    Esta función soporta ambos formatos.
    """
    ids_vistos = set()

    for elemento in expedientes_vistos:
        if isinstance(elemento, dict):
            id_licitacion = elemento.get(CLAVE_ID)
            if id_licitacion:
                ids_vistos.add(id_licitacion)
        elif isinstance(elemento, str):
            ids_vistos.add(elemento)

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
    Añade al histórico los IDs de las licitaciones nuevas.
    """
    ids_vistos = obtener_ids_vistos(expedientes_vistos)

    for licitacion in licitaciones_nuevas:
        id_licitacion = licitacion.get(CLAVE_ID)

        if id_licitacion and id_licitacion not in ids_vistos:
            expedientes_vistos.append(id_licitacion)
            ids_vistos.add(id_licitacion)

    return expedientes_vistos


def procesar_licitaciones(licitaciones_hoy):
    """
    Flujo completo del JSON parser:

    1. Guarda todas las licitaciones encontradas en licitaciones_hoy.json.
    2. Carga el histórico expedientes_vistos.json.
    3. Compara por ID para detectar licitaciones nuevas.
    4. Guarda las nuevas en licitaciones_nuevas.json.
    5. Actualiza expedientes_vistos.json añadiendo los nuevos IDs.
    6. Devuelve las licitaciones nuevas para enviarlas por email.
    """

    guardar_json(licitaciones_hoy, ARCHIVO_HOY)

    expedientes_vistos = cargar_json(ARCHIVO_VISTOS)
    ids_vistos = obtener_ids_vistos(expedientes_vistos)

    licitaciones_nuevas = filtrar_nuevas(licitaciones_hoy, ids_vistos)

    guardar_json(licitaciones_nuevas, ARCHIVO_NUEVAS)

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
    licitaciones_prueba = [
        {
            "id": "ABC123",
            "expediente": "EXP-2024-001",
            "cif": "P3803700H",
            "organo": "Órgano de ejemplo",
            "objeto": "Objeto de ejemplo",
            "tipo": "Servicios",
            "estado": "Publicada",
            "importe": "10.000,00 €",
            "fecha": "19/06/2026",
            "url": "https://contrataciondelestado.es/",
        }
    ]

    nuevas = procesar_licitaciones(licitaciones_prueba)
    print("Licitaciones nuevas:", nuevas)