import os
import sys
import json
import re
import ast
import operator
import shutil
import difflib
import traceback
import unicodedata
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

# =========================
# MARTINAKUS IA WEB V8
# Compatible amb Render i PC local
# =========================

CARPETA_IA = Path(__file__).resolve().parent

FITXER_CONEIXEMENT = CARPETA_IA / "coneixement.json"
FITXER_BIBLIOTECA = CARPETA_IA / "biblioteca_internet.json"
FITXER_PERFILS = CARPETA_IA / "perfils.json"
FITXER_CONFIG = CARPETA_IA / "config.json"
FITXER_NOTES = CARPETA_IA / "notes.json"
FITXER_HISTORIAL = CARPETA_IA / "historial_web.txt"
CARPETA_BACKUPS = CARPETA_IA / "backups"
CARPETA_BACKUPS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CARPETA_IA))

try:
    import chatbot_ia_v7 as cervell
except Exception as error:
    cervell = None
    ERROR_CERVELL = str(error)
else:
    ERROR_CERVELL = ""

    try:
        cervell.CARPETA_IA = CARPETA_IA
        cervell.FITXER_CONEIXEMENT = FITXER_CONEIXEMENT
        cervell.FITXER_BIBLIOTECA = FITXER_BIBLIOTECA
        cervell.FITXER_PERFILS = FITXER_PERFILS
        cervell.FITXER_CONFIG = FITXER_CONFIG
        cervell.FITXER_NOTES = FITXER_NOTES
        cervell.FITXER_HISTORIAL = FITXER_HISTORIAL
        cervell.CARPETA_BACKUPS = CARPETA_BACKUPS

        if hasattr(cervell, "FITXER_PERFIL"):
            cervell.FITXER_PERFIL = CARPETA_IA / "perfil.json"
    except Exception:
        pass

app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <title>MARTINAKUS IA WEB V8</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #111827;
            color: white;
        }

        .app {
            display: flex;
            height: 100vh;
        }

        .sidebar {
            width: 280px;
            background: #020617;
            padding: 20px;
            border-right: 1px solid #334155;
        }

        .sidebar h1 {
            margin-top: 0;
            color: #38bdf8;
            font-size: 24px;
        }

        .sidebar button,
        .sidebar select {
            width: 100%;
            margin-top: 10px;
            padding: 11px;
            border: none;
            border-radius: 9px;
            font-size: 14px;
        }

        .sidebar button {
            background: #2563eb;
            color: white;
            cursor: pointer;
        }

        .sidebar button:hover {
            background: #1d4ed8;
        }

        .sidebar select {
            background: white;
            color: black;
        }

        .box {
            background: #020617;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px;
            margin-top: 15px;
            font-size: 13px;
            white-space: pre-wrap;
        }

        .chat {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .topbar {
            height: 54px;
            background: #0f172a;
            border-bottom: 1px solid #334155;
            padding: 16px;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .msg {
            max-width: 900px;
            margin-bottom: 14px;
            padding: 13px;
            border-radius: 13px;
            line-height: 1.45;
            white-space: pre-wrap;
        }

        .tu {
            background: #2563eb;
            margin-left: auto;
        }

        .ia {
            background: #1e293b;
            margin-right: auto;
        }

        .error {
            background: #7f1d1d;
            margin-right: auto;
        }

        .inputbar {
            display: flex;
            gap: 10px;
            padding: 12px;
            background: #0f172a;
            border-top: 1px solid #334155;
        }

        #entrada {
            flex: 1;
            padding: 14px;
            border-radius: 10px;
            border: 2px solid white;
            font-size: 16px;
        }

        #enviarBtn {
            width: 95px;
            border: none;
            border-radius: 10px;
            background: #22c55e;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        #enviarBtn:hover {
            background: #16a34a;
        }

        .small {
            color: #93c5fd;
            font-size: 13px;
        }
    </style>
</head>

