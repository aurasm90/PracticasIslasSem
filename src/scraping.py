"""
Módulo de scraping para la Plataforma de Contratación del Sector Público.

Flujo principal:
    1. Filtra los perfiles de contratantes por Comunidad Autónoma (Canarias)
    2. Recorre todas las páginas de resultados y recopila los órganos
       que tienen licitaciones abiertas (badge > 0)
    3. Por cada órgano, navega a su perfil y lee su CIF
    4. Si el CIF está en la lista de organismos permitidos, extrae
       todas sus licitaciones en estado 'Publicada'
    5. Guarda los resultados progresivamente en datos/licitaciones_hoy.json
"""

# -----------------------------------------------
# GRUPO 0 - Librerías necesarias para Webscrapping & CONSTANTES
# -----------------------------------------------

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.logger_config import logger
import time
import random
import json

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
    ARCHIVO_HOY,
)

# -----------------------------------------------
# GRUPO 1 - Iniciar/Cerrar Navegador
# -----------------------------------------------

def iniciar_navegador():
    logger.info("Iniciando navegador...")

    try:
        options = webdriver.ChromeOptions()

        # Español
        options.add_experimental_option("prefs", {"intl.accept_languages": "es,es-ES"})

        # Específico para Azure - Headless
        options.add_argument("--headless=new")  
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        # Rendimiento
        options.add_argument("--window-size=1920,1080")

        # User agent (importante)
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Espera máximo 30 segundos a que una página/JS cargue completamente
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)

        logger.info("Navegador iniciado correctamente")
        return driver

    except WebDriverException as e:
        logger.exception("ERROR al iniciar Chrome")
        raise


def cerrar_navegador(driver):
    try:
        if driver:
            driver.quit()
            logger.info("Navegador cerrado")
    except Exception as e:
        logger.exception("ERROR al cerrar navegador")


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
    try:
        logger.info(f"Aplicando filtro de Canarias en URL: {URL_BASE}")
        driver.get(URL_BASE)
        esperar = WebDriverWait(driver, TIEMPO_ESPERA_LARGO)

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
        logger.exception("Error al filtrar por Canarias")
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
        logger.info(f"Leyendo página {pagina}...")

        try:
            esperar_largo.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.badge.info.m-0"))
            )
        except:
            logger.warning(f"Sin badges en página {pagina}, continuando...")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        filas = soup.find_all("tr")

        for fila in filas:
            try: 
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
                    logger.info(
                        f"{nombre.text.strip()} - {num_licitaciones} licitaciones"
                    )
            except Exception as e:
                logger.warning("Error leyendo fila")
                continue

        # Pasar a la siguiente página si existe
        try:
            btn_siguiente = driver.find_elements(By.ID, ID_BOTON_SIGUIENTE)
            if not btn_siguiente:
                logger.info(
                    f"Última página alcanzada ({pagina}). Total órganos: {len(organos)}"
                )
                break
            
            esperar.until(
                EC.element_to_be_clickable((By.ID, ID_BOTON_SIGUIENTE))
            ).click()
            esperar.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.badge.info.m-0"))
            )
            pagina += 1
            time.sleep(random.uniform(5, 8))
            
        except Exception as e:
            logger.exception(
                f"Error al pasar de página — total páginas leídas: {pagina}"
            )
            break

    logger.info(f"\nTotal órganos con licitaciones abiertas: {len(organos)}")
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
    
    try:
        driver.get(url)

        esperar = WebDriverWait(driver, TIEMPO_ESPERA)

        cif_elemento = esperar.until(
            EC.visibility_of_element_located((By.ID, ID_CAMPO_NIF_ORGANO))
        )

        cif = cif_elemento.text.strip() or cif_elemento.get_attribute("value")

        return cif

    except Exception as e:
        logger.exception("Error al leer CIF")
        return None


def hacer_clic_pestanya_licitaciones(driver):
    """
    Hace clic en la pestaña Licitaciones del perfil del órgano.

    Args:
        driver (webdriver): Instancia del navegador WebDriver

    Returns:
        bool: True si se hizo clic correctamente, False en caso de error
    """

    try:
        esperar = WebDriverWait(driver, TIEMPO_ESPERA)

        pestanya = esperar.until(
            EC.element_to_be_clickable(
                (By.ID, ID_BOTON_LICITACIONES)
            )
        )
        # JavaScript evita el error de 'element not clickable'
        driver.execute_script("arguments[0].click();", pestanya)
        return True

    except Exception as e:
        logger.exception(
            f"Error al hacer clic en pestaña licitaciones ({driver.current_url})"
        )
        return False


