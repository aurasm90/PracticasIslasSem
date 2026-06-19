# GESTIÓN DE LA "MEMORIA" DEL PROGRAMA
# Este módulo se encarga de recordar qué expedientes ya han sido enviados por
# email para no enviar duplicados.
#
# El archivo 'expedientes_vistos.json' guarda una lista con los números de
# expediente ya enviados. Ejemplo:
#   ["EXP-2024-001", "EXP-2024-002", "EXP-2024-003"]
#
# En cada ejecución se comparan las licitaciones nuevas con esta lista y solo
# se devuelven (para enviar) las que todavía no estén guardadas.

import json
import os

# Nombre del archivo que actúa como memoria del programa
ARCHIVO_VISTOS = "expedientes_vistos.json"

# Clave del diccionario de licitación que identifica al expediente.
# email_sender.py usa "expediente", así que mantenemos el mismo nombre.
CLAVE_EXPEDIENTE = "expediente"


def cargar_vistos(ruta=ARCHIVO_VISTOS):
    """Lee el JSON y devuelve un conjunto con los expedientes ya enviados.

    Si el archivo no existe todavía (primera ejecución) o está corrupto,
    devuelve un conjunto vacío en lugar de fallar.
    """
    if not os.path.exists(ruta):
        return set()

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
            # Usamos un set para que la comprobación "está visto?" sea rápida
            return set(datos)
    except (json.JSONDecodeError, ValueError):
        print(f"Aviso: '{ruta}' no es un JSON válido. Empezando de cero.")
        return set()


def guardar_vistos(vistos, ruta=ARCHIVO_VISTOS):
    """Guarda en el JSON el conjunto de expedientes ya enviados.

    Se guarda como lista ordenada para que el archivo sea legible y estable.
    """
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(sorted(vistos), f, ensure_ascii=False, indent=2)


def filtrar_nuevas(licitaciones, vistos):
    """Devuelve solo las licitaciones cuyo expediente no esté en 'vistos'."""
    nuevas = []
    for licitacion in licitaciones:
        expediente = licitacion.get(CLAVE_EXPEDIENTE)

        # Si la licitación no trae expediente, la ignoramos (no se puede comparar)
        if not expediente:
            continue

        if expediente not in vistos:
            nuevas.append(licitacion)

    return nuevas


def procesar_licitaciones(licitaciones, ruta=ARCHIVO_VISTOS):
    """Flujo completo de la "memoria" del programa.

    1. Carga los expedientes ya enviados.
    2. Filtra las licitaciones para quedarse solo con las nuevas.
    3. Añade las nuevas a la memoria y la guarda en disco.
    4. Devuelve la lista de licitaciones nuevas (para enviarlas por email).
    """
    vistos = cargar_vistos(ruta)
    nuevas = filtrar_nuevas(licitaciones, vistos)

    if nuevas:
        for licitacion in nuevas:
            vistos.add(licitacion[CLAVE_EXPEDIENTE])
        guardar_vistos(vistos, ruta)
        print(f"{len(nuevas)} licitaciones nuevas guardadas en '{ruta}'")
    else:
        print("No hay licitaciones nuevas")

    return nuevas


# ------------------------------
# Prueba rápida del módulo
# ------------------------------
if __name__ == "__main__":
    # Datos provisionales construidos a partir de config.py mientras el
    # scraper no está terminado.
    from config import ASUNTO, EXPEDIENTE, FECHA, URL

    licitaciones_prueba = [
        {
            "expediente": EXPEDIENTE,
            "objeto": ASUNTO,
            "fecha": FECHA,
            "url": URL,
        },
    ]

    # Primera ejecución: ambas son nuevas
    nuevas = procesar_licitaciones(licitaciones_prueba)
    print("Nuevas (1ª ejecución):", [l["expediente"] for l in nuevas])

    # Segunda ejecución con los mismos datos: ya no hay nuevas
    nuevas = procesar_licitaciones(licitaciones_prueba)
    print("Nuevas (2ª ejecución):", [l["expediente"] for l in nuevas])
