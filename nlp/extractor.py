import spacy
import re

nlp = spacy.load("en_core_web_sm")



NOISE_KEYWORDS = [
    "world cup", "cricket match", "football match", "ronaldo", "match result", "toss",
    "diplomacy", "bilateral", "summit meeting", "parliament session", "senate session",
    "budget announcement", "stock exchange", "economy report", "weather forecast",
    "load shedding schedule", "inflation rate", "dollar rate", "rupee rate",
    "imf loan", "petrol price", "price hike announcement", "trade agreement",
    "foreign visit", "state visit", "pm meets", "president meets",
    "inaugurated", "inauguration", "ribbon cutting", "foundation stone",
    "scholarship", "admission", "exam results", "university ranking"
]
CRIME_TYPE_MAP = {
    "murder": [
        "murder", "murdered", "kills", "killed", "killing", "shot dead", "dead body",
        "found dead", "hanged", "body found", "body dumped", "dumped body", "corpse",
        "slain", "slaughter", "beheaded", "stabbed to death", "strangled", "poisoned",
        "burnt alive", "honor killing", "karo kari", "qatl", "dead", "dies", "died",
        "death", "fatally", "fatal", "lifeless body", "unidentified body", "mutilated"
    ],
    "robbery": [
        "robbery", "robbed", "rob", "dacoity", "daaku", "dacoit", "looted", "loot",
        "armed robbery", "bank robbery", "mugging", "mugged", "snatching", "snatched",
        "carjacking", "carjacked", "hold up", "holdup", "heist", "plunder", "plundered",
        "looters", "armed men looted", "cash snatched", "mobile snatched", "gold snatched",
        "jewellery snatched", "vehicle snatched", "bike snatched"
    ],
    "theft": [
        "theft", "stolen", "steal", "stole", "burglary", "burglar", "broke into",
        "house break-in", "shoplifting", "pickpocket", "pickpocketing", "pilferage",
        "embezzlement", "fraud", "scam", "swindled", "cheated", "forgery", "counterfeit",
        "misappropriation", "corruption", "bribery", "bribe", "took bribes",
        "vehicle theft", "car theft", "motorcycle theft", "cattle theft", "livestock stolen"
    ],
    "kidnapping": [
        "kidnapping", "kidnapped", "kidnap", "abducted", "abduction", "abduct",
        "missing person", "gone missing", "disappeared", "forced disappearance",
        "enforced disappearance", "taken hostage", "hostage", "ransom", "ransom demand",
        "child abduction", "woman abducted", "girl abducted", "taken away forcibly",
        "recovered", "traced", "found after missing"
    ],
    "assault": [
        "assault", "assaulted", "attacked", "attack", "beaten", "beat up", "thrashed",
        "torture", "tortured", "torturing", "acid attack", "acid thrown", "acid hurled",
        "stabbed", "stabbing", "knifed", "slashed", "injured", "injuries", "wounded",
        "grievously hurt", "critical condition after attack", "mob beating", "lynched",
        "pelted", "stoned", "hit with", "baton charge", "police torture", "custodial torture",
        "domestic violence", "child abuse", "elder abuse", "harassment at workplace"
    ],
    "rape": [
        "rape", "raped", "gang rape", "gang-raped", "sexual assault", "sexually assaulted",
        "molested", "molestation", "sexual abuse", "sexually abused", "sodomy",
        "sexual harassment", "harassment", "eve teasing", "indecent assault",
        "obscene act", "obscenity", "sexual violence", "survivor", "victim of assault",
        "child sexual abuse", "csa", "minor abused"
    ],
    "arrest": [
        "arrested", "arrest", "nabbed", "detained", "detention", "caught", "apprehended",
        "remand", "physical remand", "judicial remand", "booked", "case registered",
        "fir registered", "fir lodged", "challan", "sentenced", "conviction", "convicted",
        "jailed", "imprisonment", "behind bars", "in custody", "taken into custody",
        "handed over to police", "police action", "crackdown", "rounded up", "raid",
        "raided", "operation", "anti-crime operation", "police recovered"
    ],
    "firing": [
        "firing", "gunshot", "gunfire", "shot", "shots fired", "bullet", "bullets",
        "armed", "blast", "blasts", "bomb", "bombing", "explosion", "exploded",
        "suicide bombing", "suicide attack", "ied", "improvised explosive",
        "landmine", "mortar", "rocket attack", "grenade", "grenade attack",
        "target killing", "targeted", "drive-by shooting", "aerial firing",
        "celebratory firing", "stray bullet", "crossfire", "exchange of fire",
        "encounter", "shootout", "gunfight", "armed clash", "gun battle"
    ],
    "terrorism": [
        "terrorist", "terrorists", "terrorism", "ibo", "intelligence based operation",
        "intelligence operation", "suicide bomber", "suicide attacker", "militant",
        "militants", "extremist", "extremists", "insurgent", "insurgents",
        "banned outfit", "banned organization", "ttp", "bnla", "bla", "bra",
        "daesh", "isis", "al qaeda", "fidayeen", "fidai", "terror attack",
        "terrorist attack", "counter terrorism", "ctd", "rangers operation",
        "military operation", "zarb e azb", "radd ul fasaad"
    ],
    "kidnapping_for_ransom": [
        "ransom", "ransom demand", "ransom paid", "released after ransom",
        "businessmen kidnapped", "trader kidnapped", "child kidnapped for ransom"
    ],
    "drug": [
        "drugs", "drug trafficking", "narcotics", "heroin", "cocaine", "hashish",
        "charas", "ice drug", "crystal meth", "smuggling", "drug smuggler",
        "drug peddler", "drug dealer", "drug recovered", "drug haul", "contraband",
        "excise", "anti narcotics", "anf", "drug bust"
    ],
    "accident": [
        "road accident", "traffic accident", "car accident", "vehicle accident",
        "collision", "crashed", "crash", "overturned", "fell into", "drowned",
        "electrocuted", "electrocution", "fire incident", "building collapse",
        "roof collapse", "wall collapse", "stampede", "train accident",
        "bus accident", "hit and run"
    ],
    "violence": [
        "violence", "violent", "riot", "rioting", "clash", "clashes", "mob",
        "mob attack", "lynching", "lynched", "sectarian violence", "ethnic violence",
        "political violence", "land dispute", "property dispute", "water dispute",
        "tribal clash", "armed clash", "skirmish", "unrest", "turmoil"
    ],
    "missing": [
        "missing", "gone missing", "disappeared", "whereabouts unknown",
        "not found", "search operation", "traced", "missing child", "missing woman",
        "missing person report"
    ],
    "property_crime": [
        "arson", "set on fire", "torched", "vandalism", "vandalized", "damaged property",
        "encroachment", "illegal construction", "bulldozed", "demolition"
    ],
    "cybercrime": [
        "cybercrime", "cyber crime", "hacked", "hacking", "online fraud",
        "social media blackmail", "blackmail", "extortion", "sextortion",
        "fake account", "identity theft", "phishing", "data breach", "pta"
    ],
}

