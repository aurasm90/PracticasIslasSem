# CONFIGURACIÓN - CONSTANTES


# -----------------------------------------
# CONFIGURACIÓN DEl EMAIL
# -----------------------------------------
EMAIL_REMITENTE = "a127islassem@gmail.com"

EMAIL_DESTINO = [
    "antonioislassem@gmail.com",
    "a127islassem@email.com",
]

ASUNTO = "Prueba Licitaciones Canarias"

# -----------------------------------------
# CONFIGURACIÓN DEL SCRAPING
# -----------------------------------------

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

# -----------------------------------------
# CONFIGURACIÓN DE SMTP
# -----------------------------------------

SMTP_SERVER = "smtp.gmail.com"

SMTP_PORT = 465

# Constantes para las pruebas
URL = "https://contrataciondelestado.es/"

FECHA = "19/06/2026"

ID = "ABC123"

EXPEDIENTE = "EXP-2024-001"

ORGANO = "Órgano de ejemplo"

OBJETO = "Cerramiento de puertas antirretorno norte"

TIPO = "Servicios"

ESTADO = "Publicada"

IMPORTE = "10.000,00 €"
