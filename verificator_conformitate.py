# verificator_conformitate.py — v2: AUDIT COMPLET DE CONFORMITATE (Design System)
# /opt/iconta/venv/bin/python3 verificator_conformitate.py
# v2 adauga: BANI (sume afisate fara formator), SPATIERE (Total0,00), MENIURI (dialecte),
# CULORI_HARDCODATE (stiluri inline in afara tokenilor), ETICHETE (campuri doar cu placeholder)
import re, os

BAZA = os.path.expanduser("~/iconta_nou/static/js/ecrane")

CUVINTE = ["inca", "raspuns", "adauga", "sterge", "stergi", "cauta", "fara",
           "numar", "incarca", "gaseste", "banca", "plata", "pastreaza",
           "creeaza", "urmator", "dispozitie", "noua", "incasare", "asteapta", "asteptare",
           "genereaza", "blocheaza", "deblocheaza", "valideaza", "editeaza", "salveaza", "renunta",
           "astazi", "productia", "sesizari", "prioritatile"]
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

rap = {k: [] for k in ["hex_semafor", "culoare_card_hex", "diacritice", "precompletari", "butoane", "entitate_in_titlu",
                        "dialog_browser", "bani_neformatati", "spatiere", "culori_hardcodate",
                        "etichete_lipsa", "input_contrast", "antet", "camp_dialect", "mig_text", "fmt_local", "data_dialect", "data_bruta", "icoane_local", "font_inline", "radius_inline", "card_inline", "checkbox_dialect", "caseta_info", "stare_goala", "poarta_inline",
                        "esc_local", "caseta_atentie", "backend_ui_brut", "verdict_colapsat"]}
meniuri = {}