PAKISTAN_LOCATIONS = [
    "karachi", "lahore", "islamabad", "rawalpindi", "peshawar",
    "quetta", "multan", "faisalabad", "hyderabad", "sialkot",
    "sargodha", "bahawalpur", "gujranwala", "abbottabad", "mardan",
    "sukkur", "larkana", "dera ghazi khan", "gujrat", "kasur",
    "sahiwal", "okara", "jhang", "sheikhupura", "nawabshah",
    "mirpur", "muzaffarabad", "gilgit", "dera ismail khan",
    "kohat", "bannu", "swat", "turbat", "gwadar", "jacobabad",
    "khuzdar", "chaman", "mingora", "rahim yar khan", "attock",
    "chakwal", "jhelum", "mianwali", "khushab", "narowal",
    "hafizabad", "chiniot", "toba tek singh", "vehari", "khanewal",
    "muzaffargarh", "bahawalnagar", "sadiqabad", "shikarpur",
    "dadu", "jamshoro", "thatta", "badin", "mirpurkhas",
    "umerkot", "sanghar", "naushahro feroze", "khairpur", "ghotki",
    "kashmore", "kandhkot", "sibi", "ziarat", "loralai", "zhob",
    "gulberg", "model town", "johar town", "dha lahore", "bahria town lahore",
    "garden town", "iqbal town", "township", "shadman", "faisal town",
    "wapda town", "cavalry ground", "cantt lahore", "shahdara", "raiwind",
    "clifton", "defence karachi", "dha karachi", "gulshan", "nazimabad",
    "north nazimabad", "korangi", "landhi", "malir", "orangi",
    "saddar karachi", "kemari", "lyari", "baldia", "shah faisal",
    "federal b area", "north karachi", "surjani",
    "f-6", "f-7", "f-8", "f-10", "f-11", "g-6", "g-7", "g-8",
    "g-9", "g-10", "g-11", "i-8", "i-9", "i-10", "e-7", "e-11",
    "blue area", "hayatabad", "university town", "saddar peshawar",
    "mansehra", "haripur", "taxila", "wah cantt", "murree",
]

BAD_LOCATIONS = {
    "pakistan", "punjab", "sindh", "kpk", "balochistan",
    "khyber pakhtunkhwa", "gilgit baltistan", "azad kashmir",
    "unknown", "city", "area", "district", "province"
}

