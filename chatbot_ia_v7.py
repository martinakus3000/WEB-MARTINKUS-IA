import json
import os
import sys
import difflib
import re
import ast
import operator
import shutil
import unicodedata
from pathlib import Path
from datetime import datetime

# =========================
# MARTINAKUS IA V7
# =========================
# En iniciar només surt:
# Tu:
#
# Novetats V7:
# - Cerca intel·ligent dins coneixement.json
# - Cerca intel·ligent dins biblioteca_internet.json
# - Entén frases com:
#   "parlem de raspberry pi 5"
#   "que es una raspberry pi 5"
#   "per que serveix una raspberry pi 5"
#   "explica raspberry pi 5"
#   "que saps de raspberry pi 5"
# - Manté perfils múltiples
# - Tracte diferent per Martí i Clàudia
# - /activar_inici obre aquesta V7 amb Windows

CARPETA_IA = Path(r"C:\Users\marti\Desktop\ia")
CARPETA_IA.mkdir(parents=True, exist_ok=True)

FITXER_CONEIXEMENT = CARPETA_IA / "coneixement.json"
FITXER_BIBLIOTECA = CARPETA_IA / "biblioteca_internet.json"
FITXER_PERFIL = CARPETA_IA / "perfil.json"
FITXER_PERFILS = CARPETA_IA / "perfils.json"
FITXER_CONFIG = CARPETA_IA / "config.json"
FITXER_NOTES = CARPETA_IA / "notes.json"
FITXER_HISTORIAL = CARPETA_IA / "historial.txt"

CARPETA_BACKUPS = CARPETA_IA / "backups"
CARPETA_BACKUPS.mkdir(parents=True, exist_ok=True)

NOM_BAT_INICI = "martinakus_ia_auto.bat"


# =========================
# EINES BÀSIQUES
# =========================

def ara():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def treure_accents(text):
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return text


def normalitzar_text(text):
    text = str(text).lower().strip()
    text = treure_accents(text)

    caracters = ".,;:!?¿¡()[]{}\"'`´’“”"
    for caracter in caracters:
        text = text.replace(caracter, "")

    text = " ".join(text.split())
    return text


def carregar_json(ruta, valor_defecte):
    if ruta.exists():
        try:
            with open(ruta, "r", encoding="utf-8") as fitxer:
                return json.load(fitxer)
        except Exception:
            return valor_defecte

    guardar_json(ruta, valor_defecte)
    return valor_defecte


def guardar_json(ruta, dades):
    with open(ruta, "w", encoding="utf-8") as fitxer:
        json.dump(dades, fitxer, ensure_ascii=False, indent=4)


def guardar_historial(qui, missatge):
    with open(FITXER_HISTORIAL, "a", encoding="utf-8") as fitxer:
        fitxer.write(f"[{ara()}] {qui}: {missatge}\n")


def clau_bonica(clau):
    return str(clau).replace("_", " ")


def valor_bonic(valor):
    if isinstance(valor, list):
        return ", ".join(str(x) for x in valor)

    return str(valor)


def netejar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


# =========================
# CONEIXEMENT
# =========================

