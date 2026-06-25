"""
Módulo de scraping v2 - Flujo por Canarias sin filtro CIF previo
"""
# -----------------------------------------------
# GRUPO 0 - Librerías necesarias para Webscrapping & CONSTANTES
# -----------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import random
import json
import os

from src.config import (
    URL_BASE,
    COMUNIDAD,
    TIEMPO_ESPERA,
    TIEMPO_ESPERA_LARGO,
    ID_SELECT_COMUNIDAD,
    ID_BOTON_BUSCAR,
    ID_CAMPO_NIF_ORGANO,
    ID_BOTON_SIGUIENTE,
    ID_BOTON_LICITACIONES,
    CLASE_RESULTADOS,
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

    print(f"Aplicando filtro de Canarias...")
    driver.get(URL_BASE)
    esperar = WebDriverWait(driver, TIEMPO_ESPERA_LARGO)

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
        print(f"Error al filtrar por Canarias: {type(e).__name__}")
        return False


def obtener_organos_canarias_con_licitaciones(driver):
    """
    Recorre todas las páginas de Canarias y devuelve órganos con licitacines abiertas(badge) > 0
    
    Args:
        driver (webdriver): Instancia del navegador WebDriver

    Returns:
        list: Lista de diccionarios con nombre, url y número de licitaciones abiertas
    """

    organos = []
    pagina = 1
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)
    esperar_largo = WebDriverWait(driver, TIEMPO_ESPERA_LARGO)

    while True:
        print(f"Leyendo página {pagina}...")

        try:
            esperar_largo.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.badge.info.m-0"))
            )
            time.sleep(1)
        except:
            print(f"Sin badges en página {pagina}, continuando...")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        filas = soup.find_all("tr")

        for fila in filas:
            badge = fila.find("p", class_="badge info m-0")
            if not badge or int(badge.text.strip()) == 0:
                continue

            nombre = fila.find("span", id=lambda i: i and "textoEnlace" in str(i))
            enlace = fila.find("a", href=lambda h: h and "perfilContratante" in str(h))

            if nombre and enlace:
                num_licitaciones = int(badge.text.strip())
                organos.append(
                    {
                        "nombre": nombre.text.strip(),
                        "url": enlace["href"],
                        "licitaciones_abiertas": num_licitaciones,
                    }
                )
                print(f"{nombre.text.strip()} - {num_licitaciones} licitaciones")

        # Pasar a la siguiente página si existe
        try:
            esperar.until(
                EC.element_to_be_clickable((By.ID, ID_BOTON_SIGUIENTE))
            ).click()
            esperar.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.badge.info.m-0"))
            )
            pagina += 1
            time.sleep(random.uniform(2, 4))
        except:
            print(f"No hay más páginas — total páginas leídas: {pagina}")
            break

    print(f"\nTotal órganos con licitaciones abiertas: {len(organos)}")
    return organos


def obtener_cif_organo(driver, url):
    """
    Navega al perfil del órgano y extrae su CIF/NIF.
    
     Args:
        driver (webdriver): Instancia del navegador WebDriver
        url (str): URL del perfil del órgano

    Returns:
        str: CIF del órgano, o None si no se pudo leer
    """

    driver.get(url)
    time.sleep(random.uniform(2, 4))

    try:
        esperar = WebDriverWait(driver, TIEMPO_ESPERA)
        cif_elemento = esperar.until(
            EC.presence_of_element_located((By.ID, ID_CAMPO_NIF_ORGANO))
        )
        cif = cif_elemento.text.strip()
        return cif

    except Exception as e:
        print(f"Error al leer CIF: {type(e).__name__}")
        return None


def hacer_clic_pestanya_licitaciones(driver):
    """
    Hace clic en la pestaña Licitaciones del perfil del órgano.

    Args:
        driver (webdriver): Instancia del navegador WebDriver

    Returns:
        bool: True si se hizo clic correctamente, False en caso de error
    """

    esperar = WebDriverWait(driver, TIEMPO_ESPERA)
    time.sleep(2)

    try:
        pestanya = esperar.until(
            EC.element_to_be_clickable(
                (By.ID, ID_BOTON_LICITACIONES)
            )
        )
        # JavaScript evita el error de 'element not clickable'
        driver.execute_script("arguments[0].click();", pestanya)
        return True

    except Exception as e:
        print(f"Error al hacer clic en pestaña licitaciones: {type(e).__name__}")
        return False


