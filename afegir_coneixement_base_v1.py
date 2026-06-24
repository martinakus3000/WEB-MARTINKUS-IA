import json
import shutil
from pathlib import Path
from datetime import datetime

CARPETA_IA = Path(r"C:\Users\marti\Desktop\ia")
FITXER_CONEIXEMENT = CARPETA_IA / "coneixement.json"

CARPETA_BACKUPS = CARPETA_IA / "backups"
CARPETA_BACKUPS.mkdir(parents=True, exist_ok=True)


def ara():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalitzar(text):
    text = text.lower().strip()

    canvis = {
        "à": "a",
        "á": "a",
        "è": "e",
        "é": "e",
        "í": "i",
        "ò": "o",
        "ó": "o",
        "ú": "u",
        "ç": "c",
        "·": ""
    }

    for antic, nou in canvis.items():
        text = text.replace(antic, nou)

    caracters = ".,;:!?¿¡()[]{}\"'`´’“”"
    for caracter in caracters:
        text = text.replace(caracter, "")

    text = " ".join(text.split())
    return text


def carregar_coneixement():
    if FITXER_CONEIXEMENT.exists():
        with open(FITXER_CONEIXEMENT, "r", encoding="utf-8") as fitxer:
            return json.load(fitxer)

    return {}


def guardar_coneixement(coneixement):
    with open(FITXER_CONEIXEMENT, "w", encoding="utf-8") as fitxer:
        json.dump(coneixement, fitxer, ensure_ascii=False, indent=4)


def fer_backup():
    if FITXER_CONEIXEMENT.exists():
        nom = f"coneixement_backup_abans_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(FITXER_CONEIXEMENT, CARPETA_BACKUPS / nom)
        print("Backup creat abans de tocar la memòria ✅")


def afegir(coneixement, preguntes, resposta, categoria):
    for pregunta in preguntes:
        clau = normalitzar(pregunta)

        coneixement[clau] = {
            "resposta": resposta,
            "vegades_utilitzat": 0,
            "creat": ara(),
            "categoria": categoria,
            "font": "Pack base MARTINAKUS IA"
        }


def eliminar_errors(coneixement):
    claus_a_borrar = []

    for clau, dades in coneixement.items():
        resposta = ""

        if isinstance(dades, dict):
            resposta = dades.get("resposta", "")
        else:
            resposta = str(dades)

        text = normalitzar(clau + " " + resposta)

        if "legon cities fc" in text:
            claus_a_borrar.append(clau)

    for clau in claus_a_borrar:
        del coneixement[clau]

    if claus_a_borrar:
        print(f"He eliminat {len(claus_a_borrar)} entrada/es equivocada/es ✅")


