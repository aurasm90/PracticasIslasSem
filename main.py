# PAGINA PRINCIPAL PROGRAMA
import schedule
import time

from src.scraping import main_scraping
from src.json_parser import procesar_licitaciones
from src.email_sender import enviar_email_json

def ejecutar_programa():
    
    print("=" * 60)
    print("PROGRAMA DE SCRAPING - CONTRATACIONES DEL ESTADO")
    print("=" * 60)
    print("Iniciando revisión automática de licitaciones...")
    
    # 1. Ejecutar scraping
    print("\nEjecutando scraping...")
    licitaciones = main_scraping()

    if not licitaciones:
        print("No se han encontrado licitaciones nuevas publicadas.")
        return

    licitaciones_nuevas = procesar_licitaciones(licitaciones) # Parte JSON_parser

    if licitaciones_nuevas:
        enviar_email_json(licitaciones_nuevas)
        print("Email enviado con las licitaciones nuevas.")
    else:
        print("No hay licitaciones nuevas para enviar.")


# def obtener_licitaciones_publicadas():
#     print("Iniciando navegador...")
#     navegador = iniciar_navegador()
#     todas_licitaciones = []

#     try:
#         resultado = filtrar_pagina_canarias(navegador)

#         if not resultado:
#             print("No se pudo aplicar el filtro de Canarias.")
#             return []

#         print("Filtro aplicado correctamente.")
#         organos = obtener_organos_con_licitaciones(navegador)

#         for organo in organos[:5]:
#             licitaciones = obtener_licitaciones_organo(navegador, organo)
#             todas_licitaciones.extend(licitaciones)

#         print(f"Total licitaciones publicadas encontradas: {len(todas_licitaciones)}")
#         return todas_licitaciones

#     except Exception as e:
#         print(f"Error durante el scraping: {e}")
#         return []

#     finally:
#         cerrar_navegador(navegador)


if __name__ == "__main__":
    ejecutar_programa()

    schedule.every().day.at("09:00").do(ejecutar_programa)

    print(
        "Automatización activada. El programa revisará licitaciones cada día a las 09:00."
    )

    while True:
        schedule.run_pending()
        time.sleep(60)