def aplicar_filtro_publicada(driver):
    """
    Selecciona el filtro 'Publicada' en la pestaña de licitaciones y lanza la búsqueda

    Args:
        driver (webdriver): Instancia del navegador WebDriver

    Returns:
        bool: True si hay licitaciones publicadas, False si no hay o hay error
    """

    try:
        esperar = WebDriverWait(driver, TIEMPO_ESPERA)

        select_estado = esperar.until(
        EC.presence_of_element_located((By.ID, ID_FILTRO_ESTADO))
        )

        lista_estados = Select(select_estado)
        lista_estados.select_by_value(ESTADO_PUBLICADA)

        time.sleep(5)

        select_estado = Select(driver.find_element(By.ID, ID_FILTRO_ESTADO))
        logger.info(f"Estado seleccionado: {select_estado.first_selected_option.text}")

        #  Guardamos referencia a una fila ya presente (si la hay) para
        # detectar que la tabla se ha refrescado tras aplicar el filtro
        filas_previas = driver.find_elements(By.CLASS_NAME, "tdExpediente")

        boton_buscar = esperar.until(
            EC.element_to_be_clickable((By.ID, ID_BOTON_BUSCAR_LIC))
        )
        boton_buscar.click()

        if filas_previas:
            esperar.until(EC.staleness_of(filas_previas[0]))

        # Esperar a que termine la carga
        esperar.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for fila in soup.find_all("tr", class_=lambda c: c in ["par", "impar"]):
            estado = fila.find("td", class_="tdEstado")
            if estado:
                logger.info(f"Estado encontrado: {estado.text.strip()}")

        esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "tdExpediente")))
        return True

    except Exception:
        logger.info("Sin licitaciones publicadas")
        return False


def obtener_pagina_actual_y_total(driver):
    """
    Lee el número de página actual y el total de páginas del paginador de licitaciones.
    Devuelve (pagina_actual, total_paginas) o (1, 1) si no encuentra el paginador.
    """
    
    try:
        pagina_actual = driver.find_element(
            By.CSS_SELECTOR, "span[id$='textNumPagasdasd']"
        ).text.strip()

        total_paginas = driver.find_element(
            By.CSS_SELECTOR, "span[id$='textTotalPaginaasdasd']"
        ).text.strip()

        return int(pagina_actual), int(total_paginas)

    except Exception:
        return 1, 1


def extraer_todas_licitaciones_organo(driver, nombre_organo, cif_organo=""):
    """
    Extrae todas las licitaciones publicadas de un órgano,
    recorriendo todas las páginas de resultados.

    Args:
        driver (webdriver): Instancia del navegador WebDriver
        nombre_organo (str): Nombre del órgano contratante
        cif_organo (str): CIF del órgano contratante

    Returns:
        list: Lista de todas las licitaciones extraídas
    """
    
    todas_extraidas = []
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)

    while True:
        pagina_actual, total_paginas = obtener_pagina_actual_y_total(driver)
        logger.info(f"  Página {pagina_actual}/{total_paginas} — {nombre_organo}")

        todas_extraidas.extend(extraer_licitaciones_pagina(driver, nombre_organo, cif_organo))

        if pagina_actual >= total_paginas:
            logger.info(f"  Última página alcanzada ({pagina_actual})")
            break

        try:
            filas_previas = driver.find_elements(By.CLASS_NAME, "tdExpediente")

            boton_siguiente = driver.find_element(
                By.CSS_SELECTOR, "input[id$='siguienteLink']"
            )
            driver.execute_script("arguments[0].click();", boton_siguiente)

            if filas_previas:
                esperar.until(EC.staleness_of(filas_previas[0]))

            esperar.until(
                EC.presence_of_element_located((By.CLASS_NAME, "tdExpediente"))
            )

            time.sleep(random.uniform(2, 4))

        except Exception:
            logger.warning(
                f"  Error al pasar de página en {nombre_organo}, parando aquí"
            )
            break

    logger.info(f"  Total extraídas de {nombre_organo}: {len(todas_extraidas)}")
    return todas_extraidas


