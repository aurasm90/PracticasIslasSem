# CONFIGURACIÓN - CONSTANTES

# -----------------------------------------
# CONFIGURACIÓN DE RUTAS
# -----------------------------------------

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datos"


# -----------------------------------------
# CONFIGURACIÓN DEL SCRAPING
# -----------------------------------------

URL_BASE = "https://contrataciondelestado.es/wps/portal/plataforma/perfil_contratante/lista_perfiles/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziHcNcAx09LY0N3IMCXA2MnILMzUzc_I0NDIz0w8EKTI2dTcK8wgLMgj3dDQw8PdxcfEINTQ3cjcz0o4jRb4ADOBoQpx-Pgij8xofrR-G3wgCqAJ8XCVlSkBsaGmGQ6QkATfmaFQ!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/IZ7_AVEQAI930GRPE02BR764FO30G0=CZ6_AVEQAI930GRPE02BR764FO3002=LA0=Ecom.ibm.faces.portlet.VIEWID!QCPjspQCPlistPerfilesQCPAdminAFPListPerfPortletAppView.jsp==/#Z7_AVEQAI930GRPE02BR764FO30G0"
COMUNIDAD = "Canarias"
TIEMPO_ESPERA = 10  # segundos para WebDriverWait
TIEMPO_ESPERA_LARGO = 20 # tiempo + largo para CIFs
ID_SELECT_COMUNIDAD = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:menu111MAQ"
ID_BOTON_BUSCAR = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:botonbuscar"
ID_CAMPO_NIF_ORGANO = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:perfilComp:idNumDoc"
CLASE_RESULTADOS = "badge"
ID_BOTON_SIGUIENTE = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:listaperfiles:siguienteLink"
ID_PESTANYA_LICITACIONES = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:textLinkLic"
ID_FILTRO_ESTADO = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:busReasProc11"
ID_BOTON_LICITACIONES = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:perfilComp:linkPrepLic"
ESTADO_PUBLICADA = "PUB"
ID_BOTON_BUSCAR_LIC = "viewns_Z7_AVEQAI930GRPE02BR764FO30G0_:form1:busReasProc18"


# -----------------------------------------
# CONFIGURACIÓN DEL JSON_parser
# -----------------------------------------

# Clave que identifica de forma única a cada licitación (para evitar duplicados)
CLAVE_ID = "id"

ARCHIVO_HOY = DATA_DIR / "licitaciones_hoy.json"

ARCHIVO_VISTOS = DATA_DIR / "expedientes_vistos.json"

ARCHIVO_NUEVAS = DATA_DIR / "licitaciones_nuevas.json"


# -----------------------------------------
# CONFIGURACIÓN DEl EMAIL
# -----------------------------------------

EMAIL_REMITENTE = "a127islassem@gmail.com"

EMAIL_DESTINO = [
    "antonioislassem@gmail.com",
    "a127islassem@gmail.com",
    "violetaislassem@gmail.com",
    "marketing@islassem.com",
]

ASUNTO = "Licitaciones Canarias"


# -----------------------------------------
# CONFIGURACIÓN DE SMTP
# -----------------------------------------

SMTP_SERVER = "smtp.gmail.com"

SMTP_PORT = 465


# -----------------------------------------
# CONFIGURACIÓN DE CIFS
# -----------------------------------------

RUTA_ORIGINAL = DATA_DIR / "cifs_lista_original.txt"
RUTA_CIFS = DATA_DIR / "cifs_permitidos.txt"


def cargar_cifs_permitidos():
    """
    Carga la lista de CIFs permitidos ordenados ABC desde un archivo de texto.

    Returns:
        set: Conjunto de CIFs permitidos
    """
    try:
        with open(RUTA_CIFS, "r", encoding="utf-8") as f:
            cifs = {
                linea.strip()
                for linea in RUTA_CIFS.read_text(encoding="utf-8").splitlines()
                if linea.strip()
            }

        print(f"Cargados {len(cifs)} CIFs desde '{RUTA_CIFS.name}'")
        return cifs

    except FileNotFoundError:
        print(f"No se encontró el archivo '{RUTA_CIFS}'")
        return None

    except Exception as e:
        print(f"Error al leer el archivo de CIFs: {e}")
        return None

