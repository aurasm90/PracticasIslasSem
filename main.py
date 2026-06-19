# PAGINA PRINCIPAL PROGRAMA

# Archivo principal que une todo
# Llama al scraping
# Recoge los resultados en JSON
# Llama al email
# Programa la ejecución automática diaria

# Llamar a webscrapping
from src.scraping import main_scraping

def main():
    print("=" * 60)
    print("🚀 PROGRAMA DE SCRAPING - CONTRATACIÓN DEL ESTADO")
    print("=" * 60)

    # 1. Ejecutar scraping (tu código)
    print("\n📊 Ejecutando scraping...")
    licitaciones = main_scraping()  # ← Tu función debe DEVOLVER los datos
