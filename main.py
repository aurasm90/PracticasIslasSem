# PAGINA PRINCIPAL PROGRAMA
# Archivo principal que une todo.
# Llama al scraping, recoge los resultados y llama al email.
# También programa la ejecución automática diaria.


# A partir de la ejecución del main se creará un archivo JSON 'expedientes.json'(nombre a escoger):
# Para recordar qué expedientes ya han sido enviados por email, evitando así enviar duplicados.
# El archivo expedientes_vistos.json guarda una lista de los números de expediente que ya han sido enviados por email. Básicamente es la "memoria" del programa.
# Por ejemplo, después de la primera ejecución el archivo contendría algo así:
# ["EXP-2024-001", "EXP-2024-002", "EXP-2024-003"]
# La próxima vez que el programa se ejecute, compara los expedientes nuevos con esta lista y solo envía los que no estén aquí, evitando duplicados.
