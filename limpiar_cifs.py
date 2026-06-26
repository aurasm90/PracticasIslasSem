"""
Utilidad para limpiar el archivo de CIFs permitidos

Lee el archivo original de CIFs copiados del Excel, elimina duplicados y líneas vacías,
y genera un archivo limpio ordenado alfabéticamente.

Archivos usados:
    - datos/cifs_lista_original.txt: archivo original con los CIFs en bruto
    - datos/cifs_permitidos.txt: archivo limpio generado por este script
"""

from src.config import RUTA_ORIGINAL, RUTA_LIMPIO

def limpiar_archivo_cifs():
    """
    Lee el archivo original de CIFs y genera uno nuevo
    sin duplicados ni líneas vacías, ordenado alfabéticamente.
    """

    if not RUTA_ORIGINAL.exists():
        print(f"No se encontró {RUTA_ORIGINAL}")
        return

    with open(RUTA_ORIGINAL, "r", encoding="utf-8") as f:
        cifs_unicos = set()
        lineas_vacias = 0

        for linea in f:
            cif = linea.strip()
            if not cif:
                lineas_vacias += 1
                continue
            cifs_unicos.add(cif)

    with open(RUTA_LIMPIO, "w", encoding="utf-8") as f:
        for cif in sorted(cifs_unicos):
            f.write(cif + "\n")

    print(f"Archivo limpio creado: {RUTA_LIMPIO}")
    print(f"   Total CIFs únicos: {len(cifs_unicos)}")
    print(f"   Líneas vacías eliminadas: {lineas_vacias}")

if __name__ == "__main__":
    limpiar_archivo_cifs()