def aplicar_filtro_publicada(driver):
    """
    Selecciona el filtro 'Publicada' en la pestaña de licitaciones y lanza la búsqueda

    Args:
        driver (webdriver): Instancia del navegador WebDriver

    Returns:
        bool: True si hay licitaciones publicadas, False si no hay o hay error
    """

    esperar = WebDriverWait(driver, TIEMPO_ESPERA)    

    try:
        select_estado = esperar.until(
        EC.presence_of_element_located((By.ID, ID_FILTRO_ESTADO))
        )

        lista_estados = Select(select_estado)
        lista_estados.select_by_value(ESTADO_PUBLICADA)      

        boton_buscar = esperar.until(
            EC.element_to_be_clickable((By.ID, ID_BOTON_BUSCAR_LIC))
        )
        boton_buscar.click()
        time.sleep(2)

        esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "tdExpediente")))
        return True
    
    except Exception as e:
        print(f"Sin licitaciones publicadas: {type(e).__name__}")
        return False


def extraer_licitaciones_pagina(driver, nombre_organo, cif_organo=""):
    """
    Extrae todas las licitaciones de la página actual
    
    Args:
        driver (webdriver): Instancia del navegador WebDriver
        nombre_organo (str): Nombre del órgano contratante
        cif_organo (str): CIF del órgano contratante

    Returns:
        list: Lista de licitaciones extraídas de la página

    """
    
    licitaciones = []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    filas = soup.find_all("tr", class_=lambda c: c in ["par", "impar"])

    for fila in filas:
        licitacion = extraer_licitacion_fila(fila, nombre_organo, cif_organo)
        if licitacion:
            licitaciones.append(licitacion)

    print(f"{len(licitaciones)} licitaciones publicadas encontradas")
    return licitaciones


def extraer_licitacion_fila(fila, nombre_organo, cif_organo=""):
    """
    Extrae los datos de una sola fila de licitación
    
    Args:
        fila: Elemento BeautifulSoup con los datos de la fila
        nombre_organo (str): Nombre del órgano contratante
        cif_organo (str): CIF del órgano contratante

    Returns:
        dict: Datos de la licitación, o None si la fila no contiene licitación
    """

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
        "cif": cif_organo,
        "organo": nombre_organo,
        "objeto": objeto,
        "tipo": tipo,
        "estado": estado,
        "importe": importe,
        "fecha": fecha,
        "url": url_licitacion,
    }


def main_scraping():
    """
    Flujo principal del scraping
    
    1. Filtra por Canarias y obtiene todos los órganos con licitaciones abiertas
    2. Por cada órgano, lee su CIF y compara con la lista permitida
    3. Si el CIF está en la lista, extrae sus licitaciones publicadas
    4. Guarda progresivamente en JSON

    Returns:
        list: Lista de todas las licitaciones extraídas
    """

    print("Iniciando scraping...")
    driver = iniciar_navegador()
    todas_licitaciones = []

    try:
        from src.config import cargar_cifs_permitidos
        cifs_permitidos = set(cargar_cifs_permitidos())

        # PASO 1: Filtrar Canarias y obtener órganos con licitaciones abiertas
        if not filtrar_pagina_canarias(driver):
            print("Error al filtrar por Canarias. Abortando.")
            return []

        organos = obtener_organos_canarias_con_licitaciones(driver)
        print(f"\nTotal órganos con licitaciones abiertas: {len(organos)}")

        # PASO 2: Por cada órgano, leer CIF y comparar con lista
        for i, organo in enumerate(organos, 1):
            print(f"\n[{i}/{len(organos)}] {organo['nombre']}")

            cif = obtener_cif_organo(driver, organo["url"])

            if not cif:
                print("No se pudo leer el CIF, saltando...")
                continue

            if cif not in cifs_permitidos:
                print(f"CIF {cif} no está en la lista, saltando...")
                continue

            print(f"CIF {cif} está en la lista, extrayendo licitaciones...")

            # PASO 3: Extraer licitaciones
            if not hacer_clic_pestanya_licitaciones(driver):
                print(f"No se encontró pestaña licitaciones")
                continue

            try:
                if aplicar_filtro_publicada(driver):
                    licitaciones = extraer_licitaciones_pagina(driver, organo["nombre"], cif)
                    todas_licitaciones.extend(licitaciones)
                    os.makedirs("datos", exist_ok=True)
                    with open("datos/licitaciones_hoy.json", "w", encoding="utf-8") as f:
                        json.dump(todas_licitaciones, f, ensure_ascii=False, indent=2)
                    print(
                        f"Progreso guardado: {len(todas_licitaciones)} licitaciones"
                    )
            except Exception as e:
                print(
                    f"Error extrayendo licitaciones de {organo['nombre']}: {type(e).__name__}"
                )
                continue

            time.sleep(random.uniform(2, 4))

        print(
            f"\nSCRAPPING COMPLETADO — {len(todas_licitaciones)} licitaciones extraídas"
        )
        return todas_licitaciones

    except Exception as e:
        print(f"Error en scraping: {type(e).__name__}: {e}")
        return []
    finally:
        cerrar_navegador(driver)


if __name__ == "__main__":
    main_scraping()
