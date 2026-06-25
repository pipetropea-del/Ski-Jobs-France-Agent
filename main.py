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
    "Chamonix": {
        "sitios": [
            {"nombre": "CoolSkiJobs", "url": "https://www.coolskijobs.com/ski-resorts/chamonix/"},
            {"nombre": "SeeChamonix", "url": "https://www.seechamonix.com/season-work/"},
            {"nombre": "SeasonWorkers", "url": "https://www.seasonworkers.com/skijobs/resorts/france/chamonix-39.aspx"},
        ]
    },
    "Val d'Isere": {
        "sitios": [
            {"nombre": "Consensio", "url": "https://www.consensiochalets.co.uk/ski-season-jobs/"},
            {"nombre": "Le Ski", "url": "https://www.leski.com/ski-jobs/apply"},
            {"nombre": "BestSkiJobs", "url": "https://www.bestskijobs.co.uk/france.php"},
        ]
    },
    "Courchevel / Meribel": {
        "sitios": [
            {"nombre": "Purple Ski", "url": "https://www.purpleski.com/jobs/"},
            {"nombre": "SeasonWorkers", "url": "https://www.seasonworkers.com/skijobs/resorts/ski-jobs-france.aspx"},
            {"nombre": "Natives", "url": "https://natives.co.uk"},
        ]
    },
    "Morzine / Les Gets": {
        "sitios": [
            {"nombre": "Hunter Chalets", "url": "https://hunterchalets.com/ski-season-jobs/"},
            {"nombre": "SnowSeason", "url": "https://www.snowseasoncentral.com/france"},
        ]
    },
    "Otras zonas": {
        "sitios": [
            {"nombre": "SkiWorld", "url": "https://www.skiworld.co.uk/recruitment/ski-season-jobs"},
            {"nombre": "SkiWeekends", "url": "https://www.skiweekends.com/overseas-jobs"},
            {"nombre": "Indeed FR", "url": "https://fr.indeed.com/emplois?q=saisonnier+ski+loge+nourri&l=France"},
        ]
    }
}

KEYWORDS_TRABAJO = [
    "chef", "host", "bar", "kitchen", "reception", "housekeeper", "driver",
    "maintenance", "assistant", "manager", "staff", "waiter", "waitress",
    "cleaner", "cook", "nanny", "childcare", "instructor", "guide",
    "saisonnier", "emploi", "cuisinier", "serveur", "femme de chambre",
    "animateur", "receptionniste", "plongeur", "commis"
]

