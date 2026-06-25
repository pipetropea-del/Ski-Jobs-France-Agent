import requests
from datetime import datetime
from urllib.parse import quote

WHATSAPP_PHONE = "5491122803223"
WHATSAPP_APIKEY = "5295938"

SITIOS = [
    "https://www.seasonworkers.com/skijobs/resorts/ski-jobs-france.aspx",
    "https://www.bestskijobs.co.uk/france.php",
    "https://www.snowseasoncentral.com/france",
    "https://www.coolskijobs.com/ski-resorts/chamonix/",
    "https://hunterchalets.com/ski-season-jobs/",
]

def enviar_whatsapp(mensaje):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={quote(mensaje)}&apikey={WHATSAPP_APIKEY}"
    requests.get(url)

def main():
    hoy = datetime.now().strftime("%d/%m/%Y")
    mensaje = f"🏔️ Ski Jobs Francia - {hoy}\n\nEl agente está corriendo en la nube y buscando ofertas. Revisá ski_jobs_francia.html para ver los resultados."
    enviar_whatsapp(mensaje)
    print("WhatsApp enviado correctamente")

if __name__ == "__main__":
    main()
