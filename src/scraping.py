"""
Módulo de scraping para la contratación pública del estado

"""

# -----------------------------------------------
# GRUPO 0 - Importamos librerías necesarias para Webscrapping & CONSTANTES
# -----------------------------------------------

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
import random

from src.config import (
    URL_BASE,
    COMUNIDAD,
    TIEMPO_ESPERA,
    ID_SELECT_COMUNIDAD,
    ID_BOTON_BUSCAR,
    CLASE_RESULTADOS,
    ID_BOTON_SIGUIENTE,
    ID_FILTRO_ESTADO,
    ESTADO_PUBLICADA,
    ID_BOTON_BUSCAR_LIC,
)

# -----------------------------------------------
# GRUPO 1 - Iniciar/Cerrar Navegador
# -----------------------------------------------

def iniciar_navegador():
    print('Inciando navegador...')
    options = webdriver.ChromeOptions()
    # Evita que Chrome se cierre solo
    options.add_experimental_option("detach", True)

    # Español
    options.add_argument("--lang=es")
    options.add_experimental_option("prefs", {"intl.accept_languages": "es,es-ES"})

    # Hace que parezca un navegador normal
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Evita errores de memoria después de muchas páginas
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Elimina la detección de webdriver
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def cerrar_navegador(driver):
    driver.quit()
    print("Navegador cerrado")


# -----------------------------------------------
# GRUPO 2 - Funciones de Navegación
# -----------------------------------------------

def filtrar_pagina_canarias(driver):
    """
    Navega hasta la página de <<perfil contratantes>> y filtra los órganos por Canarias

    Args:
        driver (webdriver): Instancia del navegador WebDriver

    Returns:
        bool: True si el filtro se aplicó correctamente, False en caso de error
    """
    
    print(f"Navegando a: {URL_BASE}")
    driver.get(URL_BASE)
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)

    try:
        menu = esperar.until(
            EC.presence_of_element_located((By.ID, ID_SELECT_COMUNIDAD))
        )
        lista = Select(menu)
        lista.select_by_visible_text(COMUNIDAD)
        buscar_boton = esperar.until(
            EC.element_to_be_clickable((By.ID, ID_BOTON_BUSCAR))
        )
        buscar_boton.click()
        esperar.until(
            EC.presence_of_element_located((By.CLASS_NAME, CLASE_RESULTADOS))
        )
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def obtener_organos_con_licitaciones(driver):
    """
    Obtiene la lista de órganos con un número > 0 de licitaciones abiertas en Canarias 

    Args:
        driver (webdriver): Instancia del navegador WebDriver.

    Returns:
        list: Lista de diccionarios con los datos de cada órgano.
    """

    print("Leyendo órganos de Canarias...")
    organos = []
    pagina = 1

    while pagina <=2:
        print(f"\nLeyendo página {pagina}...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        filas = soup.find_all("tr")

        for fila in filas:

            badge_licitaciones = fila.find("p", class_="badge info m-0")
            if not badge_licitaciones:
                continue

            num_licitaciones = int(badge_licitaciones.text.strip())
            if num_licitaciones == 0:
                continue

            nombre = fila.find("span", id=lambda i: i and "textoEnlace" in str(i))

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

        try:
            boton_siguiente = driver.find_element(By.ID, ID_BOTON_SIGUIENTE)
            print(f"Botón siguiente encontrado")
            boton_siguiente.click()
            esperar = WebDriverWait(driver, TIEMPO_ESPERA)
            esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "badge")))
            pagina += 1

        except Exception as e:
            print(f"Botón siguiente NO encontrado: {e}")
            # No hay botón siguiente, hemos llegado al final
            print(f"\nTotal leídos: {len(organos)} órganos en {pagina} páginas")
            break

    return organos


# -----------------------------------------------
# FUNCIONES AUXILIARES A 'obtener_licitaciones_organo'
# -----------------------------------------------

def navegar_a_organo(driver, url):
    """Navega a la URL del órgano"""
    print("  Navegando a URL...")
    driver.get(url)
    time.sleep(random.uniform(3, 6))


def hacer_clic_pestanya_licitaciones(driver):
    """Busca la pestaña Licitaciones y hace clic"""
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)
    # Pequeña pausa para estabilizar el DOM después de cargar
    time.sleep(2)

    try:
        # Esperar a que el botón esté disponible y clickeable
        pestanya = esperar.until(
            EC.element_to_be_clickable(
                (By.ID, "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:perfilComp:linkPrepLic")
            )
        )
        # JavaScript evita el error de 'element not clickable'
        driver.execute_script("arguments[0].click();", pestanya)
        print("Pestaña Licitaciones clickeada")
        return True
    except Exception as e:
        print(f"Error al hacer clic en pestaña: {e}")
        return False


def aplicar_filtro_publicada(driver):
    """Selecciona Publicada en el filtro de estado"""
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)

    print("  Seleccionando filtro Publicada...")
    select_estado = esperar.until(
        EC.presence_of_element_located((By.ID, ID_FILTRO_ESTADO))
    )
    lista_estados = Select(select_estado)
    lista_estados.select_by_value(ESTADO_PUBLICADA)
    print("Filtro Publicada seleccionado")

    print("  Buscando botón Buscar...")
    boton_buscar = esperar.until(
        EC.element_to_be_clickable((By.ID, ID_BOTON_BUSCAR_LIC))
    )
    boton_buscar.click()
    time.sleep(2)

    try:
        esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "tdExpediente")))
        print("Licitaciones cargadas")
        return True
    except:
        print("Sin licitaciones publicadas")
        return False


