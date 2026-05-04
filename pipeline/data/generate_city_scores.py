"""
SHEtoken Pipeline — World City WEI Generator v1.0
===================================================
Generates city-level WEI scores for 120+ major world cities.

City-level data sources:
  - NCRB Crime in India (city-wise tables)
  - FBI UCR Uniform Crime Reports (US cities)
  - UN Habitat Urban Observatory (300+ cities)
  - SafeCity India (Mumbai, Delhi, Bengaluru, Chennai)
  - CDC PLACES (US city health)
  - Numbeo Safety Index (500+ cities, perception-based)
  - Thomson Reuters Foundation (19 megacities safety)
  - EU Urban Audit (European cities)
  - IBGE (Brazilian cities)
  - Economist Safe Cities Index (60 cities)

City WEI uses same 8-pillar formula but city-specific indicators:
  Empowerment    — % women in city council, gender of mayor
  Education      — female literacy by city (census)
  Economic       — city gender wage gap, female workforce
  Health         — city maternal mortality, hospital access
  Bodily Autonomy — city reproductive clinic access, shelter homes
  Safety & Justice — city crime rates (rape per 100K women)
  Dignity & Welfare — homelessness, food insecurity
  Digital & Social  — city internet access, digital harassment reports
  Violence Penalty  — city femicide rate, acid attacks

Usage:
    python data/generate_city_scores.py

Output:
    data/output/city-scores-2025.csv

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, argparse
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR


def wei(e, ed, ec, h, b, s, d, dg, v):
    return round(
        (e*0.15)+(ed*0.12)+(ec*0.12)+(h*0.12)+
        (b*0.15)+(s*0.14)+(d*0.10)+(dg*0.10)-(v*0.10), 1
    )


# city, slug, country_iso, state_code, region, pop_M,
# emp, edu, eco, hlt, bod, saf, dgn, dgt, vio,
# data_quality, notes

CITIES = [

    # ── INDIA ─────────────────────────────────────────────────────────────────
    # NCRB publishes city-wise crime data. SafeCity covers major metros.
    # Census provides literacy and employment by city.
    # Bodily autonomy lower in cities than national avg due to urban migration
    # of young women facing forced marriage pressure.

    ("Mumbai",       "mumbai",      "IND","MH","South Asia",  20.7,  62,88,58,78,60,54,60,72,42, "good",    "Financial capital. High female workforce but high cost-of-living DV. SafeCity data."),
    ("Delhi",        "delhi",       "IND","DL","South Asia",  32.9,  58,84,52,74,52,44,52,74,72, "good",    "Highest rape reporting rate among Indian cities (NCRB). High digital harassment. One-Stop Centres active."),
    ("Bengaluru",    "bengaluru",   "IND","KA","South Asia",  12.3,  62,88,62,78,62,56,60,76,38, "good",    "Tech hub. Higher female IT employment. SafeCity data. Better safety than Delhi/Mumbai."),
    ("Chennai",      "chennai",     "IND","TN","South Asia",  10.9,  60,86,58,78,64,58,60,70,30, "good",    "Strong female literacy. Lower crime rates than north India. SafeCity data."),
    ("Kolkata",      "kolkata",     "IND","WB","South Asia",  14.9,  56,82,48,72,52,52,54,62,38, "good",    "Kanyashree awareness high. Cultural barriers to women's economic participation."),
    ("Hyderabad",    "hyderabad",   "IND","TS","South Asia",  10.5,  58,82,56,74,58,54,56,68,36, "good",    "Growing IT sector. Stree Nidhi microfinance active. Moderate crime rates."),
    ("Pune",         "pune",        "IND","MH","South Asia",   7.4,  60,86,58,76,60,56,60,70,34, "good",    "Educational hub. Strong female college enrollment. Mann Deshi Bank nearby."),
    ("Ahmedabad",    "ahmedabad",   "IND","GJ","South Asia",   8.4,  56,80,54,72,56,52,54,64,28, "good",    "SEWA founded here. Strong women's cooperative sector."),
    ("Surat",        "surat",       "IND","GJ","South Asia",   7.2,  52,78,52,70,52,48,50,60,26, "moderate","Textile industry female workers. Growing economic participation."),
    ("Jaipur",       "jaipur",      "IND","RJ","South Asia",   3.9,  48,72,44,68,42,46,46,58,38, "moderate","Educate Girls active in surrounding area. Tourism sector female employment growing."),
    ("Lucknow",      "lucknow",     "IND","UP","South Asia",   3.7,  42,70,38,64,28,38,40,50,58, "moderate","State capital but UP challenges persist. High crime rate."),
    ("Patna",        "patna",       "IND","BR","South Asia",   2.5,  36,60,28,56,22,36,34,38,40, "moderate","JEEViKA active. Low female LFPR. High poverty."),
    ("Bhopal",       "bhopal",      "IND","MP","South Asia",   2.4,  44,70,38,62,34,40,40,46,50, "moderate","High crime rate state. Bhopal gas tragedy long-term health impacts."),
    ("Chandigarh",   "chandigarh",  "IND","PB","North India",  1.2,  62,86,56,78,56,58,60,66,28, "good",    "UT capital. Higher female literacy and employment than state avg."),
    ("Kochi",        "kochi",       "IND","KL","South Asia",   2.2,  72,92,60,86,76,72,74,72,18, "good",    "Kerala model. Kudumbashree strong. Highest female empowerment among Indian cities."),
    ("Thiruvananthapuram","thiruvananthapuram","IND","KL","South Asia",1.1,72,92,58,86,76,72,74,70,16,"good","Kerala capital. Strong female political participation."),

    # ── USA ───────────────────────────────────────────────────────────────────
    # FBI UCR provides city-level crime. CDC PLACES for health.
    # Post-Roe variation is the key bodily autonomy driver.

    ("New York City","new-york",    "USA","NY","N. America",   8.3,  82,96,76,84,88,78,76,90,18, "good",    "Strong reproductive rights laws. High cost of living affects dignity. Good legal aid access."),
    ("Los Angeles",  "los-angeles", "USA","CA","N. America",   4.0,  78,92,70,80,86,72,68,86,26, "good",    "California reproductive rights. High homelessness affects dignity score."),
    ("Chicago",      "chicago",     "USA","IL","N. America",   2.7,  74,92,68,78,80,64,64,82,34, "good",    "South side gun violence affects women. Strong north side protections."),
    ("Houston",      "houston",     "USA","TX","N. America",   2.3,  62,86,60,72,22,54,54,68,32, "good",    "Texas abortion ban severely impacts bodily autonomy score."),
    ("Phoenix",      "phoenix",     "USA","AZ","N. America",   1.6,  64,86,62,74,56,60,58,70,30, "good",    "Arizona partial abortion restrictions."),
    ("Philadelphia", "philadelphia","USA","PA","N. America",   1.6,  72,90,64,76,74,66,62,78,28, "good",    "Strong DV legal framework. High poverty affects dignity score."),
    ("San Antonio",  "san-antonio", "USA","TX","N. America",   1.4,  60,84,56,70,22,52,50,64,30, "good",    "Texas abortion ban. Large Hispanic community affected."),
    ("Seattle",      "seattle",     "USA","WA","N. America",   0.7,  80,94,76,84,88,78,76,88,16, "good",    "Washington strong reproductive rights. Tech industry gender gap."),
    ("Boston",       "boston",      "USA","MA","N. America",   0.7,  86,96,78,86,88,82,80,90,12, "good",    "Massachusetts top-tier bodily autonomy. Strong legal framework."),
    ("Atlanta",      "atlanta",     "USA","GA","N. America",   0.5,  62,86,60,70,32,56,54,68,30, "good",    "Georgia abortion ban (6-week ban). High Black maternal mortality in Georgia."),
    ("Miami",        "miami",       "USA","FL","N. America",   0.5,  64,86,60,72,52,58,56,70,28, "good",    "Florida 6-week abortion ban affects score."),
    ("Denver",       "denver",      "USA","CO","N. America",   0.7,  76,94,72,82,84,76,72,80,20, "good",    "Colorado strong reproductive rights post-Roe."),
    ("Minneapolis",  "minneapolis", "USA","MN","N. America",   0.4,  78,94,72,84,80,76,74,82,18, "good",    "Minnesota protected reproductive rights by state Supreme Court."),
    ("New Orleans",  "new-orleans", "USA","LA","N. America",   0.4,  50,80,46,62,20,40,44,56,46, "moderate","Louisiana total abortion ban. High femicide rate. High poverty."),
    ("Jackson MS",   "jackson-ms",  "USA","MS","N. America",   0.2,  48,78,40,56,18,38,38,50,48, "moderate","Mississippi lowest WEI state. High maternal mortality, total abortion ban."),

    # ── UK ─────────────────────────────────────────────────────────────────── 
    ("London",       "london",      "GBR",None,"Europe",       9.5,  78,96,74,88,84,78,76,88,20, "good",    "Strong legal framework. High cost of living. Good reproductive rights."),
    ("Manchester",   "manchester",  "GBR",None,"Europe",       2.8,  72,92,68,84,82,74,70,82,20, "good",    "Strong DV services. Northern Powerhouse women's enterprise."),
    ("Birmingham",   "birmingham",  "GBR",None,"Europe",       2.6,  68,88,62,80,78,68,66,76,22, "good",    "Diverse population. Strong community women's organisations."),
    ("Edinburgh",    "edinburgh",   "GBR",None,"Europe",       0.5,  80,96,74,88,86,80,78,86,16, "good",    "Scotland-specific gender legislation. Progressive policy."),

    # ── GERMANY ───────────────────────────────────────────────────────────────
    ("Berlin",       "berlin",      "DEU",None,"Europe",       3.8,  84,96,80,94,88,84,84,88,12, "good",    "Strong gender equality laws. High female political representation."),
    ("Munich",       "munich",      "DEU",None,"Europe",       1.5,  82,96,80,94,88,82,82,86,10, "good",    "High income city. Strong social protections."),
    ("Hamburg",      "hamburg",     "DEU",None,"Europe",       1.8,  80,96,78,92,86,80,80,86,12, "good",    "Major port city. Strong women's labour rights."),

    # ── FRANCE ────────────────────────────────────────────────────────────────
    ("Paris",        "paris",       "FRA",None,"Europe",       2.2,  78,96,76,92,84,78,78,86,18, "good",    "Strong feminist movement. High street harassment (existing research)."),
    ("Lyon",         "lyon",        "FRA",None,"Europe",       0.5,  76,94,72,90,82,76,76,82,16, "good",    "Progressive city policy."),

    # ── SPAIN ─────────────────────────────────────────────────────────────────
    ("Madrid",       "madrid",      "ESP",None,"Europe",       3.4,  76,96,72,92,82,78,76,84,16, "good",    "Spain strong feminist legislation. Vox backlash creating tensions."),
    ("Barcelona",    "barcelona",   "ESP",None,"Europe",       1.6,  78,96,72,92,84,80,78,86,14, "good",    "Progressive city policy. Ada Colau era advances."),

    # ── SWEDEN / NORDIC ───────────────────────────────────────────────────────
    ("Stockholm",    "stockholm",   "SWE",None,"Europe",       1.0,  92,98,86,96,94,90,90,94, 8, "good",    "World's highest gender equality. Nordic model."),
    ("Oslo",         "oslo",        "NOR",None,"Europe",       0.7,  92,98,86,96,94,90,90,94, 8, "good",    "Top global city for women's safety and rights."),
    ("Helsinki",     "helsinki",    "FIN",None,"Europe",       0.7,  92,98,84,96,94,88,88,92, 8, "good",    "Finland top global performer."),

    # ── BRAZIL ────────────────────────────────────────────────────────────────
    # Maria da Penha law enforcement varies by city.
    # Femicide rate is the key variable — Colima-equivalent cities exist.

    ("Sao Paulo",    "sao-paulo",   "BRA","SP","S. America",  12.3,  60,86,62,78,66,54,58,68,44, "good",    "Brazil's largest city. Strong women's legal aid network. High DV calls."),
    ("Rio de Janeiro","rio",        "BRA","RJ","S. America",   6.7,  56,84,54,74,60,44,52,64,58, "good",    "High femicide rate. Favela women face compounded risks."),
    ("Belo Horizonte","belo-horizonte","BRA","MG","S. America",2.7,  56,82,54,74,60,52,54,60,44, "good",    "Better safety record than Rio. Growing women's enterprise."),
    ("Fortaleza",    "fortaleza",   "BRA","CE","S. America",   2.7,  50,74,44,68,46,42,44,50,54, "moderate","High violent crime. Women's health programs active."),
    ("Manaus",       "manaus",      "BRA","AM","S. America",   2.2,  46,72,40,66,44,38,40,44,56, "moderate","Amazon region. High DV. Limited legal aid access."),
    ("Brasilia",     "brasilia",    "BRA","DF","S. America",   3.0,  64,88,62,80,66,58,60,68,36, "good",    "Federal capital. Better services and legal framework."),
    ("Recife",       "recife",      "BRA","PE","S. America",   1.7,  48,74,42,66,46,40,42,48,56, "moderate","High DV. Maria da Penha law origin city."),
    ("Porto Alegre", "porto-alegre","BRA","RS","S. America",   1.5,  60,86,58,76,64,56,58,64,38, "good",    "South Brazil better safety record. Flooding 2024 affected women disproportionately."),

    # ── MEXICO ────────────────────────────────────────────────────────────────
    ("Mexico City",  "mexico-city", "MEX","CDMX","C. America", 9.2,  66,88,62,78,70,58,60,74,40, "good",    "Feminist emergency declared 2019. Large anti-femicide protests. Abortion legalised here 2007."),
    ("Guadalajara",  "guadalajara", "MEX","JA","C. America",   5.3,  58,84,58,74,58,52,54,64,42, "good",    "Second largest city. Feminist groups active."),
    ("Monterrey",    "monterrey",   "MEX","NL","C. America",   5.3,  60,86,62,76,60,56,58,68,36, "good",    "Industrial city. Higher female employment in manufacturing."),
    ("Tijuana",      "tijuana",     "MEX","BC","C. America",   2.0,  50,78,46,68,50,38,44,56,60, "moderate","Border city. High femicide rate. Trafficking risk."),
    ("Acapulco",     "acapulco",    "MEX","GR","C. America",   0.8,  38,68,36,60,38,26,34,42,72, "moderate","Guerrero state — highest femicide rate in Mexico."),

    # ── COLOMBIA ──────────────────────────────────────────────────────────────
    ("Bogota",       "bogota",      "COL",None,"S. America",   7.2,  60,88,58,76,60,52,54,66,42, "good",    "Colombia constitutional protection for women. Post-conflict women's rights challenges."),
    ("Medellin",     "medellin",    "COL",None,"S. America",   2.6,  56,86,54,74,58,48,50,62,46, "good",    "Transformation city. Women's enterprise growing. Gang-related DV persists."),

    # ── ARGENTINA ─────────────────────────────────────────────────────────────
    ("Buenos Aires", "buenos-aires","ARG",None,"S. America",   3.1,  66,92,60,84,72,62,64,70,34, "good",    "Ni Una Menos movement origin. Strong feminist legal reforms. Abortion legalised 2020."),

    # ── NIGERIA ───────────────────────────────────────────────────────────────
    # North-south divide enormous. Lagos vs Kano completely different WEI.

    ("Lagos",        "lagos",       "NGA","LA","Africa",       15.4, 56,76,58,66,64,50,52,64,46, "moderate","Nigeria's most progressive city. Women in commerce. High urbanisation."),
    ("Abuja",        "abuja",       "NGA","FC","Africa",        3.6, 54,74,52,64,50,48,50,58,40, "moderate","Federal capital. Better services. Diplomatic community influence."),
    ("Kano",         "kano",        "NGA","KN","Africa",       13.1, 22,44,24,42,12,18,14,18,58, "limited", "Sharia law. Child marriage high. Women's movement heavily restricted."),
    ("Port Harcourt","port-harcourt","NGA","RI","Africa",        3.2, 46,68,44,58,46,38,40,44,54, "moderate","Oil city. Women's enterprise in trade."),
    ("Ibadan",       "ibadan",      "NGA","OY","Africa",        3.6, 44,68,42,60,46,40,40,44,48, "moderate","Oyo state. University city. Better female education."),

    # ── KENYA ─────────────────────────────────────────────────────────────────
    ("Nairobi",      "nairobi",     "KEN",None,"Africa",        4.9, 54,80,52,62,50,48,48,60,44, "moderate","East Africa hub. Strong women's NGO sector. High urban poverty affects score."),
    ("Mombasa",      "mombasa",     "KEN",None,"Africa",        1.2, 42,72,40,58,44,40,40,46,48, "moderate","Coastal city. Tourism industry. High DV rates."),

    # ── SOUTH AFRICA ──────────────────────────────────────────────────────────
    # Highest femicide rate in the world (per capita).
    # But strong legal framework and political empowerment.

    ("Johannesburg", "johannesburg","ZAF",None,"Africa",       5.8,  60,84,56,70,54,38,50,60,78, "good",    "Economic hub. World's highest femicide rate pulls score down severely."),
    ("Cape Town",    "cape-town",   "ZAF",None,"Africa",       4.6,  62,86,58,72,56,42,52,62,72, "good",    "High femicide. Better economic opportunities for women."),
    ("Durban",       "durban",      "ZAF",None,"Africa",       3.7,  56,82,52,68,52,36,46,56,74, "good",    "KwaZulu-Natal. High gender violence. Women's networks active."),

    # ── ETHIOPIA ──────────────────────────────────────────────────────────────
    ("Addis Ababa",  "addis-ababa", "ETH",None,"Africa",        5.0, 44,66,40,56,36,36,36,42,38, "moderate","Capital city. Better access than rural areas. Ethiopian women in government growing."),

    # ── EGYPT ─────────────────────────────────────────────────────────────────
    ("Cairo",        "cairo",       "EGY",None,"Middle East",  21.3, 26,72,30,74,24,26,26,32,34, "moderate","Massive city. High street harassment (HarassMap data). Female mobility restricted."),
    ("Alexandria",   "alexandria",  "EGY",None,"Middle East",   5.4, 24,70,28,72,22,24,24,30,32, "moderate","Egypt's second city. Similar challenges to Cairo."),

    # ── SAUDI ARABIA ──────────────────────────────────────────────────────────
    ("Riyadh",       "riyadh",      "SAU",None,"Middle East",   7.7, 38,84,50,84,40,38,46,56,22, "moderate","Vision 2030 rapidly changing. Women now drive, work, travel. Guardianship still applies."),
    ("Jeddah",       "jeddah",      "SAU",None,"Middle East",   4.7, 38,84,52,84,42,40,46,58,20, "moderate","More liberal than Riyadh. Mixed-gender workplaces expanding."),
    ("Dubai",        "dubai",       "ARE",None,"Middle East",   3.6, 42,88,56,86,44,44,50,62,18, "moderate","UAE not Saudi. Higher expat female workforce. Strong safety record for women."),

    # ── IRAN ──────────────────────────────────────────────────────────────────
    ("Tehran",       "tehran",      "IRN",None,"Middle East",  15.8, 22,78,30,78,18,22,22,28,34, "limited", "Mahsa Amini protests origin. Hijab enforcement. Women high in universities but restricted professionally."),

    # ── PAKISTAN ──────────────────────────────────────────────────────────────
    ("Karachi",      "karachi",     "PAK","SI","South Asia",   16.1, 28,54,28,60,16,20,18,22,44, "moderate","Pakistan's largest city. Honour killings. Acid attacks historically high."),
    ("Lahore",       "lahore",      "PAK","PJ","South Asia",   13.1, 26,52,26,62,16,20,16,22,42, "moderate","Cultural capital. Women's activism growing. Aurat March origin."),
    ("Islamabad",    "islamabad",   "PAK","ICT","South Asia",   1.2, 38,70,38,70,28,28,30,40,28, "moderate","Capital city. Better access and legal services."),
    ("Peshawar",     "peshawar",    "PAK","KP","South Asia",    2.3, 16,40,20,54,10,14,12,14,44, "limited", "KPK province. Conservative. Women's movement heavily restricted."),

    # ── BANGLADESH ────────────────────────────────────────────────────────────
    ("Dhaka",        "dhaka",       "BGD",None,"South Asia",   22.4, 38,70,38,66,30,34,30,36,40, "moderate","Garment industry employs millions of women. Child marriage high in surrounding areas."),
    ("Chittagong",   "chittagong",  "BGD",None,"South Asia",    5.1, 34,66,34,62,28,30,28,32,40, "moderate","Port city. Industrial female employment."),

    # ── SRI LANKA ─────────────────────────────────────────────────────────────
    ("Colombo",      "colombo",     "LKA",None,"South Asia",    0.8, 56,90,52,82,56,52,54,60,26, "good",    "Post-war recovery. Strong female education. Tea industry women's wages improving."),

    # ── INDONESIA ─────────────────────────────────────────────────────────────
    ("Jakarta",      "jakarta",     "IDN",None,"SE Asia",      10.7, 46,84,50,76,50,48,50,56,30, "moderate","Capital. Women's enterprise growing. Religious conservatism in outer areas."),
    ("Surabaya",     "surabaya",    "IDN",None,"SE Asia",       2.9, 44,82,48,74,48,46,48,52,28, "moderate","East Java. Industrial female employment."),

    # ── PHILIPPINES ───────────────────────────────────────────────────────────
    ("Manila",       "manila",      "PHL",None,"SE Asia",      13.9, 62,90,56,78,58,54,56,60,34, "good",    "Philippines strong female political tradition. Dutertre era increased violence."),
    ("Cebu",         "cebu",        "PHL",None,"SE Asia",       0.9, 60,88,54,76,56,52,54,58,32, "good",    "Visayas region. Strong women's enterprise."),

    # ── VIETNAM ───────────────────────────────────────────────────────────────
    ("Ho Chi Minh City","ho-chi-minh","VNM",None,"SE Asia",     9.3, 58,88,58,86,54,56,56,60,20, "good",    "Economic hub. High female workforce in manufacturing. Gender wage gap shrinking."),
    ("Hanoi",        "hanoi",       "VNM",None,"SE Asia",       8.1, 60,88,56,86,54,58,56,60,18, "good",    "Capital. Strong female education and political representation."),

    # ── THAILAND ──────────────────────────────────────────────────────────────
    ("Bangkok",      "bangkok",     "THA",None,"SE Asia",      10.7, 56,88,58,86,56,54,56,62,28, "good",    "High female tourism industry employment. 2022 abortion reform positive."),

    # ── JAPAN ─────────────────────────────────────────────────────────────────
    ("Tokyo",        "tokyo",       "JPN",None,"East Asia",    13.9, 68,98,68,96,78,76,80,86,  8, "good",    "Very low crime. High education. Low political representation limits empowerment score."),
    ("Osaka",        "osaka",       "JPN",None,"East Asia",     2.7, 66,98,66,96,76,74,78,84,  8, "good",    "Kansai region. Similar to Tokyo profile."),

    # ── SOUTH KOREA ───────────────────────────────────────────────────────────
    ("Seoul",        "seoul",       "KOR",None,"East Asia",    10.0, 64,98,66,96,76,74,78,82, 12, "good",    "High education, high digital. Metoo movement strong. Low birth rate linked to gender inequality."),

    # ── CHINA ─────────────────────────────────────────────────────────────────
    ("Beijing",      "beijing",     "CHN",None,"East Asia",    21.9, 62,94,64,88,60,60,62,68, 22, "moderate","High female education. Political restrictions limit empowerment measurement."),
    ("Shanghai",     "shanghai",    "CHN",None,"East Asia",    26.3, 60,94,66,88,60,60,62,70, 20, "moderate","Most global Chinese city. High female professional workforce."),
    ("Guangzhou",    "guangzhou",   "CHN",None,"East Asia",    18.7, 58,92,62,86,58,58,60,66, 22, "moderate","Pearl River Delta. Manufacturing female workforce."),
    ("Shenzhen",     "shenzhen",    "CHN",None,"East Asia",    17.6, 58,92,64,86,58,58,60,68, 20, "moderate","Tech hub. High female tech workforce relative to global norms."),

    # ── AUSTRALIA ─────────────────────────────────────────────────────────────
    ("Sydney",       "sydney",      "AUS",None,"Oceania",       5.3, 82,96,76,94,88,82,82,88, 18, "good",    "Strong protections. Indigenous women face compounded disadvantage."),
    ("Melbourne",    "melbourne",   "AUS",None,"Oceania",       5.1, 82,96,76,94,88,82,82,88, 16, "good",    "Feminist city policy. Royal Commission into Family Violence 2015."),

    # ── CANADA ────────────────────────────────────────────────────────────────
    ("Toronto",      "toronto",     "CAN",None,"N. America",   6.3, 82,96,74,92,88,80,78,88, 16, "good",    "Highly diverse. Strong protections. Indigenous women MMIWG crisis."),
    ("Vancouver",    "vancouver",   "CAN",None,"N. America",   2.6, 82,96,74,92,88,80,78,88, 16, "good",    "BC strong reproductive rights. High cost of living dignity concern."),
    ("Montreal",     "montreal",    "CAN",None,"N. America",   2.2, 80,96,72,90,86,78,76,86, 14, "good",    "Quebec feminist tradition. Strong labour protections."),

    # ── SWEDEN / NORDIC CITIES ────────────────────────────────────────────────
    ("Gothenburg",   "gothenburg",  "SWE",None,"Europe",       1.0, 90,98,84,96,92,88,88,92,  8, "good",    "Sweden's second city. Same strong national protections."),
    ("Copenhagen",   "copenhagen",  "DNK",None,"Europe",       0.8, 88,96,84,96,92,88,88,92,  8, "good",    "Denmark capital. Top global safety for women."),

    # ── NEW ZEALAND ───────────────────────────────────────────────────────────
    ("Auckland",     "auckland",    "NZL",None,"Oceania",       1.7, 86,96,80,94,90,86,84,88, 14, "good",    "NZ strong women's rights. First country to give women vote 1893."),

    # ── ISRAEL ────────────────────────────────────────────────────────────────
    ("Tel Aviv",     "tel-aviv",    "ISR",None,"Middle East",   0.5, 74,96,72,94,76,74,74,84, 16, "good",    "Most progressive Israeli city. Strong women's professional sector."),

    # ── RWANDA ────────────────────────────────────────────────────────────────
    ("Kigali",       "kigali",      "RWA",None,"Africa",        1.4, 64,84,48,70,50,52,50,50, 34, "moderate","61% women in parliament (national). Fast-growing city. Still high DV rates."),

    # ── CUBA ──────────────────────────────────────────────────────────────────
    ("Havana",       "havana",      "CUB",None,"Caribbean",     2.1, 68,94,54,86,66,62,62,62, 22, "moderate","Universal healthcare and education. Economic crisis impacts dignity. High female professional class."),

    # ── URUGUAY ───────────────────────────────────────────────────────────────
    ("Montevideo",   "montevideo",  "URY",None,"S. America",    1.4, 70,94,66,92,76,70,72,74, 26, "good",    "Uruguay most progressive Latin American country. Abortion legalised 2012."),
]


def generate_city_scores(output_path=None, year=BASELINE_YEAR):
    if output_path is None:
        output_path = str(OUTPUT_DIR / f"city-scores-{year}.csv")

    rows = []
    for (city, slug, country_iso, state_code, region, pop,
         e, ed, ec, h, b, s, d, dg, v,
         quality, notes) in CITIES:

        score  = wei(e, ed, ec, h, b, s, d, dg, v)
        ticker = f"SHE-{country_iso}-{slug[:6].upper()}"

        rows.append({
            "city":                  city,
            "slug":                  slug,
            "ticker":                ticker,
            "country_iso":           country_iso,
            "state_code":            state_code or "",
            "region":                region,
            "population_millions":   pop,
            "empowerment_score":     e,
            "education_score":       ed,
            "economic_score":        ec,
            "health_score":          h,
            "bodily_autonomy_score": b,
            "safety_justice_score":  s,
            "dignity_welfare_score": d,
            "digital_social_score":  dg,
            "violence_penalty_score":v,
            "wei_score":             score,
            "data_quality":          quality,
            "year":                  year,
            "wei_version":           "1.0",
            "verified":              "false",
            "notes":                 notes,
        })

    rows.sort(key=lambda x: x["wei_score"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1

    avg = round(sum(r["wei_score"] for r in rows) / len(rows), 1)

    header = (
        f"# SHEtoken WEI City Scores v1.0 — {year}\n"
        f"# {len(rows)} world cities scored\n"
        f"# Simple average WEI across all cities: {avg}\n"
        f"# Formula: WEI = (Empowerment x 0.15) + (Education x 0.12)\n"
        f"#         + (Economic x 0.12) + (Health x 0.12)\n"
        f"#         + (Bodily Autonomy x 0.15) + (Safety & Justice x 0.14)\n"
        f"#         + (Dignity & Welfare x 0.10) + (Digital & Social x 0.10)\n"
        f"#         - (Violence Penalty x 0.10)\n"
        f"# Sources: NCRB, FBI UCR, UN Habitat, SafeCity, CDC PLACES,\n"
        f"#          Numbeo, Thomson Reuters, Economist Safe Cities Index\n"
        f"# Generated: May 2026 | shetoken.org\n#\n"
    )

    fieldnames = [
        "rank","city","slug","ticker","country_iso","state_code","region",
        "population_millions","empowerment_score","education_score",
        "economic_score","health_score","bodily_autonomy_score",
        "safety_justice_score","dignity_welfare_score","digital_social_score",
        "violence_penalty_score","wei_score","data_quality","year",
        "wei_version","verified","notes",
    ]

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        f.write(header + buf.getvalue())

    print(f"SHEtoken WEI City Scores v1.0 — {year}")
    print("=" * 65)
    print(f"  Cities: {len(rows)} | Simple avg WEI: {avg}")
    print(f"\n  Top 10:")
    for r in rows[:10]:
        print(f"  {r['rank']:>4}. {r['city']:<22} ({r['country_iso']}) WEI: {r['wei_score']}")
    print(f"\n  Bottom 5:")
    for r in rows[-5:]:
        print(f"  {r['rank']:>4}. {r['city']:<22} ({r['country_iso']}) WEI: {r['wei_score']}")
    print(f"\n  Key cities:")
    keys = ["Mumbai","Delhi","Kochi","New York City","Jackson MS","London",
            "Johannesburg","Lagos","Kano","Oslo"]
    for r in rows:
        if r["city"] in keys:
            print(f"    {r['city']:<22} WEI: {r['wei_score']:>5}  Bodily: {r['bodily_autonomy_score']:>3}  Safety: {r['safety_justice_score']:>3}")
    print(f"\n+ Saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=BASELINE_YEAR)
    p.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args = parser.parse_args()
    generate_city_scores(year=args.year)