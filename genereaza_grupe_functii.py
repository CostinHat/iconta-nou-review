#!/usr/bin/env python3
"""Generator UNIC pentru GRUPE_FUNC din pagina Functionalitati (static/js/ecrane/login.js).
SURSA DE ADEVAR: FUNCTIONALITATI.csv (doar Stare=LIVE). Contine EXPLICIT regulile de
repartizare + excludere -> reproductibil, versionat.
Rulare:  python3 genereaza_grupe_functii.py           (dry-run: afiseaza totalurile)
         python3 genereaza_grupe_functii.py --scrie   (rescrie GRUPE_FUNC in login.js)
verificator_conformitate.py importa repartizeaza() ca sursa unica (nu duplica regulile)."""
import csv, re, json, os

_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DEFAULT = os.path.join(_DIR, "FUNCTIONALITATI.csv")
LOGIN_DEFAULT = os.path.join(_DIR, "static", "js", "ecrane", "login.js")

GRUPE = ["Contabilitate", "Fiscalitate", "Control fiscal", "Facturare si e-Factura",
         "Salarizare", "Stocuri, banca si casa", "Cabinet si portal client"]
ICON = {"Contabilitate": "brief", "Fiscalitate": "declaratii", "Control fiscal": "shield",
        "Facturare si e-Factura": "facturi", "Salarizare": "users",
        "Stocuri, banca si casa": "building", "Cabinet si portal client": "documente"}
COMASAT = ("Import la preluarea firmei", "Cabinet si portal client")

# --- REGULI DE REPARTIZARE (explicite, versionate) ---
# override manual de grupa (peste keyword), decis cu fondatorul
EXPLICIT = {"F164": "Control fiscal", "F108": "Cabinet si portal client", "F002": "Contabilitate",
    "F023": "Fiscalitate", "F025": "Fiscalitate", "F048": "Facturare si e-Factura",
    "F044": "Facturare si e-Factura", "F049": "Fiscalitate", "F057": "Contabilitate",
    "F062": "Cabinet si portal client", "F071": "Contabilitate", "F077": "Contabilitate",
    "F093": "Cabinet si portal client", "F102": "Facturare si e-Factura", "F114": "Cabinet si portal client",
    "F115": "Cabinet si portal client", "F144": "Contabilitate", "F145": "Contabilitate",
    "F147": "Cabinet si portal client", "F152": "Cabinet si portal client", "F028": "Fiscalitate",
    "F081": "Control fiscal", "F009": "Contabilitate", "F182": "Facturare si e-Factura",
    "F187": "Facturare si e-Factura",
    "F204": "Cabinet si portal client", "F205": "Cabinet si portal client"}
# cross-check-urile fiscale -> Control fiscal (NU Fiscalitate, desi numele incepe cu declaratia)
CROSS = {"F162", "F163", "F169", "F180", "F184"}
# EXCLUSE: infrastructura invizibila utilizatorului + variante superadmin + pagina insasi + cont gratuit inchis
EXCLUDE = {
    # infra invizibila
    "F060", "F083", "F092", "F104", "F106", "F110", "F111", "F112", "F113", "F116", "F119",
    "F165", "F170", "F177", "F178", "F179", "F189", "F201", "F202",
    # meta / superadmin / pagina insasi
    "F001", "F008", "F105", "F117", "F124", "F186", "F199", "F200", "F203",
    # mecanism intern de coliziune (nu capabilitate)
    "F185",
    # cont gratuit: palnie publica INCHISA (DECIZII 25.07) -> nu afisam functii inaccesibile
    "F153", "F160"}
# variantele "in contul gratuit" (se subinteleg; oricum palnia e inchisa)
GRATUIT = {"F154", "F155", "F156", "F157", "F158", "F159"}
# importuri de migrare -> comasate intr-o singura intrare (COMASAT)
MIGR_EXPLICIT = {"F191"}

def _e_migrare(idc, nume):
    return idc in MIGR_EXPLICIT or bool(re.search(r"import.*(migrare|preluar)|(migrare|preluar).*import|la migrare", nume.lower()))

