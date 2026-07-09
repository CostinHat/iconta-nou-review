# verificator_conformitate.py — AUDIT COMPLET DE CONFORMITATE (Design System)
# Ruleaza pe server: /opt/iconta/venv/bin/python3 verificator_conformitate.py
# Scaneaza TOATE ecranele pe toate regulile; raport pe categorii, cu fisier:linie.
# Unealta permanenta de audit. Zero modificari — doar raport.
import re, os

BAZA = os.path.expanduser("~/iconta_nou/static/js/ecrane")
NAV = os.path.expanduser("~/iconta_nou/static/js/navigator.js")

# cuvinte scrise sigur gresit fara diacritice (lista conservatoare, fara ambiguitati)
CUVINTE = ["inca", "raspuns", "adauga", "sterge", "stergi", "cauta", "fara",
           "numar", "incarca", "gaseste", "banca", "plata", "luna viitoare",
           "trimite-ne", "pastreaza", "creaza", "creeaza", "urmator", "intelege",
           "dispozitie", "noua", "incasare", "aceasta", "asteapta", "asteptare"]
RE_CUV = re.compile(r'[">\s(](' + "|".join(CUVINTE) + r')[\s.,:!?<")]', re.IGNORECASE)

CLASE_BUTON_OK = {"buton-primar", "buton-secundar", "buton-sters", "buton-verde",
                  "buton-mic", "btn-link", "btn-nav", "buton-activ", "buton-ingust"}

fisiere = {}
for f in sorted(os.listdir(BAZA)):
    if f.endswith(".js") and ".bak" not in f:
        with open(os.path.join(BAZA, f), encoding="utf-8") as h:
            fisiere[f] = h.read()

rap = {"diacritice": [], "precompletari": [], "butoane": [], "entitate_in_titlu": [],
       "dialog_browser": [], "clase_camp_vechi": []}

for nume, t in fisiere.items():
    for i, lin in enumerate(t.split("\n"), 1):
        # doar texte vizibile (in template-uri HTML), nu cod
        if "<" in lin or 'textContent' in lin or 'placeholder' in lin or '"' in lin:
            m = RE_CUV.search(lin)
            if m and "//" not in lin.split(m.group(1))[0][-30:]:
                rap["diacritice"].append((nume, i, m.group(1), lin.strip()[:70]))
        if re.search(r'value="(0|1|0\.00|0,00)"', lin) or 'value="${ziAzi}"' in lin or 'value="${azi' in lin:
            rap["precompletari"].append((nume, i, "", lin.strip()[:70]))
        for bm in re.finditer(r'<button[^>]*class="([^"]*)"', lin):
            cls = set(bm.group(1).split())
            if not (cls & CLASE_BUTON_OK) and "fir-veriga" not in cls and "nav-" not in bm.group(1):
                rap["butoane"].append((nume, i, bm.group(1)[:30], lin.strip()[:60]))
        if re.search(r'<h2[^>]*>[^<]*\$\{[^}]*nume', lin):
            rap["entitate_in_titlu"].append((nume, i, "", lin.strip()[:70]))
        if re.search(r'\balert\(|\bconfirm\(', lin) and "confirmaCaseta" not in lin:
            rap["dialog_browser"].append((nume, i, "", lin.strip()[:70]))

print("=" * 90)
print("RAPORT DE CONFORMITATE — Design System")
print("=" * 90)
for cat, lista in rap.items():
    print("\n### %s: %d gasite" % (cat.upper(), len(lista)))
    for nume, i, extra, lin in lista[:30]:
        print("  %-22s %5d  %-12s %s" % (nume, i, extra, lin))
    if len(lista) > 30:
        print("  ... si inca %d" % (len(lista) - 30))
print("\n" + "=" * 90)
total = sum(len(v) for v in rap.values())
print("TOTAL: %d neconformitati candidate (diacriticele pot avea fals-pozitive rare)" % total)
