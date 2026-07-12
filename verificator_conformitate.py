# verificator_conformitate.py — v2: AUDIT COMPLET DE CONFORMITATE (Design System)
# /opt/iconta/venv/bin/python3 verificator_conformitate.py
# v2 adauga: BANI (sume afisate fara formator), SPATIERE (Total0,00), MENIURI (dialecte),
# CULORI_HARDCODATE (stiluri inline in afara tokenilor), ETICHETE (campuri doar cu placeholder)
import re, os

BAZA = os.path.expanduser("~/iconta_nou/static/js/ecrane")

CUVINTE = ["inca", "raspuns", "adauga", "sterge", "stergi", "cauta", "fara",
           "numar", "incarca", "gaseste", "banca", "plata", "pastreaza",
           "creeaza", "urmator", "dispozitie", "noua", "incasare", "asteapta", "asteptare"]
RE_CUV = re.compile(r'[">\s(](' + "|".join(CUVINTE) + r')[\s.,:!?<")]', re.IGNORECASE)
CLASE_BUTON_OK = {"buton-primar", "buton-secundar", "buton-sters", "buton-verde",
                  "buton-mic", "btn-link", "btn-nav", "buton-activ"}
# componente structurale si selectoare de optiune — limbaj propriu, nu butoane de actiune (Design System v1.1)
CLASE_COMPONENTA_OK = {"firme-optiune", "cab-card", "acces-card", "meniu-card", "sub-inapoi",
                       "firme-inapoi", "rap-tab", "ac-per", "mig-dec", "vf-opt", "sa-asist",
                       "val-btn", "mf-font-opt", "mf-culoare-opt", "pagina-card-buton",
                       "pagina-bara-acces", "pacm-x", "acces-x", "rec-modal-x", "pf-frand"}
# culori-token permise inline (semafor canonic + entitate + fir)
ZEBRA_INTERZISE = {"#fdeef2", "#eaf2fb", "#f4f7fb", "#f7f8fa"}  # alternante vechi, inlocuite de STANDARD_ZEBRA
CULORI_OK = {"#1d7a4d", "#c9961f", "#ff3b30", "#1d4ed8", "#5b6b7c", "#1d3a5f", "#8a97a5", "#e11d1d"}

fisiere = {}
for f in sorted(os.listdir(BAZA)):
    if f.endswith(".js") and ".bak" not in f:
        with open(os.path.join(BAZA, f), encoding="utf-8") as h:
            fisiere[f] = h.read()

rap = {k: [] for k in ["diacritice", "precompletari", "butoane", "entitate_in_titlu",
                        "dialog_browser", "bani_neformatati", "spatiere", "culori_hardcodate",
                        "etichete_lipsa", "input_contrast", "antet", "camp_dialect", "mig_text", "fmt_local", "data_dialect", "data_bruta", "icoane_local", "font_inline"]}
meniuri = {}

