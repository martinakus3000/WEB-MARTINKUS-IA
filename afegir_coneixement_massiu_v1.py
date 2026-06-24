import json
import shutil
import unicodedata
from pathlib import Path
from datetime import datetime

# =========================
# PACK MASSIU DE CONEIXEMENT
# MARTINAKUS IA
# =========================
# Aquest script afegeix moltes preguntes i respostes
# a coneixement.json sense utilitzar internet.
#
# Després funcionarà tant a:
# - chatbot_ia_v7.py
# - ia_web_v8.py

CARPETA_IA = Path(r"C:\Users\marti\Desktop\ia")
CARPETA_IA.mkdir(parents=True, exist_ok=True)

FITXER_CONEIXEMENT = CARPETA_IA / "coneixement.json"

CARPETA_BACKUPS = CARPETA_IA / "backups"
CARPETA_BACKUPS.mkdir(parents=True, exist_ok=True)

SOBREESCRIURE_PACK = True


def ara():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def treure_accents(text):
    text = unicodedata.normalize("NFD", str(text))
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

    return valor_defecte


def guardar_json(ruta, dades):
    with open(ruta, "w", encoding="utf-8") as fitxer:
        json.dump(dades, fitxer, ensure_ascii=False, indent=4)


def fer_backup():
    if FITXER_CONEIXEMENT.exists():
        nom = f"coneixement_backup_abans_pack_massiu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(FITXER_CONEIXEMENT, CARPETA_BACKUPS / nom)
        print(f"Backup creat: {CARPETA_BACKUPS / nom}")


def eliminar_errors_importador(coneixement):
    claus_a_borrar = []

    for clau, dades in coneixement.items():
        if isinstance(dades, dict):
            resposta = dades.get("resposta", "")
        else:
            resposta = str(dades)

        text_total = normalitzar_text(clau + " " + resposta)

        if "legon cities fc" in text_total:
            claus_a_borrar.append(clau)

    for clau in claus_a_borrar:
        del coneixement[clau]

    if claus_a_borrar:
        print(f"Eliminades entrades equivocades: {len(claus_a_borrar)}")


def crear_preguntes(tema, aliases):
    termes = [tema] + aliases

    plantilles = [
        "{tema}",
        "que es {tema}",
        "què és {tema}",
        "que és {tema}",
        "explica {tema}",
        "explicam {tema}",
        "parlem de {tema}",
        "parlem sobre {tema}",
        "que saps de {tema}",
        "què saps de {tema}",
        "que saps de la {tema}",
        "que saps del {tema}",
        "resum de {tema}",
        "fes un resum de {tema}",
        "per que serveix {tema}",
        "per què serveix {tema}",
        "per a que serveix {tema}",
        "per a què serveix {tema}",
        "com funciona {tema}",
        "vull saber de {tema}"
    ]

    preguntes = []

    for terme in termes:
        for plantilla in plantilles:
            preguntes.append(plantilla.format(tema=terme))

    return preguntes


def afegir_entrada(coneixement, tema, resposta, categoria, aliases=None, preguntes_extra=None):
    if aliases is None:
        aliases = []

    if preguntes_extra is None:
        preguntes_extra = []

    preguntes = crear_preguntes(tema, aliases) + preguntes_extra

    afegides = 0
    actualitzades = 0

    for pregunta in preguntes:
        clau = normalitzar_text(pregunta)

        nova_entrada = {
            "resposta": resposta,
            "vegades_utilitzat": 0,
            "creat": ara(),
            "categoria": categoria,
            "tema": tema,
            "font": "Pack manual massiu MARTINAKUS IA V1"
        }

        if clau in coneixement:
            if SOBREESCRIURE_PACK:
                coneixement[clau] = nova_entrada
                actualitzades += 1
        else:
            coneixement[clau] = nova_entrada
            afegides += 1

    return afegides, actualitzades