for nume, t in fisiere.items():
    linii = t.split("\n")
    for i, lin in enumerate(linii, 1):
        if "<" in lin or "textContent" in lin or "placeholder" in lin:
            for m in RE_CUV.finditer(lin):  # toate aparitiile, nu doar prima (bug: prima in cod ascundea restul)
                cuv = m.group(1); poz = m.start(1)
                # ignora aparitiile din cod: value="cuv", comparatii === "cuv", cai URL /cuv
                context = lin[max(0,poz-14):poz]
                if 'value="' in context or '=== "' in context or "/" == lin[poz-1:poz] or "-" == lin[poz-1:poz]:
                    continue
                # forma articulata corecta: 'plata' (plata directa, Certifica plata) nu cere diacritic
                if cuv.lower() == "plata" and lin[poz+5:poz+6] not in ("_", "-"):
                    continue
                rap["diacritice"].append((nume, i, cuv, lin.strip()[:66]))
        # exclus input-urile native de data/timp: value/min/max TREBUIE sa fie ISO (cerinta HTML),
        # iar un default rezonabil pe un FILTRU (De la/Pana la) e UX corect, nu precompletare fortata.
        _input_data_nativ = re.search(r'type="(date|month|datetime-local|time|week)"', lin)
        if (re.search(r'value="(0|1|0\.00|0,00)"', lin) and "<option" not in lin) or \
           (re.search(r'value="\$\{(azi|ziAzi)', lin) and not _input_data_nativ):
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
        # STARE_GOALA (cap.6 v2.13): starea goala = lista cu 0 randuri, clasa canonica .stare-goala
        # (gol + cauza + iesire). Clasele moarte cap-gol/sa-gol sunt interzise. Fundatura = negatie
        # bara (un singur cuvant, fara cauza/iesire) intr-o .stare-goala. NOTA: .mig-gol NU se
        # interzice inca aici - utilizarile ramase sunt mesaje de eroare din catch (datorie DE_FACUT
        # -> arataMesaj); interdictia lui totala se adauga cand se inchide acea tema.
        if re.search(r'class="(cap-gol|sa-gol)"', lin):
            rap["stare_goala"].append((nume, i, "clasa-moarta", lin.strip()[:66]))
        if re.search(r'class="stare-goala[^"]*">\s*(Niciun?|Nicio|Nimic)\s+\w+\.?\s*</', lin):
            rap["stare_goala"].append((nume, i, "fundatura", lin.strip()[:66]))
        # CARD_INLINE (cap.2a): card deschis inline in corpul panoului in loc de nav.deschide.
        # Semnatura interzisa: randeazaMeniu*(continut,...) sau handler .cab-card care scrie in continut.
        if re.search(r'randeazaMeniu\w+\(\s*continut\b', lin):
            rap["card_inline"].append((nume, i, "", lin.strip()[:66]))
        # CASETA_INFO (cap.5): nota informativa standing reprodusa ad-hoc inline (fundalul
        # casetei-info #eef4fd) in loc de clasa .caseta-info. Culorile de paleta/iconita
        # (#e9f0fe) au reguli proprii (CULOARE_CARD_HEX); nu intra aici.
        if re.search(r'style="[^"]*background:\s*#eef4f[df]', lin, re.I) and "caseta-info" not in lin:
            rap["caseta_info"].append((nume, i, "", lin.strip()[:66]))
        # POARTA_INLINE (cap.5 v2.14): caseta-poarta (#fbf7ee) reprodusa ad-hoc inline in loc de .caseta-poarta
        if re.search(r'style="[^"]*background:\s*#fbf7ee', lin, re.I) and "caseta-poarta" not in lin:
            rap["poarta_inline"].append((nume, i, "", lin.strip()[:66]))
        # ESC_LOCAL (cap.10, SECURITATE): variante locale de escaping (_esc/escB/escV/escS/escC/escJ) in loc
        # de esc() canonic din api.js - risc XSS (variantele omit apostroful). Apel de functie, nu cuvant.
        for em in re.finditer(r'\b(_esc|escB|escV|escS|escC|escJ)\s*\(', lin):
            rap["esc_local"].append((nume, i, em.group(1), lin.strip()[:60]))
        # CASETA_ATENTIE (cap.5): caseta de atentionare (#fdf3f3, per .caseta-atentie din stil.css) reprodusa
        # ad-hoc inline in loc de clasa canonica. Simetric cu CASETA_INFO/POARTA_INLINE. NU #fdeef2 (ala e
        # zebra/landing - login.js pagina-card-mare, exclus DS cap.15) ca sa nu dea fals-pozitiv.
        if re.search(r'style="[^"]*background:\s*#fdf3f3', lin, re.I) and "caseta-atentie" not in lin:
            rap["caseta_atentie"].append((nume, i, "", lin.strip()[:66]))
        # CARD_INACTIV (cap.2b) NEAUTOMATIZAT: semnatura { cheie: ... desc: ... } e partajata intre carduri
        # firme-optiune (cer activ) SI pasi de wizard migrare (nr:, .mig-pasi, NU cer activ) -> line-regex nu
        # distinge cert fara euristici fragile. Ramane verificare manuala (DE_FACUT). Nu automatizat = fara fals-pozitive.
        # CHECKBOX_DIALECT (cap.2): <label> cu checkbox si text-eticheta, dar fara .set-bifa
        # (dialect inline sau clasa ad-hoc). Excludem label-urile care POARTA set-bifa.
        if re.search(r'<label(?![^>]*set-bifa)[^>]*>\s*<input[^>]*type="checkbox"', lin) and "set-bifa" not in lin:
            rap["checkbox_dialect"].append((nume, i, "", lin.strip()[:66]))
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
        # HEX_SEMAFOR: culori de semafor literale in loc de var(--rosu-semafor)/var(--galben)/var(--verde). Exceptii: definitia tokenilor si gradientul dot:
        if re.search(r'#(ff3b30|c9961f|1d7a4d|9aa3b2|3a4250)\b', lin, re.I) and '--rosu-semafor:' not in lin and '--galben:' not in lin and '--verde:' not in lin and '--gri-semafor:' not in lin and '--gri-fundal-semafor:' not in lin and 'dot:' not in lin:
            rap["hex_semafor"].append((nume, i, "", lin.strip()[:66]))
        # CULOARE_CARD_HEX: bg:/fg: cu hex literal pe carduri in loc de ...CULORI_CARD.cheie (exceptie: semafor control.js, are dot:)
        if re.search(r'\b(bg|fg)\s*:\s*"#', lin) and 'dot:' not in lin:
            rap["culoare_card_hex"].append((nume, i, "", lin.strip()[:66]))
        # RADIUS_INLINE: border-radius cu valoare literala in loc de var(--raza) (exceptie: 50% pentru cercuri, 20px landing)
        for rm in re.finditer(r'border-radius:\s*([0-9]+px)', lin):
            if 'pagina-' not in lin and 'login' not in nume:
                rap["radius_inline"].append((nume, i, rm.group(1), lin.strip()[:56]))
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

