# PAGINA PRINCIPAL PROGRAMA
# import schedule
# import time

from src.scraping import main_scraping
from src.json_parser import procesar_licitaciones
from src.email_sender import enviar_email_json

def ejecutar_programa():
    """Función principal que orquesta todo el proceso"""
    print("-" * 50)
    print("PROGRAMA DE SCRAPING - CONTRATACIONES DEL ESTADO")
    print("-" * 50)

    print("\nIniciando revisión automática de licitaciones...")

    # 1. Ejecutar scraping
    print("\nPASO 1: Extrayendo licitaciones de la web...")
    licitaciones = main_scraping()

    if not licitaciones:
        print("No se han encontrado licitaciones")
        return

    print(f"Extraídas {len(licitaciones)} licitaciones")

    # 2. Procesar licitaciones nuevas
    print("\nPASO 2: Filtrando licitaciones nuevas...")
    licitaciones_nuevas = procesar_licitaciones(licitaciones)

    if licitaciones_nuevas:
        print(f"Licitaciones nuevas: {len(licitaciones_nuevas)}")
        # 3. Enviar email
        print("\nPASO 3: Enviando email...")
        enviar_email_json(licitaciones_nuevas)
    else:
        print("No hay licitaciones nuevas para enviar.")

    print("\n" + "-" * 50)
    print("PROGRAMA COMPLETADO")
    print("-" * 50)


if __name__ == "__main__":
    ejecutar_programa()

    # schedule.every().day.at("09:00").do(ejecutar_programa)

    # print(
    #     "Automatización activada. El programa revisará licitaciones cada día a las 09:00."
    # )

    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
