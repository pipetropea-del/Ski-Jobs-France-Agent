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

KEYWORDS = ["chef", "host", "bar", "kitchen", "reception", "housekeeper", "driver",
            "maintenance", "assistant", "manager", "staff", "waiter", "cook",
            "ski rental", "ski hire", "location ski", "ski shop", "ski tech",
            "boot fitter", "equipment", "materiel", "magasin",
            "saisonnier", "emploi", "cuisinier", "serveur", "animateur"]

KEYWORDS_GRUPO = ["team", "couple", "group", "several", "multiple", "positions", "plusieurs", "postes"]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


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
                    ofertas.append({
                        "puesto": texto[:70],
                        "zona": zona,
                        "salario": "Ver oferta",
                        "inicio": "Dic 2026",
                        "fin": "Mar 2027",
                        "ski_pass": "ski pass" in tl,
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
    return (
        '<div class="card" style="' + border + '">'
        '<div class="card-top">'
        '<div><h3>' + o["puesto"] + '</h3><div class="centro">' + o["zona"] + '</div></div>'
        '<span class="badge">' + o["fuente"] + '</span>'
        '</div>'
        '<div class="tags">'
        '<span class="tag tgreen">Alojamiento</span>'
        '<span class="tag tgreen">Comida</span>' + ski + grp +
        '</div>'
        '<div class="detalles">' + o["salario"] + ' | ' + o["inicio"] + ' - ' + o["fin"] + '</div>'
        '<div class="card-bottom">'
        '<span class="fecha">Temporada ' + o["inicio"] + '</span>'
        '<a href="' + o["link"] + '" class="btn" target="_blank">Aplicar</a>'
        '</div></div>'
    )


def generar_html(por_zona, fecha):
    total = sum(len(v) for v in por_zona.values())
    grupos = [o for v in por_zona.values() for o in v if o["para_grupo"]]
    sitios = sum(len(ZONAS[z]) for z in ZONAS)

    sec_grupos = ""
    if grupos:
        cards = "".join(tarjeta(o, True) for o in grupos)
        sec_grupos = '<div class="sec-grupos"><h2>Ofertas para grupos (3+ personas)</h2><p class="sub">Estas ofertas buscan multiples personas - perfectas para ir los 3 juntos</p><div class="grid">' + cards + '</div></div>'

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
.tags{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.tag{font-size:11px;padding:3px 10px;border-radius:20px}
.tgreen{background:#D6F0E0;color:#1A7A3C;font-weight:bold}
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
<div class="stat"><div class="num">""" + str(len(grupos)) + """</div><div class="label">Para grupos</div></div>
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
        msg = "Ski Jobs Francia - " + fecha + "\n" + str(total) + " ofertas - " + str(len(grupos)) + " para grupos.\nVer: " + link
    else:
        msg = "Ski Jobs Francia - " + fecha + "\n" + str(total) + " ofertas encontradas hoy."
    enviar_whatsapp(msg)
    print("Listo")


if __name__ == "__main__":
    main()