def coneixement_inicial():
    return {
        "hola": {
            "resposta": "Hola, bro! 😎 Com va?",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "com estas": {
            "resposta": "Estic genial, crack! Preparat per aprendre coses noves 🤖🔥",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "qui ets": {
            "resposta": "Soc MARTINAKUS IA V7, una IA creada pel Martí 🤖🔥",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "que pots fer": {
            "resposta": "Puc aprendre respostes, calcular, gestionar perfils, recordar coses, guardar notes, fer backups i buscar millor dins la meva memòria.",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "adeu": {
            "resposta": "Adeu, crack! Ens veiem aviat 👋",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "raspberry pi 5": {
            "resposta": "La Raspberry Pi 5 és un mini ordinador molt petit i potent. Serveix per aprendre programació, fer projectes d'electrònica, muntar servidors, robots, automatitzacions, retro gaming i moltes proves de tecnologia.",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "que es una raspberry pi 5": {
            "resposta": "La Raspberry Pi 5 és un mini ordinador molt petit i potent. Es pot fer servir per programar, aprendre Linux, muntar servidors, fer projectes amb sensors, robòtica, domòtica i experiments de tecnologia.",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "per que serveix una raspberry pi 5": {
            "resposta": "Una Raspberry Pi 5 serveix per aprendre programació, crear robots, fer servidors casolans, muntar una consola retro, controlar llums o sensors, fer projectes d'intel·ligència artificial petits i practicar tecnologia.",
            "vegades_utilitzat": 0,
            "creat": ara()
        }
    }


def arreglar_format_coneixement(coneixement):
    coneixement_arreglat = {}

    for pregunta, dades in coneixement.items():
        pregunta_normal = normalitzar_text(pregunta)

        if isinstance(dades, dict):
            resposta = dades.get("resposta", "")
            vegades = dades.get("vegades_utilitzat", 0)
            creat = dades.get("creat", ara())
        else:
            resposta = str(dades)
            vegades = 0
            creat = ara()

        coneixement_arreglat[pregunta_normal] = {
            "resposta": resposta,
            "vegades_utilitzat": vegades,
            "creat": creat
        }

        if isinstance(dades, dict):
            if "font" in dades:
                coneixement_arreglat[pregunta_normal]["font"] = dades["font"]
            if "url" in dades:
                coneixement_arreglat[pregunta_normal]["url"] = dades["url"]

    return coneixement_arreglat


def carregar_coneixement():
    base = coneixement_inicial()
    coneixement = carregar_json(FITXER_CONEIXEMENT, base)
    coneixement = arreglar_format_coneixement(coneixement)

    for pregunta, dades in base.items():
        pregunta_normal = normalitzar_text(pregunta)

        if pregunta_normal not in coneixement:
            coneixement[pregunta_normal] = dades

    guardar_json(FITXER_CONEIXEMENT, coneixement)
    return coneixement


def guardar_coneixement(coneixement):
    guardar_json(FITXER_CONEIXEMENT, coneixement)


def buscar_resposta(pregunta, coneixement):
    pregunta_normal = normalitzar_text(pregunta)

    if pregunta_normal in coneixement:
        coneixement[pregunta_normal]["vegades_utilitzat"] += 1
        return coneixement[pregunta_normal]["resposta"], pregunta_normal, 1.0

    preguntes_guardades = list(coneixement.keys())

    semblants = difflib.get_close_matches(
        pregunta_normal,
        preguntes_guardades,
        n=1,
        cutoff=0.72
    )

    if semblants:
        pregunta_trobada = semblants[0]
        coneixement[pregunta_trobada]["vegades_utilitzat"] += 1

        semblanca = difflib.SequenceMatcher(
            None,
            pregunta_normal,
            pregunta_trobada
        ).ratio()

        return coneixement[pregunta_trobada]["resposta"], pregunta_trobada, semblanca

    return None, None, 0


def ensenyar_resposta(pregunta, resposta, coneixement):
    pregunta_normal = normalitzar_text(pregunta)

    coneixement[pregunta_normal] = {
        "resposta": resposta,
        "vegades_utilitzat": 0,
        "creat": ara()
    }

    guardar_coneixement(coneixement)
    print("IA: Apuntat! Ara ja ho recordaré 🧠💾")


# =========================
# BIBLIOTECA INTERNET
# =========================

def carregar_biblioteca():
    return carregar_json(FITXER_BIBLIOTECA, {})


def guardar_biblioteca(biblioteca):
    guardar_json(FITXER_BIBLIOTECA, biblioteca)


# =========================
# CERCADOR INTEL·LIGENT
# =========================

PARAULES_BUIDES = {
    "el", "la", "els", "les", "un", "una", "uns", "unes",
    "de", "del", "dels", "al", "als", "a", "amb", "en",
    "i", "o", "que", "es", "és", "son", "són", "per", "perque",
    "perquè", "serveix", "serveixen", "explica", "parlem",
    "sobre", "vull", "saps", "saber", "diguem", "digues",
    "em", "pots", "dir", "aixo", "això", "una", "un"
}


def paraules_importants(text):
    text_normal = normalitzar_text(text)
    parts = text_normal.split()

    resultat = []

    for paraula in parts:
        if len(paraula) <= 2:
            continue

        if paraula in PARAULES_BUIDES:
            continue

        resultat.append(paraula)

    return resultat


def extreure_tema_de_pregunta(text):
    text_normal = normalitzar_text(text)

    patrons = [
        r"^parlem de (.+)$",
        r"^parlem sobre (.+)$",
        r"^vull parlar de (.+)$",
        r"^vull saber de (.+)$",
        r"^que es (.+)$",
        r"^que és (.+)$",
        r"^què és (.+)$",
        r"^explica (.+)$",
        r"^explicam (.+)$",
        r"^explica'm (.+)$",
        r"^que saps de (.+)$",
        r"^què saps de (.+)$",
        r"^resum de (.+)$",
        r"^fes un resum de (.+)$",
        r"^per que serveix (.+)$",
        r"^per què serveix (.+)$",
        r"^per a que serveix (.+)$",
        r"^per a què serveix (.+)$",
        r"^quina utilitat te (.+)$",
        r"^quina utilitat té (.+)$"
    ]

    for patro in patrons:
        patro_normal = normalitzar_text(patro)
        try:
            coincidencia = re.match(patro, text_normal, re.IGNORECASE)
        except Exception:
            coincidencia = None

        if coincidencia:
            tema = coincidencia.group(1).strip()
            return tema

    paraules = paraules_importants(text_normal)

    if len(paraules) >= 2:
        return " ".join(paraules)

    return text_normal


def tipus_de_pregunta(text):
    text_normal = normalitzar_text(text)

    if "serveix" in text_normal or "utilitat" in text_normal or "fer amb" in text_normal:
        return "serveix"

    if text_normal.startswith("parlem"):
        return "parlem"

    if text_normal.startswith("explica") or "resum" in text_normal:
        return "explica"

    if "que es" in text_normal or "què és" in text_normal:
        return "definicio"

    return "general"


def puntuacio_text(pregunta, tema, text_candidat):
    pregunta_normal = normalitzar_text(pregunta)
    tema_normal = normalitzar_text(tema)
    candidat_normal = normalitzar_text(text_candidat)

    score = 0

    if tema_normal and tema_normal in candidat_normal:
        score += 60

    if pregunta_normal and pregunta_normal in candidat_normal:
        score += 50

    paraules_tema = paraules_importants(tema_normal)
    paraules_pregunta = paraules_importants(pregunta_normal)

    paraules = list(set(paraules_tema + paraules_pregunta))

    for paraula in paraules:
        if paraula in candidat_normal:
            score += 8

    ratio_tema = difflib.SequenceMatcher(None, tema_normal, candidat_normal[:200]).ratio()
    ratio_pregunta = difflib.SequenceMatcher(None, pregunta_normal, candidat_normal[:200]).ratio()

    score += ratio_tema * 20
    score += ratio_pregunta * 10

    return score


def crear_resposta_segons_pregunta(pregunta, resposta_base, font=None, url=None):
    tipus = tipus_de_pregunta(pregunta)

    resposta_base = str(resposta_base).strip()

    if resposta_base == "":
        return None

    if tipus == "serveix":
        resposta = "Pel que tinc guardat, serveix o es pot utilitzar així:\n"
        resposta += resposta_base
    elif tipus == "parlem":
        resposta = "Vale, parlem d’això. Tinc guardat això:\n"
        resposta += resposta_base
    elif tipus == "explica":
        resposta = "T’ho explico amb el que tinc a la memòria:\n"
        resposta += resposta_base
    elif tipus == "definicio":
        resposta = resposta_base
    else:
        resposta = resposta_base

    if font and url:
        if "Font:" not in resposta:
            resposta += f"\n\nFont: {font} - {url}"
    elif font:
        if "Font:" not in resposta:
            resposta += f"\n\nFont: {font}"

    return resposta


def buscar_a_biblioteca_intelligent(pregunta, biblioteca):
    if not biblioteca:
        return None

    tema = extreure_tema_de_pregunta(pregunta)

    millor_score = 0
    millor_entrada = None

    for clau, entrada in biblioteca.items():
        if not isinstance(entrada, dict):
            continue

        titol = entrada.get("titol", "")
        tema_entrada = entrada.get("tema", "")
        resum = entrada.get("resum", "")

        text_total = f"{clau} {titol} {tema_entrada} {resum}"

        score = puntuacio_text(pregunta, tema, text_total)

        if score > millor_score:
            millor_score = score
            millor_entrada = entrada

    if millor_entrada and millor_score >= 45:
        titol = millor_entrada.get("titol", "")
        resum = millor_entrada.get("resum", "")
        font = millor_entrada.get("font", "Internet")
        url = millor_entrada.get("url", "")

        resposta_base = f"{titol}: {resum}"
        return crear_resposta_segons_pregunta(pregunta, resposta_base, font, url)

    return None


def buscar_a_coneixement_intelligent(pregunta, coneixement):
    tema = extreure_tema_de_pregunta(pregunta)

    millor_score = 0
    millor_clau = None
    millor_dades = None

    for clau, dades in coneixement.items():
        if isinstance(dades, dict):
            resposta = dades.get("resposta", "")
        else:
            resposta = str(dades)

        text_total = f"{clau} {resposta}"

        score = puntuacio_text(pregunta, tema, text_total)

        if score > millor_score:
            millor_score = score
            millor_clau = clau
            millor_dades = dades

    if millor_dades and millor_score >= 45:
        if isinstance(millor_dades, dict):
            millor_dades["vegades_utilitzat"] = millor_dades.get("vegades_utilitzat", 0) + 1
            resposta_base = millor_dades.get("resposta", "")
            font = millor_dades.get("font")
            url = millor_dades.get("url")
        else:
            resposta_base = str(millor_dades)
            font = None
            url = None

        resposta = crear_resposta_segons_pregunta(pregunta, resposta_base, font, url)

        return resposta

    return None


def buscar_resposta_intelligent(pregunta, coneixement, biblioteca):
    resposta_coneixement = buscar_a_coneixement_intelligent(pregunta, coneixement)

    if resposta_coneixement:
        return resposta_coneixement

    resposta_biblioteca = buscar_a_biblioteca_intelligent(pregunta, biblioteca)

    if resposta_biblioteca:
        return resposta_biblioteca

    return None


# =========================
# PERFIL PRINCIPAL ANTIC
# =========================

def perfil_inicial():
    return {
        "nom": "Martí",
        "creador_de_la_ia": "Martí",
        "nom_de_la_ia": "MARTINAKUS IA",
        "color_preferit": "groc",
        "web": "https://martinakus.wordpress.com/",
        "youtube": "www.youtube.com/@MARTINAKUSWORLD",
        "li_agrada": [
            "tecnologia",
            "videojocs",
            "Minecraft",
            "LEGO",
            "màgia amb cartes",
            "kendama",
            "programar"
        ],
        "creat": ara()
    }


def carregar_perfil():
    perfil = carregar_json(FITXER_PERFIL, perfil_inicial())

    base = perfil_inicial()

    for clau, valor in base.items():
        if clau not in perfil:
            perfil[clau] = valor

    guardar_json(FITXER_PERFIL, perfil)
    return perfil


def guardar_perfil(perfil):
    guardar_json(FITXER_PERFIL, perfil)


# =========================
# PERFILS MÚLTIPLES
# =========================

def perfils_inicials():
    return {
        "marti": {
            "nom": "Martí",
            "genere": "noi",
            "tracte": "bro",
            "color_preferit": "groc",
            "web": "https://martinakus.wordpress.com/",
            "youtube": "www.youtube.com/@MARTINAKUSWORLD",
            "li_agrada": [
                "tecnologia",
                "videojocs",
                "Minecraft",
                "LEGO",
                "màgia amb cartes",
                "kendama",
                "programar"
            ]
        },
        "claudia": {
            "nom": "Clàudia",
            "genere": "noia",
            "tracte": "tia",
            "edat": 10,
            "color_preferit": "rosa",
            "li_agrada": [
                "manualitats"
            ],
            "web": "https://elracodart.wordpress.com/"
        }
    }


def carregar_perfils():
    perfils = carregar_json(FITXER_PERFILS, perfils_inicials())
    base = perfils_inicials()

    if "germana" in perfils:
        if "claudia" not in perfils:
            perfils["claudia"] = perfils["germana"]
        del perfils["germana"]

    for clau, dades_base in base.items():
        if clau not in perfils:
            perfils[clau] = dades_base
        else:
            for camp, valor in dades_base.items():
                if camp not in perfils[clau]:
                    perfils[clau][camp] = valor

    perfils["claudia"]["nom"] = "Clàudia"
    perfils["claudia"]["genere"] = "noia"
    perfils["claudia"]["tracte"] = "tia"
    perfils["claudia"]["edat"] = 10
    perfils["claudia"]["color_preferit"] = "rosa"
    perfils["claudia"]["li_agrada"] = ["manualitats"]
    perfils["claudia"]["web"] = "https://elracodart.wordpress.com/"

    perfils["marti"]["nom"] = "Martí"
    perfils["marti"]["genere"] = "noi"
    perfils["marti"]["tracte"] = "bro"

    guardar_json(FITXER_PERFILS, perfils)
    return perfils


def guardar_perfils(perfils):
    guardar_json(FITXER_PERFILS, perfils)


def config_inicial():
    return {
        "perfil_actiu": "marti"
    }


def carregar_config():
    config = carregar_json(FITXER_CONFIG, config_inicial())

    if "perfil_actiu" not in config:
        config["perfil_actiu"] = "marti"

    if config["perfil_actiu"] == "germana":
        config["perfil_actiu"] = "claudia"

    guardar_json(FITXER_CONFIG, config)
    return config


def guardar_config(config):
    guardar_json(FITXER_CONFIG, config)


def obtenir_clau_perfil_actiu(perfils, config):
    perfil_actiu = config.get("perfil_actiu", "marti")

    if perfil_actiu == "germana":
        perfil_actiu = "claudia"
        config["perfil_actiu"] = "claudia"
        guardar_config(config)

    if perfil_actiu in perfils:
        return perfil_actiu

    if "marti" in perfils:
        config["perfil_actiu"] = "marti"
        guardar_config(config)
        return "marti"

    primera_clau = list(perfils.keys())[0]
    config["perfil_actiu"] = primera_clau
    guardar_config(config)
    return primera_clau


def obtenir_nom_perfil_actiu(perfils, config):
    clau = obtenir_clau_perfil_actiu(perfils, config)
    return perfils[clau].get("nom", clau)


def obtenir_tracte(perfils, config):
    clau = obtenir_clau_perfil_actiu(perfils, config)
    dades = perfils[clau]

    tracte = dades.get("tracte")

    if tracte:
        return tracte

    nom = normalitzar_text(dades.get("nom", ""))

    if clau == "claudia" or nom == "claudia":
        return "tia"

    return "bro"


def es_claudia_activa(perfils, config):
    clau = obtenir_clau_perfil_actiu(perfils, config)
    nom = normalitzar_text(perfils[clau].get("nom", ""))

    return clau == "claudia" or nom == "claudia"


def personalitzar_resposta(text, perfils, config):
    if not es_claudia_activa(perfils, config):
        return text

    substitucions = [
        ("bro", "tia"),
        ("Bro", "Tia"),
        ("BRO", "TIA"),
        ("crack", "noia"),
        ("Crack", "Noia"),
        ("CRACK", "NOIA"),
        ("tio", "tia"),
        ("Tio", "Tia"),
        ("TIO", "TIA")
    ]

    resposta = text

    for antic, nou in substitucions:
        resposta = resposta.replace(antic, nou)

    return resposta


def dir_ia(text, perfils, config):
    text = personalitzar_resposta(text, perfils, config)
    print(f"IA: {text}")
    guardar_historial("IA", text)


def mostrar_perfil_actual(perfils, config):
    nom = obtenir_nom_perfil_actiu(perfils, config)
    tracte = obtenir_tracte(perfils, config)
    print(f"IA: Ara estàs amb el perfil de {nom}, {tracte} 👤")


def mostrar_perfil_actiu(perfils, config):
    clau = obtenir_clau_perfil_actiu(perfils, config)
    dades = perfils[clau]
    nom = dades.get("nom", clau)

    print(f"\n👤 Perfil actiu: {nom}")
    print("--------------------")

    for camp, valor in dades.items():
        print(f"{clau_bonica(camp)}: {valor_bonic(valor)}")

    print("--------------------\n")


def mostrar_perfils(perfils):
    print("\n👥 Perfils")
    print("--------------------")

    claus = list(perfils.keys())

    for index, clau in enumerate(claus, start=1):
        nom = perfils[clau].get("nom", clau)
        print(f"{index}. {nom}")

    print("--------------------")


def entrar_a_perfil(perfils, config):
    mostrar_perfils(perfils)

    claus = list(perfils.keys())
    opcio = input("A quin perfil vols entrar? Escriu el número o Enter per sortir: ").strip()

    if opcio == "":
        return

    try:
        numero = int(opcio)

        if numero < 1 or numero > len(claus):
            print("IA: Aquest perfil no existeix 😅")
            return

        clau_nova = claus[numero - 1]
        config["perfil_actiu"] = clau_nova
        guardar_config(config)

        nom = perfils[clau_nova].get("nom", clau_nova)
        tracte = obtenir_tracte(perfils, config)

        print(f"IA: Has entrat al perfil de {nom}, {tracte} ✅")

    except ValueError:
        print("IA: Has d'escriure un número 😅")


def trobar_perfil_per_text(text, perfils):
    text_normal = normalitzar_text(text)

    for clau, dades in perfils.items():
        nom = dades.get("nom", clau)

        clau_normal = normalitzar_text(clau)
        nom_normal = normalitzar_text(nom)

        if clau_normal in text_normal or nom_normal in text_normal:
            return clau

    return None


def intentar_canviar_perfil_per_text(text, perfils, config):
    text_normal = normalitzar_text(text)

    vol_canviar = (
        "perfil" in text_normal and
        (
            "entra" in text_normal or
            "entrar" in text_normal or
            "canvia" in text_normal or
            "canviar" in text_normal or
            "posa" in text_normal
        )
    )

    if not vol_canviar:
        return None

    clau = trobar_perfil_per_text(text, perfils)

    if clau is None:
        return "No he trobat aquest perfil 😅 Escriu /entrar_perfil per triar-lo."

    config["perfil_actiu"] = clau
    guardar_config(config)

    nom = perfils[clau].get("nom", clau)
    tracte = obtenir_tracte(perfils, config)

    return f"Has entrat al perfil de {nom}, {tracte} ✅"


def respondre_pregunta_perfil_actual(text, perfils, config):
    text_normal = normalitzar_text(text)

    preguntes = [
        "amb quin perfil estic ara",
        "quin perfil tinc actiu",
        "en quin perfil estic",
        "quin perfil estic fent servir",
        "qui soc ara"
    ]

    if text_normal in preguntes:
        nom = obtenir_nom_perfil_actiu(perfils, config)
        tracte = obtenir_tracte(perfils, config)
        return f"Ara estàs amb el perfil de {nom}, {tracte} 👤"

    if "perfil" in text_normal and ("estic" in text_normal or "actiu" in text_normal):
        nom = obtenir_nom_perfil_actiu(perfils, config)
        tracte = obtenir_tracte(perfils, config)
        return f"Ara estàs amb el perfil de {nom}, {tracte} 👤"

    return None


def resum_perfil(dades):
    nom = dades.get("nom", "Aquest perfil")
    resposta = f"{nom}:\n"

    for camp, valor in dades.items():
        resposta += f"- {clau_bonica(camp)}: {valor_bonic(valor)}\n"

    return resposta.strip()


def respondre_des_de_perfils(text, perfils):
    text_normal = normalitzar_text(text)

    for clau_perfil, dades in perfils.items():
        nom = dades.get("nom", clau_perfil)
        nom_normal = normalitzar_text(nom)
        clau_normal = normalitzar_text(clau_perfil)

        parla_del_perfil = nom_normal in text_normal or clau_normal in text_normal

        if not parla_del_perfil:
            continue

        if "web" in text_normal and "web" in dades:
            return f"La web de {nom} és: {dades['web']}"

        if "color" in text_normal and "color_preferit" in dades:
            return f"El color preferit de {nom} és {dades['color_preferit']}"

        if ("edat" in text_normal or "anys" in text_normal) and "edat" in dades:
            return f"{nom} té {dades['edat']} anys"

        if "agrada" in text_normal or "agraden" in text_normal:
            if "li_agrada" in dades:
                return f"A {nom} li agrada: {valor_bonic(dades['li_agrada'])}"

        for camp, valor in dades.items():
            camp_text = normalitzar_text(clau_bonica(camp))

            if camp_text in text_normal:
                return f"{clau_bonica(camp)} de {nom}: {valor_bonic(valor)}"

        return resum_perfil(dades)

    return None


def respondre_des_del_perfil_actiu(text, perfils, config):
    text_normal = normalitzar_text(text)

    clau_perfil = obtenir_clau_perfil_actiu(perfils, config)
    dades = perfils[clau_perfil]
    nom = dades.get("nom", clau_perfil)
    tracte = obtenir_tracte(perfils, config)

    if text_normal in ["que saps de mi", "que recordes de mi", "ensenya el meu perfil"]:
        resposta = f"Recordo això del perfil de {nom}:\n"

        for camp, valor in dades.items():
            resposta += f"- {clau_bonica(camp)}: {valor_bonic(valor)}\n"

        return resposta.strip()

    if text_normal in ["com em dic", "quin es el meu nom", "saps el meu nom"]:
        return f"Aquest perfil és de {nom}, {tracte} 👤"

    if "color" in text_normal and "color_preferit" in dades:
        return f"El color preferit de {nom} és {dades['color_preferit']}"

    if ("edat" in text_normal or "anys" in text_normal) and "edat" in dades:
        return f"{nom} té {dades['edat']} anys"

    if "web" in text_normal and "web" in dades:
        return f"La web de {nom} és: {dades['web']}"

    if ("agrada" in text_normal or "agraden" in text_normal) and "li_agrada" in dades:
        return f"A {nom} li agrada: {valor_bonic(dades['li_agrada'])}"

    for camp, valor in dades.items():
        camp_text = normalitzar_text(clau_bonica(camp))

        if camp_text in text_normal:
            return f"{clau_bonica(camp)} de {nom}: {valor_bonic(valor)}"

    return None


def recordar_manual_perfil_actiu(perfils, config):
    clau_perfil = obtenir_clau_perfil_actiu(perfils, config)
    nom = perfils[clau_perfil].get("nom", clau_perfil)

    clau = input(f"Què vols que recordi al perfil de {nom}? ").strip()
    valor = input("Quin valor té? ").strip()

    if clau == "" or valor == "":
        print("IA: No ho he guardat perquè falta info 😅")
        return

    clau = normalitzar_text(clau).replace(" ", "_")
    perfils[clau_perfil][clau] = valor

    guardar_perfils(perfils)
    print(f"IA: Guardat al perfil de {nom} 🧠✅")


def guardar_record_automatic_perfil_actiu(text, perfils, config):
    text_net = text.strip()

    match_nom = re.match(
        r"^\s*recorda\s+que\s+em\s+dic\s+(.+)\s*$",
        text_net,
        re.IGNORECASE
    )

    if match_nom:
        clau_perfil = obtenir_clau_perfil_actiu(perfils, config)
        nom_nou = match_nom.group(1).strip()

        perfils[clau_perfil]["nom"] = nom_nou
        guardar_perfils(perfils)

        tracte = obtenir_tracte(perfils, config)
        return f"Guardat, {tracte}! Ara aquest perfil es diu {nom_nou} 🧠💾"

    match = re.match(
        r"^\s*recorda\s+que\s+(.+?)\s+(?:es|és)\s+(.+)\s*$",
        text_net,
        re.IGNORECASE
    )

    if not match:
        return None

    clau_original = match.group(1).strip()
    valor = match.group(2).strip()

    clau_perfil = obtenir_clau_perfil_actiu(perfils, config)
    nom = perfils[clau_perfil].get("nom", clau_perfil)
    tracte = obtenir_tracte(perfils, config)

    clau = normalitzar_text(clau_original)

    prefixes = [
        "el meu ",
        "la meva ",
        "els meus ",
        "les meves ",
        "el ",
        "la ",
        "els ",
        "les "
    ]

    for prefix in prefixes:
        if clau.startswith(prefix):
            clau = clau.replace(prefix, "", 1)

    clau = clau.strip().replace(" ", "_")

    if clau == "" or valor == "":
        return "Falta alguna cosa 😅"

    perfils[clau_perfil][clau] = valor
    guardar_perfils(perfils)

    return f"Guardat, {tracte}! Al perfil de {nom}: {clau_bonica(clau)} és {valor} 🧠💾"


# =========================
# NOTES
# =========================

def carregar_notes():
    return carregar_json(FITXER_NOTES, [])


def guardar_notes(notes):
    guardar_json(FITXER_NOTES, notes)


def afegir_nota(notes):
    nota = input("Escriu la nota: ").strip()

    if nota == "":
        print("IA: Nota buida, no la guardo 😅")
        return

    notes.append({
        "text": nota,
        "creat": ara()
    })

    guardar_notes(notes)
    print("IA: Nota guardada 📝✅")


def afegir_nota_automatica(text, notes):
    text_net = text.strip()
    text_normal = normalitzar_text(text_net)

    if text_normal.startswith("apunta que "):
        nota = text_net[len("apunta que "):].strip()
    elif text_normal.startswith("nota "):
        nota = text_net[len("nota "):].strip()
    else:
        return None

    if nota == "":
        return "No he guardat la nota perquè està buida 😅"

    notes.append({
        "text": nota,
        "creat": ara()
    })

    guardar_notes(notes)
    return "Nota guardada 📝✅"


def mostrar_notes(notes):
    print("\n📝 Notes")
    print("--------------------")

    if not notes:
        print("No tens notes guardades 😅")
    else:
        for index, nota in enumerate(notes, start=1):
            print(f"{index}. {nota['text']}")
            print(f"   Creat: {nota['creat']}")

    print("--------------------\n")


def esborrar_nota(notes):
    mostrar_notes(notes)

    if not notes:
        return

    numero_text = input("Número de la nota a esborrar: ").strip()

    try:
        numero = int(numero_text)

        if numero < 1 or numero > len(notes):
            print("IA: Aquest número no existeix 😅")
            return

        nota_esborrada = notes.pop(numero - 1)
        guardar_notes(notes)

        print(f"IA: Nota esborrada: {nota_esborrada['text']} 🗑️✅")

    except ValueError:
        print("IA: Has d'escriure un número 😅")


# =========================
# CALCULADORA SEGURA
# =========================

OPERADORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow
}


def calcular_node(node):
    if isinstance(node, ast.Expression):
        return calcular_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Número no vàlid")

    if isinstance(node, ast.UnaryOp):
        valor = calcular_node(node.operand)

        if isinstance(node.op, ast.UAdd):
            return +valor

        if isinstance(node.op, ast.USub):
            return -valor

        raise ValueError("Operació no vàlida")

    if isinstance(node, ast.BinOp):
        esquerra = calcular_node(node.left)
        dreta = calcular_node(node.right)

        tipus_operador = type(node.op)

        if tipus_operador not in OPERADORS:
            raise ValueError("Operació no permesa")

        if tipus_operador == ast.Pow and abs(dreta) > 8:
            raise ValueError("Potència massa gran")

        resultat = OPERADORS[tipus_operador](esquerra, dreta)

        if abs(resultat) > 1_000_000_000:
            raise ValueError("Resultat massa gran")

        return resultat

    raise ValueError("Expressió no vàlida")


def preparar_expressio_mates(text):
    text = text.lower().strip()
    text = treure_accents(text)

    text = text.replace("¿", "")
    text = text.replace("?", "")
    text = text.replace("=", "")
    text = text.replace(",", ".")
    text = text.replace("^", "**")

    frases = [
        "quant fa",
        "que fa",
        "calcula",
        "fes",
        "resol",
        "resultat de",
        "cuanto es",
        "que es"
    ]

    for frase in frases:
        if text.startswith(frase):
            text = text.replace(frase, "", 1).strip()

    text = re.sub(r"(?<=\d)\s*x\s*(?=\d)", "*", text)

    if not re.fullmatch(r"[0-9+\-*/().%\s]+", text):
        return None

    if not re.search(r"\d", text):
        return None

    if not re.search(r"[+\-*/%]", text):
        return None

    return text.strip()


def intentar_calcular(text):
    expressio = preparar_expressio_mates(text)

    if expressio is None:
        return None

    try:
        arbre = ast.parse(expressio, mode="eval")
        resultat = calcular_node(arbre)

        if isinstance(resultat, float) and resultat.is_integer():
            resultat = int(resultat)

        return f"{expressio} = {resultat}"

    except Exception:
        return "He intentat calcular-ho, però aquesta operació m'ha petat al cervell 😵‍💫"


# =========================
# BACKUPS
# =========================

def fer_backup_complet():
    nom_carpeta = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ruta_backup = CARPETA_BACKUPS / nom_carpeta
    ruta_backup.mkdir(parents=True, exist_ok=True)

    fitxers = [
        FITXER_CONEIXEMENT,
        FITXER_BIBLIOTECA,
        FITXER_PERFIL,
        FITXER_PERFILS,
        FITXER_CONFIG,
        FITXER_NOTES,
        FITXER_HISTORIAL,
        Path(__file__).resolve()
    ]

    for fitxer in fitxers:
        if fitxer.exists():
            shutil.copy(fitxer, ruta_backup / fitxer.name)

    print("IA: Backup complet creat ✅")
    print(ruta_backup)


# =========================
# INICI AUTOMÀTIC
# =========================

def obtenir_carpeta_startup():
    appdata = os.environ.get("APPDATA")

    if not appdata:
        return None

    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def activar_inici_automatic():
    carpeta_startup = obtenir_carpeta_startup()

    if carpeta_startup is None:
        print("IA: No he trobat la carpeta d'inici automàtic 😅")
        return

    carpeta_startup.mkdir(parents=True, exist_ok=True)

    ruta_bat = carpeta_startup / NOM_BAT_INICI
    ruta_script = Path(__file__).resolve()
    python_exe = Path(sys.executable).resolve()

    contingut_bat = f"""@echo off
title MARTINAKUS IA V7
cd /d "{CARPETA_IA}"
"{python_exe}" "{ruta_script}"
"""

    with open(ruta_bat, "w", encoding="utf-8") as fitxer:
        fitxer.write(contingut_bat)

    print("IA: Inici automàtic activat ✅")
    print("La IA V7 s'obrirà quan iniciïs sessió al PC.")


def desactivar_inici_automatic():
    carpeta_startup = obtenir_carpeta_startup()

    if carpeta_startup is None:
        print("IA: No he trobat la carpeta d'inici automàtic 😅")
        return

    ruta_bat = carpeta_startup / NOM_BAT_INICI

    if ruta_bat.exists():
        ruta_bat.unlink()
        print("IA: Inici automàtic desactivat ✅")
    else:
        print("IA: L'inici automàtic ja estava desactivat 😅")


# =========================
# ORDRES
# =========================

def mostrar_ajuda():
    print("\n📌 Ordres")
    print("--------------------")
    print("/ajuda             → Mostra les ordres")
    print("/perfil            → Mostra el perfil actiu")
    print("/perfils           → Mostra tots els perfils")
    print("/entrar_perfil     → Entra a un perfil")
    print("/perfil_actual     → Diu amb quin perfil estàs ara")
    print("/recorda           → Guarda una dada al perfil actiu")
    print("/notes             → Mostra notes")
    print("/nota              → Crea una nota")
    print("/esborra_nota      → Esborra una nota")
    print("/llista            → Mostra el que sap la IA")
    print("/stats             → Estadístiques")
    print("/ensenya           → Ensenya pregunta/resposta")
    print("/edita             → Edita una resposta")
    print("/esborra           → Esborra una pregunta")
    print("/cerca             → Busca al coneixement")
    print("/backup            → Backup complet")
    print("/activar_inici     → Obre la IA V7 quan encens el PC")
    print("/desactivar_inici  → Treu l'inici automàtic")
    print("/neteja            → Neteja la pantalla")
    print("/sortir            → Tanca la IA")
    print("--------------------\n")


def llistar_coneixement(coneixement):
    print("\n🧠 Coneixement")
    print("--------------------")

    if not coneixement:
        print("Encara no sé res 😅")
    else:
        for index, pregunta in enumerate(coneixement.keys(), start=1):
            resposta = coneixement[pregunta]["resposta"]
            print(f"{index}. Pregunta: {pregunta}")
            print(f"   Resposta: {resposta}")

    print("--------------------\n")


def mostrar_estadistiques(coneixement, biblioteca, notes, perfils, config):
    total = len(coneixement)
    total_biblio = len(biblioteca)
    nom_actiu = obtenir_nom_perfil_actiu(perfils, config)
    tracte = obtenir_tracte(perfils, config)

    print("\n📊 Estadístiques")
    print("--------------------")
    print(f"Preguntes apreses: {total}")
    print(f"Temes a biblioteca internet: {total_biblio}")
    print(f"Perfils guardats: {len(perfils)}")
    print(f"Perfil actiu: {nom_actiu}")
    print(f"Tracte actual: {tracte}")
    print(f"Notes guardades: {len(notes)}")

    if total > 0:
        pregunta_mes_utilitzada = max(
            coneixement,
            key=lambda pregunta: coneixement[pregunta].get("vegades_utilitzat", 0)
        )

        vegades = coneixement[pregunta_mes_utilitzada].get("vegades_utilitzat", 0)

        print(f"Pregunta més utilitzada: {pregunta_mes_utilitzada}")
        print(f"Vegades utilitzada: {vegades}")

    print("--------------------\n")


def ensenyar_manual(coneixement):
    pregunta = input("Pregunta que vols que aprengui: ").strip()
    resposta = input("Resposta que ha de donar: ").strip()

    if pregunta == "" or resposta == "":
        print("IA: No ho he guardat perquè falta info 😅")
        return

    ensenyar_resposta(pregunta, resposta, coneixement)


def editar_resposta(coneixement):
    pregunta = input("Quina pregunta vols editar? ").strip()
    pregunta_normal = normalitzar_text(pregunta)

    if pregunta_normal not in coneixement:
        print("IA: No he trobat aquesta pregunta 😅")
        return

    print(f"Resposta actual: {coneixement[pregunta_normal]['resposta']}")
    nova_resposta = input("Nova resposta: ").strip()

    if nova_resposta == "":
        print("IA: No he canviat res.")
        return

    coneixement[pregunta_normal]["resposta"] = nova_resposta
    guardar_coneixement(coneixement)

    print("IA: Resposta editada correctament ✏️✅")


def esborrar_pregunta(coneixement):
    pregunta = input("Quina pregunta vols esborrar? ").strip()
    pregunta_normal = normalitzar_text(pregunta)

    if pregunta_normal in coneixement:
        del coneixement[pregunta_normal]
        guardar_coneixement(coneixement)
        print("IA: Pregunta esborrada 🗑️✅")
    else:
        print("IA: No he trobat aquesta pregunta 😅")


def cercar_coneixement(coneixement):
    paraula = input("Què vols buscar? ").strip()
    paraula_normal = normalitzar_text(paraula)

    print("\n🔎 Resultats")
    print("--------------------")

    trobats = 0

    for pregunta, dades in coneixement.items():
        resposta = dades.get("resposta", "")
        text_total = normalitzar_text(pregunta + " " + resposta)

        if paraula_normal in text_total:
            trobats += 1
            print(f"Pregunta: {pregunta}")
            print(f"Resposta: {resposta}")
            print("-")

    if trobats == 0:
        print("No he trobat res 😅")

    print("--------------------\n")


# =========================
# PROGRAMA PRINCIPAL
# =========================

def iniciar_chatbot():
    coneixement = carregar_coneixement()
    biblioteca = carregar_biblioteca()
    perfil = carregar_perfil()
    perfils = carregar_perfils()
    config = carregar_config()
    notes = carregar_notes()

    while True:
        pregunta = input("Tu: ").strip()

        if pregunta == "":
            continue

        guardar_historial("TU", pregunta)

        comanda = normalitzar_text(pregunta)

        if comanda == "/sortir":
            guardar_coneixement(coneixement)
            guardar_biblioteca(biblioteca)
            guardar_perfil(perfil)
            guardar_perfils(perfils)
            guardar_config(config)
            guardar_notes(notes)

            resposta_final = "Adeu, crack! He guardat la memòria 👋💾"
            dir_ia(resposta_final, perfils, config)
            break

        if comanda == "/ajuda":
            mostrar_ajuda()
            continue

        if comanda == "/perfil":
            mostrar_perfil_actiu(perfils, config)
            continue

        if comanda == "/perfils":
            mostrar_perfils(perfils)
            continue

        if comanda == "/entrar_perfil":
            entrar_a_perfil(perfils, config)
            continue

        if comanda == "/perfil_actual":
            mostrar_perfil_actual(perfils, config)
            continue

        if comanda == "/recorda":
            recordar_manual_perfil_actiu(perfils, config)
            continue

        if comanda == "/notes":
            mostrar_notes(notes)
            continue

        if comanda == "/nota":
            afegir_nota(notes)
            continue

        if comanda == "/esborra_nota":
            esborrar_nota(notes)
            continue

        if comanda == "/llista":
            llistar_coneixement(coneixement)
            continue

        if comanda == "/stats":
            mostrar_estadistiques(coneixement, biblioteca, notes, perfils, config)
            continue

        if comanda == "/ensenya":
            ensenyar_manual(coneixement)
            continue

        if comanda == "/edita":
            editar_resposta(coneixement)
            continue

        if comanda == "/esborra":
            esborrar_pregunta(coneixement)
            continue

        if comanda == "/cerca":
            cercar_coneixement(coneixement)
            continue

        if comanda == "/backup":
            fer_backup_complet()
            continue

        if comanda == "/activar_inici":
            activar_inici_automatic()
            continue

        if comanda == "/desactivar_inici":
            desactivar_inici_automatic()
            continue

        if comanda == "/neteja":
            netejar_pantalla()
            continue

        resposta_canvi_perfil = intentar_canviar_perfil_per_text(pregunta, perfils, config)

        if resposta_canvi_perfil:
            dir_ia(resposta_canvi_perfil, perfils, config)
            continue

        resposta_perfil_actual = respondre_pregunta_perfil_actual(pregunta, perfils, config)

        if resposta_perfil_actual:
            dir_ia(resposta_perfil_actual, perfils, config)
            continue

        resposta_nota = afegir_nota_automatica(pregunta, notes)

        if resposta_nota:
            dir_ia(resposta_nota, perfils, config)
            continue

        resposta_record = guardar_record_automatic_perfil_actiu(pregunta, perfils, config)

        if resposta_record:
            dir_ia(resposta_record, perfils, config)
            continue

        resposta_perfils = respondre_des_de_perfils(pregunta, perfils)

        if resposta_perfils:
            dir_ia(resposta_perfils, perfils, config)
            continue

        resposta_perfil_actiu = respondre_des_del_perfil_actiu(pregunta, perfils, config)

        if resposta_perfil_actiu:
            dir_ia(resposta_perfil_actiu, perfils, config)
            continue

        resposta_mates = intentar_calcular(pregunta)

        if resposta_mates:
            dir_ia(resposta_mates, perfils, config)
            continue

        resposta_exacta, pregunta_trobada, semblanca = buscar_resposta(pregunta, coneixement)

        if resposta_exacta and semblanca >= 0.92:
            dir_ia(resposta_exacta, perfils, config)
            guardar_coneixement(coneixement)
            continue

        resposta_intelligent = buscar_resposta_intelligent(pregunta, coneixement, biblioteca)

        if resposta_intelligent:
            dir_ia(resposta_intelligent, perfils, config)
            guardar_coneixement(coneixement)
            continue

        if resposta_exacta:
            dir_ia(f"Crec que vols dir: '{pregunta_trobada}' 🤔", perfils, config)
            dir_ia(resposta_exacta, perfils, config)
            guardar_coneixement(coneixement)
            continue

        print("IA: No sé respondre això encara 😅")
        opcio = input("Vols ensenyar-me què he de respondre? (s/n): ").strip().lower()

        if opcio == "s":
            nova_resposta = input("Què hauria de respondre la pròxima vegada? ").strip()

            if nova_resposta == "":
                print("IA: Vale, no ho guardo.")
            else:
                ensenyar_resposta(pregunta, nova_resposta, coneixement)
                guardar_historial("IA", nova_resposta)
        else:
            print("IA: Vale, ho deixem sense aprendre 😎")


if __name__ == "__main__":
    iniciar_chatbot()
