import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote
import base64
import os

WHATSAPP_PHONE = "5491122803223"
WHATSAPP_APIKEY = "5295938"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")

ZONAS = {
    "Chamonix": [
        {"nombre": "CoolSkiJobs", "url": "https://www.coolskijobs.com/ski-resorts/chamonix/"},
        {"nombre": "SeasonWorkers", "url": "https://www.seasonworkers.com/skijobs/resorts/france/chamonix-39.aspx"},
    ],
    "Val dIsere": [
        {"nombre": "Consensio", "url": "https://www.consensiochalets.co.uk/ski-season-jobs/"},
        {"nombre": "Le Ski", "url": "https://www.leski.com/ski-jobs/apply"},
    ],
    "Courchevel Meribel": [
        {"nombre": "Purple Ski", "url": "https://www.purpleski.com/jobs/"},
        {"nombre": "SeasonWorkers", "url": "https://www.seasonworkers.com/skijobs/resorts/ski-jobs-france.aspx"},
    ],
    "Morzine Les Gets": [
        {"nombre": "Hunter Chalets", "url": "https://hunterchalets.com/ski-season-jobs/"},
        {"nombre": "SnowSeason", "url": "https://www.snowseasoncentral.com/france"},
    ],
    "Otras zonas": [
        {"nombre": "SkiWorld", "url": "https://www.skiworld.co.uk/recruitment/ski-season-jobs"},
        {"nombre": "Natives", "url": "https://natives.co.uk"},
    ]
}

EMPRESAS_GRUPOS = [
    {"nombre": "Consensio Chalets", "descripcion": "Contrata equipos completos para Val dIsere, Meribel y Courchevel. Buscan grupos de 2-4 personas para cubrir chalet completo.", "link": "https://www.consensiochalets.co.uk/ski-season-jobs/", "zona": "Val dIsere / Courchevel", "roles": "Chalet Host, Chef, Driver, Housekeeper"},
    {"nombre": "Le Ski", "descripcion": "Opera chalets en Val dIsere, Courchevel y La Tania. Contrata parejas y grupos para gestionar chalets completos.", "link": "https://www.leski.com/ski-jobs/apply", "zona": "Val dIsere / La Tania", "roles": "Chalet Couple, Host, Chef"},
    {"nombre": "SkiWorld", "descripcion": "Gran operador con equipos en Alpe dHuez, Courchevel, La Plagne, Les Arcs, Meribel, Tignes, Val dIsere y Val Thorens.", "link": "https://www.skiworld.co.uk/recruitment/ski-season-jobs", "zona": "Multiples resorts", "roles": "Chalet Host, Resort Rep, Driver, Ski Tech"},
    {"nombre": "Hunter Chalets", "descripcion": "Contrata equipos para Morzine y Les Gets. Ideal para grupos de amigos que quieran trabajar juntos.", "link": "https://hunterchalets.com/ski-season-jobs/", "zona": "Morzine / Les Gets", "roles": "Chalet Host, Chef, Housekeeper"},
    {"nombre": "Purple Ski", "descripcion": "Chalets de lujo en Meribel, Courchevel y Val dIsere. Contrata personal multiple por chalet.", "link": "https://www.purpleski.com/jobs/", "zona": "Meribel / Courchevel", "roles": "Chef, Host, Driver, Nanny"},
]

KEYWORDS = ["chef", "host", "bar", "kitchen", "reception", "housekeeper", "driver",
            "maintenance", "assistant", "manager", "staff", "waiter", "cook",
            "ski rental", "ski hire", "location ski", "ski shop", "ski tech",
            "boot fitter", "equipment", "materiel", "magasin",
            "saisonnier", "emploi", "cuisinier", "serveur", "animateur"]

