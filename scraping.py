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
# PASO 1 - Iniciar Navegador
# ------------------------------

def iniciar_navegador():
    
    options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# ------------------------------
# PASO 2 - Obtener lista de Órganos de Canarias
# ------------------------------

def obtener_organos_canarias(driver):
    print("Obteniendo órganos de Canarias...")
    organos = []
    pagina = 1

    while True:
        print(f"Leyendo página {pagina}...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        filas = soup.find_all("tr")

        for fila in filas:
            # Buscamos el número de licitaciones abiertas
            badge = fila.find("p", class_="badge info m-0")
            if not badge:
                continue

            num_licitaciones = int(badge.text.strip())

            # Solo nos interesan los que tienen licitaciones > 0
            if num_licitaciones == 0:
                continue

            # Buscamos el enlace directo al órgano
            enlace = fila.find("a", href=lambda h: h and "perfilContratante" in h)
            nombre = fila.find("span", id=lambda i: i and "textoEnlace" in str(i))

            if enlace and nombre:
                organos.append(
                    {
                        "nombre": nombre.text.strip(),
                        "url": enlace["href"],
                        "licitaciones_abiertas": num_licitaciones,
                    }
                )

        # Comprobamos si hay página siguiente
        try:
            siguiente = driver.find_element(
                By.XPATH, "//a[contains(text(),'Siguiente')]"
            )
            siguiente.click()
            time.sleep(2)
            pagina += 1
        except:
            print(f"✅ Total órganos con licitaciones: {len(organos)}")
            break

    return organos


# # ============================================================
# # PASO 3: Obtener licitaciones de cada órgano
# # ============================================================
# def obtener_licitaciones(driver, organo):
#     print(f"Revisando: {organo['nombre']}")
#     licitaciones = []

#     try:
#         # Entramos en el órgano
#         driver.get(organo["url"])
#         wait = WebDriverWait(driver, 10)
#         time.sleep(2)

#         # Buscamos la pestaña Licitaciones y hacemos clic
#         pestana = wait.until(
#             EC.element_to_be_clickable(
#                 (By.XPATH, "//a[contains(text(),'Licitaciones')]")
#             )
#         )
#         pestana.click()
#         time.sleep(2)

#         # Extraemos la tabla
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         filas = soup.find_all("tr", class_=lambda c: c in ["par", "impar"])

#         for fila in filas:
#             # Número de expediente
#             expediente = fila.find("td", class_="tdExpediente")
#             if not expediente:
#                 continue

#             numero = (
#                 expediente.find("span").text.strip() if expediente.find("span") else ""
#             )

#             # URL de la licitación
#             enlace = expediente.find(
#                 "a", href=lambda h: h and "detalle_licitacion" in str(h)
#             )
#             url_licitacion = enlace["href"] if enlace else ""

#             # ID único
#             id_licitacion = (
#                 url_licitacion.split("idEvl=")[-1] if url_licitacion else numero
#             )

#             # Tipo
#             tipo = fila.find("td", class_="tdTipoContrato")
#             tipo = tipo.text.strip() if tipo else ""

#             # Objeto
#             objeto = fila.find("td", class_="tdTipoContratoLicOC")
#             objeto = objeto.text.strip() if objeto else ""

#             # Estado
#             estado = fila.find("td", class_="tdEstado")
#             estado = estado.text.strip() if estado else ""

#             # Importe
#             importe = fila.find("td", class_="tdImporte")
#             importe = importe.text.strip() if importe else ""

#             # Fechas
#             fechas = fila.find("td", class_="tdFecha")
#             fecha_publicacion = ""
#             if fechas:
#                 spans = fechas.find_all("span", class_="textAlignLeft")
#                 if spans:
#                     fecha_publicacion = spans[0].text.strip()

#             licitaciones.append(
#                 {
#                     "id": id_licitacion,
#                     "numero": numero,
#                     "organo": organo["nombre"],
#                     "tipo": tipo,
#                     "objeto": objeto,
#                     "estado": estado,
#                     "importe": importe,
#                     "fecha_publicacion": fecha_publicacion,
#                     "url": url_licitacion,
#                 }
#             )

#     except Exception as e:
#         print(f"Error en {organo['nombre']}: {e}")

#     return licitaciones


# # ============================================================
# # PASO 4: Filtrar solo las licitaciones nuevas
# # ============================================================
# def filtrar_nuevas(licitaciones):
#     archivo = "expedientes_vistos.json"

#     if os.path.exists(archivo):
#         with open(archivo, "r") as f:
#             vistos = json.load(f)
#     else:
#         vistos = []

#     # Filtramos las nuevas
#     nuevas = [l for l in licitaciones if l["id"] not in vistos]

#     # Guardamos las nuevas como vistas
#     todos = vistos + [l["id"] for l in nuevas]
#     with open(archivo, "w") as f:
#         json.dump(todos, f)

#     return nuevas


# # ============================================================
# # PASO 5: Función principal
# # ============================================================
# def ejecutar_scraping():
#     driver = iniciar_navegador()
#     todas_licitaciones = []

#     try:
#         # Abrimos la web con el filtro de Canarias ya aplicado
#         print("Abriendo web...")
#         driver.get(
#             "https://contrataciondelestado.es/wps/portal/plataforma/perfil_contratante/lista_perfiles"
#         )
#         wait = WebDriverWait(driver, 10)
#         time.sleep(2)

#         # Seleccionamos Canarias en el filtro
#         # Hay que verificar el ID real del desplegable con F12
#         select = Select(
#             wait.until(EC.presence_of_element_located((By.ID, "comunidadAutonoma")))
#         )
#         select.select_by_visible_text("Canarias")
#         time.sleep(1)

#         # Clic en buscar
#         boton = driver.find_element(By.XPATH, "//input[@type='submit']")
#         boton.click()
#         time.sleep(2)

#         # Obtenemos todos los órganos con licitaciones > 0
#         organos = obtener_organos_canarias(driver)
#         print(f"{len(organos)} órganos con licitaciones abiertas")

#         # Entramos en cada órgano y extraemos licitaciones
#         for organo in organos:
#             licitaciones = obtener_licitaciones(driver, organo)
#             todas_licitaciones.extend(licitaciones)
#             print(f"📋 {len(licitaciones)} licitaciones en {organo['nombre']}")

#     except Exception as e:
#         print(f"Error general: {e}")

#     finally:
#         driver.quit()

#     # Filtramos las nuevas
#     nuevas = filtrar_nuevas(todas_licitaciones)
#     print(f"\nTotal licitaciones nuevas: {len(nuevas)}")

#     return nuevas


# # Para probar
# if __name__ == "__main__":
#     nuevas = ejecutar_scraping()
#     for l in nuevas:
#         print(f"• {l['numero']} - {l['objeto']} - {l['estado']}")