WEAPONS = [
    # Firearms
    "pistol", "gun", "guns", "rifle", "rifles", "firearm", "firearms",
    "revolver", "shotgun", "carbine", "musket", "airgun", "air gun",
    "kalashnikov", "ak-47", "ak47", "g3", "mp5", "m16", "smg",
    "submachine gun", "machine gun", "automatic weapon", "semi-automatic",
    "double barrel", "single barrel", "licensed weapon", "unlicensed weapon",
    "illegal weapon", "country-made pistol", "desi katta", "katta",
    
    # Ammunition
    "bullet", "bullets", "cartridge", "cartridges", "shell", "shells",
    "magazine", "rounds", "ammunition", "ammo", "fired upon",
    
    # Explosives
    "bomb", "bombs", "explosion", "explosive", "explosives",
    "grenade", "grenades", "ied", "landmine", "landmines",
    "mortar", "mortar shell", "rocket", "rpg", "suicide vest",
    "pipe bomb", "time bomb", "car bomb", "roadside bomb",
    "hand grenade", "improvised explosive device",
    
    # Bladed weapons
    "knife", "knives", "blade", "blades", "dagger", "sword",
    "axe", "hatchet", "cleaver", "razor", "sharp object",
    "sharp weapon", "sharp-edged weapon", "cutter", "box cutter",
    "kirpan", "khanjar", "machete",
    
    # Blunt weapons
    "stick", "sticks", "baton", "batons", "rod", "rods", "iron rod",
    "wooden stick", "club", "hammer", "wrench", "brick", "stone",
    "bat", "cricket bat", "lathi", "danda",
    
    # Chemical/other
    "acid", "acid bottle", "chemical", "poison", "poisoned",
    "toxic", "gas", "tear gas", "pepper spray",
    
    # Fire
    "fire", "petrol bomb", "molotov", "set ablaze", "burnt",
    "torched", "kerosene", "inflammable",
    
    # Vehicles as weapons
    "ran over", "run over", "hit by vehicle", "vehicle used",
    "car rammed", "rammed into",
    
    # General
    "weapon", "weapons", "armed", "arms", "deadly weapon",
    "lethal weapon", "dangerous weapon", "recovered weapon",
    "seized weapon", "illegal arms"
]

VICTIM_PATTERNS = [
    r"(\d+)\s+(?:people|persons?|men|women|children|kids|students?|officers?)\s+(?:killed|injured|dead|wounded|abducted|raped|arrested)",
    r"(?:killed|injured|dead|wounded)\s+(\d+)",
]

def is_crime(title):
    title_lower = title.lower()
    has_crime = any(
        kw in title_lower
        for keywords in CRIME_TYPE_MAP.values()
        for kw in keywords
    )
    has_noise = any(kw in title_lower for kw in NOISE_KEYWORDS)
    return has_crime and not has_noise

def classify_crime(title):
    title_lower = title.lower()
    for crime_type, keywords in CRIME_TYPE_MAP.items():
        if any(kw in title_lower for kw in keywords):
            return crime_type
    return "other"

def extract_location(title, content=""):
    text_lower = f"{title} {content}".lower()
    for city in PAKISTAN_LOCATIONS:
        if city in text_lower:
            return city.title()
    doc = nlp(title[:500])
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"] and ent.text.lower() in PAKISTAN_LOCATIONS:
            return ent.text
    return None

def extract_entities(title, content=""):
    text = f"{title} {content}".lower()
    found_weapons = [w for w in WEAPONS if w in text]
    victim_count = None
    for pattern in VICTIM_PATTERNS:
        match = re.search(pattern, text)
        if match:
            try:
                victim_count = int(match.group(1))
                break
            except:
                pass
    victim_gender = None
    if any(w in text for w in ["woman", "women", "girl", "female", "lady"]):
        victim_gender = "female"
    elif any(w in text for w in ["man", "men", "boy", "male"]):
        victim_gender = "male"
    return {
        "weapons": found_weapons[:3],
        "victim_count": victim_count,
        "victim_gender": victim_gender,
    }

def extract_info(article):
    title = article["title"]
    content = article.get("content", "")

    if not is_crime(title):
        return None

    location = extract_location(title, content)

    if location and location.lower() in BAD_LOCATIONS:
        location = None

    source_city = article.get("source_city", "")
    if not location and source_city and source_city.lower() not in BAD_LOCATIONS:
        location = source_city.title()

    if not location:
        return None

    entities = extract_entities(title, content)

    return {
        **article,
        "crime_type": classify_crime(title),
        "location_name": location,
        **entities
    }