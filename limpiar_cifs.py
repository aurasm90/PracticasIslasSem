from pathlib import Path

RUTA_ORIGINAL = Path("datos/cifs_lista_original.txt")
RUTA_LIMPIO = Path("datos/cifs_permitidos.txt")


def limpiar_archivo_cifs():
    """Lee el archivo de CIFs y crea uno nuevo sin duplicados ni líneas vacías."""

    if not RUTA_ORIGINAL.exists():
        print(f"No se encontró {RUTA_ORIGINAL}")
        return

    # Leer y limpiar
    with open(RUTA_ORIGINAL, "r", encoding="utf-8") as f:
        cifs_unicos = set()
        lineas_vacias = 0

        for linea in f:
            cif = linea.strip()
            if not cif:
                lineas_vacias += 1
                continue
            cifs_unicos.add(cif)

    # Guardar archivo limpio
    with open(RUTA_LIMPIO, "w", encoding="utf-8") as f:
        for cif in sorted(cifs_unicos):  # Ordenar ABC para facilitar la lectura
            f.write(cif + "\n")

    print(f" Archivo limpio creado: {RUTA_LIMPIO}")
    print(f"   Total CIFs únicos: {len(cifs_unicos)}")
    print(f"   Líneas vacías eliminadas: {lineas_vacias}")

if __name__ == "__main__":
    limpiar_archivo_cifs()
