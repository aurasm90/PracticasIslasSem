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
from datetime import datetime
import json
import os
import time
import random

URL_BASE = "https://contrataciondelestado.es/wps/portal/plataforma/perfil_contratante/lista_perfiles/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziHcNcAx09LY0N3IMCXA2MnILMzUzc_I0NDIz0w8EKTI2dTcK8wgLMgj3dDQw8PdxcfEINTQ3cjcz0o4jRb4ADOBoQpx-Pgij8xofrR-G3wgCqAJ8XCVlSkBsaGmGQ6QkATfmaFQ!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/IZ7_AVEQAI930GRPE02BR764FO30G0=CZ6_AVEQAI930GRPE02BR764FO3002=LA0=Ecom.ibm.faces.portlet.VIEWID!QCPjspQCPlistPerfilesQCPAdminAFPListPerfPortletAppView.jsp==/#Z7_AVEQAI930GRPE02BR764FO30G0"
COMUNIDAD = "Canarias"
TIEMPO_ESPERA = 10  # segundos para WebDriverWait
ID_SELECT_COMUNIDAD = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:menu111MAQ"
ID_BOTON_BUSCAR = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:botonbuscar"
CLASE_RESULTADOS = "badge"
ID_BOTON_SIGUIENTE = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:siguienteLink"
ID_PESTANYA_LICITACIONES = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:textLinkLic"
ID_FILTRO_ESTADO = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:busReasProc11"
ID_BOTON_LICITACIONES = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:perfilComp:linkPrepLic"
ESTADO_PUBLICADA = "PUB"
ID_BOTON_BUSCAR_LIC = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:busReasProc18"

# ------------------------------
# GRUPO 1 - Iniciar/Cerrar Navegador
# ------------------------------

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


# ------------------------------
# GRUPO 2 - Funciones de Navegación
# ------------------------------

# FC que abre filtra los órganos con licitaciones por Canarias
def filtrar_pagina_canarias(driver):
    print(f"Navegando a: {URL_BASE}")
    driver.get(URL_BASE)

    # esperamos que la página cargue
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)
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


# FC que obtiene los órganos con licitaciones abiertas/activas > 0
def obtener_organos_con_licitaciones(driver):
    print("Leyendo órganos de Canarias...")
    organos = []
    pagina = 1

    while pagina <=1:
        print(f"\nLeyendo página {pagina}...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
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
            boton_siguiente = driver.find_element(By.ID, ID_BOTON_SIGUIENTE)
            boton_siguiente.click()

            # Esperamos que cargue la siguiente página
            esperar = WebDriverWait(driver, TIEMPO_ESPERA)
            esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "badge")))
            pagina += 1

        except:
            # No hay botón siguiente, hemos llegado al final
            print(f"\nTotal páginas leídas: {pagina}")
            print(f"Total órganos con licitaciones > 0: {len(organos)}")
            break

    return organos


# FC que entra en la pesataña 'Licitaciones' de cada órgano y filtra por <<Publicadas>>
def obtener_licitaciones_organo(driver, organo):
    print(f"\nEntrando en: {organo['nombre']}")
    licitaciones = []

    try:
        # 1. Navegar a la URL
        navegar_a_organo(driver, organo["url"])

        # 2. Hacer clic en pestaña Licitaciones
        if not hacer_clic_pestanya_licitaciones(driver):
            print(f"No se encontró pestaña en {organo['nombre']}")
            return []

        # 3. Aplicar filtro "Publicada"
        aplicar_filtro_publicada(driver)

        # 4. Buscar licitaciones
        return extraer_licitaciones_pagina(driver, organo["nombre"])

    except Exception as e:
        print(f"Error en {organo['nombre']}: {e}")
        return []


# ============================================
# 1. Navegar al órgano
# ============================================


def navegar_a_organo(driver, url):
    """Navega a la URL del órgano"""
    print("  Navegando a URL...")
    driver.get(url)
    time.sleep(random.uniform(3, 6))
    print(" URL cargada")


# ============================================
# 2. Buscar y hacer clic en pestaña Licitaciones
# ============================================


def hacer_clic_pestanya_licitaciones(driver):
    """Busca la pestaña Licitaciones y hace clic"""
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)

    # Esperar a que la página se estabilice
    time.sleep(2)

    try:
        # Buscar el botón por su ID exacto
        pestanya = esperar.until(
            EC.element_to_be_clickable(
                (By.ID, "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:perfilComp:linkPrepLic")
            )
        )
        # Hacer clic con JavaScript (más fiable)
        driver.execute_script("arguments[0].click();", pestanya)
        print("Pestaña Licitaciones clickeada")
        return True
    except Exception as e:
        print(f"Error al hacer clic: {e}")
        return False


# ============================================
# 3. Aplicar filtro "Publicada"
# ============================================


def aplicar_filtro_publicada(driver):
    """Selecciona Publicada en el filtro de estado"""
    esperar = WebDriverWait(driver, TIEMPO_ESPERA)

    print("  Seleccionando filtro Publicada...")
    select_estado = esperar.until(
        EC.presence_of_element_located((By.ID, ID_FILTRO_ESTADO))
    )
    lista_estados = Select(select_estado)
    lista_estados.select_by_value("PUB")
    print("Filtro Publicada seleccionado")

    # Hacer clic en Buscar
    print("  Buscando botón Buscar...")
    boton_buscar = esperar.until(
        EC.element_to_be_clickable((By.ID, ID_BOTON_BUSCAR_LIC))
    )
    boton_buscar.click()
    time.sleep(2)

    # Esperar resultados
    try:
        esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "tdExpediente")))
        print("Licitaciones cargadas")
        return True
    except:
        print("Sin licitaciones publicadas")
        return False


# ============================================
# 4. Extraer licitaciones de la página
# ============================================


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


# ============================================
# 5. Extraer una sola fila de licitación
# ============================================


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


# ------------------------------
# GRUPO 3: MAIN
# ------------------------------

def main_scraping():
    print("Iniciando scraping...")
    driver = iniciar_navegador()
    todas_licitaciones = []

    try: 
        resultado = filtrar_pagina_canarias(driver)

        if resultado:
            print('Filtro aplicado correctamente, continuamos...')
            organos = obtener_organos_con_licitaciones(driver)

            for organo in organos[:10]:
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

# ------------------------------
# GRUPO 4: PUNTO DE ENTRADA
# ------------------------------
if __name__ == "__main__":
    main_scraping()