def main():
    fer_backup()

    coneixement = carregar_coneixement()
    eliminar_errors(coneixement)

    afegir(
        coneixement,
        [
            "que es una raspberry pi 5",
            "raspberry pi 5",
            "per que serveix una raspberry pi 5",
            "parlem de raspberry pi 5",
            "explica raspberry pi 5",
            "que puc fer amb una raspberry pi 5"
        ],
        "La Raspberry Pi 5 és un mini ordinador molt petit però bastant potent. Serveix per aprendre programació, fer projectes d'electrònica, muntar servidors casolans, fer robots, domòtica, retro gaming, proves amb Linux i projectes de tecnologia.",
        "tecnologia"
    )

    afegir(
        coneixement,
        [
            "que es python",
            "python",
            "per que serveix python",
            "parlem de python",
            "explica python"
        ],
        "Python és un llenguatge de programació fàcil de llegir i molt utilitzat. Serveix per fer webs, automatitzar tasques, crear IA, fer scripts, treballar amb dades, controlar robots i aprendre programació.",
        "programacio"
    )

    afegir(
        coneixement,
        [
            "que es html",
            "html",
            "per que serveix html",
            "explica html",
            "parlem de html"
        ],
        "HTML és el llenguatge que estructura les pàgines web. Serveix per posar textos, botons, imatges, enllaços, formularis i l'esquelet d'una web.",
        "web"
    )

    afegir(
        coneixement,
        [
            "que es css",
            "css",
            "per que serveix css",
            "explica css"
        ],
        "CSS serveix per donar estil a una web. Amb CSS pots canviar colors, mides, fonts, marges, animacions i fer que una pàgina sigui més guapa.",
        "web"
    )

    afegir(
        coneixement,
        [
            "que es javascript",
            "javascript",
            "per que serveix javascript",
            "explica javascript"
        ],
        "JavaScript és un llenguatge de programació que dona vida a les webs. Serveix per fer botons interactius, xats, jocs web, menús, animacions i connexions amb servidors.",
        "web"
    )

    afegir(
        coneixement,
        [
            "que es flask",
            "flask",
            "per que serveix flask",
            "explica flask"
        ],
        "Flask és una eina de Python per crear webs i APIs. Serveix per connectar una pàgina HTML amb un programa Python, com estàs fent amb MARTINAKUS IA WEB.",
        "web"
    )

    afegir(
        coneixement,
        [
            "que es minecraft",
            "minecraft",
            "per que mola minecraft",
            "explica minecraft",
            "parlem de minecraft"
        ],
        "Minecraft és un videojoc de món obert on pots construir, explorar, sobreviure, crear mecanismes amb redstone i jugar amb amics. És molt bo per la creativitat i també per aprendre lògica.",
        "videojocs"
    )

    afegir(
        coneixement,
        [
            "que es redstone",
            "redstone",
            "per que serveix la redstone",
            "explica redstone"
        ],
        "La redstone és un sistema de Minecraft que funciona com una mena d'electricitat. Serveix per fer portes automàtiques, trampes, màquines, ascensors, calculadores i mecanismes molt bèsties.",
        "minecraft"
    )

    afegir(
        coneixement,
        [
            "que es lego",
            "lego",
            "per que mola lego",
            "explica lego",
            "parlem de lego"
        ],
        "LEGO és un sistema de peces de construcció que permet crear edificis, vehicles, robots, escenes i invents. Ajuda molt a la creativitat, la paciència i la imaginació.",
        "lego"
    )

    afegir(
        coneixement,
        [
            "que es lego technic",
            "lego technic",
            "per que serveix lego technic",
            "explica lego technic"
        ],
        "LEGO Technic és una línia de LEGO amb engranatges, eixos, motors, suspensions i mecanismes. Serveix per construir vehicles i màquines més realistes i tècniques.",
        "lego"
    )

    afegir(
        coneixement,
        [
            "que es lego mindstorms",
            "lego mindstorms",
            "explica lego mindstorms",
            "per que serveix lego mindstorms"
        ],
        "LEGO Mindstorms és una línia de LEGO per crear robots programables. Combina peces LEGO, motors, sensors i programació.",
        "lego"
    )

    afegir(
        coneixement,
        [
            "que es una impressora 3d",
            "impressora 3d",
            "per que serveix una impressora 3d",
            "explica impressio 3d",
            "impressio 3d"
        ],
        "Una impressora 3D serveix per crear objectes físics capa per capa amb materials com PLA. Es pot fer servir per imprimir peces, suports, figures, prototips, carcasses i invents.",
        "tecnologia"
    )

    afegir(
        coneixement,
        [
            "que es pla",
            "filament pla",
            "per que serveix el pla",
            "que es el filament pla"
        ],
        "El PLA és un material molt utilitzat en impressió 3D. És fàcil d'imprimir, va bé per peces decoratives, prototips i objectes senzills.",
        "impressio 3d"
    )

    afegir(
        coneixement,
        [
            "que es arduino",
            "arduino",
            "per que serveix arduino",
            "explica arduino"
        ],
        "Arduino és una placa electrònica programable. Serveix per controlar LEDs, motors, sensors, pantalles, robots i projectes d'electrònica.",
        "electronica"
    )

    afegir(
        coneixement,
        [
            "que es robotica",
            "robotica",
            "per que serveix la robotica",
            "explica robotica"
        ],
        "La robòtica combina programació, electrònica i mecànica per crear màquines que poden moure's, detectar coses i fer tasques automàticament.",
        "tecnologia"
    )

    afegir(
        coneixement,
        [
            "que es inteligencia artificial",
            "intelligencia artificial",
            "ia",
            "que es una ia",
            "per que serveix la ia",
            "explica inteligencia artificial"
        ],
        "La intel·ligència artificial és una tecnologia que permet a un programa aprendre patrons, respondre preguntes, classificar informació, generar textos, reconèixer imatges o ajudar en tasques.",
        "ia"
    )

    afegir(
        coneixement,
        [
            "que es chatgpt",
            "chatgpt",
            "per que serveix chatgpt",
            "explica chatgpt"
        ],
        "ChatGPT és una IA conversacional que pot respondre preguntes, ajudar a programar, explicar coses, escriure textos i donar idees.",
        "ia"
    )

    afegir(
        coneixement,
        [
            "que es martinakus world",
            "martinakus world",
            "quina es la web del marti",
            "quina es la millor web del mon"
        ],
        "MARTINAKUS WORLD és la web del Martí. És una web de tecnologia i videojocs. L'enllaç és: https://martinakus.wordpress.com/",
        "personal"
    )

    afegir(
        coneixement,
        [
            "que es el raco dart",
            "el raco dart",
            "quina es la web de la claudia",
            "web de la claudia"
        ],
        "El Racó d'Art és la web de la Clàudia. És una web de manualitats. L'enllaç és: https://elracodart.wordpress.com/",
        "personal"
    )

    afegir(
        coneixement,
        [
            "que li agrada a la claudia",
            "que saps de la claudia",
            "qui es la claudia",
            "parlem de la claudia"
        ],
        "La Clàudia té 10 anys, el seu color preferit és el rosa i li agraden les manualitats. Té la web El Racó d'Art: https://elracodart.wordpress.com/",
        "personal"
    )

    afegir(
        coneixement,
        [
            "que li agrada al marti",
            "que saps del marti",
            "qui es el marti",
            "parlem del marti"
        ],
        "El Martí és el creador de MARTINAKUS IA. Li agraden la tecnologia, Minecraft, LEGO, programar, la màgia amb cartes, el kendama i la seva web MARTINAKUS WORLD.",
        "personal"
    )

    afegir(
        coneixement,
        [
            "que es kendama",
            "kendama",
            "per que serveix un kendama",
            "explica kendama"
        ],
        "El kendama és una joguina japonesa d'habilitat amb una bola, una corda i una peça de fusta amb copes. Serveix per fer trucs, millorar coordinació i practicar paciència.",
        "hobbies"
    )

    afegir(
        coneixement,
        [
            "que es cartomagia",
            "cartomagia",
            "magia amb cartes",
            "trucs de cartes",
            "que es la magia amb cartes"
        ],
        "La cartomàgia és la màgia feta amb cartes. Inclou trucs, tècniques de mans, forces, controls, barreges falses i presentació per sorprendre la gent.",
        "hobbies"
    )

    afegir(
        coneixement,
        [
            "que es una api",
            "api",
            "per que serveix una api",
            "explica api"
        ],
        "Una API és una manera perquè dos programes es comuniquin. Per exemple, la web de la teva IA envia missatges a Python amb una API i Python retorna la resposta.",
        "programacio"
    )

    guardar_coneixement(coneixement)

    print("Pack de coneixement afegit correctament ✅")
    print(f"Total de preguntes guardades ara: {len(coneixement)}")
    print("Ara obre la IA web i prova preguntes noves.")


if __name__ == "__main__":
    main()
