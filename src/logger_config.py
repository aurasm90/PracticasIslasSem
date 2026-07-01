"""
Configuración del sistema de logging para el proyecto.

Establece un logger centralizado ('licitaciones') usado por todos los módulos,
con salida simultánea a archivo y consola.

Niveles registrados: INFO, WARNING, ERROR y CRITICAL (se ignora DEBUG).
Formato: fecha y hora | nivel | mensaje
"""

import logging
from src.config import LOG_DIR, LOG_FILE

# Crear carpeta logs si no existe
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)

logger = logging.getLogger("licitaciones")
