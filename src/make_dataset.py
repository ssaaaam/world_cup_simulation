import pandas as pd

def is_valid_tournament(row_match):
    tournament = row_match["tournament"]
    return any(t in tournament for t in valid_tournaments)

def get_confederation(team: str) -> str:
    return team_conf_dict.get(team, None)

def classify_match_attributes(comp_name):
    comp_name_lower = comp_name.lower()
    
    # Inicializamos la confederación como 'Other' por defecto
    confederation = 'Other'
    
    # ==========================================
    # 1. STAGE TYPE 
    # ==========================================
    if 'qualification' in comp_name_lower:
        stage = 'Qualification'
    elif comp_name in ['Friendly', 'Kirin Cup', 'FIFA Series']:
        stage = 'Other'
    else:
        stage = 'Tournament'
        
    # ==========================================
    # 2. COMPETITION TYPE & CONFEDERATION
    # ==========================================
    
    # 2.1 Mundial e Internacionales (Confederación: Other)
    if 'world cup' in comp_name_lower:
        competition = 'World_Cup'
        confederation = 'Other'
        
    elif comp_name in ['Confederations Cup', 'CONMEBOL–UEFA Cup of Champions']:
        competition = 'International_Cup'
        confederation = 'Other'

    # 2.2 Copas Continentales principales
    elif 'uefa euro' in comp_name_lower:
        competition = 'Continental_Cup'
        confederation = 'UEFA'
        
    elif 'copa américa' in comp_name_lower:
        competition = 'Continental_Cup'
        confederation = 'CONMEBOL'
        
    elif 'african cup of nations' in comp_name_lower:
        competition = 'Continental_Cup'
        confederation = 'CAF'
        
    elif 'afc asian cup' in comp_name_lower:
        competition = 'Continental_Cup'
        confederation = 'AFC'
        
    elif 'gold cup' in comp_name_lower:
        competition = 'Continental_Cup'
        confederation = 'CONCACAF'
        
    elif 'oceania nations cup' in comp_name_lower:
        competition = 'Continental_Cup'
        confederation = 'OFC'

    # 2.3 Amistosos
    elif comp_name in ['Friendly', 'Kirin Cup', 'FIFA Series']:
        competition = 'Friendlies'
        confederation = 'Other' # Los amistosos suelen ser intercontinentales

    # 2.4 Copas Secundarias (Nations Leagues, torneos regionales)
    else:
        competition = 'Secundary_Continental_Cup'
        # Detección de confederación para torneos secundarios
        if 'uefa' in comp_name_lower:
            confederation = 'UEFA'
        elif any(x in comp_name_lower for x in ['concacaf', 'uncaf', 'caribbean']):
            confederation = 'CONCACAF'
        elif any(x in comp_name_lower for x in ['afc', 'aff', 'eaff', 'saff', 'gulf', 'arab']):
            confederation = 'AFC'
        elif any(x in comp_name_lower for x in ['caf', 'cosafa', 'cecafa', 'nations championship']):
            confederation = 'CAF'
        else:
            confederation = 'Other'
        
    return pd.Series([stage, competition, confederation])

# Tier 1: Top competition
tier_1 = [
    'FIFA World Cup'
]

# Tier 2: Continetal Cups and Intercontintal Cup
tier_2 = [
    'UEFA Euro', 
    'Copa América', 
    'African Cup of Nations', 
    'AFC Asian Cup', 
    'Gold Cup', 
    'Oceania Nations Cup',
    'Confederations Cup', 
    'CONMEBOL–UEFA Cup of Champions' # La Finalissima
]

# Tier 3: Qualifications
tier_3 = [
    'FIFA World Cup qualification',
    'UEFA Euro qualification', 
    'Copa América qualification',
    'African Cup of Nations qualification', 
    'AFC Asian Cup qualification', 
    'Gold Cup qualification', 
    'Oceania Nations Cup qualification',
    'UEFA Nations League', 
    'CONCACAF Nations League', 
    'CONCACAF Nations League qualification'
]

# Tier 4: Regional tournaments
tier_4 = [
    'CFU Caribbean Cup', 'CFU Caribbean Cup qualification', # Caribe
    'UNCAF Cup', # Centroamérica
    'Gulf Cup', 'WAFF Championship', 'Arab Cup', # Mundo Árabe
    'AFF Championship', 'EAFF Championship', 'SAFF Cup', # Asia
    'COSAFA Cup', 'CECAFA Cup', 'African Nations Championship' # África
]

# Tier 5: Friendlies
tier_5 = [
    'Friendly', 
    # 'Kirin Cup', # Torneo amistoso clásico de Japón de mucho nivel
    # 'FIFA Series' # Nuevos amistosos intercontinentales de la FIFA
]

