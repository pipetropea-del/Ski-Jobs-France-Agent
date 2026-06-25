import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote
import base64
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

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

KEYWORDS_GRUPO = ["team", "couple", "