def extraer_licitaciones_pagina(driver, nombre_organo, cif_organo=""):
    """
    Extrae todas las licitaciones publicadas de un órgano
    
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

    logger.info(f"{len(licitaciones)} licitaciones publicadas encontradas")
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
    span = expediente.find("span")
    numero_exp = span.text.strip() if span and span.text else ""

    # URL
    enlace = expediente.find("a", href=lambda h: h and "detalle_licitacion" in str(h))
    url_licitacion = enlace["href"] if enlace else ""

    if url_licitacion:
        url_licitacion = urljoin("https://contrataciondelestado.es", url_licitacion)

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
    if estado.lower() != "publicada":
        logger.info(f"Descartando expediente {numero_exp}: estado = {estado}")
        return None

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


# -----------------------------------------------
# GRUPO 3 - Funciones de Manejo del flujo
# -----------------------------------------------

def obtener_organos(driver):
    """
    Filtra la plataforma por Canarias y devuelve todos los órganos
    con al menos una licitación abierta (badge > 0).

    Args:
        driver (webdriver): Instancia del navegador WebDriver

    Returns:
        list: Lista de órganos encontrados, o lista vacía si el filtro falla
    """
    
    if not filtrar_pagina_canarias(driver):
        logger.warning("Error filtrando Canarias")
        return []

    organos = obtener_organos_canarias_con_licitaciones(driver)
    logger.info(f"Órganos encontrados: {len(organos)}")

    return organos


def procesar_organos(driver, organos):
    """
    Por cada órgano, navega a su perfil, lee su CIF y lo compara
    con la lista de organismos permitidos. Si el CIF está en la lista,
    extrae todas sus licitaciones en estado 'Publicada'.

    Args:
        driver (webdriver): Instancia del navegador WebDriver
        organos (list): Lista de órganos obtenida por obtener_organos()

    Returns:
        list: Lista de todas las licitaciones publicadas encontradas
    """

    from src.config import cargar_cifs_permitidos

    cifs_permitidos = set(cargar_cifs_permitidos())
    todas_licitaciones = []

    logger.info(f"Procesando {len(organos)} órganos...")

    for i, organo in enumerate(organos, 1):
        logger.info(f"[{i}/{len(organos)}] {organo['nombre']}")

        try:
            cif = obtener_cif_organo(driver, organo["url"])

        except Exception as e:
            logger.exception(
                f"Error obteniendo CIF en {organo['nombre']}"
            )
            continue

        if not cif:
            logger.warning("CIF no encontrado, saltando")
            time.sleep(random.uniform(1, 3))
            continue

        if cif not in cifs_permitidos:
            logger.warning(f"CIF {cif} no permitido, saltando")
            time.sleep(random.uniform(1, 3))
            continue

        logger.info(f"CIF válido ({cif}), extrayendo licitaciones")

        if not hacer_clic_pestanya_licitaciones(driver):
            logger.warning("No se pudo abrir pestaña licitaciones, saltando")
            continue

        try: 
            if not aplicar_filtro_publicada(driver):
                logger.warning("No se pudo aplicar el filtro Publicada")
                continue     

            licitaciones = extraer_todas_licitaciones_organo(
                driver, organo["nombre"], cif
            )
            num = len(licitaciones)
            todas_licitaciones.extend(licitaciones)
            logger.info(f"{num} licitaciones extraídas")

        except Exception as e:
            logger.exception(
                f"Error extrayendo licitaciones en órgano {organo['nombre']}"
            )
            continue

        time.sleep(random.uniform(5, 10))

    logger.info(f"\nTOTAL FINAL: {len(todas_licitaciones)} licitaciones")
    return todas_licitaciones


def guardar_resultados_scraping(licitaciones):
    """
    Filtra las licitaciones recibidas para conservar solo las que están
    en estado 'Publicada' y guarda el resultado en datos/licitaciones_hoy.json.

    Si se descarta alguna licitación en este paso, se registra un aviso en el log
    como señal de que alguna capa anterior del filtro no funcionó correctamente.

    Args:
        licitaciones (list): Lista de licitaciones extraídas por procesar_organos()
    """

    licitaciones_validas = [
        lic
        for lic in licitaciones
        if lic.get("estado", "").strip().lower() == "publicada"
    ]

    descartadas = len(licitaciones) - len(licitaciones_validas)
    if descartadas:
        logger.warning(
            f"Descartadas {descartadas} licitaciones sin estado 'Publicada' antes de guardar"
        )

    with open(ARCHIVO_HOY, "w", encoding="utf-8") as f:
        json.dump(licitaciones_validas, f, ensure_ascii=False, indent=2)

    logger.info(f"Guardado JSON con {len(licitaciones_validas)} licitaciones")


def main_scraping():
    """
    Flujo principal del scraping

    1. Obtiene órganos con licitaciones
    2. Procesa órganos (CIF + licitaciones)
    3. Guarda resultados en JSON

    Returns:
        bool: True si el scraping se ejecutó correctamente, False si falló
    """

    logger.info("Iniciando scraping...")
    driver = iniciar_navegador()

    try:
        organos = obtener_organos(driver)

        if not organos:
            logger.warning("No se encontraron órganos")
            return False

        licitaciones = procesar_organos(driver, organos)

        if licitaciones is None:
            licitaciones = []

        guardar_resultados_scraping(licitaciones)
        logger.info(f"¡Scraping completado con éxito!")
        return True

    except Exception as e:
        logger.exception("Error en main_scraping")
        return False

    finally:
        cerrar_navegador(driver)


if __name__ == "__main__":
    main_scraping()