def extraer_licitaciones_pagina(driver, nombre_organo):
    """Extrae todas las licitaciones de la página actual"""
    licitaciones = []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    filas = soup.find_all("tr", class_=lambda c: c in ["par", "impar"])

    for fila in filas:
        licitacion = extraer_licitacion_fila(fila, nombre_organo)
        if licitacion:
            licitaciones.append(licitacion)

    print(f"{len(licitaciones)} licitaciones publicadas encontradas")
    return licitaciones


def obtener_licitaciones_organo(driver, organo):
    """
    Obtiene todas las licitaciones publicadas de un órgano específico
    Llama a 4 funciones auxiliares del grupo

    Args:
        driver (webdriver): Instancia del navegador WebDriver.
        organo (dict): Diccionario con los datos del órgano.

    Returns:
        list: Lista de licitaciones publicadas del órgano.
    """

    print(f"\nEntrando en: {organo['nombre']}")
    licitaciones = []

    try:
        navegar_a_organo(driver, organo["url"])

        if not hacer_clic_pestanya_licitaciones(driver):
            print(f"No se encontró pestaña en {organo['nombre']}")
            return []

        aplicar_filtro_publicada(driver)
        return extraer_licitaciones_pagina(driver, organo["nombre"])

    except Exception as e:
        print(f"Error en {organo['nombre']}: {e}")
        return []


# -----------------------------------------------
# GRUPO 3 - Extraer datos & Guardarlos en JSON
# -----------------------------------------------


def extraer_licitacion_fila(fila, nombre_organo):
    """Extrae los datos de una sola fila de licitación"""

    expediente = fila.find("td", class_="tdExpediente")
    if not expediente:
        return None

    # Número de expediente
    numero_exp = expediente.find("span").text.strip() if expediente.find("span") else ""

    # URL
    enlace = expediente.find("a", href=lambda h: h and "detalle_licitacion" in str(h))
    url_licitacion = enlace["href"] if enlace else ""
    if url_licitacion and not url_licitacion.startswith("http"):
        url_licitacion = "https://contrataciondelestado.es" + url_licitacion

    # ID
    id_licitacion = url_licitacion.split("idEvl=")[-1] if url_licitacion else numero_exp

    # Tipo
    tipo = fila.find("td", class_="tdTipoContrato")
    tipo = tipo.text.strip() if tipo else ""

    # Objeto
    objeto = fila.find("td", class_="tdTipoContratoLicOC")
    objeto = objeto.text.strip() if objeto else ""

    # Estado
    estado = fila.find("td", class_="tdEstado")
    estado = estado.text.strip() if estado else ""

    # Importe
    importe = fila.find("td", class_="tdImporte")
    importe = importe.text.strip() if importe else ""

    # Fecha
    fechas = fila.find("td", class_="tdFecha")
    fecha = ""
    if fechas:
        span_fecha = fechas.find("span", class_="textAlignLeft")
        fecha = span_fecha.text.strip() if span_fecha else ""

    return {
        "id": id_licitacion,
        "expediente": numero_exp,
        "organo": nombre_organo,
        "objeto": objeto,
        "tipo": tipo,
        "estado": estado,
        "importe": importe,
        "fecha": fecha,
        "url": url_licitacion,
    }


def guardar_licitaciones_en_json(licitaciones):
    """Guarda las licitaciones en un archivo JSON fijo"""

    os.makedirs("datos", exist_ok=True)
    nombre_archivo = "datos/licitaciones_extraidas.json"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(licitaciones, f, ensure_ascii=False, indent=2)

    print(f"Datos guardados en: {nombre_archivo}")
    print(f"Total licitaciones: {len(licitaciones)}")


# -----------------------------------------------
# GRUPO 4 - MAIN
# -----------------------------------------------

def main_scraping():
    print("Iniciando scraping...")
    driver = iniciar_navegador()
    todas_licitaciones = []

    try: 
        resultado = filtrar_pagina_canarias(driver)

        if resultado:
            print('Filtro aplicado correctamente, continuamos...')
            print("\nEstabilizando página antes de procesar órganos...")
            time.sleep(3)
            organos = obtener_organos_con_licitaciones(driver)

            for organo in organos[:20]:
                licitaciones = obtener_licitaciones_organo(driver, organo)
                todas_licitaciones.extend(licitaciones)
                # Pausa aleatoria entre órganos
                pausa = random.uniform(2, 5)
                print(f"Esperando {pausa:.1f} segundos...")
                time.sleep(pausa)

            # 1. Guardar en JSON (para que puedas ver los datos)
            guardar_licitaciones_en_json(todas_licitaciones)
        
            # 2. Devolver los datos (para que main.py los use)
            return todas_licitaciones
        else:
            print('Error al filtrar, cerrando...')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cerrar_navegador(driver)

# -----------------------------------------------
# GRUPO 5 - PUNTO DE ENTRADA
# -----------------------------------------------
if __name__ == "__main__":
    main_scraping()