KEYWORDS_GRUPO = ["team", "couple", "group", "several", "multiple", "positions", "plusieurs", "postes"]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def obtener_detalles(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        detalles = {}
        texto = soup.get_text(separator=" ", strip=True).lower()
        if "accommodation" in texto or "logement" in texto or "loge" in texto:
            detalles["alojamiento_confirmado"] = True
        if "meals" in texto or "nourri" in texto or "food provided" in texto:
            detalles["comida_confirmada"] = True
        for palabra in ["1800", "1900", "2000", "1700", "1600", "1500", "smic", "smig"]:
            if palabra in texto:
                detalles["salario_detalle"] = "Ver oferta (aprox. EUR " + palabra + "/mes)" if palabra.isdigit() else "SMIC frances (~EUR 1600/mes)"
                break
        paras = soup.find_all(["p", "li", "div"], limit=30)
        for p in paras:
            t = p.get_text(strip=True)
            if 20 < len(t) < 200 and any(k in t.lower() for k in ["accommodation", "meals", "salary", "season", "december", "logement", "nourri"]):
                detalles["descripcion"] = t[:180]
                break
        return detalles
    except Exception:
        return {}


def buscar_zona(zona, sitios):
    ofertas = []
    for sitio in sitios:
        try:
            r = requests.get(sitio["url"], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.find_all("a", href=True):
                texto = link.get_text(strip=True)
                tl = texto.lower()
                if any(k in tl for k in KEYWORDS) and len(texto) > 5:
                    href = link["href"]
                    if not href.startswith("http"):
                        base = "/".join(sitio["url"].split("/")[:3])
                        href = base + href
                    detalles = obtener_detalles(href)
                    ofertas.append({
                        "puesto": texto[:70],
                        "zona": zona,
                        "salario": detalles.get("salario_detalle", "Ver oferta"),
                        "descripcion": detalles.get("descripcion", ""),
                        "inicio": "Dic 2026",
                        "fin": "Mar 2027",
                        "ski_pass": "ski pass" in tl,
                        "aloj_confirmado": detalles.get("alojamiento_confirmado", False),
                        "comida_confirmada": detalles.get("comida_confirmada", False),
                        "para_grupo": any(k in tl for k in KEYWORDS_GRUPO),
                        "fuente": sitio["nombre"],
                        "link": href
                    })
        except Exception as e:
            print("Error en " + sitio["nombre"] + ": " + str(e))
    return ofertas[:8]


def tarjeta(o, destacada=False):
    border = 'border: 2px solid #e8a020;' if destacada else ''
    ski = '<span class="tag tblue">Ski pass</span>' if o.get("ski_pass") else ""
    grp = '<span class="tag torange">3+ personas</span>' if o.get("para_grupo") else ""
    aloj_color = "tgreen" if o.get("aloj_confirmado") else "tgray"
    com_color = "tgreen" if o.get("comida_confirmada") else "tgray"
    desc = ('<div class="descripcion">' + o["descripcion"] + '</div>') if o.get("descripcion") else ""
    return (
        '<div class="card" style="' + border + '">'
        '<div class="card-top">'
        '<div><h3>' + o["puesto"] + '</h3><div class="centro">' + o["zona"] + '</div></div>'
        '<span class="badge">' + o["fuente"] + '</span>'
        '</div>'
        + desc +
        '<div class="tags">'
        '<span class="tag ' + aloj_color + '">Alojamiento</span>'
        '<span class="tag ' + com_color + '">Comida</span>' + ski + grp +
        '</div>'
        '<div class="detalles">' + o["salario"] + ' | ' + o["inicio"] + ' - ' + o["fin"] + '</div>'
        '<div class="card-bottom">'
        '<span class="fecha">Temporada ' + o["inicio"] + '</span>'
        '<a href="' + o["link"] + '" class="btn" target="_blank">Aplicar</a>'
        '</div></div>'
    )


def tarjeta_grupo_empresa(e):
    return (
        '<div class="card" style="border: 2px solid #e8a020;">'
        '<div class="card-top">'
        '<div><h3>' + e["nombre"] + '</h3><div class="centro">' + e["zona"] + '</div></div>'
        '<span class="badge torange-badge">Grupos</span>'
        '</div>'
        '<div class="descripcion">' + e["descripcion"] + '</div>'
        '<div class="roles"><strong>Roles disponibles:</strong> ' + e["roles"] + '</div>'
        '<div class="tags">'
        '<span class="tag tgreen">Alojamiento</span>'
        '<span class="tag tgreen">Comida</span>'
        '<span class="tag torange">3+ personas</span>'
        '</div>'
        '<div class="card-bottom">'
        '<span class="fecha">Dic 2026 - Mar 2027</span>'
        '<a href="' + e["link"] + '" class="btn" target="_blank">Ver empleos</a>'
        '</div></div>'
    )


def generar_html(por_zona, fecha):
    total = sum(len(v) for v in por_zona.values())
    grupos_scraper = [o for v in por_zona.values() for o in v if o["para_grupo"]]
    sitios = sum(len(ZONAS[z]) for z in ZONAS)

    cards_empresas_grupo = "".join(tarjeta_grupo_empresa(e) for e in EMPRESAS_GRUPOS)
    cards_scraper = "".join(tarjeta(o, True) for o in grupos_scraper)
    sec_grupos = (
        '<div class="sec-grupos">'
        '<h2>Empresas que contratan grupos (3+ personas)</h2>'
        '<p class="sub">Estas empresas contratan equipos completos - perfectas para ir los 3 juntos</p>'
        '<div class="grid">' + cards_empresas_grupo + '</div>'
        + ('<h2 style="margin-top:24px;font-size:16px;color:#a06000;">Ofertas detectadas automaticamente para grupos</h2><div class="grid">' + cards_scraper + '</div>' if grupos_scraper else '') +
        '</div>'
    )

    sec_zonas = ""
    for zona, ofertas in por_zona.items():
        if ofertas:
            cards = "".join(tarjeta(o) for o in ofertas)
            sec_zonas += '<div class="sec-zona"><h2>' + zona + '</h2><div class="grid">' + cards + '</div></div>'

    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ski Jobs Francia</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;background:#f0f4f8;padding:24px}
.header{background:#1A3A5C;color:white;padding:20px 24px;border-radius:12px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.header h1{font-size:22px}
.header p{font-size:13px;opacity:0.8;margin-top:4px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:32px}
.stat{background:white;border-radius:10px;padding:16px;text-align:center;border:1px solid #dde5ee}
.stat .num{font-size:28px;font-weight:bold;color:#1A3A5C}
.stat .label{font-size:12px;color:#666;margin-top:4px}
.sec-grupos{background:#fff8ee;border:2px solid #e8a020;border-radius:12px;padding:20px;margin-bottom:32px}
.sec-grupos h2{font-size:18px;color:#a06000;margin-bottom:6px}
.sec-zona{margin-bottom:32px}
.sec-zona h2{font-size:18px;color:#1A3A5C;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #dde5ee}
.sub{font-size:13px;color:#888;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.card{background:white;border-radius:12px;padding:18px;border:1px solid #dde5ee}
.card-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:8px}
.card h3{font-size:15px;color:#1a1a1a}
.centro{font-size:13px;color:#666;margin-top:3px}
.badge{font-size:11px;padding:3px 10px;border-radius:20px;background:#EBF3FB;color:#1A3A5C;white-space:nowrap}
.torange-badge{background:#FFF0D6;color:#a06000}
.descripcion{font-size:12px;color:#555;margin:8px 0;line-height:1.5;background:#f8f9fa;padding:8px;border-radius:6px}
.roles{font-size:12px;color:#444;margin:6px 0}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.tag{font-size:11px;padding:3px 10px;border-radius:20px}
.tgreen{background:#D6F0E0;color:#1A7A3C;font-weight:bold}
.tgray{background:#f0f0f0;color:#888}
.tblue{background:#EBF3FB;color:#1A5CA0}
.torange{background:#FFF0D6;color:#a06000;font-weight:bold}
.detalles{font-size:13px;color:#555;margin:8px 0}
.card-bottom{display:flex;justify-content:space-between;align-items:center;margin-top:12px;border-top:1px solid #f0f0f0;padding-top:12px}
.fecha{font-size:12px;color:#888}
.btn{background:#1A3A5C;color:white;text-decoration:none;padding:7px 16px;border-radius:8px;font-size:13px}
.footer{margin-top:24px;font-size:12px;color:#999;text-align:center;padding-top:16px;border-top:1px solid #dde5ee}
</style>
</head>
<body>
<div class="header">
<div><h1>Ski Jobs Francia</h1><p>Actualizado el """ + fecha + """ - Solo ofertas con alojamiento y comida</p></div>
<div style="font-size:14px;opacity:0.9">""" + str(total) + """ ofertas encontradas</div>
</div>
<div class="stats">
<div class="stat"><div class="num">""" + str(total) + """</div><div class="label">Ofertas hoy</div></div>
<div class="stat"><div class="num">""" + str(len(por_zona)) + """</div><div class="label">Zonas</div></div>
<div class="stat"><div class="num">""" + str(sitios) + """</div><div class="label">Sitios revisados</div></div>
<div class="stat"><div class="num">""" + str(len(EMPRESAS_GRUPOS)) + """</div><div class="label">Empresas grupos</div></div>
</div>
""" + sec_grupos + sec_zonas + """
<div class="footer">Actualizado automaticamente cada dia a las 11 AM</div>
</body>
</html>"""


def subir_github(html):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return None
    url = "https://api.github.com/repos/" + GITHUB_REPO + "/contents/index.html"
    hdrs = {"Authorization": "token " + GITHUB_TOKEN, "Content-Type": "application/json"}
    try:
        r = requests.get(url, headers=hdrs)
        sha = r.json().get("sha") if r.status_code == 200 else None
        data = {"message": "Update " + datetime.now().strftime("%Y-%m-%d"), "content": base64.b64encode(html.encode()).decode()}
        if sha:
            data["sha"] = sha
        requests.put(url, headers=hdrs, json=data)
        parts = GITHUB_REPO.split("/")
        return "https://" + parts[0] + ".github.io/" + parts[1] + "/"
    except Exception as e:
        print("Error subiendo: " + str(e))
        return None


def enviar_whatsapp(msg):
    url = "https://api.callmebot.com/whatsapp.php?phone=" + WHATSAPP_PHONE + "&text=" + quote(msg) + "&apikey=" + WHATSAPP_APIKEY
    requests.get(url, timeout=10)


def main():
    fecha = datetime.now().strftime("%d/%m/%Y")
    print("Buscando ofertas - " + fecha)
    por_zona = {}
    for zona, sitios in ZONAS.items():
        por_zona[zona] = buscar_zona(zona, sitios)
    total = sum(len(v) for v in por_zona.values())
    grupos = [o for v in por_zona.values() for o in v if o["para_grupo"]]
    print("Encontradas: " + str(total) + " ofertas")
    html = generar_html(por_zona, fecha)
    link = subir_github(html)
    if link:
        msg = "Ski Jobs Francia - " + fecha + "\n" + str(total) + " ofertas - " + str(len(EMPRESAS_GRUPOS)) + " empresas para grupos.\nVer: " + link
    else:
        msg = "Ski Jobs Francia - " + fecha + "\n" + str(total) + " ofertas encontradas hoy."
    enviar_whatsapp(msg)
    print("Listo")


if __name__ == "__main__":
    main()