<body>
    <div class="app">
        <div class="sidebar">
            <h1>🤖 MARTINAKUS IA</h1>
            <p class="small">Web V8 · Compatible amb Render</p>

            <label>Perfil actiu:</label>
            <select id="perfilSelect"></select>

            <button onclick="canviarPerfil()">Canviar perfil</button>
            <button onclick="veurePerfil()">Veure perfil</button>
            <button onclick="veureStats()">Estadístiques</button>
            <button onclick="backup()">Backup</button>
            <button onclick="netejarChat()">Netejar xat</button>

            <div id="estat" class="box">Carregant...</div>
        </div>

        <div class="chat">
            <div class="topbar">
                <strong>MARTINAKUS IA WEB V8</strong>
                <span id="perfilActual" class="small"></span>
            </div>

            <div id="messages" class="messages"></div>

            <div class="inputbar">
                <input id="entrada" placeholder="Escriu aquí..." onkeydown="enterEnviar(event)">
                <button id="enviarBtn" onclick="enviar()">Enviar</button>
            </div>
        </div>
    </div>

    <script>
        function afegirMissatge(qui, text, tipus="normal") {
            const messages = document.getElementById("messages");
            const div = document.createElement("div");

            if (qui === "Tu") {
                div.className = "msg tu";
            } else if (tipus === "error") {
                div.className = "msg error";
            } else {
                div.className = "msg ia";
            }

            div.textContent = qui + ": " + text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        async function carregarPerfils() {
            try {
                const res = await fetch("/api/perfils");
                const data = await res.json();

                const select = document.getElementById("perfilSelect");
                select.innerHTML = "";

                for (const clau in data.perfils) {
                    const opcio = document.createElement("option");
                    opcio.value = clau;
                    opcio.textContent = data.perfils[clau].nom || clau;

                    if (clau === data.perfil_actiu) {
                        opcio.selected = true;
                    }

                    select.appendChild(opcio);
                }

                document.getElementById("perfilActual").textContent =
                    " | Perfil: " + data.nom_actiu;

                document.getElementById("estat").textContent =
                    "👤 Perfil actiu: " + data.nom_actiu +
                    "\\n💬 Tracte: " + data.tracte +
                    "\\n🧠 Coneixement: " + data.total_coneixement +
                    "\\n🌐 Biblioteca: " + data.total_biblioteca +
                    "\\n📝 Notes: " + data.total_notes +
                    "\\n⚙️ Cervell V7: " + data.estat_cervell;

            } catch (error) {
                document.getElementById("estat").textContent =
                    "Error carregant perfils: " + error;
            }
        }

        async function enviar() {
            const input = document.getElementById("entrada");
            const boto = document.getElementById("enviarBtn");
            const text = input.value.trim();

            if (text === "") {
                return;
            }

            afegirMissatge("Tu", text);
            input.value = "";
            boto.disabled = true;
            boto.textContent = "...";

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({missatge: text})
                });

                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.error || "Error HTTP " + res.status);
                }

                afegirMissatge("IA", data.resposta || "No he rebut resposta.");
                carregarPerfils();

            } catch (error) {
                afegirMissatge("IA", "Error parlant amb el servidor: " + error.message, "error");
            }

            boto.disabled = false;
            boto.textContent = "Enviar";
            input.focus();
        }

        function enterEnviar(event) {
            if (event.key === "Enter") {
                enviar();
            }
        }

        async function canviarPerfil() {
            const clau = document.getElementById("perfilSelect").value;

            try {
                const res = await fetch("/api/canviar_perfil", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({perfil: clau})
                });

                const data = await res.json();
                afegirMissatge("IA", data.resposta);
                carregarPerfils();

            } catch (error) {
                afegirMissatge("IA", "Error canviant perfil: " + error.message, "error");
            }
        }

        async function veurePerfil() {
            try {
                const res = await fetch("/api/perfil_actual");
                const data = await res.json();
                afegirMissatge("IA", data.resposta);
            } catch (error) {
                afegirMissatge("IA", "Error veient perfil: " + error.message, "error");
            }
        }

        async function veureStats() {
            try {
                const res = await fetch("/api/stats");
                const data = await res.json();
                afegirMissatge("IA", data.resposta);
            } catch (error) {
                afegirMissatge("IA", "Error veient estadístiques: " + error.message, "error");
            }
        }

        async function backup() {
            try {
                const res = await fetch("/api/backup", {method: "POST"});
                const data = await res.json();
                afegirMissatge("IA", data.resposta);
            } catch (error) {
                afegirMissatge("IA", "Error fent backup: " + error.message, "error");
            }
        }

        function netejarChat() {
            document.getElementById("messages").innerHTML = "";
        }

        carregarPerfils();
        afegirMissatge("IA", "Hola! Soc MARTINAKUS IA WEB V8 😎 Escriu /ajuda per veure què puc fer.");
    </script>