def main():
    fer_backup()

    coneixement = carregar_json(FITXER_CONEIXEMENT, {})
    eliminar_errors_importador(coneixement)

    entrades = [
        {
            "tema": "Raspberry Pi 5",
            "categoria": "tecnologia",
            "aliases": ["Raspberry Pi", "raspberry", "mini ordinador raspberry"],
            "resposta": "La Raspberry Pi 5 és un mini ordinador petit però bastant potent. Serveix per aprendre programació, provar Linux, fer servidors casolans, projectes d'electrònica, robots, domòtica, retro gaming i experiments de tecnologia."
        },
        {
            "tema": "Arduino",
            "categoria": "electrònica",
            "aliases": ["placa Arduino"],
            "resposta": "Arduino és una placa electrònica programable. Serveix per controlar LEDs, motors, sensors, pantalles, robots i invents electrònics. És molt bona per aprendre electrònica i programació física."
        },
        {
            "tema": "microcontrolador",
            "categoria": "electrònica",
            "aliases": ["micro controlador"],
            "resposta": "Un microcontrolador és un xip petit que pot executar programes i controlar components electrònics. S'utilitza en robots, electrodomèstics, sensors, joguines, plaques Arduino i molts aparells intel·ligents."
        },
        {
            "tema": "sensor",
            "categoria": "electrònica",
            "aliases": ["sensors"],
            "resposta": "Un sensor és un component que detecta alguna cosa del món real, com llum, temperatura, moviment, distància, so o humitat. Després envia aquesta informació a una placa o ordinador."
        },
        {
            "tema": "LED",
            "categoria": "electrònica",
            "aliases": ["llum LED", "diode LED"],
            "resposta": "Un LED és un component electrònic que fa llum quan hi passa corrent. Consumeix poca energia i s'utilitza en pantalles, llums, indicadors, projectes Arduino i decoració."
        },
        {
            "tema": "servo motor",
            "categoria": "robòtica",
            "aliases": ["servo", "servomotor"],
            "resposta": "Un servo motor és un motor que es pot moure a una posició concreta. Serveix per fer braços robòtics, portes automàtiques, vehicles petits, mecanismes i projectes d'Arduino."
        },
        {
            "tema": "GPIO",
            "categoria": "Raspberry Pi",
            "aliases": ["pins GPIO", "pins de la raspberry"],
            "resposta": "GPIO són pins d'entrada i sortida que té una placa com la Raspberry Pi. Serveixen per connectar LEDs, botons, sensors, relés, motors i altres components electrònics."
        },
        {
            "tema": "Linux",
            "categoria": "sistemes operatius",
            "aliases": ["GNU Linux", "sistema Linux"],
            "resposta": "Linux és un sistema operatiu molt utilitzat en servidors, Raspberry Pi, ordinadors i dispositius. És potent, personalitzable i molt important per aprendre tecnologia i programació."
        },
        {
            "tema": "terminal",
            "categoria": "programació",
            "aliases": ["consola", "cmd", "terminal de comandos"],
            "resposta": "La terminal és una finestra on escrius ordres per controlar l'ordinador. Serveix per executar programes, instal·lar paquets, moure fitxers, gestionar projectes i treballar com un programador pro."
        },
        {
            "tema": "servidor",
            "categoria": "xarxes",
            "aliases": ["server", "servidor casolà"],
            "resposta": "Un servidor és un ordinador o programa que ofereix serveis a altres dispositius. Pot servir webs, fitxers, jocs, bases de dades, APIs o automatitzacions."
        },
        {
            "tema": "NAS",
            "categoria": "xarxes",
            "aliases": ["servidor de fitxers", "emmagatzematge en xarxa"],
            "resposta": "Un NAS és un sistema d'emmagatzematge connectat a la xarxa. Serveix per guardar fitxers, fotos, vídeos i còpies de seguretat accessibles des de diferents dispositius."
        },
        {
            "tema": "domòtica",
            "categoria": "tecnologia",
            "aliases": ["casa intel·ligent", "smart home"],
            "resposta": "La domòtica és la tecnologia que automatitza coses de casa, com llums, persianes, sensors, alarmes, endolls i temperatura. Es pot fer amb Raspberry Pi, Arduino o dispositius intel·ligents."
        },
        {
            "tema": "Internet de les coses",
            "categoria": "tecnologia",
            "aliases": ["IoT", "internet of things"],
            "resposta": "L'Internet de les coses és quan objectes físics es connecten a internet o a una xarxa. Per exemple sensors, rellotges, bombetes, càmeres, termòstats i dispositius domòtics."
        },
        {
            "tema": "robòtica",
            "categoria": "tecnologia",
            "aliases": ["robots", "robotica"],
            "resposta": "La robòtica combina programació, electrònica i mecànica per crear màquines que poden moure's, detectar coses i fer tasques automàticament."
        },
        {
            "tema": "dron",
            "categoria": "tecnologia",
            "aliases": ["drone"],
            "resposta": "Un dron és un vehicle volador controlat a distància o automàticament. Pot servir per gravar vídeos, fer fotos, inspeccions, curses, aprendre electrònica i projectes de robòtica."
        },
        {
            "tema": "impressió 3D",
            "categoria": "impressió 3D",
            "aliases": ["impressora 3D", "impresora 3d", "impressio 3d"],
            "resposta": "La impressió 3D permet crear objectes físics capa per capa amb plàstic o altres materials. Serveix per fer peces, figures, prototips, suports, carcasses i invents personalitzats."
        },
        {
            "tema": "Ender 3 V2 Neo",
            "categoria": "impressió 3D",
            "aliases": ["Creality Ender 3", "Ender 3", "Ender 3 V2"],
            "resposta": "La Ender 3 V2 Neo és una impressora 3D popular de Creality. Serveix per imprimir peces amb filament com PLA i és molt bona per aprendre impressió 3D, calibració i disseny de peces."
        },
        {
            "tema": "PLA",
            "categoria": "impressió 3D",
            "aliases": ["filament PLA"],
            "resposta": "El PLA és un filament molt utilitzat en impressió 3D. És fàcil d'imprimir, va bé per figures, prototips i peces decoratives, però no aguanta tanta calor com altres materials."
        },
        {
            "tema": "PETG",
            "categoria": "impressió 3D",
            "aliases": ["filament PETG"],
            "resposta": "El PETG és un filament d'impressió 3D més resistent que el PLA i aguanta millor cops i temperatura. Pot ser una mica més difícil d'imprimir, però va bé per peces més fortes."
        },
        {
            "tema": "slicer",
            "categoria": "impressió 3D",
            "aliases": ["laminador 3D", "programa slicer"],
            "resposta": "Un slicer és un programa que converteix un model 3D en instruccions per a una impressora 3D. Genera el G-code indicant moviments, temperatura, velocitat i capes."
        },
        {
            "tema": "G-code",
            "categoria": "impressió 3D",
            "aliases": ["gcode"],
            "resposta": "El G-code és el llenguatge d'instruccions que utilitzen moltes impressores 3D i màquines CNC. Indica moviments, temperatures, velocitats i altres ordres."
        },
        {
            "tema": "Python",
            "categoria": "programació",
            "aliases": ["llenguatge Python"],
            "resposta": "Python és un llenguatge de programació fàcil de llegir i molt potent. Serveix per crear IA, webs, automatitzacions, scripts, jocs simples, bots, anàlisi de dades i projectes amb Raspberry Pi."
        },
        {
            "tema": "variable",
            "categoria": "programació",
            "aliases": ["variables"],
            "resposta": "Una variable és com una capsa amb un nom on guardes informació dins d'un programa. Pot guardar números, text, llistes, valors cert/fals i moltes altres dades."
        },
        {
            "tema": "condicional",
            "categoria": "programació",
            "aliases": ["if", "else", "if else"],
            "resposta": "Un condicional permet que un programa prengui decisions. Per exemple: si passa això, fes una cosa; si no, fes una altra."
        },
        {
            "tema": "bucle",
            "categoria": "programació",
            "aliases": ["loops", "for", "while"],
            "resposta": "Un bucle serveix per repetir instruccions. Per exemple, un bucle pot revisar tots els elements d'una llista o repetir una acció fins que es compleixi una condició."
        },
        {
            "tema": "funció",
            "categoria": "programació",
            "aliases": ["funcio", "funcions"],
            "resposta": "Una funció és un bloc de codi amb nom que pots reutilitzar. Serveix per ordenar millor un programa i evitar repetir el mateix codi moltes vegades."
        },
        {
            "tema": "llista",
            "categoria": "programació",
            "aliases": ["array", "llistes"],
            "resposta": "Una llista és una estructura que guarda diversos elements en ordre. En Python pots fer servir llistes per guardar noms, números, objectes o dades d'un programa."
        },
        {
            "tema": "diccionari",
            "categoria": "programació",
            "aliases": ["dictionary", "dict"],
            "resposta": "Un diccionari en Python guarda dades amb clau i valor. Per exemple, una clau pot ser 'nom' i el valor 'Martí'. És molt útil per perfils, configuracions i dades JSON."
        },
        {
            "tema": "JSON",
            "categoria": "programació",
            "aliases": ["fitxer JSON"],
            "resposta": "JSON és un format per guardar dades de manera ordenada amb claus i valors. La teva IA l'utilitza per guardar coneixement, perfils, notes i configuració."
        },
        {
            "tema": "API",
            "categoria": "programació web",
            "aliases": ["apis"],
            "resposta": "Una API és una manera perquè dos programes es comuniquin. Per exemple, la teva web envia un missatge a Python i Python torna una resposta a través d'una API."
        },
        {
            "tema": "Flask",
            "categoria": "programació web",
            "aliases": ["python flask"],
            "resposta": "Flask és una eina de Python per crear webs i APIs. Serveix per connectar una interfície HTML amb un programa Python, com la MARTINAKUS IA WEB."
        },
        {
            "tema": "HTML",
            "categoria": "programació web",
            "aliases": ["llenguatge HTML"],
            "resposta": "HTML és el llenguatge que dona estructura a una pàgina web. Serveix per posar títols, textos, botons, imatges, enllaços, formularis i seccions."
        },
        {
            "tema": "CSS",
            "categoria": "programació web",
            "aliases": ["estils CSS"],
            "resposta": "CSS serveix per donar estil a una web. Amb CSS pots canviar colors, fonts, mides, marges, animacions, distribució i fer que una pàgina sigui més guapa."
        },
        {
            "tema": "JavaScript",
            "categoria": "programació web",
            "aliases": ["JS"],
            "resposta": "JavaScript dona interactivitat a les webs. Serveix per fer botons, xats, menús, animacions, jocs web i comunicació amb servidors."
        },
        {
            "tema": "frontend",
            "categoria": "programació web",
            "aliases": ["front end"],
            "resposta": "El frontend és la part visible d'una web: botons, textos, colors, formularis i pantalla. Normalment es fa amb HTML, CSS i JavaScript."
        },
        {
            "tema": "backend",
            "categoria": "programació web",
            "aliases": ["back end"],
            "resposta": "El backend és la part invisible d'una web que funciona al servidor. Gestiona dades, usuaris, memòria, fitxers i respostes. En la teva IA, Python i Flask fan de backend."
        },
        {
            "tema": "base de dades",
            "categoria": "programació",
            "aliases": ["database", "BBDD"],
            "resposta": "Una base de dades serveix per guardar informació de manera organitzada i poder buscar-la ràpid. Pot guardar usuaris, missatges, productes, perfils o coneixement."
        },
        {
            "tema": "SQLite",
            "categoria": "programació",
            "aliases": ["sqlite database"],
            "resposta": "SQLite és una base de dades lleugera que funciona en un sol fitxer. És molt útil per projectes petits, apps locals i programes Python."
        },
        {
            "tema": "Git",
            "categoria": "programació",
            "aliases": ["control de versions"],
            "resposta": "Git és una eina per guardar versions del teu codi. Serveix per tornar enrere, veure canvis, treballar en projectes i no perdre el progrés."
        },
        {
            "tema": "GitHub",
            "categoria": "programació",
            "aliases": ["github repositori"],
            "resposta": "GitHub és una plataforma per guardar projectes de codi amb Git. Serveix per tenir còpies al núvol, compartir projectes, col·laborar i publicar codi."
        },
        {
            "tema": "bug",
            "categoria": "programació",
            "aliases": ["error de programació", "bugs"],
            "resposta": "Un bug és un error en un programa. Pot fer que una funció no respongui, que surti un resultat incorrecte o que el programa peti."
        },
        {
            "tema": "debugging",
            "categoria": "programació",
            "aliases": ["depurar", "debug"],
            "resposta": "Debugging és el procés de trobar i arreglar errors en un programa. Es fa llegint missatges d'error, provant parts del codi i revisant què està passant."
        },
        {
            "tema": "VS Code",
            "categoria": "programació",
            "aliases": ["Visual Studio Code"],
            "resposta": "VS Code és un editor de codi molt utilitzat. Serveix per programar en Python, HTML, CSS, JavaScript i molts altres llenguatges amb extensions útils."
        },
        {
            "tema": "WordPress",
            "categoria": "web",
            "aliases": ["wordpress web"],
            "resposta": "WordPress és una plataforma per crear webs i blogs. Serveix per publicar articles, pàgines, vídeos, notícies i contingut sense haver de programar-ho tot des de zero."
        },
        {
            "tema": "YouTube",
            "categoria": "contingut",
            "aliases": ["canal de YouTube"],
            "resposta": "YouTube és una plataforma per publicar i veure vídeos. Serveix per compartir gameplays, tutorials, novetats, ressenyes, directes i contingut creatiu."
        },
        {
            "tema": "creador de contingut",
            "categoria": "contingut",
            "aliases": ["content creator"],
            "resposta": "Un creador de contingut és algú que fa vídeos, articles, posts, directes o materials per internet. Pot parlar de videojocs, tecnologia, manualitats, ressenyes o qualsevol tema."
        },
        {
            "tema": "streaming",
            "categoria": "contingut",
            "aliases": ["directe", "stream"],
            "resposta": "Streaming és transmetre vídeo o àudio en directe o sota demanda. Serveix per fer directes de videojocs, xerrades, tutorials o esdeveniments."
        },
        {
            "tema": "intel·ligència artificial",
            "categoria": "IA",
            "aliases": ["IA", "AI", "inteligencia artificial"],
            "resposta": "La intel·ligència artificial és una tecnologia que permet que un programa faci tasques que semblen intel·ligents, com respondre preguntes, classificar informació, aprendre patrons o generar text."
        },
        {
            "tema": "machine learning",
            "categoria": "IA",
            "aliases": ["aprenentatge automàtic"],
            "resposta": "El machine learning és una part de la IA on els programes aprenen a partir de dades. En lloc de programar totes les regles a mà, el model troba patrons."
        },
        {
            "tema": "deep learning",
            "categoria": "IA",
            "aliases": ["aprenentatge profund"],
            "resposta": "El deep learning és una tècnica d'IA basada en xarxes neuronals grans. S'utilitza en reconeixement d'imatges, veu, traducció, xatbots i models avançats."
        },
        {
            "tema": "xarxa neuronal",
            "categoria": "IA",
            "aliases": ["neurones artificials", "neural network"],
            "resposta": "Una xarxa neuronal és un model d'IA inspirat en connexions entre neurones. Té capes, pesos i entrenament per aprendre patrons a partir de dades."
        },
        {
            "tema": "entrenament d'una IA",
            "categoria": "IA",
            "aliases": ["entrenar IA", "training IA"],
            "resposta": "Entrenar una IA vol dir donar-li dades i ajustar els seus pesos perquè millori les respostes o prediccions. Com més bones siguin les dades, millor pot aprendre."
        },
        {
            "tema": "model d'IA",
            "categoria": "IA",
            "aliases": ["model IA"],
            "resposta": "Un model d'IA és el cervell matemàtic que ha après patrons. Pot servir per classificar, predir, respondre preguntes, generar text o reconèixer imatges."
        },
        {
            "tema": "prompt",
            "categoria": "IA",
            "aliases": ["prompts"],
            "resposta": "Un prompt és el text que escrius a una IA per demanar-li alguna cosa. Un bon prompt és clar, concret i explica bé què vols obtenir."
        },
        {
            "tema": "chatbot",
            "categoria": "IA",
            "aliases": ["bot de xat", "xatbot"],
            "resposta": "Un chatbot és un programa que parla amb persones mitjançant text o veu. Pot respondre preguntes, ajudar amb tasques, guardar memòria o fer d'assistent."
        },
        {
            "tema": "visió artificial",
            "categoria": "IA",
            "aliases": ["computer vision", "visio artificial"],
            "resposta": "La visió artificial és una branca de la IA que permet als ordinadors entendre imatges i vídeos. Serveix per detectar objectes, cares, textos, moviments o defectes."
        },
        {
            "tema": "processament del llenguatge natural",
            "categoria": "IA",
            "aliases": ["NLP", "llenguatge natural"],
            "resposta": "El processament del llenguatge natural és una branca de la IA que treballa amb text i parla humana. Serveix per traduir, resumir, respondre preguntes i entendre frases."
        },
        {
            "tema": "Minecraft",
            "categoria": "videojocs",
            "aliases": ["maincra", "minecraft survival"],
            "resposta": "Minecraft és un videojoc de món obert on pots explorar, construir, sobreviure, crear mecanismes amb redstone i jugar sol o amb amics. També ajuda molt a la creativitat i la lògica."
        },
        {
            "tema": "mode supervivència de Minecraft",
            "categoria": "Minecraft",
            "aliases": ["survival minecraft", "supervivencia minecraft"],
            "resposta": "El mode supervivència de Minecraft és on has d'aconseguir recursos, menjar, eines i protegir-te dels mobs. L'objectiu pot ser construir, explorar i derrotar l'Ender Dragon."
        },
        {
            "tema": "mode creatiu de Minecraft",
            "categoria": "Minecraft",
            "aliases": ["creative minecraft", "creatiu minecraft"],
            "resposta": "El mode creatiu de Minecraft et dona blocs il·limitats i permet volar. Serveix per construir lliurement sense preocupar-te per vida, menjar o enemics."
        },
        {
            "tema": "redstone",
            "categoria": "Minecraft",
            "aliases": ["red stone", "mecanismes de redstone"],
            "resposta": "La redstone és com l'electricitat de Minecraft. Serveix per fer portes automàtiques, granges, trampes, ascensors, màquines, calculadores i circuits lògics."
        },
        {
            "tema": "Creeper",
            "categoria": "Minecraft",
            "aliases": ["creepers"],
            "resposta": "El Creeper és un mob de Minecraft que s'acosta al jugador i explota. És un dels enemics més famosos del joc i pot destruir construccions si no tens compte."
        },
        {
            "tema": "Ender Dragon",
            "categoria": "Minecraft",
            "aliases": ["drac de l'end", "enderdragon"],
            "resposta": "L'Ender Dragon és el boss final principal de Minecraft. Es troba a la dimensió de l'End i per derrotar-lo cal destruir cristalls i atacar-lo."
        },
        {
            "tema": "Nether",
            "categoria": "Minecraft",
            "aliases": ["el nether"],
            "resposta": "El Nether és una dimensió perillosa de Minecraft plena de lava, fortaleses, piglins, ghasts i recursos especials. És important per avançar cap al final del joc."
        },
        {
            "tema": "bioma",
            "categoria": "Minecraft",
            "aliases": ["biomes"],
            "resposta": "Un bioma és una zona amb característiques pròpies, com desert, jungla, oceà, muntanya, bosc o neu. A Minecraft cada bioma té blocs, mobs i recursos diferents."
        },
        {
            "tema": "servidor de Minecraft",
            "categoria": "Minecraft",
            "aliases": ["server minecraft", "minecraft server"],
            "resposta": "Un servidor de Minecraft permet que diversos jugadors entrin al mateix món. Pot tenir plugins, mods, minijocs, survival, creatiu o normes pròpies."
        },
        {
            "tema": "mods de Minecraft",
            "categoria": "Minecraft",
            "aliases": ["mod minecraft", "mods"],
            "resposta": "Els mods de Minecraft són modificacions que afegeixen coses al joc, com blocs, mobs, dimensions, armes, màquines, tecnologia o aventures noves."
        },
        {
            "tema": "shaders de Minecraft",
            "categoria": "Minecraft",
            "aliases": ["shaders"],
            "resposta": "Els shaders de Minecraft milloren els gràfics del joc amb llums, ombres, aigua realista i efectes visuals. Fan que el joc es vegi molt més espectacular."
        },
        {
            "tema": "LEGO",
            "categoria": "LEGO",
            "aliases": ["peces LEGO"],
            "resposta": "LEGO és un sistema de peces de construcció que permet crear edificis, vehicles, robots, escenes i invents. Ajuda a la creativitat, la paciència i la imaginació."
        },
        {
            "tema": "LEGO Technic",
            "categoria": "LEGO",
            "aliases": ["technic", "lego tecnic"],
            "resposta": "LEGO Technic és una línia de LEGO amb engranatges, eixos, motors, suspensions i mecanismes. Serveix per construir vehicles i màquines més realistes."
        },
        {
            "tema": "LEGO City",
            "categoria": "LEGO",
            "aliases": ["lego ciutat"],
            "resposta": "LEGO City és una línia de LEGO basada en ciutats, policies, bombers, vehicles, trens, edificis i escenes del dia a dia."
        },
        {
            "tema": "LEGO Mindstorms",
            "categoria": "LEGO",
            "aliases": ["mindstorms"],
            "resposta": "LEGO Mindstorms és una línia de LEGO per crear robots programables amb motors, sensors i un controlador. Combina construcció i programació."
        },
        {
            "tema": "LEGO Super Mario",
            "categoria": "LEGO",
            "aliases": ["lego mario"],
            "resposta": "LEGO Super Mario és una línia de LEGO inspirada en Mario. Permet construir nivells interactius amb personatges, plataformes, enemics i monedes."
        },
        {
            "tema": "engranatge",
            "categoria": "mecànica",
            "aliases": ["engranatges"],
            "resposta": "Un engranatge és una roda amb dents que transmet moviment a una altra peça. Serveix per canviar velocitat, força o direcció en mecanismes."
        },
        {
            "tema": "eix",
            "categoria": "mecànica",
            "aliases": ["eixos"],
            "resposta": "Un eix és una peça que transmet moviment o suporta rodes i engranatges. En LEGO Technic i en màquines reals és molt important per fer mecanismes."
        },
        {
            "tema": "Nintendo Switch",
            "categoria": "videojocs",
            "aliases": ["switch"],
            "resposta": "La Nintendo Switch és una consola híbrida que es pot usar connectada a la tele o en mode portàtil. Té jocs com Mario Kart, Zelda, Pokémon i molts més."
        },
        {
            "tema": "PlayStation 4",
            "categoria": "videojocs",
            "aliases": ["PS4"],
            "resposta": "La PlayStation 4 és una consola de Sony amb molts jocs d'acció, aventura, esport i món obert. També permet jugar online i veure contingut multimèdia."
        },
        {
            "tema": "Wii",
            "categoria": "videojocs",
            "aliases": ["Nintendo Wii"],
            "resposta": "La Wii és una consola de Nintendo famosa pels controls de moviment. Té jocs com Wii Sports, Mario Kart Wii i molts jocs familiars."
        },
        {
            "tema": "game design",
            "categoria": "videojocs",
            "aliases": ["disseny de videojocs"],
            "resposta": "El game design és el disseny de videojocs: regles, nivells, mecàniques, dificultat, recompenses, història i experiència del jugador."
        },
        {
            "tema": "sandbox",
            "categoria": "videojocs",
            "aliases": ["joc sandbox"],
            "resposta": "Un joc sandbox dona molta llibertat al jugador per explorar, construir o crear objectius propis. Minecraft és un exemple molt famós de joc sandbox."
        },
        {
            "tema": "RPG",
            "categoria": "videojocs",
            "aliases": ["joc RPG", "rol"],
            "resposta": "Un RPG és un joc de rol on normalment millores personatges, aconsegueixes equip, fas missions i prens decisions dins una història o món."
        },
        {
            "tema": "FPS",
            "categoria": "videojocs",
            "aliases": ["shooter", "joc de trets"],
            "resposta": "Un FPS és un joc en primera persona, normalment de trets. La càmera mostra el que veuria el personatge, com si fossis dins del joc."
        },
        {
            "tema": "pixel art",
            "categoria": "art digital",
            "aliases": ["art pixelat"],
            "resposta": "El pixel art és un estil d'art digital fet amb píxels visibles. S'utilitza molt en videojocs retro, icones, sprites i animacions senzilles."
        },
        {
            "tema": "kendama",
            "categoria": "hobbies",
            "aliases": ["joc kendama"],
            "resposta": "El kendama és una joguina japonesa d'habilitat amb una bola, una corda i una peça de fusta amb copes. Serveix per fer trucs i millorar coordinació, paciència i pràctica."
        },
        {
            "tema": "cartomàgia",
            "categoria": "màgia",
            "aliases": ["cartomagia", "màgia amb cartes", "trucs de cartes"],
            "resposta": "La cartomàgia és la màgia feta amb cartes. Inclou tècniques de mans, barreges falses, controls, forces, distracció i presentació per sorprendre el públic."
        },
        {
            "tema": "misdirection",
            "categoria": "màgia",
            "aliases": ["distracció en màgia", "desviament d'atenció"],
            "resposta": "La misdirection és una tècnica de màgia per dirigir l'atenció del públic cap a un lloc mentre el truc real passa en un altre."
        },
        {
            "tema": "baralla de cartes",
            "categoria": "màgia",
            "aliases": ["cartes", "deck de cartes"],
            "resposta": "Una baralla de cartes és un conjunt de cartes utilitzat per jugar o fer màgia. En cartomàgia és important saber controlar cartes, barrejar i presentar bé el truc."
        },
        {
            "tema": "electricitat",
            "categoria": "ciència",
            "aliases": ["energia elèctrica"],
            "resposta": "L'electricitat és una forma d'energia relacionada amb el moviment de càrregues elèctriques. Serveix per alimentar aparells, circuits, ordinadors, motors i llums."
        },
        {
            "tema": "circuit elèctric",
            "categoria": "electrònica",
            "aliases": ["circuit"],
            "resposta": "Un circuit elèctric és un camí per on passa el corrent. Normalment té una font d'energia, cables i components com LEDs, resistències, motors o sensors."
        },
        {
            "tema": "voltatge",
            "categoria": "electrònica",
            "aliases": ["tensió elèctrica", "volts"],
            "resposta": "El voltatge és la força que empeny el corrent elèctric dins un circuit. Es mesura en volts i és important per alimentar components correctament."
        },
        {
            "tema": "corrent elèctric",
            "categoria": "electrònica",
            "aliases": ["corrent", "amperes"],
            "resposta": "El corrent elèctric és el moviment de càrrega elèctrica per un circuit. Es mesura en amperes i indica quanta electricitat està circulant."
        },
        {
            "tema": "resistència",
            "categoria": "electrònica",
            "aliases": ["resistencia", "ohms"],
            "resposta": "La resistència limita el pas del corrent elèctric. Es mesura en ohms i serveix per protegir components com LEDs o controlar senyals."
        },
        {
            "tema": "bateria",
            "categoria": "electrònica",
            "aliases": ["pila", "bateries"],
            "resposta": "Una bateria guarda energia química i la converteix en energia elèctrica. Serveix per alimentar mòbils, ordinadors, robots, comandaments i molts dispositius."
        },
        {
            "tema": "contrasenya segura",
            "categoria": "ciberseguretat",
            "aliases": ["password segura", "clau segura"],
            "resposta": "Una contrasenya segura ha de ser llarga, difícil d'endevinar i única per cada compte. És millor combinar paraules, números i símbols, o usar un gestor de contrasenyes."
        },
        {
            "tema": "verificació en dos passos",
            "categoria": "ciberseguretat",
            "aliases": ["2FA", "doble factor", "autenticació de dos factors"],
            "resposta": "La verificació en dos passos afegeix una capa extra de seguretat. Encara que algú sàpiga la contrasenya, també necessita un codi, app o dispositiu per entrar."
        },
        {
            "tema": "phishing",
            "categoria": "ciberseguretat",
            "aliases": ["estafa phishing", "correu fals"],
            "resposta": "El phishing és una estafa on algú intenta enganyar-te perquè donis contrasenyes, dades personals o diners. Sovint arriba per correu, missatge o webs falses."
        },
        {
            "tema": "còpia de seguretat",
            "categoria": "seguretat",
            "aliases": ["backup", "copia de seguretat"],
            "resposta": "Una còpia de seguretat és una còpia dels teus fitxers importants. Serveix per recuperar dades si s'esborren, es trenquen o passa algun problema."
        },
        {
            "tema": "MARTINAKUS WORLD",
            "categoria": "personal",
            "aliases": ["web del Martí", "martinakus", "martinakus world web"],
            "resposta": "MARTINAKUS WORLD és la web del Martí sobre tecnologia i videojocs. L'enllaç és: https://martinakus.wordpress.com/"
        },
        {
            "tema": "El Racó d'Art",
            "categoria": "personal",
            "aliases": ["web de la Clàudia", "raco art", "el raco dart"],
            "resposta": "El Racó d'Art és la web de la Clàudia. És una web de manualitats i l'enllaç és: https://elracodart.wordpress.com/"
        },
        {
            "tema": "Clàudia",
            "categoria": "personal",
            "aliases": ["la Claudia", "germana del Martí"],
            "resposta": "La Clàudia té 10 anys, el seu color preferit és el rosa i li agraden les manualitats. També té la web El Racó d'Art: https://elracodart.wordpress.com/"
        },
        {
            "tema": "Martí",
            "categoria": "personal",
            "aliases": ["el Marti", "creador de MARTINAKUS IA"],
            "resposta": "El Martí és el creador de MARTINAKUS IA. Li agraden la tecnologia, Minecraft, LEGO, programar, la màgia amb cartes, el kendama i crear projectes com MARTINAKUS WORLD."
        },
        {
            "tema": "Sucra i Mel",
            "categoria": "personal",
            "aliases": ["gosses del Martí", "gossos del Martí"],
            "resposta": "Sucra i Mel són les dues gosses del Martí."
        },
        {
            "tema": "Japó",
            "categoria": "viatges",
            "aliases": ["Japo", "viatge a Japó"],
            "resposta": "Japó és un país asiàtic famós per la tecnologia, temples, anime, manga, menjar, trens ràpids, ciutats com Tòquio, Kyoto i Osaka, i una cultura molt especial."
        },
        {
            "tema": "Tòquio",
            "categoria": "viatges",
            "aliases": ["Tokyo"],
            "resposta": "Tòquio és la capital del Japó i una ciutat gegant plena de tecnologia, botigues, temples, menjar, videojocs, anime i barris famosos com Akihabara i Shibuya."
        },
        {
            "tema": "Kyoto",
            "categoria": "viatges",
            "aliases": ["Kioto"],
            "resposta": "Kyoto és una ciutat japonesa famosa pels temples, jardins, santuaris, carrers tradicionals i cultura històrica."
        },
        {
            "tema": "Osaka",
            "categoria": "viatges",
            "aliases": ["Osaka Japó"],
            "resposta": "Osaka és una ciutat japonesa coneguda pel menjar, l'ambient divertit, botigues, llums i llocs com Dotonbori."
        },
        {
            "tema": "anime",
            "categoria": "cultura japonesa",
            "aliases": ["animació japonesa"],
            "resposta": "L'anime és animació japonesa. Pot tenir molts gèneres: acció, aventures, comèdia, fantasia, ciència-ficció, esport o històries emocionals."
        },
        {
            "tema": "manga",
            "categoria": "cultura japonesa",
            "aliases": ["còmic japonès"],
            "resposta": "El manga és el còmic japonès. Normalment es llegeix de dreta a esquerra i pot tractar molts gèneres diferents."
        },
        {
            "tema": "samurai",
            "categoria": "història",
            "aliases": ["samurais"],
            "resposta": "Els samurais eren guerrers del Japó feudal. Eren coneguts pel seu entrenament, disciplina, armadura, espases i codi d'honor."
        },
        {
            "tema": "ninja",
            "categoria": "història",
            "aliases": ["ninjas"],
            "resposta": "Els ninjas eren agents especialitzats en espionatge, infiltració i tàctiques secretes al Japó antic. Sovint apareixen en històries i videojocs."
        },
        {
            "tema": "Shinkansen",
            "categoria": "tecnologia",
            "aliases": ["tren bala", "tren japonès ràpid"],
            "resposta": "El Shinkansen és el tren d'alta velocitat del Japó. És famós per ser ràpid, puntual i molt eficient."
        },
        {
            "tema": "macarrons",
            "categoria": "menjar",
            "aliases": ["pasta", "macarrons de la iaia"],
            "resposta": "Els macarrons són un tipus de pasta molt popular. Es poden fer amb tomàquet, formatge, carn, verdures o moltes altres salses."
        },
        {
            "tema": "cinema d'acció",
            "categoria": "cinema",
            "aliases": ["pel·lícules d'acció", "pelis d'acció"],
            "resposta": "El cinema d'acció és un gènere amb persecucions, lluites, explosions, aventures, herois i escenes espectaculars."
        },
        {
            "tema": "Star Wars",
            "categoria": "cinema",
            "aliases": ["la guerra de les galàxies"],
            "resposta": "Star Wars és una saga de ciència-ficció amb jedis, siths, naus espacials, planetes, la Força i aventures entre el bé i el mal."
        },
        {
            "tema": "Marvel",
            "categoria": "cinema",
            "aliases": ["Marvel Studios", "superherois Marvel"],
            "resposta": "Marvel és coneguda pels seus superherois com Spider-Man, Iron Man, Thor, Hulk i molts altres. Té còmics, pel·lícules i sèries."
        },
        {
            "tema": "Nike",
            "categoria": "marques",
            "aliases": ["marca Nike"],
            "resposta": "Nike és una marca de roba i sabates esportives. És famosa per bambes, xandalls, samarretes i material esportiu."
        },
        {
            "tema": "Adidas Campus",
            "categoria": "marques",
            "aliases": ["Campus 00s", "adidas campus 00s"],
            "resposta": "Les Adidas Campus són unes sabates d'Adidas amb estil retro i urbà. Les Campus 00s són una versió popular amb forma més ampla."
        },
        {
            "tema": "iPhone 14 Pro",
            "categoria": "tecnologia",
            "aliases": ["iphone", "iphone 14"],
            "resposta": "L'iPhone 14 Pro és un telèfon d'Apple amb bones càmeres, pantalla d'alta qualitat, molta potència i funcions avançades."
        },
        {
            "tema": "JBL GO 4",
            "categoria": "tecnologia",
            "aliases": ["JBL", "altaveu JBL"],
            "resposta": "El JBL GO 4 és un altaveu Bluetooth petit i portàtil. Serveix per escoltar música des del mòbil, tablet o ordinador."
        },
        {
            "tema": "R36S",
            "categoria": "videojocs",
            "aliases": ["consola retro R36S", "consola emuladora"],
            "resposta": "La R36S és una consola retro portàtil que pot executar emuladors de consoles antigues. Serveix per jugar a jocs clàssics en format portàtil."
        },
        {
            "tema": "Samsung Galaxy Tab A7",
            "categoria": "tecnologia",
            "aliases": ["tablet Samsung", "Galaxy Tab A7"],
            "resposta": "La Samsung Galaxy Tab A7 és una tablet Android útil per veure vídeos, navegar, estudiar, jugar, llegir i fer tasques bàsiques."
        }
    ]

    total_afegides = 0
    total_actualitzades = 0

    for entrada in entrades:
        afegides, actualitzades = afegir_entrada(
            coneixement=coneixement,
            tema=entrada["tema"],
            resposta=entrada["resposta"],
            categoria=entrada["categoria"],
            aliases=entrada.get("aliases", []),
            preguntes_extra=entrada.get("preguntes_extra", [])
        )

        total_afegides += afegides
        total_actualitzades += actualitzades

    guardar_json(FITXER_CONEIXEMENT, coneixement)

    print("====================================")
    print("PACK MASSIU AFEGIT CORRECTAMENT ✅")
    print("====================================")
    print(f"Entrades noves: {total_afegides}")
    print(f"Entrades actualitzades: {total_actualitzades}")
    print(f"Total de preguntes a coneixement.json: {len(coneixement)}")
    print("====================================")
    print("Ara pots obrir ia_web_v8.py i provar preguntes noves.")


if __name__ == "__main__":
    main()