def _keyword(s):
    if re.search(r"control|semafor|verdict|incrucis|paritate|tipare|vector fiscal|verificatoare de coeren|prag.*intrastat|audit.*preluar", s): return "Control fiscal"
    if re.search(r"salar|reges|concedi|fluturas|pontaj|tichet|cadou|beneficii|drepturi de autor|\bcda\b|zilieri|cenzori|adeverint|\bcor\b", s): return "Salarizare"
    if re.search(r"stoc|gestiun|inventar|barcode|cod.*bare|reteta|articol|\bnir\b|banca|extras|reconcil|\bcasa\b|amef|raport z|bon fisc|numerar|credite banc", s): return "Stocuri, banca si casa"
    if re.search(r"factur|proform|aviz|emitere|e-?factur|efactur|\bspv\b|model factura|link de plata|serie doc|chitant|e-transport|etransport|comodat|intracomunitar", s): return "Facturare si e-Factura"
    if re.search(r"declarati|d100|d101|d112|d205|d212|d300|d301|d390|d394|d406|d710|saf-?t|cota|cotelor|\btva\b|curs valutar|\bbnr\b|impozit|intrastat|taxare inversa|regim special", s): return "Fiscalitate"
    if re.search(r"nota|note contab|monografi|plan.*cont|inregistr|solduri|balanta|jurnal|bilant|motor contab|carte mare|inchidere|leasing|decont|diurna|sponsoriz|subventi|provizion|reevaluar|perisabil|productie|\bsgr\b|\bong\b|amortiz|mijloace fixe|bacsis|obiecte de inventar|lichidar", s): return "Contabilitate"
    if re.search(r"portal|povest|asistent|cabinet|recomand|pachete|capacitate|suspend|documente|solicitar|magic|kpi client|forecast|scadent|api public|chei api", s): return "Cabinet si portal client"
    return None

def repartizeaza(csv_path=CSV_DEFAULT):
    """Intoarce lista celor 7 grupe [{titlu, icon, functii:[nume sortate]}]. Ridica daca ceva ramane neclasificat."""
    rows = list(csv.reader(open(csv_path, encoding="utf-8")))[1:]
    NAME, ID, ST, UI, SRC = 0, 2, 7, 4, 5
    g = {gr: [] for gr in GRUPE}
    nec = []
    for r in rows:
        if len(r) < 8 or not r[ST].strip().upper().startswith("LIVE"):
            continue
        idc = r[ID].strip()
        if idc in GRATUIT or idc in EXCLUDE:
            continue
        if _e_migrare(idc, r[NAME]):
            continue
        if idc in EXPLICIT:
            g[EXPLICIT[idc]].append(r[NAME].strip()); continue
        if idc in CROSS:
            g["Control fiscal"].append(r[NAME].strip()); continue
        gr = _keyword((r[SRC] + " " + r[NAME] + " " + r[UI]).lower())
        if gr is None:
            nec.append(idc)
        else:
            g[gr].append(r[NAME].strip())
    g[COMASAT[1]].append(COMASAT[0])
    if nec:
        raise ValueError("pozitii LIVE neclasificate (adauga in EXPLICIT/EXCLUDE/keyword): %s" % nec)
    return [{"titlu": gr, "icon": ICON[gr], "functii": sorted(g[gr])} for gr in GRUPE]

def as_json(csv_path=CSV_DEFAULT):
    return json.dumps(repartizeaza(csv_path), ensure_ascii=False)

def scrie_login(login_path=LOGIN_DEFAULT, csv_path=CSV_DEFAULT):
    s = open(login_path, encoding="utf-8").read()
    s2, n = re.subn(r"const GRUPE_FUNC = \[.*?\];", "const GRUPE_FUNC = " + as_json(csv_path) + ";", s, count=1)
    assert n == 1, "ancora GRUPE_FUNC gasita de %d ori" % n
    open(login_path, "w", encoding="utf-8").write(s2)

if __name__ == "__main__":
    import sys
    grupe = repartizeaza()
    print("TOTALURI:", {gr["titlu"]: len(gr["functii"]) for gr in grupe},
          "| total:", sum(len(gr["functii"]) for gr in grupe))
    if "--scrie" in sys.argv:
        scrie_login(); print("login.js: GRUPE_FUNC rescris")
