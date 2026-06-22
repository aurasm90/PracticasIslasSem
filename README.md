# PracticasIslasSem

Proyectos de prácticas de IslasSem

# README.md - Instrucciones para el administrador

## Instalación

1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar variables de entorno (si las hay)

## Ejecución manual

`python main.py`

## Programar ejecución diaria

### En Linux (cron)

Añadir al crontab: 0 9 \* \* \* cd /ruta/al/proyecto && python main.py

### En Windows (Programador de tareas)

1. Abrir Programador de tareas
2. Crear tarea que ejecute: `python C:\ruta\main.py`
3. Programar para las 09:00 diario