# ============================================================================================
# BACKEND_UI_BRUT (DS cap.4 date + cap.7 sume): sume/date BRUTE in text destinat UTILIZATORULUI,
# construit in Python (mesaj/temei/cauza/motiv/avert/descriere/actiune). Garzile BANI/DATA de mai
# sus scaneaza DOAR .js; backendul emite text care ajunge la user si scapa complet (dovedit F183,
# 22.07). Sursa canonica unica: pdf_util.bani + pdf_util.data_ro. Vezi DESIGN_SYSTEM cap.4/7.
#
# EXCEPTII documentate (NU sunt violari, nu se cere formator canonic):
#  - XML/SAF-T (etransport_send, d406): ISO cerut de spec ANAF, nu de UI.
#  - export_winmentor: strftime cu format cerut de programul destinatie.
#  - :g lipit de lei = valoare UNITARA intentionata (tichet/plafon per-unitate), nu suma-total.
#  - "%s lei" = string DEJA compus (lectia d300.py:273 - _f formateaza deja; nu se cere bani() pe
#    text care contine deja o suma formatata).
#  - isoformat() si strftime("%Y...") = format ISO -> DATA/XML/JSON/log, NICIODATA display uman
#    (camp JSON formatat client-side prin dataRo, timestamp de log, valoare interna). Se flag DOAR
#    strftime("%d...") = zi-intai = data pentru OCHI, care trebuie sa treaca prin data_ro.
#  - sabloane .format() umplute CENTRAL (common.CODURI -> common.problema aplica bani pe campurile
#    monetare): flag-am doar f-string-uri (valoarea e pe linie) si %-format; un "{x} lei" fara prefix f
#    e placeholder .format, formatat aiurea = la locul umplerii, nu aici (altfel fals-pozitiv pe CODURI).
#  - comentarii (#) si docstring-uri (""" ... """) - nu se randeaza.
RE_SUMA_FSTR  = re.compile(r'\{[^{}]*\}\s*lei\b')                   # {x} lei intr-un f-string
RE_SUMA_PCT   = re.compile(r'%[df]\s*lei\b')                        # %d lei / %f lei (valoare pe linie)
RE_ARE_FSTR   = re.compile(r'''\bf["']''')                          # linia contine un f-string
RE_UNIT_G     = re.compile(r':g\}?\s*lei')                          # {x:g} lei = rata unitara
RE_PCT_S_LEI  = re.compile(r'%s\s*lei\b')                           # %s lei = string pre-formatat
# VERDICT_COLAPSAT (clasa BACKEND_UI_BRUT, forma "verdict" nu "suma"): o constatare/verdict destinat
# UI-ului trebuie sa fie STRUCTURAT (dot + mesaj + TEMEI + remediu; contractul control_incrucisat), nu
# un string-eticheta colapsat in backend care pierde temeiul (dovedit F163, 23.07: „solduri creditoare
# trezorerie" fara temei). Regula MECANICA: intr-o lista cu nume de verdict (contabil/constatari/
# probleme/verdicte), un element care e string LITERAL (append sau prim element de list-literal) = colaps.
# O lista de string-uri legitima NU se numeste asa (foloseste `mesaje`, `etichete`, `motive`).
RE_VERDICT_APPEND = re.compile(r'\b(contabil|constatari|probleme|verdicte|findinguri)\s*\.append\(\s*f?["\']')
RE_VERDICT_LIT    = re.compile(r'\b(contabil|constatari|probleme|verdicte)\s*\+?=\s*\[\s*f?["\']')
# Sub-regula (aceeasi familie): stratul de agregare NU-si alege culoarea de verdict ca LITERAL. Constatarea
# de afisare (_flag) primeste culoarea DERIVATA din nivelul motorului (common.stare_din_nivel) sau prin
# passthrough (`.get("stare")`), niciodata un literal "rosu"/"galben"/... la locul apelului (dovedit 23.07:
# _flag("galben",...) slabea un BLOCANT de trezorerie la galben). LIMITA: ancorat pe helperul de afisare
# `_flag(` - un motor care isi DECLARA verdictul (audit_preluare `_c("verde",...)`, control_incrucisat
# `stare="rosu"`) e legitim si NU trebuie prins; regula sintactica pura nu separa "motor declara" de
# "agregator recoloreaza", deci ancoram pe numele constructorului de afisare, nu pe orice literal de culoare.
RE_FLAG_STARE_LIT = re.compile(r'_flag\(\s*["\'](rosu|galben|verde|gri)["\']')
# Regula sora (extinsa dincolo de _flag): MUTATIA unei stari de verdict la un literal - `x["stare"] = "rosu"`
# (forma de AGREGATOR: escaladeaza starea unei entitati deja construite, cum era vechea bucla de portofoliu
# `r["stare"]="rosu"`). Severitatea trebuie sa vina din constatari (common.pastila_firma) sau din nivel, nu
# dintr-un literal. LIMITA: prinde DOAR forma subscript `x["stare"]=lit`. Forma plain `stare = "rosu"` NU e
# prinsa: e folosita LEGITIM de motoarele care isi calculeaza verdictul propriu din constatari (control_
# incrucisat:346/381/720+, audit_preluare:349 - `stare = "rosu" if any(...) else ...`), sintactic identica cu
# o escaladare gresita. O regula pe forma plain ar fi numai fals-pozitive. Nu e exprimabila mecanic - vezi DECIZII.
RE_STARE_SUBSCRIPT_LIT = re.compile(r'''\w+\[["']stare["']\]\s*=\s*["'](rosu|galben|verde|gri)["']''')
RE_DATA_DISP  = re.compile(r'\.strftime\(\s*["\']%d[./]')          # strftime("%d.%m/%d/%m") = display RO
RE_FORMATATOR = re.compile(r'\b(bani|data_ro|_lei|_dmy|_data_ro|_f|_q)\s*\(')  # deja canonic/local-ok
PY_EXCEPT_FILE = {"etransport_send.py", "d406.py", "export_winmentor.py",
                  "pdf_util.py", "verificator_conformitate.py"}