KEYWORDS_GRUPO = [
    "team", "couple", "group", "several", "multiple", "positions",
    "equipe", "plusieurs", "postes", "couples"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def buscar_en_zona(zona, sitios):
    ofertas = []
    for sitio in sitios:
        try:
            r = requests.get(sitio["url"], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all("a", href=True)
            for link in links:
                texto = link.get_text(strip=True)
                texto_lower = texto.lower()
                if any(k in texto_lower for k in KEYWORDS_TRABAJO) and len(texto) > 5:
                    href = link["href"]
                    if not href.startswith("http"):
                        base = "/".join(sitio["url"].split("/")[:3])
                        href = base + href
                    para_grupo = any(k in texto_lower for k in KEYWORDS_GRUPO)
                    ofertas.append({
                        "puesto": texto[:70],
                        "zona": zona,
                        "salario": "Ver oferta",
                        "inicio": "Dic 2026",
                        "fin": "Mar 2027",
                        "alojamiento": True,
                        "comida": True,
                        "ski_pass": "ski pass" in texto_lower or "forfait" in texto_lower,
                        "para_grupo": para_grupo,
                        "fuente": sitio["nombre"],
                        "link": href
                    })
        except Exception as e:
            print(f"Error en {sitio['nombre']}: {e}")
    return ofertas[:8]


def buscar_todas_ofertas():
    todas = []
    grupos = []
    por_zona = {}
    for zona, config in ZONAS.items():
        ofertas_zona = buscar_en_zona(zona, config["sitios"])
        por_zona[zona] = ofertas_zona
        for o in ofertas_zona:
            if o["para_grupo"]:
                grupos.append(o)
            else:
                todas.append(o)
    return todas, grupos, por_zona


def tarjeta_html(o, destacada=False):
    ski_pass = '<span class="tag tag-blue">Ski pass</span>' if o.get("ski_pass") else ""
    grupo_badge = '<span class="tag tag-orange">3+ personas</span>' if o.get("para_grupo") else ""
    border = "border: 2px solid #e8a020;" if destacada else ""
    return f"""
    <div class="card" style="{border}">
        <div class="card-top">
            <div><h3>{o['puesto']}</h3><div class="centro">{o['zona']}</div></div>
            <span class="badge badge-empresa">{o['fuente']}</span>
        </div>
        <div class="tags">
            <span class="tag tag-green">Alojamiento</span>
            <span class="tag tag-green">Comida</span>
            {ski_pass}
            {grupo_badge}
        </div>
        <div class="detalles">
            <span>{o['salario']}</span>
            <span>{o['inicio']} - {o['fin']}</span>
        </div>
        <div class="card-bottom">
            <div class="fecha">Temporada {o['inicio']}</div>
            <a href="{o['link']}" class="btn" target="_blank">Aplicar</a>
        </div>
    </div>"""


def generar_html(todas, grupos, por_zona, fecha):
    total = sum(len(v) for v in por_zona.values())
    sitios_revisados = sum(len(ZONAS[z]["sitios"]) for z in ZONAS)

    seccion_grupos = ""
    if grupos:
        tarjetas_grupo = "".join(tarjeta_html(o, destacada=True) for o in grupos)
        seccion_grupos = f"""
        <div class="seccion-grupos">
            <h2>Ofertas para grupos (3+ personas)</h2>
            <p class="subtitulo">Estas ofertas buscan multiples personas - perfectas para ir los 3 juntos</p>
            <div class="grid">{tarjetas_grupo}</div>
        </div>"""

    secciones_zonas = ""
    for zona, ofertas in por_zona.items():
        if not ofertas:
            continue
        tarjetas = "".join(tarjeta_html(o) for o in ofertas)
        secciones_zonas += f"""
        <div class="seccion-zona">
            <h2>{zona}</h2>
            <div class="grid">{tarjetas}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ski Jobs Francia</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Arial, sans-serif; background: #f0f4f8; padding: 24px; }}
  .header {{ background: #1A3A5C; color: white; padding: 20px 24px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .header h1 {{ font-size: 22px; }}
  .header p {{ font-size: 13px; opacity: 0.8; margin-top: 4px; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 32px; }}
  .stat {{ background: white; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #dde5ee; }}
  .stat .num {{ font-size: 28px; font-weight: bold; color: #1A3A5C; }}
  .stat .label {{ font-size: 12px; color: #666; margin-top: 4px; }}
  .seccion-grupos {{ background: #fff8ee; border: 2px solid #e8a020; border-radius: 12px; padding: 20px; margin-bottom: 32px; }}
  .seccion-grupos h2 {{ font-size: 18px; color: #a06000; margin-bottom: 6px; }}
  .seccion-zona {{ margin-bottom: 32px; }}
  .seccion-zona h2 {{ font-size: 18px; color: #1A3A5C; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #dde5ee; }}
  .subtitulo {{ font-size: 13px; color: #888; margin-bottom: 16px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
  .card {{ background: white; border-radius: 12px; padding: 18px; border: 1px solid #dde5ee; }}
  .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; gap: 8px; }}
  .card h3 {{ font-size: 15px; color: #1a1a1a; }}
  .centro {{ font-size: 13px; color: #666; margin-top: 3px; }}
  .badge {{ font-size: 11px; padding: 3px 10px; border-radius: 20px; white-space: nowrap; }}
  .badge-empresa {{ background: #EBF3FB; color: #1A3A5C; }}
  .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0; }}
  .tag {{ font-size: 11px; padding: 3px 10px; border-radius: 20px; }}
  .tag-green {{ background: #D6F0E0; color: #1A7A3C; font-weight: bold; }}
  .tag-blue {{ background: #EBF3FB; color: #1A5CA0; }}
  .tag-orange {{ background: #FFF0D6; color: #a06000; font-weight: bold; }}
  .detalles {{ display: flex; gap: 16px; font-size: 13px; color: #555; margin: 8px 0; flex-wrap: wrap; }}
  .card-bottom {{ display: flex; justify-content: space-between; align-items: center; margin-top: 12px; border-top: 1px solid #f0f0f0; padding-top: 12px; }}
  .fecha {{ font-size: 12px; color: #888; }}
  .btn {{ background: #1A3A5C; color: white; text-decoration: none; padding: 7px 16px; border-radius: 8px; font-size: 13px; }}
  .footer {{ margin-top: 24px; font-size: 12px; color: #999; text-align: center; padding-top: 16px; border-top: 1px solid #dde5ee; }}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>Ski Jobs Francia</h1>
    <p>Actualizado el {fecha} - Solo ofertas con alojamiento y comida incluidos</p>
  </div>
  <div style="text-align:right;font-size:14px;opacity:0.9;">{total} ofertas encontradas</div>
</div>
<div class="stats">
  <div class="stat"><div class="num">{total}</div><div class="label">Ofertas hoy</div></div>
  <div class="stat"><div class="num">{len(por_zona)}</div><div class="label">Zonas cubiertas</div></div>
  <div class="stat"><div class="num">{sitios_revisados}</div><div class="label">Sitios revisados</div></div>
  <div class="stat"><div class="num">{len(grupos)}</div><div class="label">Para grupos</div></div>
</div>
{seccion_grupos}
{secciones_zonas}
<div class="footer">Actualizado automaticamente cada dia a las 11 AM - Ski Jobs Francia Agent</div>
</body>
</html>"""


def subir_html_github(html_content):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("Sin token de GitHub")
        return None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/index.html"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    try:
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        data = {
            "message": f"Update ski jobs {datetime.now().strftime('%Y-%m-%d')}",
            "content": base64.b64encode(html_content.encode()).decode(),
        }
        if sha:
            data["sha"] = sha
        requests.put(url, headers=headers, json=data)
        return f"https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/"
    except Exception as e:
        print(f"Error subiendo HTML: {e}")
        return None


def enviar_whatsapp(mensaje):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={quote(mensaje)}&apikey={WHATSAPP_APIKEY}"
    requests.get(url, timeout=10)


def main():
    fecha = datetime.now().strftime("%d/%m/%Y")
    print(f"Buscando ofertas - {fecha}")
    todas, grupos, por_zona = buscar_todas_ofertas()
    total = sum(len(v) for v in por_zona.values())
    print(f"Encontradas: {total} ofertas, {len(grupos)} para grupos")
    html = generar_html(todas, grupos, por_zona, fecha)
    link = subir_html_github(html)
    if link:
        mensaje = f"Ski Jobs Francia - {fecha}\n{total} ofertas - {len(grupos)} para grupos de 3.\nVer: {link}"
    else:
        mensaje = f"Ski Jobs Francia - {fecha}\n{total} ofertas encontradas hoy."
    enviar_whatsapp(mensaje)
    print("L
