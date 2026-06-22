# GESTIÓN DE LA "MEMORIA" DEL PROGRAMA
# Este módulo se encarga de recordar qué licitaciones ya han sido enviadas por
# email para no enviar duplicados.
#
# El archivo 'expedientes_vistos.json' guarda la lista completa de licitaciones
# ya enviadas (no solo su número). Cada licitación es un objeto con esta forma:
#   {
#       "id": "...",          # identificador único (clave de comparación)
#       "expediente": "...",      # número de expediente
#       "organo": "...",
#       "objeto": "...",
#       "tipo": "...",
#       "importe": "...",
#       "fecha": "...",
#       "url": "...",
#   }
#
# En cada ejecución se comparan las licitaciones nuevas con las ya guardadas
# (por su "id") y solo se devuelven las que todavía no estén en el archivo.

import json
import os

from src.config import ESTADO

# Nombre del archivo que actúa como memoria del programa
ARCHIVO_VISTOS = "datos/expedientes_vistos.json"

# Clave que identifica de forma única a cada licitación (para evitar duplicados)
CLAVE_ID = "id"


def cargar_vistas(ruta=ARCHIVO_VISTOS):
    """Lee el JSON y devuelve la lista de licitaciones ya enviadas.

    Si el archivo no existe todavía (primera ejecución) o está corrupto,
    devuelve una lista vacía en lugar de fallar.
    """
    if not os.path.exists(ruta):
        return []

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        print(f"Aviso: '{ruta}' no es un JSON válido. Empezando de cero.")
        return []


def guardar_vistas(licitaciones, ruta=ARCHIVO_VISTOS):
    """Guarda en el JSON la lista completa de licitaciones ya enviadas."""
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(licitaciones, f, ensure_ascii=False, indent=2)


def filtrar_nuevas(licitaciones, vistas):
    """Devuelve solo las licitaciones cuyo 'id' no esté ya en 'vistas'."""
    # Conjunto de ids ya vistos para que la comprobación sea rápida (O(1))
    ids_vistos = {lic.get(CLAVE_ID) for lic in vistas}

    nuevas = []
    for licitacion in licitaciones:
        id_licitacion = licitacion.get(CLAVE_ID)

        # Si la licitación no trae id, la ignoramos (no se puede comparar)
        if not id_licitacion:
            continue

        if id_licitacion not in ids_vistos:
            nuevas.append(licitacion)

    return nuevas


def procesar_licitaciones(licitaciones, ruta=ARCHIVO_VISTOS):
    """Flujo completo de la "memoria" del programa.

    1. Carga las licitaciones ya enviadas.
    2. Filtra para quedarse solo con las nuevas (por 'id').
    3. Añade las nuevas a la memoria y la guarda en disco.
    4. Devuelve la lista de licitaciones nuevas (para enviarlas por email).
    """
    vistas = cargar_vistas(ruta)
    nuevas = filtrar_nuevas(licitaciones, vistas)

    if nuevas:
        vistas.extend(nuevas)
        guardar_vistas(vistas, ruta)
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
    from config import ID, EXPEDIENTE, FECHA, URL, ORGANO, OBJETO, TIPO, ESTADO, IMPORTE

    licitaciones_prueba = [
        {
            "id": ID,
            "expediente": EXPEDIENTE,
            "organo": ORGANO,
            "objeto": OBJETO,
            "tipo": TIPO,
            "estado": ESTADO,
            "importe": IMPORTE,
            "fecha": FECHA,
            "url": URL,
        },
    ]

    # Primera ejecución: la licitación es nueva
    nuevas = procesar_licitaciones(licitaciones_prueba)
    print("Nuevas (1ª ejecución):", [lic["id"] for lic in nuevas])

    # Segunda ejecución con los mismos datos: ya no hay nuevas
    nuevas = procesar_licitaciones(licitaciones_prueba)
    print("Nuevas (2ª ejecución):", [lic["id"] for lic in nuevas])