BAZA_PY = os.path.expanduser("~/iconta_nou")
for pdir in (os.path.join(BAZA_PY, "core"), BAZA_PY):
    for f in sorted(os.listdir(pdir)):
        cale = os.path.join(pdir, f)
        if not f.endswith(".py") or f.startswith("test_") or f in PY_EXCEPT_FILE or not os.path.isfile(cale):
            continue
        with open(cale, encoding="utf-8") as h:
            src = h.read()
        in_doc = False
        for i, lin in enumerate(src.split("\n"), 1):
            s = lin.strip()
            q = s.count('"""') + s.count("'''")
            if in_doc:
                if q % 2 == 1:
                    in_doc = False
                continue
            if q % 2 == 1:
                in_doc = True
                continue
            if s.startswith("#") or ('"' not in lin and "'" not in lin):
                continue
            if RE_VERDICT_APPEND.search(lin) or RE_VERDICT_LIT.search(lin):
                rap["verdict_colapsat"].append((f, i, "verdict->str", s[:60]))
            if RE_FLAG_STARE_LIT.search(lin) or RE_STARE_SUBSCRIPT_LIT.search(lin):
                rap["verdict_colapsat"].append((f, i, "stare-literal", s[:60]))
            if RE_FORMATATOR.search(lin):
                continue
            suma_bruta = (RE_SUMA_PCT.search(lin) or (RE_ARE_FSTR.search(lin) and RE_SUMA_FSTR.search(lin)))
            if suma_bruta and not RE_UNIT_G.search(lin) and not RE_PCT_S_LEI.search(lin):
                rap["backend_ui_brut"].append((f, i, "suma", s[:60]))
            if RE_DATA_DISP.search(lin):
                rap["backend_ui_brut"].append((f, i, "data", s[:60]))

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
