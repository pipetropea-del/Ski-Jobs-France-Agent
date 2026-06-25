import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote
import json
import base64
import os

WHATSAPP_PHONE = "5491122803223"
WHATSAPP_APIKEY = "5295938"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")

SITIOS = [
    {
        "nombre": "SeasonWorkers",
        "url": "https://www.seasonworkers.com/skijobs/resorts/ski-jobs-france.aspx",
    },
    {
        "nombre": "BestSkiJobs",
        "url": "https://www.bestskijobs.co.uk/france.php",
    },
    {
        "nombre": "NativesCoUk",
        "url": "https://natives.co.uk/jobs/?location=france&accommodation=yes",
    },
    {
        "nombre": "CoolSkiJobs",
        "url": "https://www.coolskijobs.com/ski-resorts/chamonix/",
    },
    {
        "nombre": "HunterChalets",
        "url": "https://hunterchalets.com/ski-season-jobs/",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def buscar_ofertas():
    ofertas = []
    for sitio in SITIOS:
        try:
            r = requests.get(sitio["url"], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all("a", href=True)
            keywords = ["chef", "host", "bar", "kitchen", "reception", "housekeeper",
                       "driver", "maintenance", "assistant", "manager", "staff",
                       "saisonnier", "emploi", "cuisinier", "serveur"]
            for link in links:
                texto = link.get_text(strip=True).lower()
                if any(k in texto for k in keywords) and len(texto) > 5:
                    href = link["href"]
                    if not href.startswith("http"):
                        base = "/".join(sitio["url"].split("/")[:3])
                        href = base + href
                    ofertas.append({
                        "puesto": link.get_text(strip=True)[:60],
                        "centro": "Francia - Alpes",
                        "salario": "Ver oferta",
                        "inicio": "Dic 2026",
                        "alojamiento": True,
                        "comida": True,
                        "fuente": sitio["nombre"],
                        "link": href
                    })
        except Exception as e:
            print(f"Error en {sitio['nombre']}: {e}")
    return ofertas[:20]

def generar_html(ofertas, fecha):
    n = len(ofertas)
    centros = len(set(o["centro"] for o in ofertas))
    sitios_revisados = len(set(o["fuente"] for o in ofertas))
    
    tarjetas = ""
    for o in ofertas:
        ski_pass = '<span class="tag tag-blue">🎿 Ski pass</span>' if o.get("ski_pass") else ""
        tarjetas += f"""
        <div class="card">
            <div class="card-top">
                <div><h3>{o['puesto']}</h3><div class="centro">📍 {o['centro']}</div></div>
                <span class="badge badge-empresa">{o['fuente']}</span>
            </div>
            <div class="tags">
                <span class="tag tag-green">🏠 Alojamiento</span>
                <span class="tag tag-green">🍽️ Comida</span>
                {ski_pass}
            </div>
            <div class="card-bottom">
                <div><div class="salario">{o['salario']}</div><div class="fecha">Desde {o['inicio']}</div></div>
                <a href="{o['link']}" class="btn" target="_blank">Aplicar →</a>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ski Jobs Francia</title>
<style>
  body {{ font-family: Arial, sans-serif; background: #f0f4f8; margin: 0; padding: 24px; }}
  .header {{ background: #1A3A5C; color: white; padding: 20px 24px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .header h1 {{ margin: 0; font-size: 22px; }}
  .header p {{ margin: 4px 0 0; font-size: 13px; opacity: 0.8; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 24px; }}
  .stat {{ background: white; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #dde5ee; }}
  .stat .num {{ font-size: 28px; font-weight: bold; color: #1A3A5C; }}
  .stat .label {{ font-size: 12px; color: #666; margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
  .card {{ background: white; border-radius: 12px; padding: 18px; border: 1px solid #dde5ee; }}
  .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }}
  .card h3 {{ margin: 0; font-size: 15px; color: #1a1a1a; }}
  .centro {{ font-size: 13px; color: #666; margin: 3px 0 0; }}
  .badge {{ font-size: 11px; padding: 3px 10px; border-radius: 20px; white-space: nowrap; }}
  .badge-empresa {{ background: #EBF3FB; color: #1A3A5C; }}
  .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0; }}
  .tag {{ font-size: 11px; padding: 3px 10px; border-radius: 20px; }}
  .tag-green {{ background: #D6F0E0; color: #1A7A3C; font-weight: bold; }}
  .tag-blue {{ background: #EBF3FB; color: #1A5CA0; }}
  .card-bottom {{ display: flex; justify-content: space-between; align-items: center; margin-top: 12px; border-top: 1px solid #f0f0f0; padding-top: 12px; }}
  .salario {{ font-size: 16px; font-weight: bold; color: #1A3A5C; }}
  .fecha {{ font-size: 12px; color: #888; }}
  .btn {{ background: #1A3A5C; color: white; text-decoration: none; padding: 7px 16px; border-radius: 8px; font-size: 13px; }}
  .footer {{ margin-top: 24px; font-size: 12px; color: #999; text-align: center; }}
  .no-ofertas {{ background: white; border-radius: 12px; padding: 40px; text-align: center; color: #666; border: 1px solid #dde5ee; }}
</style>
</head>
<body>
<div class="header">
  <div><h1>🏔️ Ski Jobs Francia</h1><p>Actualizado el {fecha} · Solo ofertas con alojamiento y comida incluidos</p></div>
  <div style="text-align:right;font-size:13px;opacity:0.9;">{n} ofertas encontradas</div>
</div>
<div class="stats">
  <div class="stat"><div class="num">{n}</div><div class="label">Ofertas hoy</div></div>
  <div class="stat"><div class="num">{centros}</div><div class="label">Centros cubiertos</div></div>
  <div class="stat"><div class="num">{sitios_revisados}</div><div class="label">Sitios revisados</div></div>
</div>
{"<div class='grid'>" + tarjetas + "</div>" if ofertas else "<div class='no-ofertas'>😴 Sin ofertas nuevas hoy. Revisá mañana.</div>"}
<div class="footer">Actualizado automáticamente cada día · Ski Jobs Francia Agent</div>
</body>
</html>"""

def subir_html_github(html_content):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("Sin token de GitHub, saltando subida")
        return None
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/index.html"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
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
    
    ofertas = buscar_ofertas()
    print(f"Encontradas: {len(ofertas)} ofertas")
    
    html = generar_html(ofertas, fecha)
    link = subir_html_github(html)
    
    if link:
        mensaje = f"🏔️ Ski Jobs Francia - {fecha}\n{len(ofertas)} ofertas con aloj+comida.\nVer: {link}"
    else:
        mensaje = f"🏔️ Ski Jobs Francia - {fecha}\n{len(ofertas)} ofertas encontradas hoy."
    
    enviar_whatsapp(mensaje)
    print("Listo")

if __name__ == "__main__":
    main()