for nume, t in fisiere.items():
    linii = t.split("\n")
    for i, lin in enumerate(linii, 1):
        if "<" in lin or "textContent" in lin or "placeholder" in lin:
            m = RE_CUV.search(lin)
            if m:
                cuv = m.group(1); poz = m.start(1)
                # ignora aparitiile din cod: value="cuv", comparatii === "cuv", cai URL /cuv
                context = lin[max(0,poz-14):poz]
                if 'value="' in context or '=== "' in context or "/" == lin[poz-1:poz] or "-" == lin[poz-1:poz]:
                    continue
                # forma articulata corecta: 'plata' (plata directa, Certifica plata) nu cere diacritic
                if cuv.lower() == "plata" and lin[poz+5:poz+6] not in ("_", "-"):
                    continue
                rap["diacritice"].append((nume, i, cuv, lin.strip()[:66]))
        if (re.search(r'value="(0|1|0\.00|0,00)"', lin) and "<option" not in lin) or re.search(r'value="\$\{(azi|ziAzi)', lin):
            rap["precompletari"].append((nume, i, "", lin.strip()[:66]))
        for bm in re.finditer(r'<button[^>]*class="([^"]*)"', lin):
            cls = set(bm.group(1).split())
            if not (cls & CLASE_BUTON_OK) and not (cls & CLASE_COMPONENTA_OK) and "fir-veriga" not in cls and "nav-" not in bm.group(1) and "${cls}" not in bm.group(1) and not any(ok in bm.group(1) for ok in CLASE_BUTON_OK):
                rap["butoane"].append((nume, i, bm.group(1)[:26], lin.strip()[:56]))
        if re.search(r'<h2[^>]*>[^<]*\$\{[^}]*nume', lin):
            rap["entitate_in_titlu"].append((nume, i, "", lin.strip()[:66]))
        # ANTET (cap.9): titlu de fereastra cu sufix de nivel "· Cabinet"/"· Firma" = entitate dublata in titlu
        if re.search(r'titlu-entitate|nivel[^=]*==[^?]*\?\s*"Cabinet"', lin):
            rap["antet"].append((nume, i, "", lin.strip()[:66]))
        # INPUT_CONTRAST: fundal alb fortat inline pe casete (incalca STANDARD_INPUT_CONTRAST)
        if re.search(r'<(input|select|textarea)[^>]*style="[^"]*background:\s*(#f5f6f8|#eee|#eeeeee|#f7f8fa|#f7f9fc)', lin):
            rap["input_contrast"].append((nume, i, "", lin.strip()[:66]))
        if re.search(r'\balert\(|(?<!confirma)\bconfirm\(', lin):
            rap["dialog_browser"].append((nume, i, "", lin.strip()[:66]))
        # BANI: ${expr} imediat urmat de RON/lei/EUR fara formator cunoscut in expresie
        for bm in re.finditer(r'\$\{([^}]*)\}\s*(RON|lei|EUR|\$\{[^}]*moneda)', lin):
            expr = bm.group(1)
            if not re.search(r'_bani|toLocaleString|fmt|bani\(', expr):
                rap["bani_neformatati"].append((nume, i, expr[:22], lin.strip()[:60]))
        # SPATIERE: cuvant lipit direct de ${ (ex: Total${...})
        for sm in re.finditer(r'>([A-Za-z\u00c0-\u024f]{3,})\$\{', lin):
            rap["spatiere"].append((nume, i, sm.group(1), lin.strip()[:60]))
        # CULORI: style cu hex in afara tokenilor
        for cm in re.finditer(r'style="[^"]*color:\s*(#[0-9a-fA-F]{3,6})', lin):
            if cm.group(1).lower() not in CULORI_OK:
                rap["culori_hardcodate"].append((nume, i, cm.group(1), lin.strip()[:56]))
        # MENIURI: dialecte de optiuni
        for dm in re.finditer(r'class="((?:fac|firme)-optiune)', lin):
            meniuri.setdefault(dm.group(1), []).append((nume, i))
        # CAMP_DIALECT (#61): <label>text<br><input|select> in loc de .camp canonic
        if re.search(r'<label[^>]*>[^<]*<br>\s*(<input|<select|\$\{input)', lin):
            rap["camp_dialect"].append((nume, i, "", lin.strip()[:66]))
        # MIG_TEXT: input/select cu clasa mig-text (dialect de contrast, textarea-only) in loc de camp-input
        if re.search(r'<(input|select)[^>]*class="[^"]*\bmig-text\b', lin):
            rap["mig_text"].append((nume, i, "", lin.strip()[:66]))
        # FMT_LOCAL: definitie locala de format monetar (const fmt = ...toLocaleString) in loc de bani() canonic
        if re.search(r'const\s+(?!pct\b)\w+\s*=.*toLocaleString\("ro-RO"', lin):
            rap["fmt_local"].append((nume, i, "", lin.strip()[:66]))
        # DATA_DIALECT: functie locala de formatare data (toLocaleDateString sau split("-") pt reordonare zi/luna/an) in loc de dataRo()
        if re.search(r'toLocaleDateString', lin) or re.search(r'const\s+fmt\w*\s*=.*split\("-"\)', lin):
            rap["data_dialect"].append((nume, i, "", lin.strip()[:66]))
        # DATA_BRUTA: ${x.data} sau ${x.data_ceva} afisat direct in template fara dataRo (exclus value= de input si payload)
        # ICOANE_LOCAL: dictionar local de iconite (building/report/shield cu <path) in loc de ICOANE canonic
        if re.search(r'(building|report|shield|clipboard)\s*:\s*.<path', lin):
            rap["icoane_local"].append((nume, i, "", lin.strip()[:60]))
        # FONT_INLINE: font-size cu valoare literala inline (px/em) in loc de var(--text-*) sau clasa .tip-*
        for fm in re.finditer(r'font-size:\s*([0-9.]+(?:px|em|rem))', lin):
            rap["font_inline"].append((nume, i, fm.group(1), lin.strip()[:56]))
        if 'value="' not in lin and "value='" not in lin:
            for dm in re.finditer(r'\$\{(\w+\.data\w*)\s*(?:\|\|[^}]*)?\}', lin):
                pre = lin[:dm.start()]
                # doar daca e in context de afisare (are tag HTML inainte pe linie) si nu e deja prin dataRo
                if 'dataRo' not in dm.group(0) and re.search(r'<(div|span|td|p|b|label|h\d)', pre):
                    rap["data_bruta"].append((nume, i, dm.group(1)[:20], lin.strip()[:60]))
                    break
        # ETICHETE: input cu placeholder informativ dar fara label/eticheta pe linie/vecinatate
        if re.search(r'<input[^>]*placeholder="[^"]{4,}', lin) and "camp-eticheta" not in lin and "<label" not in lin and "aria-label" not in lin:
            vecini = "\n".join(linii[max(0,i-3):i] + linii[i:i+4])
            if "camp-eticheta" not in vecini and "<label" not in vecini and "aria-label" not in vecini:
                rap["etichete_lipsa"].append((nume, i, "", lin.strip()[:66]))

print("=" * 92)
print("RAPORT DE CONFORMITATE v2 — Design System")
print("=" * 92)
for cat, lista in rap.items():
    print("\n### %s: %d" % (cat.upper(), len(lista)))
    for nume, i, extra, lin in lista:
        print("  %-22s %5d  %-14s %s" % (nume, i, extra, lin))
    if len(lista) > 25:
        pass  # listare completa
print("\n### MENIURI (dialecte de optiuni):")
for cls, loc in meniuri.items():
    print("  %-16s %d aparitii (%s)" % (cls, len(loc), ", ".join(sorted(set(x[0] for x in loc)))))
print("\n" + "=" * 92)
print("TOTAL:", sum(len(v) for v in rap.values()), "candidate")