</body>
</html>
"""


# =========================
# FUNCIONS BÀSIQUES
# =========================

def ara():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def treure_accents(text):
    text = unicodedata.normalize("NFD", str(text))
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return text


def normalitzar_text(text):
    if cervell and hasattr(cervell, "normalitzar_text"):
        try:
            return cervell.normalitzar_text(text)
        except Exception:
            pass

    text = str(text).lower().strip()
    text = treure_accents(text)

    caracters = ".,;:!?¿¡()[]{}\"'`´’“”"
    for caracter in caracters:
        text = text.replace(caracter, "")

    text = " ".join(text.split())
    return text


def carregar_json(ruta, defecte):
    if ruta.exists():
        try:
            with open(ruta, "r", encoding="utf-8") as fitxer:
                return json.load(fitxer)
        except Exception:
            return defecte

    guardar_json(ruta, defecte)
    return defecte


def guardar_json(ruta, dades):
    with open(ruta, "w", encoding="utf-8") as fitxer:
        json.dump(dades, fitxer, ensure_ascii=False, indent=4)


def guardar_historial(qui, missatge):
    try:
        with open(FITXER_HISTORIAL, "a", encoding="utf-8") as fitxer:
            fitxer.write(f"[{ara()}] {qui}: {missatge}\n")
    except Exception:
        pass


def clau_bonica(clau):
    noms = {
        "nom": "Nom",
        "genere": "Gènere",
        "tracte": "Tracte",
        "edat": "Edat",
        "color_preferit": "Color preferit",
        "web": "Web",
        "youtube": "YouTube",
        "li_agrada": "Li agrada"
    }

    if clau in noms:
        return noms[clau]

    return str(clau).replace("_", " ").capitalize()


def valor_bonic(valor):
    if isinstance(valor, list):
        return ", ".join(str(x) for x in valor)
    return str(valor)


# =========================
# DADES
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


def coneixement_inicial():
    return {
        "hola": {
            "resposta": "Hola, bro! 😎 Com va?",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "qui ets": {
            "resposta": "Soc MARTINAKUS IA WEB V8, una IA creada pel Martí 🤖🔥",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "que pots fer": {
            "resposta": "Puc parlar, recordar coses, gestionar perfils, fer càlculs i buscar dins la meva memòria.",
            "vegades_utilitzat": 0,
            "creat": ara()
        },
        "raspberry pi 5": {
            "resposta": "La Raspberry Pi 5 és un mini ordinador petit però bastant potent. Serveix per aprendre programació, provar Linux, fer servidors casolans, projectes d'electrònica, robots, domòtica, retro gaming i experiments de tecnologia.",
            "vegades_utilitzat": 0,
            "creat": ara()
        }
    }


def carregar_coneixement():
    if cervell and hasattr(cervell, "carregar_coneixement"):
        try:
            return cervell.carregar_coneixement()
        except Exception:
            pass

    return carregar_json(FITXER_CONEIXEMENT, coneixement_inicial())


def guardar_coneixement(coneixement):
    if cervell and hasattr(cervell, "guardar_coneixement"):
        try:
            cervell.guardar_coneixement(coneixement)
            return
        except Exception:
            pass

    guardar_json(FITXER_CONEIXEMENT, coneixement)


def carregar_biblioteca():
    if cervell and hasattr(cervell, "carregar_biblioteca"):
        try:
            return cervell.carregar_biblioteca()
        except Exception:
            pass

    return carregar_json(FITXER_BIBLIOTECA, {})


def carregar_perfils():
    if cervell and hasattr(cervell, "carregar_perfils"):
        try:
            return cervell.carregar_perfils()
        except Exception:
            pass

    perfils = carregar_json(FITXER_PERFILS, perfils_inicials())
    base = perfils_inicials()

    for clau, dades in base.items():
        if clau not in perfils:
            perfils[clau] = dades
        else:
            for camp, valor in dades.items():
                if camp not in perfils[clau]:
                    perfils[clau][camp] = valor

    guardar_json(FITXER_PERFILS, perfils)
    return perfils


def carregar_config():
    if cervell and hasattr(cervell, "carregar_config"):
        try:
            return cervell.carregar_config()
        except Exception:
            pass

    config = carregar_json(FITXER_CONFIG, {"perfil_actiu": "marti"})

    if "perfil_actiu" not in config:
        config["perfil_actiu"] = "marti"

    guardar_json(FITXER_CONFIG, config)
    return config


def guardar_config(config):
    if cervell and hasattr(cervell, "guardar_config"):
        try:
            cervell.guardar_config(config)
            return
        except Exception:
            pass

    guardar_json(FITXER_CONFIG, config)


def carregar_notes():
    if cervell and hasattr(cervell, "carregar_notes"):
        try:
            return cervell.carregar_notes()
        except Exception:
            pass

    return carregar_json(FITXER_NOTES, [])


def carregar_tot():
    coneixement = carregar_coneixement()
    biblioteca = carregar_biblioteca()
    perfils = carregar_perfils()
    config = carregar_config()
    notes = carregar_notes()

    return coneixement, biblioteca, perfils, config, notes


def obtenir_clau_perfil_actiu(perfils, config):
    if cervell and hasattr(cervell, "obtenir_clau_perfil_actiu"):
        try:
            return cervell.obtenir_clau_perfil_actiu(perfils, config)
        except Exception:
            pass

    clau = config.get("perfil_actiu", "marti")

    if clau not in perfils:
        clau = "marti"

    return clau


def obtenir_nom_perfil_actiu(perfils, config):
    clau = obtenir_clau_perfil_actiu(perfils, config)
    return perfils.get(clau, {}).get("nom", clau)


def obtenir_tracte(perfils, config):
    if cervell and hasattr(cervell, "obtenir_tracte"):
        try:
            return cervell.obtenir_tracte(perfils, config)
        except Exception:
            pass

    clau = obtenir_clau_perfil_actiu(perfils, config)
    return perfils.get(clau, {}).get("tracte", "bro")


def personalitzar_resposta(text, perfils, config):
    if cervell and hasattr(cervell, "personalitzar_resposta"):
        try:
            return cervell.personalitzar_resposta(text, perfils, config)
        except TypeError:
            try:
                return cervell.personalitzar_resposta(text)
            except Exception:
                pass
        except Exception:
            pass

    clau = obtenir_clau_perfil_actiu(perfils, config)

    if clau != "claudia":
        return str(text)

    resposta = str(text)
    resposta = resposta.replace("bro", "tia")
    resposta = resposta.replace("Bro", "Tia")
    resposta = resposta.replace("crack", "noia")
    resposta = resposta.replace("Crack", "Noia")
    return resposta


# =========================
# FORMATADORS
# =========================

def formatar_ajuda():
    resposta = "📌 Ajuda de MARTINAKUS IA WEB V8\n"
    resposta += "━━━━━━━━━━━━━━━━━━━━\n\n"

    resposta += "👤 Perfils:\n"
    resposta += "- /perfil → Mostra el perfil actiu ordenat.\n"
    resposta += "- /perfils → Mostra tots els perfils disponibles.\n"
    resposta += "- /perfil_actual → Diu amb quin perfil estàs ara.\n"
    resposta += "- També pots escriure: entra al perfil de Clàudia\n\n"

    resposta += "🧠 Memòria i coneixement:\n"
    resposta += "- /stats → Mostra quantes coses sap la IA.\n"
    resposta += "- /backup → Fa una còpia de seguretat completa.\n\n"

    resposta += "💬 Pots preguntar coses normals:\n"
    resposta += "- que saps de la Raspberry Pi 5?\n"
    resposta += "- que es una Raspberry Pi 5?\n"
    resposta += "- per que serveix una Raspberry Pi 5?\n"
    resposta += "- explica Minecraft\n"
    resposta += "- que li agrada a la Clàudia?\n\n"

    resposta += "📝 Per ensenyar-li coses:\n"
    resposta += "- recorda que el meu color preferit és groc\n"
    resposta += "- recorda que el meu joc preferit és Minecraft"

    return resposta


def formatar_perfil(clau, dades):
    nom = dades.get("nom", clau)

    resposta = f"👤 Perfil actiu: {nom}\n"
    resposta += "━━━━━━━━━━━━━━━━━━━━\n\n"

    resposta += "📌 Dades principals:\n"

    camps_principals = ["nom", "genere", "tracte", "edat", "color_preferit"]

    for camp in camps_principals:
        if camp in dades:
            resposta += f"- {clau_bonica(camp)}: {valor_bonic(dades[camp])}\n"

    resposta += "\n🔗 Enllaços:\n"

    hi_ha_enllacos = False

    for camp in ["web", "youtube"]:
        if camp in dades:
            hi_ha_enllacos = True
            resposta += f"- {clau_bonica(camp)}: {valor_bonic(dades[camp])}\n"

    if not hi_ha_enllacos:
        resposta += "- No hi ha enllaços guardats.\n"

    if "li_agrada" in dades:
        resposta += "\n⭐ Li agrada:\n"

        if isinstance(dades["li_agrada"], list):
            for item in dades["li_agrada"]:
                resposta += f"- {item}\n"
        else:
            resposta += f"- {dades['li_agrada']}\n"

    altres = []

    for camp, valor in dades.items():
        if camp not in camps_principals and camp not in ["web", "youtube", "li_agrada"]:
            altres.append((camp, valor))

    if altres:
        resposta += "\n🧠 Altres dades:\n"

        for camp, valor in altres:
            resposta += f"- {clau_bonica(camp)}: {valor_bonic(valor)}\n"

    return resposta.strip()


def formatar_perfils(perfils, config):
    clau_activa = obtenir_clau_perfil_actiu(perfils, config)

    resposta = "👥 Perfils disponibles\n"
    resposta += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for index, clau in enumerate(perfils.keys(), start=1):
        nom = perfils[clau].get("nom", clau)
        marca = "✅" if clau == clau_activa else "•"
        resposta += f"{marca} {index}. {nom}\n"

    resposta += "\nPer canviar de perfil pots usar el selector de l'esquerra o escriure:\n"
    resposta += "- entra al perfil de Martí\n"
    resposta += "- entra al perfil de Clàudia"

    return resposta


def formatar_stats(coneixement, biblioteca, perfils, config, notes):
    nom = obtenir_nom_perfil_actiu(perfils, config)
    tracte = obtenir_tracte(perfils, config)

    resposta = "📊 Estadístiques\n"
    resposta += "━━━━━━━━━━━━━━━━━━━━\n\n"
    resposta += f"- Preguntes apreses: {len(coneixement)}\n"
    resposta += f"- Temes biblioteca internet: {len(biblioteca)}\n"
    resposta += f"- Perfils guardats: {len(perfils)}\n"
    resposta += f"- Notes guardades: {len(notes)}\n"
    resposta += f"- Perfil actiu: {nom}\n"
    resposta += f"- Tracte actual: {tracte}\n"
    resposta += f"- Cervell V7 importat: {'sí' if cervell else 'no'}"

    if ERROR_CERVELL:
        resposta += f"\n- Error cervell V7: {ERROR_CERVELL}"

    return resposta


# =========================
# CALCULADORA
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

    if isinstance(node, ast.BinOp):
        esquerra = calcular_node(node.left)
        dreta = calcular_node(node.right)
        operador = type(node.op)

        if operador not in OPERADORS:
            raise ValueError("Operació no permesa")

        return OPERADORS[operador](esquerra, dreta)

    if isinstance(node, ast.UnaryOp):
        valor = calcular_node(node.operand)

        if isinstance(node.op, ast.UAdd):
            return valor

        if isinstance(node.op, ast.USub):
            return -valor

    raise ValueError("Expressió no vàlida")


def intentar_calcular(text):
    if cervell and hasattr(cervell, "intentar_calcular"):
        try:
            resposta = cervell.intentar_calcular(text)
            if resposta:
                return resposta
        except Exception:
            pass

    text_normal = normalitzar_text(text)
    text_normal = text_normal.replace("quant fa", "")
    text_normal = text_normal.replace("calcula", "")
    text_normal = text_normal.replace("que fa", "")
    text_normal = text_normal.replace("x", "*")
    text_normal = text_normal.strip()

    if not re.fullmatch(r"[0-9+\-*/().%\s]+", text_normal):
        return None

    if not re.search(r"[+\-*/%]", text_normal):
        return None

    try:
        arbre = ast.parse(text_normal, mode="eval")
        resultat = calcular_node(arbre)

        if isinstance(resultat, float) and resultat.is_integer():
            resultat = int(resultat)

        return f"{text_normal} = {resultat}"

    except Exception:
        return None


# =========================
# CERCADOR DE MEMÒRIA
# =========================

PARAULES_BUIDES = {
    "el", "la", "els", "les", "un", "una", "uns", "unes",
    "de", "del", "dels", "a", "amb", "en", "i", "o",
    "que", "es", "per", "perque", "perquè", "serveix",
    "explica", "explicam", "parlem", "sobre", "vull",
    "saps", "saber", "dir", "em", "pots", "quin", "quina",
    "fes", "resum", "aixo", "això"
}


def paraules_importants(text):
    text = normalitzar_text(text)
    resultat = []

    for paraula in text.split():
        if len(paraula) <= 1:
            continue

        if paraula in PARAULES_BUIDES:
            continue

        resultat.append(paraula)

    return resultat


def extreure_tema(text):
    text_normal = normalitzar_text(text)

    patrons = [
        r"^que saps de (.+)$",
        r"^que es (.+)$",
        r"^per que serveix (.+)$",
        r"^per a que serveix (.+)$",
        r"^explica (.+)$",
        r"^parlem de (.+)$",
        r"^parlem sobre (.+)$",
        r"^resum de (.+)$",
        r"^fes un resum de (.+)$"
    ]

    for patro in patrons:
        coincidencia = re.match(patro, text_normal)

        if coincidencia:
            return coincidencia.group(1).strip()

    paraules = paraules_importants(text_normal)

    if paraules:
        return " ".join(paraules)

    return text_normal


def puntuacio(pregunta, clau, resposta):
    pregunta_normal = normalitzar_text(pregunta)
    tema = extreure_tema(pregunta)
    candidat = normalitzar_text(str(clau) + " " + str(resposta))

    score = 0

    if tema in candidat:
        score += 90

    if pregunta_normal in candidat:
        score += 70

    paraules = paraules_importants(tema)

    for paraula in paraules:
        if paraula in candidat:
            score += 16

    if paraules and all(p in candidat for p in paraules):
        score += 40

    ratio = difflib.SequenceMatcher(None, tema, candidat[:250]).ratio()
    score += ratio * 25

    return score


def formatar_resposta_memoria(pregunta, resposta):
    pregunta_normal = normalitzar_text(pregunta)

    if "serveix" in pregunta_normal:
        return "Pel que tinc guardat, serveix o es pot utilitzar així:\n" + resposta

    if pregunta_normal.startswith("parlem"):
        return "Vale, parlem d’això. Tinc guardat això:\n" + resposta

    if pregunta_normal.startswith("explica") or "resum" in pregunta_normal:
        return "T’ho explico amb el que tinc a la memòria:\n" + resposta

    return resposta


def buscar_memoria_fallback(pregunta, coneixement, biblioteca):
    pregunta_normal = normalitzar_text(pregunta)

    if pregunta_normal in coneixement:
        dades = coneixement[pregunta_normal]

        if isinstance(dades, dict):
            return dades.get("resposta", "")
        return str(dades)

    millor_score = 0
    millor_resposta = None

    for clau, dades in coneixement.items():
        if isinstance(dades, dict):
            resposta = dades.get("resposta", "")
        else:
            resposta = str(dades)

        score = puntuacio(pregunta, clau, resposta)

        if score > millor_score:
            millor_score = score
            millor_resposta = resposta

    for clau, entrada in biblioteca.items():
        if not isinstance(entrada, dict):
            continue

        titol = entrada.get("titol", "")
        tema = entrada.get("tema", "")
        resum = entrada.get("resum", "")
        font = entrada.get("font", "")
        url = entrada.get("url", "")

        resposta = f"{titol}: {resum}"

        if font or url:
            resposta += f"\n\nFont: {font} - {url}"

        score = puntuacio(pregunta, f"{clau} {titol} {tema}", resposta)

        if score > millor_score:
            millor_score = score
            millor_resposta = resposta

    if millor_score >= 55 and millor_resposta:
        return formatar_resposta_memoria(pregunta, millor_resposta)

    return None


def buscar_resposta_intelligent(pregunta, coneixement, biblioteca):
    if cervell and hasattr(cervell, "buscar_resposta_intelligent"):
        try:
            resposta = cervell.buscar_resposta_intelligent(pregunta, coneixement, biblioteca)
            if resposta:
                return resposta
        except Exception:
            pass

    return buscar_memoria_fallback(pregunta, coneixement, biblioteca)


def buscar_resposta_exacta(pregunta, coneixement):
    if cervell and hasattr(cervell, "buscar_resposta"):
        try:
            resposta, pregunta_trobada, semblanca = cervell.buscar_resposta(pregunta, coneixement)
            return resposta, pregunta_trobada, semblanca
        except Exception:
            pass

    pregunta_normal = normalitzar_text(pregunta)

    if pregunta_normal in coneixement:
        dades = coneixement[pregunta_normal]

        if isinstance(dades, dict):
            return dades.get("resposta", ""), pregunta_normal, 1.0

        return str(dades), pregunta_normal, 1.0

    millor = None
    millor_score = 0

    for clau in coneixement.keys():
        ratio = difflib.SequenceMatcher(None, pregunta_normal, clau).ratio()

        if ratio > millor_score:
            millor_score = ratio
            millor = clau

    if millor and millor_score >= 0.75:
        dades = coneixement[millor]

        if isinstance(dades, dict):
            return dades.get("resposta", ""), millor, millor_score

        return str(dades), millor, millor_score

    return None, None, 0


# =========================
# RESPOSTA PRINCIPAL
# =========================

def resposta_web(missatge):
    coneixement, biblioteca, perfils, config, notes = carregar_tot()

    pregunta = str(missatge).strip()

    if pregunta == "":
        return ""

    guardar_historial("TU", pregunta)

    comanda = normalitzar_text(pregunta)

    if comanda == "/sortir":
        return "A la web no cal fer /sortir. Tanca la pestanya o para el servidor amb Ctrl + C."

    if comanda == "/ajuda":
        resposta = formatar_ajuda()
        guardar_historial("IA", resposta)
        return personalitzar_resposta(resposta, perfils, config)

    if comanda == "/perfil":
        clau = obtenir_clau_perfil_actiu(perfils, config)
        resposta = formatar_perfil(clau, perfils[clau])
        guardar_historial("IA", resposta)
        return personalitzar_resposta(resposta, perfils, config)

    if comanda == "/perfils":
        resposta = formatar_perfils(perfils, config)
        guardar_historial("IA", resposta)
        return personalitzar_resposta(resposta, perfils, config)

    if comanda == "/perfil_actual":
        nom = obtenir_nom_perfil_actiu(perfils, config)
        tracte = obtenir_tracte(perfils, config)
        resposta = f"👤 Ara estàs amb el perfil de {nom}.\n💬 Tracte actual: {tracte}"
        guardar_historial("IA", resposta)
        return personalitzar_resposta(resposta, perfils, config)

    if comanda == "/stats":
        resposta = formatar_stats(coneixement, biblioteca, perfils, config, notes)
        guardar_historial("IA", resposta)
        return personalitzar_resposta(resposta, perfils, config)

    if comanda == "/backup":
        fer_backup_complet()
        resposta = "💾 Backup complet creat correctament ✅"
        guardar_historial("IA", resposta)
        return personalitzar_resposta(resposta, perfils, config)

    resposta_canvi_perfil = intentar_canviar_perfil(pregunta, perfils, config)

    if resposta_canvi_perfil:
        guardar_historial("IA", resposta_canvi_perfil)
        return personalitzar_resposta(resposta_canvi_perfil, perfils, config)

    resposta_record = intentar_recordar(pregunta, perfils, config)

    if resposta_record:
        guardar_historial("IA", resposta_record)
        return personalitzar_resposta(resposta_record, perfils, config)

    resposta_perfil = respondre_perfil(pregunta, perfils, config)

    if resposta_perfil:
        guardar_historial("IA", resposta_perfil)
        return personalitzar_resposta(resposta_perfil, perfils, config)

    resposta_mates = intentar_calcular(pregunta)

    if resposta_mates:
        guardar_historial("IA", resposta_mates)
        return personalitzar_resposta(resposta_mates, perfils, config)

    resposta_exacta, pregunta_trobada, semblanca = buscar_resposta_exacta(pregunta, coneixement)

    if resposta_exacta and semblanca >= 0.92:
        guardar_coneixement(coneixement)
        guardar_historial("IA", resposta_exacta)
        return personalitzar_resposta(resposta_exacta, perfils, config)

    resposta_memoria = buscar_resposta_intelligent(pregunta, coneixement, biblioteca)

    if resposta_memoria:
        guardar_coneixement(coneixement)
        guardar_historial("IA", resposta_memoria)
        return personalitzar_resposta(resposta_memoria, perfils, config)

    if resposta_exacta:
        resposta = f"Crec que vols dir: '{pregunta_trobada}' 🤔\n\n{resposta_exacta}"
        guardar_coneixement(coneixement)
        guardar_historial("IA", resposta)
        return personalitzar_resposta(resposta, perfils, config)

    resposta = "No sé respondre això encara 😅\n\nPer ensenyar-m'ho, escriu per exemple:\n- recorda que el meu joc preferit és Minecraft"
    guardar_historial("IA", resposta)
    return personalitzar_resposta(resposta, perfils, config)


def intentar_canviar_perfil(pregunta, perfils, config):
    if cervell and hasattr(cervell, "intentar_canviar_perfil_per_text"):
        try:
            resposta = cervell.intentar_canviar_perfil_per_text(pregunta, perfils, config)
            if resposta:
                return resposta
        except Exception:
            pass

    text = normalitzar_text(pregunta)

    if "perfil" not in text and "entra" not in text:
        return None

    for clau, dades in perfils.items():
        nom = normalitzar_text(dades.get("nom", clau))

        if clau in text or nom in text:
            config["perfil_actiu"] = clau
            guardar_config(config)

            tracte = dades.get("tracte", "bro")
            return f"Has entrat al perfil de {dades.get('nom', clau)}, {tracte} ✅"

    return None


def intentar_recordar(pregunta, perfils, config):
    if cervell and hasattr(cervell, "guardar_record_automatic_perfil_actiu"):
        try:
            resposta = cervell.guardar_record_automatic_perfil_actiu(pregunta, perfils, config)
            if resposta:
                return resposta
        except Exception:
            pass

    match = re.match(r"recorda que (.+?) (?:es|és) (.+)", pregunta, re.IGNORECASE)

    if not match:
        return None

    clau_perfil = obtenir_clau_perfil_actiu(perfils, config)
    camp = normalitzar_text(match.group(1)).replace(" ", "_")
    valor = match.group(2).strip()

    perfils[clau_perfil][camp] = valor
    guardar_json(FITXER_PERFILS, perfils)

    tracte = obtenir_tracte(perfils, config)

    return f"Guardat, {tracte}! {clau_bonica(camp)} és {valor} 🧠💾"


def respondre_perfil(pregunta, perfils, config):
    if cervell and hasattr(cervell, "respondre_des_de_perfils"):
        try:
            resposta = cervell.respondre_des_de_perfils(pregunta, perfils)
            if resposta:
                return resposta
        except Exception:
            pass

    if cervell and hasattr(cervell, "respondre_des_del_perfil_actiu"):
        try:
            resposta = cervell.respondre_des_del_perfil_actiu(pregunta, perfils, config)
            if resposta:
                return resposta
        except Exception:
            pass

    text = normalitzar_text(pregunta)

    clau = obtenir_clau_perfil_actiu(perfils, config)
    dades = perfils[clau]
    nom = dades.get("nom", clau)

    if text in ["que saps de mi", "que recordes de mi", "perfil", "veure perfil"]:
        return formatar_perfil(clau, dades)

    if "com em dic" in text:
        return f"Et dius {nom}."

    if "color preferit" in text and "color_preferit" in dades:
        return f"El color preferit de {nom} és {dades['color_preferit']}."

    if "que li agrada" in text or "que tagrada" in text:
        if "li_agrada" in dades:
            return f"A {nom} li agrada: {valor_bonic(dades['li_agrada'])}."

    return None


def fer_backup_complet():
    temps = datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta = CARPETA_BACKUPS / f"backup_web_{temps}"
    carpeta.mkdir(parents=True, exist_ok=True)

    fitxers = [
        FITXER_CONEIXEMENT,
        FITXER_BIBLIOTECA,
        FITXER_PERFILS,
        FITXER_CONFIG,
        FITXER_NOTES
    ]

    for fitxer in fitxers:
        if fitxer.exists():
            shutil.copy(fitxer, carpeta / fitxer.name)


# =========================
# API WEB
# =========================

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "app": "MARTINAKUS IA WEB V8"
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        dades = request.get_json(silent=True) or {}
        missatge = dades.get("missatge", "")

        resposta = resposta_web(missatge)

        return jsonify({
            "resposta": resposta
        })

    except Exception as error:
        print("ERROR A /api/chat:")
        traceback.print_exc()

        return jsonify({
            "error": str(error),
            "resposta": "Error intern del servidor."
        }), 500


@app.route("/api/perfils")
def api_perfils():
    try:
        coneixement, biblioteca, perfils, config, notes = carregar_tot()

        clau = obtenir_clau_perfil_actiu(perfils, config)
        nom_actiu = perfils[clau].get("nom", clau)
        tracte = obtenir_tracte(perfils, config)

        return jsonify({
            "perfils": perfils,
            "perfil_actiu": clau,
            "nom_actiu": nom_actiu,
            "tracte": tracte,
            "total_coneixement": len(coneixement),
            "total_biblioteca": len(biblioteca),
            "total_notes": len(notes),
            "estat_cervell": "OK" if cervell else "fallback"
        })

    except Exception as error:
        print("ERROR A /api/perfils:")
        traceback.print_exc()

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/canviar_perfil", methods=["POST"])
def api_canviar_perfil():
    try:
        dades = request.get_json(silent=True) or {}
        perfil_nou = dades.get("perfil", "marti")

        coneixement, biblioteca, perfils, config, notes = carregar_tot()

        if perfil_nou not in perfils:
            return jsonify({
                "resposta": "Aquest perfil no existeix 😅"
            })

        config["perfil_actiu"] = perfil_nou
        guardar_config(config)

        nom = perfils[perfil_nou].get("nom", perfil_nou)
        tracte = obtenir_tracte(perfils, config)

        resposta = f"Has entrat al perfil de {nom}, {tracte} ✅"
        resposta = personalitzar_resposta(resposta, perfils, config)

        guardar_historial("IA", resposta)

        return jsonify({
            "resposta": resposta
        })

    except Exception as error:
        print("ERROR A /api/canviar_perfil:")
        traceback.print_exc()

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/perfil_actual")
def api_perfil_actual():
    try:
        coneixement, biblioteca, perfils, config, notes = carregar_tot()

        clau = obtenir_clau_perfil_actiu(perfils, config)
        resposta = formatar_perfil(clau, perfils[clau])
        resposta = personalitzar_resposta(resposta, perfils, config)

        return jsonify({
            "resposta": resposta
        })

    except Exception as error:
        print("ERROR A /api/perfil_actual:")
        traceback.print_exc()

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/stats")
def api_stats():
    try:
        coneixement, biblioteca, perfils, config, notes = carregar_tot()

        resposta = formatar_stats(coneixement, biblioteca, perfils, config, notes)
        resposta = personalitzar_resposta(resposta, perfils, config)

        return jsonify({
            "resposta": resposta
        })

    except Exception as error:
        print("ERROR A /api/stats:")
        traceback.print_exc()

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/backup", methods=["POST"])
def api_backup():
    try:
        fer_backup_complet()

        return jsonify({
            "resposta": "💾 Backup complet creat correctament ✅"
        })

    except Exception as error:
        print("ERROR A /api/backup:")
        traceback.print_exc()

        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("MARTINAKUS IA WEB V8")
    print("Obre al navegador:")
    print(f"http://127.0.0.1:{port}")

    app.run(host="0.0.0.0", port=port, debug=False)
