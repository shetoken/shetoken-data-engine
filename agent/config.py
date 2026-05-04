"""
SHEtoken WEI News Agent — Configuration v2.0
All settings, 100+ news sources, WEI signal keywords.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "signals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SLM Models (Ollama)
ENGLISH_MODEL      = "phi3.5"
MULTILINGUAL_MODEL = "qwen2.5:3b"
OLLAMA_HOST        = os.getenv("OLLAMA_HOST", "http://localhost:11434")

LANGUAGE_MODEL_MAP = {
    "en": ENGLISH_MODEL,
    "hi": MULTILINGUAL_MODEL,   # Hindi
    "bn": MULTILINGUAL_MODEL,   # Bengali
    "ur": MULTILINGUAL_MODEL,   # Urdu
    "ar": MULTILINGUAL_MODEL,   # Arabic
    "pt": MULTILINGUAL_MODEL,   # Portuguese
    "es": MULTILINGUAL_MODEL,   # Spanish
    "fr": MULTILINGUAL_MODEL,   # French
    "ta": MULTILINGUAL_MODEL,   # Tamil
    "te": MULTILINGUAL_MODEL,   # Telugu
    "mr": MULTILINGUAL_MODEL,   # Marathi
    "sw": MULTILINGUAL_MODEL,   # Swahili
    "id": MULTILINGUAL_MODEL,   # Indonesian
}

# Email
GMAIL_USER     = os.getenv("GMAIL_USER")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASSWORD")
REPORT_TO      = os.getenv("REPORT_TO_EMAIL", os.getenv("GMAIL_USER"))
REPORT_SUBJECT = "SHEtoken WEI Weekly Signal Report"

# Google Sheets
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SA_JSON  = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SIGNALS_TAB     = "📡 Weekly Signals"
WEI_LIVE_TAB    = "📊 WEI Live Scores"

# Agent settings
MAX_ARTICLES_PER_SOURCE = 25
MAX_ARTICLE_LENGTH      = 900
MIN_CONFIDENCE          = 0.55
CRISIS_THRESHOLD        = 0.80
REQUEST_TIMEOUT         = 12
REQUEST_DELAY           = 0.5
MAX_WORKERS             = 8

# WEI update settings
SIGNAL_WEIGHT      = 0.08   # max % a single week of signals can move a pillar
MAX_WEEKLY_DELTA   = 2.0    # max WEI points movable per week from signals
DECAY_HALFLIFE_WEEKS = 12   # signals lose half their weight after 12 weeks

# News sources: (name, rss_url, language, region, tier)
NEWS_SOURCES = [

    # ── GLOBAL ENGLISH — Tier 1 ──────────────────────────────────────────────
    ("BBC World",          "https://feeds.bbci.co.uk/news/world/rss.xml",             "en","global","global"),
    ("AP News",            "https://feeds.apnews.com/rss/apf-topnews",               "en","global","global"),
    ("Al Jazeera",         "https://www.aljazeera.com/xml/rss/all.xml",               "en","global","global"),
    ("The Guardian GD",    "https://www.theguardian.com/global-development/rss",      "en","global","global"),
    ("The Guardian Women", "https://www.theguardian.com/lifeandstyle/women/rss",      "en","global","global"),
    ("Human Rights Watch", "https://www.hrw.org/rss.xml",                             "en","global","global"),
    ("UN News Women",      "https://news.un.org/feed/subscribe/en/news/topic/women/feed/rss.xml","en","global","global"),
    ("UN News Human Rights","https://news.un.org/feed/subscribe/en/news/topic/human-rights/feed/rss.xml","en","global","global"),
    ("Plan International", "https://plan-international.org/feed/",                    "en","global","global"),
    ("Girls Not Brides",   "https://www.girlsnotbrides.org/feed/",                    "en","global","global"),
    ("AWID",               "https://www.awid.org/rss.xml",                            "en","global","global"),
    ("Ms Magazine",        "https://msmagazine.com/feed/",                            "en","global","global"),
    ("Devex",              "https://www.devex.com/news/rss.xml",                      "en","global","global"),
    ("IPS News",           "https://www.ipsnews.net/feed/",                           "en","global","global"),
    ("Open Democracy 50-50","https://www.opendemocracy.net/en/5050/rss/",             "en","global","global"),
    ("Women Media Center", "https://womensmediacenter.com/feed",                      "en","global","global"),
    ("Global Fund Women",  "https://www.globalfundforwomen.org/feed/",                "en","global","global"),
    ("ActionAid",          "https://www.actionaid.org/feed",                          "en","global","global"),
    ("Equality Now",       "https://equalitynow.org/feed/",                           "en","global","global"),
    ("Gender Policy Report","https://genderpolicyreport.umn.edu/feed/",               "en","global","global"),
    ("Jezebel",            "https://jezebel.com/rss",                                 "en","global","global"),

    # ── INDIA — English ───────────────────────────────────────────────────────
    ("The Hindu",          "https://www.thehindu.com/news/national/feeder/default.rss","en","India","regional"),
    ("The Wire",           "https://thewire.in/feed",                                 "en","India","regional"),
    ("Wire Gender",        "https://thewire.in/women/feed",                           "en","India","regional"),
    ("Indian Express",     "https://indianexpress.com/section/india/feed/",            "en","India","regional"),
    ("NDTV India",         "https://feeds.feedburner.com/ndtvnews-india-news",        "en","India","regional"),
    ("Scroll.in",          "https://scroll.in/feed",                                  "en","India","regional"),
    ("The Print",          "https://theprint.in/feed/",                               "en","India","regional"),
    ("Hindustan Times",    "https://www.hindustantimes.com/feeds/rss/india/rssfeed.xml","en","India","regional"),
    ("Feminism in India",  "https://feminisminindia.com/feed/",                       "en","India","regional"),
    ("The Quint Women",    "https://www.thequint.com/topic/women.rss",                "en","India","regional"),
    ("LiveMint Women",     "https://www.livemint.com/rss/women.xml",                  "en","India","regional"),
    ("Economic Times",     "https://economictimes.indiatimes.com/rssfeedstopstories.cms","en","India","regional"),
    ("India Today Women",  "https://www.indiatoday.in/rss/1206614",                   "en","India","regional"),
    ("Outlook India",      "https://www.outlookindia.com/rss/main/magazine",          "en","India","regional"),
    ("The News Minute",    "https://www.thenewsminute.com/feeds/latest/rss.xml",      "en","South India","regional"),

    # ── INDIA — Hindi ─────────────────────────────────────────────────────────
    ("Dainik Bhaskar",     "https://www.bhaskar.com/rss-feed/8/",                     "hi","India","regional"),
    ("Amar Ujala",         "https://www.amarujala.com/rss/breaking-news.xml",         "hi","India","regional"),
    ("Jagran",             "https://www.jagran.com/rss/news-national.xml",            "hi","India","regional"),
    ("Dainik Jagran",      "https://epaper.jagran.com/rss/national.xml",              "hi","India","regional"),
    ("Patrika Hindi",      "https://www.patrika.com/rss/national-news.xml",           "hi","India","regional"),
    ("Hindi Samachar",     "https://hindi.news18.com/rss/news/india/national.xml",    "hi","India","regional"),

    # ── INDIA — Bengali ───────────────────────────────────────────────────────
    ("Anandabazar",        "https://www.anandabazar.com/rss/latest-news",             "bn","West Bengal","local"),
    ("Eisamay",            "https://eisamay.com/feeds/rss/bengal-news.cms",           "bn","West Bengal","local"),
    ("Sangbad Pratidin",   "https://www.sangbadpratidin.in/feed/",                    "bn","West Bengal","local"),
    ("Bartaman",           "https://www.bartamanpatrika.com/feed/",                   "bn","West Bengal","local"),

    # ── INDIA — Tamil ─────────────────────────────────────────────────────────
    ("Dinamalar",          "https://www.dinamalar.com/rss/tamilnadu_news.asp",        "ta","Tamil Nadu","local"),
    ("Dinamani",           "https://www.dinamani.com/rss/tamilnadu.xml",              "ta","Tamil Nadu","local"),
    ("Vikatan",            "https://www.vikatan.com/rss/news.xml",                    "ta","Tamil Nadu","local"),

    # ── INDIA — Telugu ────────────────────────────────────────────────────────
    ("Sakshi",             "https://www.sakshi.com/rss/state.xml",                    "te","Andhra Pradesh","local"),
    ("Eenadu",             "https://www.eenadu.net/rss/telangana.xml",                "te","Telangana","local"),

    # ── INDIA — Marathi ───────────────────────────────────────────────────────
    ("Loksatta",           "https://www.loksatta.com/rss/loksatta.rss",               "mr","Maharashtra","local"),
    ("Maharashtra Times",  "https://maharashtratimes.com/rssfeedstopstories.cms",     "mr","Maharashtra","local"),

    # ── PAKISTAN ──────────────────────────────────────────────────────────────
    ("Dawn",               "https://www.dawn.com/feeds/home",                         "en","Pakistan","regional"),
    ("The News Pakistan",  "https://www.thenews.com.pk/rss/1/news",                   "en","Pakistan","regional"),
    ("Express Tribune",    "https://tribune.com.pk/feed",                             "en","Pakistan","regional"),
    ("Geo News",           "https://www.geo.tv/rss/10",                               "en","Pakistan","regional"),
    ("Daily Pakistan",     "https://en.dailypakistan.com.pk/feed/",                   "en","Pakistan","regional"),
    ("Jang Urdu",          "https://jang.com.pk/rss/breaking-news",                   "ur","Pakistan","regional"),
    ("Nawa-i-Waqt",        "https://www.nawaiwaqt.com.pk/rss/news",                   "ur","Pakistan","regional"),

    # ── BANGLADESH ────────────────────────────────────────────────────────────
    ("Daily Star BD",      "https://www.thedailystar.net/rss.xml",                    "en","Bangladesh","regional"),
    ("Dhaka Tribune",      "https://www.dhakatribune.com/feed",                       "en","Bangladesh","regional"),
    ("Prothom Alo",        "https://www.prothomalo.com/feed",                         "bn","Bangladesh","regional"),
    ("Bdnews24",           "https://bdnews24.com/?widgetName=rssfeed&widgetId=1&getXmlFeed=true","en","Bangladesh","regional"),

    # ── SRI LANKA ─────────────────────────────────────────────────────────────
    ("Daily Mirror SL",    "https://www.dailymirror.lk/rss/",                         "en","Sri Lanka","regional"),
    ("Daily FT",           "https://www.ft.lk/rss",                                   "en","Sri Lanka","regional"),

    # ── NEPAL ─────────────────────────────────────────────────────────────────
    ("Kathmandu Post",     "https://kathmandupost.com/rss",                            "en","Nepal","regional"),
    ("My Republica",       "https://myrepublica.nagariknetwork.com/feed/",             "en","Nepal","regional"),

    # ── NIGERIA ───────────────────────────────────────────────────────────────
    ("Vanguard Nigeria",   "https://www.vanguardngr.com/feed/",                       "en","Nigeria","regional"),
    ("Premium Times NG",   "https://www.premiumtimesng.com/feed",                     "en","Nigeria","regional"),
    ("Punch Nigeria",      "https://punchng.com/feed/",                               "en","Nigeria","regional"),
    ("The Nation Nigeria", "https://thenationonlineng.net/feed/",                     "en","Nigeria","regional"),
    ("Guardian Nigeria",   "https://guardian.ng/feed/",                               "en","Nigeria","regional"),
    ("This Day Nigeria",   "https://www.thisdaylive.com/index.php/feed/",             "en","Nigeria","regional"),

    # ── KENYA + EAST AFRICA ───────────────────────────────────────────────────
    ("Daily Nation Kenya", "https://nation.africa/kenya/rss.xml",                     "en","Kenya","regional"),
    ("The Standard Kenya", "https://www.standardmedia.co.ke/rss/kenya.php",           "en","Kenya","regional"),
    ("The East African",   "https://www.theeastafrican.co.ke/tea/rss",               "en","Africa","regional"),

    # ── SOUTH AFRICA ──────────────────────────────────────────────────────────
    ("Daily Maverick",     "https://www.dailymaverick.co.za/feed/",                   "en","South Africa","regional"),
    ("Mail & Guardian",    "https://mg.co.za/feed/",                                  "en","South Africa","regional"),
    ("Ground Up SA",       "https://groundup.org.za/feed/",                           "en","South Africa","regional"),

    # ── ETHIOPIA + HORN OF AFRICA ─────────────────────────────────────────────
    ("Addis Standard",     "https://addisstandard.com/feed/",                         "en","Ethiopia","regional"),
    ("The Reporter ET",    "https://www.thereporterethiopia.com/feed",                "en","Ethiopia","regional"),

    # ── GHANA + WEST AFRICA ───────────────────────────────────────────────────
    ("Graphic Online GH",  "https://www.graphic.com.gh/feed",                         "en","Ghana","regional"),
    ("JoyNews Ghana",      "https://www.myjoyonline.com/feed/",                       "en","Ghana","regional"),
    ("AllAfrica Women",    "https://allafrica.com/tools/headlines/rdf/women/headlines.rdf","en","Africa","global"),

    # ── BRAZIL ────────────────────────────────────────────────────────────────
    ("Folha SP",           "https://feeds.folha.uol.com.br/mundo/rss091.xml",         "pt","Brazil","regional"),
    ("G1 Globo",           "https://g1.globo.com/rss/g1/",                            "pt","Brazil","regional"),
    ("Patricia Galvao",    "https://agenciapatriciagalvao.org.br/feed/",              "pt","Brazil","regional"),
    ("Agencia Publica",    "https://apublica.org/feed/",                              "pt","Brazil","regional"),
    ("Conectas",           "https://www.conectas.org/feed/",                          "pt","Brazil","regional"),

    # ── MEXICO ────────────────────────────────────────────────────────────────
    ("La Jornada",         "https://www.jornada.com.mx/rss/sociedad.xml",             "es","Mexico","regional"),
    ("Cimac Noticias",     "https://cimacnoticias.com.mx/feed/",                      "es","Mexico","regional"),
    ("Pie de Pagina",      "https://piedepagina.mx/feed/",                            "es","Mexico","regional"),
    ("Animal Politico",    "https://www.animalpolitico.com/feed/",                    "es","Mexico","regional"),
    ("Sin Embargo",        "https://www.sinembargo.mx/feed",                          "es","Mexico","regional"),

    # ── COLOMBIA + LATIN AMERICA ──────────────────────────────────────────────
    ("El Espectador",      "https://www.elespectador.com/arc/outboundfeeds/rss/",     "es","Colombia","regional"),
    ("La Silla Vacia",     "https://lasillavacia.com/feed",                           "es","Colombia","regional"),
    ("La Nacion AR",       "https://www.lanacion.com.ar/arcio/rss/",                  "es","Argentina","regional"),
    ("Infobae",            "https://www.infobae.com/feeds/rss/",                      "es","Argentina","regional"),
    ("La Diaria",          "https://ladiaria.com.uy/feed/",                           "es","Uruguay","regional"),

    # ── MIDDLE EAST ───────────────────────────────────────────────────────────
    ("Middle East Eye",    "https://www.middleeasteye.net/rss",                       "en","Middle East","regional"),
    ("Al Monitor",         "https://www.al-monitor.com/rss.xml",                     "en","Middle East","regional"),
    ("Haaretz Women",      "https://www.haaretz.com/srv/haaretz-feed.xml",            "en","Israel","regional"),

    # ── INDONESIA + SE ASIA ───────────────────────────────────────────────────
    ("Jakarta Post",       "https://www.thejakartapost.com/feed",                     "en","Indonesia","regional"),
    ("Rappler Philippines","https://www.rappler.com/feed/",                           "en","Philippines","regional"),
    ("Coconuts Media",     "https://coconuts.co/feed/",                               "en","SE Asia","regional"),

    # ── INTERNATIONAL POLICY + RESEARCH ──────────────────────────────────────
    ("Overseas Dev Institute","https://odi.org/en/rss/",                              "en","global","global"),
    ("Brookings Gender",   "https://www.brookings.edu/topic/gender-equality/feed/",   "en","global","global"),
    ("Center for Global Dev","https://www.cgdev.org/rss.xml",                         "en","global","global"),
    ("UN Women Watch",     "https://www.un.org/womenwatch/feature/",                  "en","global","global"),
    ("Landesa",            "https://www.landesa.org/feed/",                           "en","global","global"),
    # ── INDIA — Anandabazar Patrika (Bengali) ─────────────────────────────────
    ("Anandabazar Patrika",    "https://www.anandabazar.com/rss/latest-news",         "bn","West Bengal","local"),
    ("Anandabazar National",   "https://www.anandabazar.com/rss/national-news",       "bn","India","regional"),
    ("Anandabazar State",      "https://www.anandabazar.com/rss/state-news",          "bn","West Bengal","local"),

    # ── INDIA — The Hindu (multiple feeds) ────────────────────────────────────
    ("The Hindu National",     "https://www.thehindu.com/news/national/feeder/default.rss","en","India","regional"),
    ("The Hindu States",       "https://www.thehindu.com/news/states/feeder/default.rss","en","India","regional"),
    ("The Hindu Women",        "https://www.thehindu.com/society/women-empowerment/feeder/default.rss","en","India","regional"),
    ("The Hindu Education",    "https://www.thehindu.com/education/feeder/default.rss","en","India","regional"),

    # ── INDIA — Times of India ────────────────────────────────────────────────
    ("Times of India",         "https://timesofindia.indiatimes.com/rssfeedstopstories.cms","en","India","regional"),
    ("TOI India",              "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms","en","India","regional"),
    ("TOI Women",              "https://timesofindia.indiatimes.com/rssfeeds/2647163.cms","en","India","regional"),
    ("TOI World",              "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms","en","global","regional"),

    # ── USA — CNN ─────────────────────────────────────────────────────────────
    ("CNN World",              "http://rss.cnn.com/rss/edition_world.rss",             "en","global","global"),
    ("CNN US",                 "http://rss.cnn.com/rss/edition.rss",                  "en","USA","regional"),
    ("CNN Health",             "http://rss.cnn.com/rss/edition_health.rss",           "en","global","global"),

    # ── USA — Fox News ────────────────────────────────────────────────────────
    ("Fox News World",         "https://moxie.foxnews.com/google-publisher/world.xml","en","global","global"),
    ("Fox News US",            "https://moxie.foxnews.com/google-publisher/us.xml",   "en","USA","regional"),
    ("Fox News Politics",      "https://moxie.foxnews.com/google-publisher/politics.xml","en","USA","regional"),

    # ── USA — Other major outlets ─────────────────────────────────────────────
    ("New York Times World",   "https://rss.nytimes.com/services/xml/rss/nyt/World.xml","en","global","global"),
    ("New York Times US",      "https://rss.nytimes.com/services/xml/rss/nyt/US.xml", "en","USA","regional"),
    ("Washington Post World",  "https://feeds.washingtonpost.com/rss/world",          "en","global","global"),
    ("NPR News",               "https://feeds.npr.org/1001/rss.xml",                  "en","USA","regional"),
    ("PBS NewsHour",           "https://www.pbs.org/newshour/feeds/rss/headlines",    "en","USA","regional"),

    # ── UK ────────────────────────────────────────────────────────────────────
    ("The Times UK",           "https://www.thetimes.co.uk/rss/news",                 "en","global","global"),
    ("The Independent",        "https://www.independent.co.uk/news/rss",              "en","global","global"),
    ("Sky News World",         "https://feeds.skynews.com/feeds/rss/world.xml",       "en","global","global"),

    # ── AUSTRALIA ─────────────────────────────────────────────────────────────
    ("ABC Australia",          "https://www.abc.net.au/news/feed/51120/rss.xml",      "en","Australia","regional"),

    # ── CANADA ────────────────────────────────────────────────────────────────
    ("CBC Canada",             "https://www.cbc.ca/cmlink/rss-topstories",            "en","Canada","regional"),
    ("Globe and Mail",         "https://www.theglobeandmail.com/arc/outboundfeeds/rss/","en","Canada","regional"),

]

# WEI signal keywords (used to pre-filter articles before SLM)
WEI_KEYWORDS = {
    "empowerment":     ["women parliament","female minister","women president",
                        "women elected","gender quota","women leadership",
                        "women rights law","महिला संसद","নারী সংসদ",
                        "women mayor","female governor","women senator"],
    "education":       ["girls school","female literacy","women education",
                        "girls dropout","menstrual hygiene","kanyashree",
                        "beti bachao","educate girls","girls university",
                        "लड़कियों की शिक्षा","মেয়েদের শিক্ষা","period school"],
    "economic":        ["gender pay gap","women workforce","female employment",
                        "maternity leave","women entrepreneur","microfinance women",
                        "SHG","self help group","kudumbashree","jeevika",
                        "lakshmi bhandar","women bank","gender wage"],
    "health":          ["maternal mortality","women health","reproductive health",
                        "cervical cancer","breast cancer","anaemia women",
                        "maternal death","female life expectancy","मातृ मृत्यु"],
    "bodily_autonomy": ["abortion","reproductive rights","child marriage",
                        "child bride","FGM","female genital","period poverty",
                        "menstrual","forced marriage","contraception",
                        "बाल विवाह","গর্ভপাত","زواج الأطفال",
                        "casamento infantil","matrimonio infantil",
                        "niñas madres","child wed"],
    "safety_justice":  ["domestic violence","femicide","rape","sexual assault",
                        "gender violence","honour killing","acid attack",
                        "dowry death","harassment women","stealthing",
                        "घरेलू हिंसा","গৃহহিংসা","violencia doméstica",
                        "feminicidio","عنف ضد المرأة","تیزاب حملہ",
                        "marital rape","dv shelter","restraining order"],
    "dignity_welfare": ["widow rights","widow property","caregiver women",
                        "unpaid care","food insecurity women","women housing",
                        "विधवा अधिकार","women eviction","female poverty"],
    "digital_social":  ["online harassment women","cyber harassment",
                        "deepfake women","digital violence","cyberstalking",
                        "image abuse","revenge porn","online abuse women"],
    "violence_penalty":["femicide","acid attack","dowry death","honour killing",
                        "trafficking women","rape conviction","तेज़ाब","दहेज",
                        "tizab","stoning women","lashing women"],
}

# Geography keywords → (country_iso, state_code)
GEOGRAPHY_KEYWORDS = {
    "West Bengal":    ("IND","WB"),  "Kerala":       ("IND","KL"),
    "Bihar":          ("IND","BR"),  "Tamil Nadu":   ("IND","TN"),
    "Uttar Pradesh":  ("IND","UP"),  "Maharashtra":  ("IND","MH"),
    "Rajasthan":      ("IND","RJ"),  "Gujarat":      ("IND","GJ"),
    "Delhi":          ("IND","DL"),  "Odisha":       ("IND","OD"),
    "Assam":          ("IND","AS"),  "Haryana":      ("IND","HR"),
    "Karnataka":      ("IND","KA"),  "Andhra Pradesh":("IND","AP"),
    "Telangana":      ("IND","TS"),  "Punjab":       ("IND","PB"),
    "Texas":          ("USA","TX"),  "Mississippi":  ("USA","MS"),
    "Alabama":        ("USA","AL"),  "Massachusetts":("USA","MA"),
    "California":     ("USA","CA"),  "Florida":      ("USA","FL"),
    "Lagos":          ("NGA","LA"),  "Zamfara":      ("NGA","ZM"),
    "Kano":           ("NGA","KN"),  "Abuja":        ("NGA","FC"),
    "Sao Paulo":      ("BRA","SP"),  "Para":         ("BRA","PA"),
    "Maranhao":       ("BRA","MA"),  "Rio de Janeiro":("BRA","RJ"),
    "Mexico City":    ("MEX","CDMX"),"Guerrero":     ("MEX","GR"),
    "Punjab Pakistan":("PAK","PJ"),  "Balochistan":  ("PAK","BL"),
    "Afghanistan":    ("AFG",None),  "Pakistan":     ("PAK",None),
    "Bangladesh":     ("BGD",None),  "Nigeria":      ("NGA",None),
    "Saudi Arabia":   ("SAU",None),  "Iran":         ("IRN",None),
    "Mexico":         ("MEX",None),  "Brazil":       ("BRA",None),
    "India":          ("IND",None),  "Kenya":        ("KEN",None),
    "Ethiopia":       ("ETH",None),  "South Africa": ("ZAF",None),
    "Indonesia":      ("IDN",None),  "Philippines":  ("PHL",None),
    "Colombia":       ("COL",None),  "Nepal":        ("NPL",None),
    "Sri Lanka":      ("LKA",None),  "Ghana":        ("GHA",None),
}