valid_tournaments = tier_1 + tier_2 + tier_3  + tier_5

team_conf_dict = {
    # UEFA (Europa y selecciones/regiones europeas)
    "Spain": "UEFA", "Faroe Islands": "UEFA", "Iceland": "UEFA", "Armenia": "UEFA", 
    "Cyprus": "UEFA", "Finland": "UEFA", "Romania": "UEFA", "Moldova": "UEFA", 
    "Norway": "UEFA", "Albania": "UEFA", "Georgia": "UEFA", "Latvia": "UEFA", 
    "Bulgaria": "UEFA", "Andorra": "UEFA", "Belgium": "UEFA", "Croatia": "UEFA", 
    "England": "UEFA", "Estonia": "UEFA", "France": "UEFA", "Greece": "UEFA", 
    "Hungary": "UEFA", "Republic of Ireland": "UEFA", "Israel": "UEFA", "Italy": "UEFA", 
    "Luxembourg": "UEFA", "North Macedonia": "UEFA", "Netherlands": "UEFA", "Turkey": "UEFA", 
    "Serbia": "UEFA", "Austria": "UEFA", "Bosnia and Herzegovina": "UEFA", 
    "Czech Republic": "UEFA", "Portugal": "UEFA", "Scotland": "UEFA", "Switzerland": "UEFA", 
    "Wales": "UEFA", "Kazakhstan": "UEFA", "Denmark": "UEFA", "Germany": "UEFA", 
    "Liechtenstein": "UEFA", "Lithuania": "UEFA", "Northern Ireland": "UEFA", 
    "Poland": "UEFA", "Russia": "UEFA", "San Marino": "UEFA", "Slovakia": "UEFA", 
    "Slovenia": "UEFA", "Sweden": "UEFA", "Azerbaijan": "UEFA", "Gibraltar": "UEFA", 
    "Belarus": "UEFA", "Ukraine": "UEFA", "Kosovo": "UEFA", "Montenegro": "UEFA", 
    "Yugoslavia": "UEFA", "Serbia and Montenegro": "UEFA", "Czechia": "UEFA",
    "Malta": "UEFA", # ¡Añadido!
    "Kernow": "UEFA", "Alderney": "UEFA", "Jersey": "UEFA", "Catalonia": "UEFA", 
    "Andalusia": "UEFA", "Basque Country": "UEFA", "Guernsey": "UEFA", "Greenland": "UEFA", 
    "Ynys Môn": "UEFA", "Isle of Wight": "UEFA", "Isle of Man": "UEFA", 
    "Saare County": "UEFA", "Orkney": "UEFA", "Rhodes": "UEFA", "Monaco": "UEFA", 
    "Canary Islands": "UEFA", "Frøya": "UEFA", "Shetland": "UEFA", "Gotland": "UEFA", 
    "Sark": "UEFA", "Åland Islands": "UEFA", "Occitania": "UEFA", "Chechnya": "UEFA", 
    "Western Isles": "UEFA", "Galicia": "UEFA", "Northern Cyprus": "UEFA", 
    "Republic of St. Pauli": "UEFA", "Găgăuzia": "UEFA", "Sápmi": "UEFA", "Silesia": "UEFA", 
    "Romani people": "UEFA", "Menorca": "UEFA", "Brittany": "UEFA", "Provence": "UEFA", 
    "Padania": "UEFA", "Corsica": "UEFA", "Gozo": "UEFA", "Sealand": "UEFA", 
    "Raetia": "UEFA", "Saugeais": "UEFA", "Ellan Vannin": "UEFA", "Vatican City": "UEFA", 
    "Franconia": "UEFA", "County of Nice": "UEFA", "Seborga": "UEFA", "Székely Land": "UEFA", 
    "Felvidék": "UEFA", "Hitra": "UEFA", "Luhansk PR": "UEFA", "Donetsk PR": "UEFA", 
    "Délvidék": "UEFA", "Kárpátalja": "UEFA", "Yorkshire": "UEFA", "Parishes of Jersey": "UEFA", 
    "Chameria": "UEFA", "Elba Island": "UEFA", "Ticino": "UEFA", "Crimea": "UEFA", 
    "Two Sicilies": "UEFA", "Cilento": "UEFA", "Surrey": "UEFA", "Madrid": "UEFA",

    # CONMEBOL (Sudamérica y regiones)
    "Chile": "CONMEBOL", "Colombia": "CONMEBOL", "Bolivia": "CONMEBOL", "Ecuador": "CONMEBOL", 
    "Venezuela": "CONMEBOL", "Argentina": "CONMEBOL", "Peru": "CONMEBOL", "Uruguay": "CONMEBOL", 
    "Paraguay": "CONMEBOL", "Brazil": "CONMEBOL", "Falkland Islands": "CONMEBOL", 
    "Mapuche": "CONMEBOL", "Aymara": "CONMEBOL", "Maule Sur": "CONMEBOL",

    # CONCACAF (Norte/Centroamérica, Caribe y regiones)
    "Trinidad and Tobago": "CONCACAF", "Guatemala": "CONCACAF", "Mexico": "CONCACAF", 
    "Bermuda": "CONCACAF", "Jamaica": "CONCACAF", "United States": "CONCACAF", "USA": "CONCACAF", 
    "Panama": "CONCACAF", "Costa Rica": "CONCACAF", "United States Virgin Islands": "CONCACAF", 
    "British Virgin Islands": "CONCACAF", "Saint Kitts and Nevis": "CONCACAF", 
    "Cayman Islands": "CONCACAF", "Honduras": "CONCACAF", "Dominican Republic": "CONCACAF", 
    "Haiti": "CONCACAF", "Canada": "CONCACAF", "Barbados": "CONCACAF", "Dominica": "CONCACAF", 
    "El Salvador": "CONCACAF", "Anguilla": "CONCACAF", "Cuba": "CONCACAF", 
    "Saint Lucia": "CONCACAF", "Saint Vincent and the Grenadines": "CONCACAF", 
    "Aruba": "CONCACAF", "Curaçao": "CONCACAF", "Grenada": "CONCACAF", "Puerto Rico": "CONCACAF", 
    "Bahamas": "CONCACAF", "Belize": "CONCACAF", "Montserrat": "CONCACAF", 
    "Nicaragua": "CONCACAF", "Suriname": "CONCACAF", "Turks and Caicos Islands": "CONCACAF", 
    "Guyana": "CONCACAF", "Saint Martin": "CONCACAF", "Martinique": "CONCACAF", 
    "Guadeloupe": "CONCACAF", "French Guiana": "CONCACAF", "Sint Maarten": "CONCACAF", 
    "Bonaire": "CONCACAF", "Saint Barthélemy": "CONCACAF", "Saint Pierre and Miquelon": "CONCACAF", 
    "Cascadia": "CONCACAF", "Antigua and Barbuda": "CONCACAF", # ¡Añadido!

    # AFC (Asia y regiones)
    "China PR": "AFC", "Qatar": "AFC", "Kuwait": "AFC", "Japan": "AFC", "Singapore": "AFC", 
    "Syria": "AFC", "Hong Kong": "AFC", "Nepal": "AFC", "Australia": "AFC", "Yemen": "AFC", 
    "Macau": "AFC", "Turkmenistan": "AFC", "Malaysia": "AFC", "Bhutan": "AFC", 
    "Lebanon": "AFC", "South Korea": "AFC", "Korea Republic": "AFC", # Nombres dobles
    "Oman": "AFC", "United Arab Emirates": "AFC", "Thailand": "AFC", "Uzbekistan": "AFC", 
    "Jordan": "AFC", "Bahrain": "AFC", "Maldives": "AFC", "Palestine": "AFC", "Myanmar": "AFC", 
    "Pakistan": "AFC", "Iran": "AFC", "IR Iran": "AFC", # Nombres dobles
    "Laos": "AFC", "Bangladesh": "AFC", "India": "AFC", "Kyrgyzstan": "AFC", "Iraq": "AFC", 
    "Saudi Arabia": "AFC", "Cambodia": "AFC", "Tajikistan": "AFC", "Mongolia": "AFC", 
    "Sri Lanka": "AFC", "Brunei": "AFC", "Taiwan": "AFC", "Chinese Taipei": "AFC", # Nombres dobles
    "North Korea": "AFC", "Korea DPR": "AFC", # Nombres dobles
    "Afghanistan": "AFC", "Guam": "AFC", "Timor-Leste": "AFC", "Northern Mariana Islands": "AFC", 
    "Vietnam": "AFC", "Philippines": "AFC", "Indonesia": "AFC", # ¡Añadido!
    "Tibet": "AFC", "Arameans Suryoye": "AFC", "Iraqi Kurdistan": "AFC", "Chagos Islands": "AFC", 
    "Abkhazia": "AFC", "Artsakh": "AFC", "South Ossetia": "AFC", "Panjab": "AFC", 
    "United Koreans in Japan": "AFC", "Western Armenia": "AFC", "Ryūkyū": "AFC", 
    "Hmong": "AFC", "West Papua": "AFC", "Tamil Eelam": "AFC",

    # CAF (África y regiones)
    "Egypt": "CAF", "Tunisia": "CAF", "Burkina Faso": "CAF", "Ivory Coast": "CAF", "Côte d'Ivoire": "CAF", # Nombres dobles
    "Senegal": "CAF", "Ghana": "CAF", "Morocco": "CAF", "Togo": "CAF", "Nigeria": "CAF", 
    "South Africa": "CAF", "DR Congo": "CAF", "Congo DR": "CAF", # Nombres dobles
    "Uganda": "CAF", "Cameroon": "CAF", 
    "Algeria": "CAF", "Zambia": "CAF", "Botswana": "CAF", "Ethiopia": "CAF", 
    "Zimbabwe": "CAF", "Namibia": "CAF", "Gambia": "CAF", "Tanzania": "CAF", 
    "Djibouti": "CAF", "Mauritania": "CAF", "Central African Republic": "CAF", 
    "Guinea-Bissau": "CAF", "Madagascar": "CAF", "Malawi": "CAF", "São Tomé and Príncipe": "CAF", 
    "Seychelles": "CAF", "Benin": "CAF", "Cape Verde": "CAF", "Chad": "CAF", 
    "Equatorial Guinea": "CAF", "Eritrea": "CAF", "Libya": "CAF", "Rwanda": "CAF", 
    "Sudan": "CAF", "Eswatini": "CAF", "Mali": "CAF", "Gabon": "CAF", "Kenya": "CAF", 
    "Sierra Leone": "CAF", "Angola": "CAF", "Congo": "CAF", "Guinea": "CAF", 
    "Liberia": "CAF", "Mozambique": "CAF", "Niger": "CAF", "Burundi": "CAF", 
    "Mauritius": "CAF", "Somalia": "CAF", "Comoros": "CAF", "South Sudan": "CAF", 
    "Zanzibar": "CAF", "Mayotte": "CAF", "Réunion": "CAF", "Western Sahara": "CAF", 
    "Darfur": "CAF", "Somaliland": "CAF", "Barawa": "CAF", "Matabeleland": "CAF", 
    "Kabylia": "CAF", "Saint Helena": "CAF", "Yoruba Nation": "CAF", "Biafra": "CAF", 
    "Ambazonia": "CAF", "Lesotho": "CAF", # Revisado

    # OFC (Oceanía y regiones)
    "New Zealand": "OFC", "Fiji": "OFC", "New Caledonia": "OFC", "Solomon Islands": "OFC", 
    "Vanuatu": "OFC", "Papua New Guinea": "OFC", "Tonga": "OFC", "American Samoa": "OFC", 
    "Tahiti": "OFC", "Samoa": "OFC", "Cook Islands": "OFC", "Tuvalu": "OFC", 
    "Micronesia": "OFC", "Kiribati": "OFC", "Marshall Islands": "OFC"
}

