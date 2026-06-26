# PracticasIslasSem

Proyecto de prácticas de IslasSem

# Scraping de Licitaciones - Contratación del Estado (Canarias)

Sistema automatizado para la extracción y seguimiento de licitaciones públicas de la comunidad autónoma de Canarias, publicado en la Plataforma de Contratación del Estado.

## Descripción

Este script realiza scraping de la página de contratación del estado, filtrando exclusivamente los órganos de Canarias. Extrae las licitaciones publicadas de cada órgano, las compara con las ya enviadas (para evitar duplicados) y envía un correo electrónico con las nuevas licitaciones detectadas.

# README.md - Instrucciones para el administrador

## Instalación

1. Clonar el repositorio

2. Configurar variables de entorno (si las hay)

# En Linux/Mac

python3 -m venv venv
source venv/bin/activate

# En Windows

python -m venv venv
venv\Scripts\activate

3. Instalar dependencias
   pip install -r requirements.txt

## Programar ejecución diaria

### En Linux (cron)

Añadir al crontab: 0 9 \* \* \* cd /ruta/al/proyecto && python main.py

### En Windows (Programador de tareas)

1. Abrir Programador de tareas
2. Crear tarea que ejecute: `python C:\ruta\main.py`
3. Programar para las 06:00 diario
