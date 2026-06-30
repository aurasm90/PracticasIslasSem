"""
Punto de entrada principal del programa de seguimiento de licitaciones.

Flujo principal:
    1. Ejecuta el scraping de la Plataforma de Contratación del Sector Público
       y guarda todas las licitaciones encontradas en datos/licitaciones_hoy.json
    2. Compara las licitaciones de hoy con el histórico y detecta las nuevas,
       guardándolas en datos/licitaciones_nuevas.json
    3. Envía por email las licitaciones nuevas al destinatario configurado

Automatización:
    El programa puede programarse para ejecutarse diariamente a las 06:00am con un cron en el servidor
"""
from src.scraping import main_scraping
from src.json_parser import procesar_licitaciones
from src.email_sender import enviar_email_json
from src.logger_config import logger

def ejecutar_programa():
    """Función principal que orquesta todo el proceso"""

    try:

        logger.info("-" * 50)
        logger.info("PROGRAMA DE SCRAPING - CONTRATACIONES DEL ESTADO")
        logger.info("-" * 50)

        logger.info("Iniciando revisión automática de licitaciones...")

        # 1. Ejecutar scraping
        logger.info("PASO 1: Extrayendo licitaciones de la web...")

        scraping_ok = main_scraping()

        if not scraping_ok:
            logger.error(
                "El scraping no finalizó correctamente. Se detiene la ejecución."
            )
            return

        # 2. Procesar licitaciones nuevas
        logger.info("PASO 2: Filtrando licitaciones nuevas...")

        licitaciones_nuevas = procesar_licitaciones()

        if licitaciones_nuevas:
            # 3. Enviar email
            logger.info("PASO 3: Enviando email...")
            enviar_email_json(licitaciones_nuevas)
        else:
            logger.info("No hay licitaciones nuevas para enviar.")

        logger.info("-" * 50)
        logger.info("PROGRAMA COMPLETADO")
        logger.info("-" * 50)

    except KeyboardInterrupt:
        logger.warning("Programa interrumpido por el usuario")
        return

    except Exception:
        logger.exception(f"Error inesperado")


if __name__ == "__main__":
    ejecutar_programa()
