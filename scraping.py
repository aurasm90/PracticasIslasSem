# PASOS:
# 1 - Entrar en la web
# 2 - Filtrar por Canarias
# 3 - Leer TODAS las páginas de resultados
# 4 - Para cada órgano con licitaciones > 0 entrar y extraer las licitaciones
# 5 - Comparar con las ya vistas en JSON
# 6 - Si hay nuevas → ENVIAR por email
# 7 - Guardar las nuevas en JSON


# ------------------------------
# GRUPO 0 - Importamos librerías necesarias para Webscrapping + CONSTANTES
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

URL_BASE = "https://contrataciondelestado.es/wps/portal/plataforma/perfil_contratante/lista_perfiles/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziHcNcAx09LY0N3IMCXA2MnILMzUzc_I0NDIz0w8EKTI2dTcK8wgLMgj3dDQw8PdxcfEINTQ3cjcz0o4jRb4ADOBoQpx-Pgij8xofrR-G3wgCqAJ8XCVlSkBsaGmGQ6QkATfmaFQ!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/IZ7_AVEQAI930GRPE02BR764FO30G0=CZ6_AVEQAI930GRPE02BR764FO3002=LA0=Ecom.ibm.faces.portlet.VIEWID!QCPjspQCPlistPerfilesQCPAdminAFPListPerfPortletAppView.jsp==/#Z7_AVEQAI930GRPE02BR764FO30G0"
COMUNIDAD = "Canarias"
TIEMPO_ESPERA = 10  # segundos para WebDriverWait
ID_SELECT_COMUNIDAD = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:menu111MAQ"
ID_BOTON_BUSCAR = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:botonbuscar"
CLASE_RESULTADOS = "badge"
ID_BOTON_SIGUIENTE = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:siguienteLink"


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

def filtrar_pagina_canarias(mi_navegador):
    print(f"Navegando a: {URL_BASE}")
    mi_navegador.get(URL_BASE)

    # esperamos que la página cargue
    esperar = WebDriverWait(mi_navegador, TIEMPO_ESPERA)
    print('Página cargando...')

    try:
        # Esperar el select
        menu = esperar.until(
            EC.presence_of_element_located((By.ID, ID_SELECT_COMUNIDAD))
        )
        print("Select encontrado!")

        # Creamos el objeto Select
        lista = Select(menu)

        print('Seleccionando Canarias...')
        lista.select_by_visible_text(COMUNIDAD)

        print('Canarias escogido')
        print('Buscando botón FILTRAR...')

        buscar_boton = esperar.until(
            EC.element_to_be_clickable((By.ID, ID_BOTON_BUSCAR))
        )
        buscar_boton.click()
        # Esperamos a que aparezca algún badge de licitaciones
        esperar.until(
            EC.presence_of_element_located((By.CLASS_NAME, CLASE_RESULTADOS))
        )
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def obtener_organos_con_licitaciones(mi_navegador):
    print("Leyendo órganos de Canarias...")
    organos = []
    pagina = 1

    while True:
        print(f"\nLeyendo página {pagina}...")
        soup = BeautifulSoup(mi_navegador.page_source, "html.parser")
        filas = soup.find_all("tr")

        for fila in filas:

            # Buscamos el número de licitaciones abiertas
            badge_licitaciones = fila.find("p", class_="badge info m-0")
            if not badge_licitaciones:
                continue

            # Convertimos a número y filtramos los que tienen 0
            num_licitaciones = int(badge_licitaciones.text.strip())
            if num_licitaciones == 0:
                continue

            # Cogemos el nombre del órgano
            nombre = fila.find("span", id=lambda i: i and "textoEnlace" in str(i))

            # Cogemos la URL directa
            enlace = fila.find("a", href=lambda h: h and "perfilContratante" in str(h))

            if nombre and enlace:
                organos.append(
                    {
                        "nombre": nombre.text.strip(),
                        "url": enlace["href"],
                        "licitaciones_abiertas": num_licitaciones,
                    }
                )
                print(f"{nombre.text.strip()} - {num_licitaciones} licitaciones")

        # Comprobamos si hay página siguiente
        try:
            boton_siguiente = mi_navegador.find_element(By.ID, ID_BOTON_SIGUIENTE)
            boton_siguiente.click()

            # Esperamos que cargue la siguiente página
            esperar = WebDriverWait(mi_navegador, TIEMPO_ESPERA)
            esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "badge")))
            pagina += 1

        except:
            # No hay botón siguiente, hemos llegado al final
            print(f"\nTotal páginas leídas: {pagina}")
            print(f"Total órganos con licitaciones > 0: {len(organos)}")
            break

    return organos


# ------------------------------
# GRUPO 3: MAIN
# ------------------------------

def main():
    print('Inciando navegador...')
    mi_navegador = iniciar_navegador()

    try: 
        resultado = filtrar_pagina_canarias(mi_navegador)

        if resultado:
            print('Filtro aplicado correctamente, continuamos...')
            organos = obtener_organos_con_licitaciones(mi_navegador)
            # AQUI PASOS SIGUIENTES
        else:
            print('Error al filtrar, cerrando...')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cerrar_navegador(mi_navegador)

# ------------------------------
# GRUPO 4: PUNTO DE ENTRADA
# ------------------------------
if __name__ == "__main__":
    main()
