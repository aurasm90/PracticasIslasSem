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
ID_PESTANYA_LICITACIONES = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:textLinkLic"
ID_FILTRO_ESTADO = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:busReasProc11"
ID_BOTON_BUSCAR_LIC = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:busReasProc18"
ESTADO_PUBLICADA = "PUB"


# ------------------------------
# GRUPO 1 - Iniciar/Cerrar Navegador
# ------------------------------

def iniciar_navegador():

    options = webdriver.ChromeOptions()
    # Evita que Chrome se cierre solo
    options.add_experimental_option("detach", True)

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

    while pagina <=1:
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


def obtener_licitaciones_organo(mi_navegador, organo):
    print(f"\nEntrando en: {organo['nombre']}")
    licitaciones = []

    try:
        print("Navegando a URL...")
        mi_navegador.get(organo["url"])
        time.sleep(2)  # ← pausa para que cargue

        print("Buscando pestaña...")
        esperar = WebDriverWait(mi_navegador, TIEMPO_ESPERA)

        # Hacemos clic en la pestaña Licitaciones
        pestanya = esperar.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Licitaciones')]")))
        pestanya.click()
        print("Pestaña Licitaciones abierta")

        # Seleccionamos "Publicada" en el filtro de estado
        select_estado = esperar.until(
            EC.presence_of_element_located((By.ID, ID_FILTRO_ESTADO))
        )
        lista_estados = Select(select_estado)
        lista_estados.select_by_value(ESTADO_PUBLICADA)
        print("Filtro Publicada seleccionado")

        # Hacemos clic en Buscar
        boton_buscar = esperar.until(
            EC.element_to_be_clickable((By.ID, ID_BOTON_BUSCAR_LIC))
        )
        boton_buscar.click()

        # Esperamos que carguen los resultados
        esperar.until(EC.presence_of_element_located((By.CLASS_NAME, "tdExpediente")))
        print("Licitaciones cargadas")

        # Extraemos los datos
        soup = BeautifulSoup(mi_navegador.page_source, "html.parser")
        filas = soup.find_all("tr", class_=lambda c: c in ["par", "impar"])

        for fila in filas:
            # Número de expediente
            expediente = fila.find("td", class_="tdExpediente")
            if not expediente:
                continue

            numero = (
                expediente.find("span").text.strip() if expediente.find("span") else ""
            )

            # URL directa de la licitación
            enlace = expediente.find(
                "a", href=lambda h: h and "detalle_licitacion" in str(h)
            )
            url_licitacion = enlace["href"] if enlace else ""

            # ID único
            id_licitacion = (
                url_licitacion.split("idEvl=")[-1] if url_licitacion else numero
            )

            # Tipo
            tipo = fila.find("td", class_="tdTipoContrato")
            tipo = tipo.text.strip() if tipo else ""

            # Objeto
            objeto = fila.find("td", class_="tdTipoContratoLicOC")
            objeto = objeto.text.strip() if objeto else ""

            # Importe
            importe = fila.find("td", class_="tdImporte")
            importe = importe.text.strip() if importe else ""

            # Fecha
            fechas = fila.find("td", class_="tdFecha")
            fecha = ""
            if fechas:
                span_fecha = fechas.find("span", class_="textAlignLeft")
                fecha = span_fecha.text.strip() if span_fecha else ""

            licitaciones.append(
                {
                    "id": id_licitacion,
                    "numero": numero,
                    "organo": organo["nombre"],
                    "tipo": tipo,
                    "objeto": objeto,
                    "importe": importe,
                    "fecha": fecha,
                    "url": url_licitacion,
                }
            )

        print(f"{len(licitaciones)} licitaciones publicadas encontradas")

    except Exception as e:
        print(f"Error en {organo['nombre']}: {e}")

    return licitaciones


# ------------------------------
# GRUPO 3: MAIN
# ------------------------------

def main():
    print('Inciando navegador...')
    mi_navegador = iniciar_navegador()
    todas_licitaciones = []

    try: 
        resultado = filtrar_pagina_canarias(mi_navegador)

        if resultado:
            print('Filtro aplicado correctamente, continuamos...')
            organos = obtener_organos_con_licitaciones(mi_navegador)
            for organo in organos[:1]:
                licitaciones = obtener_licitaciones_organo(mi_navegador, organo)
                todas_licitaciones.extend(licitaciones)

            print(f"\nTotal licitaciones publicadas: {len(todas_licitaciones)}")

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