def make_dataset(input_path, output_path):
    datapath = input_path
    df = pd.read_csv(datapath)
    # Drop duplicates
    df = df.drop_duplicates(keep="first")

    # df[df.isna().any(axis=1)]
    # The NaNs values are from World Cup 2026, future matches 
    df = df.dropna()

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df = df[df["date"].dt.year >= 2000]

   # Rename cols
    df.rename(columns={
        "home_team": "home", 
        "away_team": "away",
    }, inplace=True)

    # Select specific tournaments
    df = df[df.apply(is_valid_tournament, axis=1)]

    # Rename some names

    diccionario_nombres = {
        'Ivory Coast': "Côte d'Ivoire",
        'DR Congo': 'Congo DR',
        'South Korea': 'Korea Republic',
        'North Korea': 'Korea DPR',
        'Taiwan': 'Chinese Taipei',
        'Iran': 'IR Iran',
        'United States': 'USA', 
        'Republic of Ireland': 'Republic of Ireland' 
    }
    df['home'] = df['home'].replace(diccionario_nombres)
    df['away'] = df['away'].replace(diccionario_nombres)
    df["country"] = df["country"].replace(diccionario_nombres)

    # Make new cols
    df["home_confederation"] = df["home"].apply(get_confederation)
    df["away_confederation"] = df["away"].apply(get_confederation)
    df = df.dropna(subset=["home_confederation", "away_confederation"])
    df["is_intercontinental"] = df.apply(lambda row: row["home_confederation"] != row["away_confederation"], axis=1)

    # df["is_intercontinental"] = df["is_intercontinental"]*1
    df["neutral"] = df["neutral"]*1

    df[["stage", "competition", "confederation"]] = df["tournament"].apply(classify_match_attributes)

    df.to_csv(output_path, index=False)