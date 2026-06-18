# Aura:

# PASOS:
# 1 - Entrar en la web
# 2 - Filtrar por Canarias
# 3 - Leer TODAS las páginas de resultados
# 4 - Para cada órgano con licitaciones > 0 entrar y extraer las licitaciones
# 5 - Comparar con las ya vistas en JSON
# 6 - Si hay nuevas → ENVIAR por email
# 7 - Guardar las nuevas en JSON


# ------------------------------
# PASO 0 - Importamos librerías necesarias para Webscrapping
# ------------------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import os
import time

# ------------------------------
# GRUPO 1 - Iniciar/Cerrar Navegador
# ------------------------------

def iniciar_navegador():
    
    options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def cerrar_navegador(mi_navegador):
    input("Presiona ENTER para cerrar el navegador...")
    # Cerrar nav
    mi_navegador.quit()
    print("Navegador cerrado")


# ------------------------------
# GRUPO 2 - Funciones de Navegación
# ------------------------------

# Código prueba de acceso a la página

def filtrar_pagina_canarias(mi_navegador, url):
    print(f"Navegando a: {url}")
    mi_navegador.get(url)

    # esperamos que la página cargue
    esperar = WebDriverWait(mi_navegador, 10)
    print('Página cargando...')
    
    try:
        # Esperar el select
        menu = esperar.until(EC.presence_of_element_located((By.ID, "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:menu111MAQ")))
        print("Select encontrado!")

        # Creamos el objeto Select
        lista = Select(menu)

        print('Seleccionando Canarias...')
        lista.select_by_visible_text('Canarias')

        print('Canarias escogido')
        print('Buscando botón FILTRAR...')

        buscar_boton = esperar.until(
            EC.element_to_be_clickable(
                (By.ID, "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:botonbuscar")
            )
        )
        buscar_boton.click()

        # esperar un momento
        time.sleep(3)
        print("Filtro aplicado correctamente!")
        
    except Exception as e:
        print(f"Error: {e}")


# ------------------------------
# GRUPO 3: MAIN
# ------------------------------

def main():
    print('Inciando navegador...')
    mi_navegador = iniciar_navegador()
    url = "https://contrataciondelestado.es/wps/portal/plataforma/perfil_contratante/lista_perfiles/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziHcNcAx09LY0N3IMCXA2MnILMzUzc_I0NDIz0w8EKTI2dTcK8wgLMgj3dDQw8PdxcfEINTQ3cjcz0o4jRb4ADOBoQpx-Pgij8xofrR-G3wgCqAJ8XCVlSkBsaGmGQ6QkATfmaFQ!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/IZ7_AVEQAI930GRPE02BR764FO30G0=CZ6_AVEQAI930GRPE02BR764FO3002=LA0=Ecom.ibm.faces.portlet.VIEWID!QCPjspQCPlistPerfilesQCPAdminAFPListPerfPortletAppView.jsp==/#Z7_AVEQAI930GRPE02BR764FO30G0"

    try: 
        filtrar_pagina_canarias(mi_navegador, url)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cerrar_navegador(mi_navegador)

# ------------------------------
# GRUPO 4: PUNTO DE ENTRADA
# ------------------------------
if __name__ == "__main__":
    main()
