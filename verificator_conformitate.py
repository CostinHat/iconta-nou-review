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
                       "pagina-bara-acces", "pacm-x", "acces-x", "rec-modal-x", "pf-frand", "func-card"}  # func-card = selector card grupa (F203), ca cab-card/acces-card/meniu-card
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
                        "esc_local", "caseta_atentie", "backend_ui_brut", "verdict_colapsat", "default_fiscal_tacit", "card_regim", "import_versiune", "verdict_paritate"]}
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
        # CARD_REGIM (cap.18): cardul din meniuFirma (firme.js optiuni) declara `regim` (ambele/simpla/dubla)
        # OBLIGATORIU imediat dupa cheie - FARA default tacit. Vizibilitatea deriva prin regim_contabil (o sursa,
        # nu listele DOAR_SRL/DOAR_PFA - eliminate 23.07). Scoped la firme.js (unicul loc cu optiuni de card pe firma).
        if nume.endswith("firme.js") and re.search(r'\{\s*cheie:\s*"[a-z]+",\s+(?!regim:)', lin):
            rap["card_regim"].append((nume, i, "", lin.strip()[:66]))
        # CASETA_INFO (cap.5): nota informativa standing reprodusa ad-hoc inline (fundalul
        # casetei-info #eef4fd) in loc de clasa .caseta-info. Culorile de paleta/iconita
        # (#e9f0fe) au reguli proprii (CULOARE_CARD_HEX); nu intra aici.
        if re.search(r'style="[^"]*background:\s*#eef4f[df]', lin, re.I) and "caseta-info" not in lin:
            rap["caseta_info"].append((nume, i, "", lin.strip()[:66]))
        # DATA_LUNA_AN (cap.4 v2.21, 27.07.2026): perioada luna/an compusa MANUAL cu padStart in
        # loc de dataRo(..., "luna_an_numeric"). Garda DATA_DIALECT nu prindea forma asta (cauta
        # luni[...]/toLocaleDateString/split("-")). Gasita in firme.js x12 + facturi_ecran.js x2.
        # Forma AFISATA ramane numerica (07/2026, decis 27.07) - se schimba doar CINE o produce.
        if re.search(r'String\(\w+\)\.padStart\(2, ?"0"\)\}/\$\{', lin):
            rap["data_dialect"].append((nume, i, "", lin.strip()[:66]))

        # POARTA_INLINE (cap.5 v2.14): caseta-poarta (#fbf7ee) reprodusa ad-hoc inline in loc de .caseta-poarta
        if re.search(r'style="[^"]*background:\s*#fbf7ee', lin, re.I) and "caseta-poarta" not in lin:
            rap["poarta_inline"].append((nume, i, "", lin.strip()[:66]))
        # ESC_LOCAL (cap.10, SECURITATE): variante locale de escaping (_esc/escB/escV/escS/escC/escJ) in loc
        # de esc() canonic din api.js - risc XSS (variantele omit apostroful). Apel de functie, nu cuvant.
        for em in re.finditer(r'\b(_esc|escB|escV|escS|escC|escJ)\s*\(', lin):
            rap["esc_local"].append((nume, i, em.group(1), lin.strip()[:60]))
        # ESC_LOCAL extins (cap.10, SECURITATE): REDEFINIRE locala a lui `esc` intr-un ecran (function esc /
        # const|let|var esc =) in loc de importul canonic din api.js. O copie locala poate fi mai SLABA (setari.js
        # escapa DOAR `"` -> XSS pe <> in continut de element, gasit 24.07) si oricum e a doua sursa de adevar pt
        # o primitiva de securitate. api.js (sursa canonica) e in static/js/, NU in ecrane/ -> nu se auto-flag.
        if re.search(r'\bfunction\s+esc\s*\(', lin) or re.search(r'\b(?:const|let|var)\s+esc\s*=', lin):
            rap["esc_local"].append((nume, i, "redef-esc", lin.strip()[:60]))
        # ESC_LOCAL extins v3 (cap.10): STRIP inline de caractere HTML (.replace(/[...<>&...]/,...)) ca sanitizare
        # ad-hoc in loc de esc canonic. NU e XSS (scoate <>), dar e DATA-LOSSY (scoate & din nume: "A&B"->"AB") si
        # o a doua sursa de sanitizare. Prinde orice clasa de caractere care contine TOATE din <>& (robust la
        # reordonare/caractere extra). api.js (sursa canonica) e in static/js/, nescanat -> fara auto-flag.
        for _ms in re.finditer(r'\.replace\(\s*/\[([^\]]*)\]/', lin):
            if all(ch in _ms.group(1) for ch in "<>&"):
                rap["esc_local"].append((nume, i, "strip-html", lin.strip()[:60]))
                break
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
        # DATA_DIALECT: formator LOCAL de data in loc de dataRo() din api.js. Prinde: toLocaleDateString;
        # const fmt=...split("-"); SI un array de nume de luni INDEXAT prin parseInt (ex. luni[parseInt(p[1])-1])
        # = parsare manuala a unei date -> forma functiei dataLunga (gaura descoperita 23.07: forma veche o rata).
        # Precis pe UTILIZARE, nu pe declaratie: NU atinge pickerele de luna (LUNI.map(...) pt <option>) sau
        # etichetele din stare (LUNI[S.luna-1], fara parseInt) - acelea sunt legitime. Exceptat api.js (sursa canonica).
        # doua forme prin array de luni: (a) parsare completa (dataLunga: luni[parseInt(...)]); (b) eticheta
        # luna-AN (luni[<idx>] ... ${...an}) care ocoleste dataRo("luna_an"). NU prinde luna-DOAR (luni[r.luna]
        # fara an - nu are echivalent dataRo, legitim) si nici pickerul (LUNI.map pt <option>). Gaura a doua
        # descoperita 23.07 pe ecranul Declaratii (etPerioada). Exceptat api.js (sursa canonica).
        _data_local = (not nume.endswith("api.js") and (
            re.search(r'\w*luni\w*\s*\[\s*parseInt\(', lin, re.I)
            or re.search(r'\w*luni\w*\s*\[[^\]]+\][^\n]{0,30}?\ban\b', lin, re.I)))
        if re.search(r'toLocaleDateString', lin) or re.search(r'const\s+fmt\w*\s*=.*split\("-"\)', lin) or _data_local:
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
# DEFAULT_FISCAL_TACIT: un camp fiscal decisiv (regim_fiscal/tip_firma/platitor_tva/tip_decont/operatiuni_ic) NU se
# defaulteaza pe LITERAL inline (x or "micro" / x || "srl" / ... else "pfa" / operatiuni_ic or False). Faptul +
# normalizarea + default-ul traiesc INTR-UN singur loc — primitivele din migrare_api (regim_contabil, regim_efectiv,
# tip_firma_nrm). O cale care re-defaulteaza inline reintroduce bug-ul termene ("regim_fiscal or 'micro'" -> D100
# fabricat pe un PFA), sau ascunde obligatia D390 ("operatiuni_ic or False" -> D390 ratat cand exista facturi IC).
# Se prinde forma or/||/else (fallback pe CITIRE); atribuirea simpla `x = "srl"` NU (declaratie, nu fallback).
# operatiuni_ic = al 5-lea camp (boolean): literal True/False sau "da"/"nu". Exceptat: migrare_api.py. Vezi DESIGN_SYSTEM cap.17.
RE_DEFAULT_FISCAL = re.compile(r'''\b(regim_fiscal|tip_firma|platitor_tva|tip_decont|operatiuni_ic)\b[^\n]{0,80}?(\bor\b|\|\||\belse\b)\s*(["'](micro|profit|srl|pfa|lunar|trimestrial|da|nu)["']|\b(?:True|False)\b)''')
FISCAL_EXEMPT_FILE = {"migrare_api.py"}
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
            if f not in FISCAL_EXEMPT_FILE and RE_DEFAULT_FISCAL.search(lin):
                rap["default_fiscal_tacit"].append((f, i, "fiscal-lit", s[:60]))
            if RE_FORMATATOR.search(lin):
                continue
            suma_bruta = (RE_SUMA_PCT.search(lin) or (RE_ARE_FSTR.search(lin) and RE_SUMA_FSTR.search(lin)))
            if suma_bruta and not RE_UNIT_G.search(lin) and not RE_PCT_S_LEI.search(lin):
                rap["backend_ui_brut"].append((f, i, "suma", s[:60]))
            if RE_DATA_DISP.search(lin):
                rap["backend_ui_brut"].append((f, i, "data", s[:60]))

# DEFAULT_FISCAL_TACIT si pe .js: aceleasi 5 campuri (regim_fiscal/tip_firma/platitor_tva/tip_decont/operatiuni_ic);
# forme JS `field || "lit"` si ternar `... ? ... : "lit"` unde litералul fiscal e ramura ELSE (= default cand campul
# lipseste). Pt operatiuni_ic (boolean): `|| false` / `? … : false` / `: "nu"`. NU prinde `field === "lit" ? "lit" : …`
# (mapare valoare->eticheta) — ramura ELSE nu e literal. Frontendul foloseste FAPTUL expus de backend, nu defaulteaza
# inline (operatiuni_ic trimite null cand nu e ales -> backend respinge 400). Vezi DESIGN_SYSTEM cap.17.
RE_JS_FISCAL = re.compile(r'''\b(regim_fiscal|tip_firma|platitor_tva|tip_decont|operatiuni_ic)\b[^\n]{0,60}?(\|\||\?[^\n?]{0,40}?:)\s*(["'](micro|profit|srl|pfa|lunar|trimestrial|da|nu)["']|\b(?:true|false)\b)''')
for nume, t in fisiere.items():
    for i, lin in enumerate(t.split("\n"), 1):
        s = lin.strip()
        if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
            continue
        if RE_JS_FISCAL.search(lin):
            rap["default_fiscal_tacit"].append((nume, i, "fiscal-lit-js", s[:60]))

# IMPORT_VERSIUNE (cap.19): acelasi modul importat cu tokeni de versiune DIVERGENTI (?v=7 intr-un loc,
# fara versiune in altul) => browserul trateaza `/x.js` si `/x.js?v=7` ca DOUA module distincte, ruleaza
# DOUA instante, iar starea/efectele uneia nu se vad in cealalta. Simptom prins 23.07: antetul din firme.js
# aparea pe calea FIRME dar lipsea pe calea TERMENE (termene.js importa ./firme.js fara ?v, restul ?v=7).
# Grupam pe calea REZOLVATA relativ la fisierul care importa (nu pe basename — doua fisiere omonime din
# directoare diferite pot avea legitim versiuni proprii). Un modul cu >1 token distinct de versiune = eroare.
RE_IMPORT_JS = re.compile(r'''(?:from|import\()\s*["']([^"']+\.js(?:\?[^"']*)?)["']''')
BAZA_JS = os.path.expanduser("~/iconta_nou/static/js")
_imp = {}  # cale_rezolvata -> list de (fisier_relativ, linie, token_versiune)
for rad, _dirs, _fis in os.walk(BAZA_JS):
    for f in sorted(_fis):
        if not f.endswith(".js") or ".bak" in f:
            continue
        cale = os.path.join(rad, f)
        rel_fis = os.path.relpath(cale, BAZA_JS)
        with open(cale, encoding="utf-8") as h:
            for i, lin in enumerate(h.read().split("\n"), 1):
                s = lin.strip()
                if s.startswith("//") or s.startswith("*"):
                    continue
                for m in RE_IMPORT_JS.finditer(lin):
                    spec = m.group(1)
                    mod, _, ver = spec.partition("?")
                    if not mod.startswith("."):
                        continue  # doar module locale relative (nu URL-uri externe)
                    rez = os.path.normpath(os.path.join(rad, mod))
                    _imp.setdefault(rez, []).append((rel_fis, i, ver or "(fara)"))
for rez, aparitii in sorted(_imp.items()):
    if len(set(v for _, _, v in aparitii)) > 1:
        modrel = os.path.relpath(rez, BAZA_JS)
        for rel_fis, i, ver in aparitii:
            rap["import_versiune"].append((rel_fis, i, ver, "%s importat ca %s" % (modrel, ver)))

# ============================================================================================
# VERDICT_PARITATE (DS cap.20): renderer-ul verdictului de control fiscal (control_verdict.js) alege chei pe
# NUME din payload-ul verificari_contabile (vc). O cheie noua produsa de backend fara consumator ramane
# INVIZIBILA, tacut (cazul DANTE 24.07: cele 4 rosii pe salarii nu apareau pe cardul din fisa). Doua parities,
# ambele mecanice, peste cheile PRODUSE efectiv (parsate din sursa, nu hardcodate — o cheie noua e prinsa auto):
#  1. RANDARE: fiecare cheie vc ∈ inventarul declarat VC_RANDATE din control_verdict.js.
#  2. SEVERITATE: fiecare cheie vc e ori pliata in `contabil` (_construieste_contabil -> pastila_firma), ori
#     declarata VC_FARA_SEVERITATE (cu motiv) in main.py.
# Limita (ca la CARD_REGIM): garanteaza ca fiecare cheie e DECLARATA undeva, nu ca directiva chiar randeaza /
# ridica severitatea. Inchide clasa "omisiune tacuta", nu "declarat ca no-op".
def _felie_py(text, ancora, capete):
    i = text.find(ancora)
    if i < 0:
        return ""
    rest = text[i + len(ancora):]
    poz = [rest.find(c) for c in capete if rest.find(c) >= 0]
    return rest[:min(poz)] if poz else rest

_main_src = open(os.path.join(BAZA_PY, "main.py"), encoding="utf-8").read()
# chei PRODUSE: dict-ul `rezultat = {...}` din _verificari_contabile + orice rezultat["x"] = ...
_vf = _felie_py(_main_src, "def _verificari_contabile", ("\ndef ",))
_produse = set()
_mrez = re.search(r'rezultat\s*=\s*\{(.*?)\n    \}', _vf, re.S)
if _mrez:
    _produse |= set(re.findall(r'"(\w+)"\s*:', _mrez.group(1)))
_produse |= set(re.findall(r'rezultat\[\s*"(\w+)"\s*\]\s*=', _vf))
# chei PLIATE in contabil (severitate): vc.get("x") + tuplul (cheie, eticheta) din _construieste_contabil
_cc = _felie_py(_main_src, "def _construieste_contabil", ("\ndef ",))
_pliate = set(re.findall(r'vc\.get\(\s*"(\w+)"', _cc))
_pliate |= set(re.findall(r'"(\w+_incrucisat|cota_tva_conformitate)"\s*,', _cc))
# exceptii de severitate declarate (cu motiv)
_fara_sev = set(re.findall(r'"(\w+)"\s*:', _felie_py(_main_src, "VC_FARA_SEVERITATE = {", ("\n}",))))
# inventar de randare declarat in control_verdict.js
_randate = set()
_cv = os.path.join(BAZA, "control_verdict.js")
if not os.path.exists(_cv):
    rap["verdict_paritate"].append(("control_verdict.js", 0, "lipsa", "modulul renderer-ului verdictului lipseste"))
else:
    _inv = _felie_py(open(_cv, encoding="utf-8").read(), "VC_RANDATE = {", ("\n};",))
    _randate = set(re.findall(r'\n\s*(\w+)\s*:', _inv))
# al DOILEA consumator care alege chei vc pe NUME: ecranVerificari (firme.js, endpoint /firme/{id}/verificari,
# vc brut pe luna). Aceeasi paritate de randare, acelasi mecanism: inventar declarat VC_VERIFICARI (randat sau
# ignorat-cu-motiv). Cross-check-urile sunt ignorate declarat aici (apartin exclusiv verdictului Control fiscal).
_vf_randate = set()
_fj = os.path.join(BAZA, "firme.js")
if os.path.exists(_fj):
    _vfinv = _felie_py(open(_fj, encoding="utf-8").read(), "VC_VERIFICARI = {", ("\n};",))
    _vf_randate = set(re.findall(r'\n\s*(\w+)\s*:', _vfinv))
if not _produse:
    rap["verdict_paritate"].append(("main.py", 0, "parsare", "n-am putut extrage cheile vc produse (_verificari_contabile) — verifica ancora"))
for _cheie in sorted(_produse):
    if _cheie not in _randate:
        rap["verdict_paritate"].append(("main.py -> control_verdict.js", 0, "randare", "cheie vc `%s` produsa dar fara intrare in VC_RANDATE" % _cheie))
    if _cheie not in _vf_randate:
        rap["verdict_paritate"].append(("main.py -> firme.js/ecranVerificari", 0, "randare", "cheie vc `%s` produsa dar fara intrare in VC_VERIFICARI" % _cheie))
    if _cheie not in _pliate and _cheie not in _fara_sev:
        rap["verdict_paritate"].append(("main.py", 0, "severitate", "cheie vc `%s` nici pliata in contabil, nici in VC_FARA_SEVERITATE" % _cheie))

# --- GRUPE_FUNC (pagina Functionalitati) vs FUNCTIONALITATI.csv: registrul nu trebuie sa se departeze tacit ---
rap["grupe_func_stale"] = []
try:
    import sys as _sys, json as _json, csv as _csv
    _sys.path.insert(0, BAZA_PY)
    import genereaza_grupe_functii as _gen
    _asteptat = _gen.repartizeaza()
    _login = open(os.path.join(BAZA, "login.js"), encoding="utf-8").read()
    _zona = re.search(r"// <GRUPE_FUNC_AUTO>.*?// </GRUPE_FUNC_AUTO>", _login, re.S)  # [preturi_v1] valideaza DOAR zona auto (nu continutul scris de mana din afara ancorelor)
    _m = re.search(r"const GRUPE_FUNC = (\[.*?\]);", _zona.group(0) if _zona else "")
    if not _m:
        rap["grupe_func_stale"].append(("login.js", 0, "parsare", "GRUPE_FUNC negasit in login.js"))
    else:
        _pagina = _json.loads(_m.group(1))
        _cod = {}
        for _r in _csv.reader(open(os.path.join(BAZA_PY, "FUNCTIONALITATI.csv"), encoding="utf-8")):
            if len(_r) > 2 and _r[2].strip().startswith("F"):
                _cod[_r[0].strip()] = _r[2].strip()
        _ea = {g["titlu"]: set(g["functii"]) for g in _asteptat}
        _pa = {g["titlu"]: set(g["functii"]) for g in _pagina}
        _ta = sum(len(v) for v in _ea.values()); _tp = sum(len(v) for v in _pa.values())
        if _ta != _tp:
            rap["grupe_func_stale"].append(("login.js GRUPE_FUNC", 0, "total",
                "TOTAL: CSV %d, pagina %d (difera cu %d) -> ruleaza: python3 genereaza_grupe_functii.py --scrie" % (_ta, _tp, abs(_ta - _tp))))
        for _t in _gen.GRUPE:
            _a = _ea.get(_t, set()); _p = _pa.get(_t, set())
            if _a != _p:
                _lipsa = sorted(_a - _p); _extra = sorted(_p - _a)
                _det = "CSV %d, pagina %d" % (len(_a), len(_p))
                if _lipsa: _det += "; lipseste din pagina: " + ", ".join("%s (%s)" % (f, _cod.get(f, "?")) for f in _lipsa)
                if _extra: _det += "; in pagina dar nu in CSV: " + ", ".join(_extra)
                rap["grupe_func_stale"].append(("login.js GRUPE_FUNC", 0, _t[:14], _det))
except Exception as _e:
    rap["grupe_func_stale"] = [("genereaza_grupe_functii", 0, "eroare", str(_e)[:90])]

# ============================================================================================
# BRAND_EU (MARKETING.md, cap. BRAND / DESIGN_SYSTEM.md cap.21): marca se scrie PESTE TOT
# "iConta.eu" in orice material PUBLIC. Scaneaza frontend (static/**/*.{js,mjs,html}) +
# literalele publice din backend (main.py = rute care emit email/UI; notificari_scadenta.py +
# observare.py = canalele de email). Semnaleaza orice "iConta" NEURMAT de ".eu". Al DOILEA
# assert al regulii: zero "iConta.eu.eu" (dublura aparuta din corectii peste corectii). Motiv
# si exceptii: DECIZII 26.07.2026.
#
# LISTA ALBA (fiecare cu motiv scris):
#  - "Admin iConta"          -> nume propriu al panoului de administrare (decizie fondator,
#                               DECIZII 26.07), NU o aparitie a marcii. Sarit per-aparitie
#                               (secventa "Admin " imediat inaintea marcii).
#  - "<SoftwareCompanyName>" -> identificarea softului catre ANAF in SAF-T (core/d406.py:418).
#                               Camp FISCAL, nu cosmetica; schimbarea = decizie separata (DECIZII
#                               26.07). d406.py e IN AFARA scopului scanat (fisier fiscal, alaturi
#                               de <SoftwareID>); garda ramane defensiva daca fisierul intra vreodata.
#  - comentarii (// in js/html, # in py — inclusiv trailing) si docstring-uri (triple-quote)
#                            -> nu se randeaza, nu-s material public.
#  - iconta_nou / iconta-nou / iconta_v2 -> cale de cod / unit systemd / schema DB. Sunt cu 'c'
#                               mic; regexul marcii ("iConta", C mare) NU le prinde oricum.
RE_BRAND = re.compile(r'iConta(?!\.eu)')
RE_BRAND_DBL = re.compile(r'iConta\.eu\.eu')
rap["brand_eu"] = []

def _brand_hits(text):
    """Nr. aparitii "iConta" bare din `text`, sarind "Admin iConta" (nume panou)."""
    h = 0
    for m in RE_BRAND.finditer(text):
        st = m.start()
        if text[max(0, st - 6):st] == "Admin ":
            continue
        h += 1
    return h

def _cod_fara_comentariu_py(linia):
    """Taie comentariul # (trailing/intreg) respectand string-urile — hex #rrggbb din ele raman cod."""
    in_s = None
    for idx, ch in enumerate(linia):
        if in_s:
            if ch == in_s:
                in_s = None
        elif ch in ("'", '"'):
            in_s = ch
        elif ch == "#":
            return linia[:idx]
    return linia

def _brand_flag(rel, i, text):
    if "<SoftwareCompanyName>" in text:  # camp fiscal SAF-T (decizie separata)
        return
    s = text.strip()
    if _brand_hits(text):
        rap["brand_eu"].append((rel, i, "bare", s[:60]))
    if RE_BRAND_DBL.search(text):
        rap["brand_eu"].append((rel, i, ".eu.eu", s[:60]))

_BRAND_STATIC = os.path.expanduser("~/iconta_nou/static")
for _rad, _d, _fis in os.walk(_BRAND_STATIC):  # frontend: js/mjs/html
    for _f in sorted(_fis):
        if not _f.endswith((".js", ".mjs", ".html")) or ".bak" in _f:
            continue
        _rel = os.path.relpath(os.path.join(_rad, _f), _BRAND_STATIC)
        with open(os.path.join(_rad, _f), encoding="utf-8") as _h:
            for _i, _lin in enumerate(_h.read().split("\n"), 1):
                if _lin.strip().startswith(("//", "/*", "*", "<!--")):  # comentariu
                    continue
                _brand_flag(_rel, _i, _lin)

for _rel in ("main.py", "core/notificari_scadenta.py", "core/observare.py"):  # backend: material public
    _cale = os.path.join(BAZA_PY, _rel)
    if not os.path.isfile(_cale):
        continue
    _in_doc = False
    with open(_cale, encoding="utf-8") as _h:
        for _i, _lin in enumerate(_h.read().split("\n"), 1):
            _s = _lin.strip()
            _q = _s.count('"""') + _s.count("'''")
            if _in_doc:
                if _q % 2 == 1:
                    _in_doc = False
                continue
            if _q % 2 == 1:  # deschide docstring (nu single-line, care are q par)
                _in_doc = True
                continue
            if _s.startswith("#"):
                continue
            _brand_flag(os.path.basename(_rel), _i, _cod_fara_comentariu_py(_lin))


# --- GHID_ZONA (DS cap.22): continutul ghidurilor sub aceleasi reguli ca orice interfata ---
rap["ghid_zona"] = []
_GHID_MD = os.path.join(BAZA_PY, "ghid")
if os.path.isdir(_GHID_MD):
    _re_hex = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
    for _gf in sorted(os.listdir(_GHID_MD)):
        if not _gf.endswith(".md"):
            continue
        for _gi, _gl in enumerate(open(os.path.join(_GHID_MD, _gf), encoding="utf-8"), 1):
            _st = _gl.strip()[:60]
            if _re_hex.search(_gl):
                rap["ghid_zona"].append((_gf, _gi, "culoare", "hex literal - foloseste tokeni (cap.15): " + _st))
            if re.search(r"style\s*=", _gl):
                rap["ghid_zona"].append((_gf, _gi, "stil-inline", "style= inline interzis - clase+tokeni: " + _st))
            if re.search(r"font-size", _gl, re.I):
                rap["ghid_zona"].append((_gf, _gi, "tipografie", "font-size literal - scara cap.14: " + _st))
            if re.search(r"border-radius", _gl, re.I):
                rap["ghid_zona"].append((_gf, _gi, "raza", "border-radius literal - var(--raza) cap.15: " + _st))
            if re.search(r"<svg|<path", _gl, re.I):
                rap["ghid_zona"].append((_gf, _gi, "icoane", "SVG inline - foloseste ICOANE canonic (cap.13): " + _st))

# --- GARD GRI COTA (verde / ACCEPTAT / gri / rosu): fiecare cota literala e VIZIBILA, nu tacuta.
# Inlocuieste ratchet-ul pe numar brut (opac) cu un REGISTRU clasificat (31.07.2026):
#   VERDE    = cota din common.cota("tva_standard") period-aware (nu apare ca literal aici).
#   ACCEPTAT = etalon de test (golden/fixture; regula ETALON, DECIZII 31.07) SAU parametru de
#              generator pur prin design (def foo(cota_tva=21)). Temei cunoscut, NU e datorie.
#   GRI      = literal de productie ne-atasat la sursa, dar cu TEMEI IDENTIFICABIL. Datorie
#              VIZIBILA si localizata (fisier:linie:valoare:semantica:temei). Ratchet doar pe GRI.
#   ROSU     = literal fara temei identificabil (temei=???) -> flag RISC, BLOCHEAZA mereu.
# Acceptatele nu se numara (nu sunt datorie - altfel ratchet-ul le urmareste la infinit pentru nimic).
GRI_BASELINE = 2   # masurat 31.07.2026 dupa reparatia granitelor API (main.py: agregare pe rata)
_re_tva_dec = re.compile(r"(?<![\w.])0\.(?:21|19|11)(?![\w])")
_re_tva_int = re.compile(r"(?<![\w.])(?:21|19|11)(?![\w.%])")
_TVA_EXCLUSE = {"common.py", "verificator_conformitate.py", "cote_tva.py",
                "d406.py", "d300.py", "d301.py", "d390.py", "d394.py", "amef_import.py",
                "export_winmentor.py"}
# valoare -> (semantica, temei): sursa unica a citarii. Valoare care NU e aici -> temei=??? -> ROSU.
_TVA_TEMEI = {
    "21": ("cota standard 21%", "Legea 141/2025 art.291(1) CF, de la 01.08.2025"),
    "0.21": ("cota standard 21%", "Legea 141/2025 art.291(1) CF, de la 01.08.2025"),
    "11": ("cota redusa 11%", "Legea 141/2025 art.291(2) CF, de la 01.08.2025"),
    "0.11": ("cota redusa 11%", "Legea 141/2025 art.291(2) CF"),
    "19": ("cota standard istorica 19%", "Legea 227/2015, pana la 31.07.2025"),
    "0.19": ("cota standard istorica 19%", "Legea 227/2015"),
}
_re_param_cota = re.compile(r'''cota\w*\s*=\s*21\b|\.get\(\s*["']cota["']\s*,\s*21\s*\)''')
def _clasa_cota(_fis, _lin):
    if "alin" in _lin.lower():          # referinta legala in docstring ("alin. 11") - nu e o cota
        return None
    if "test" in _fis:
        return "ACCEPTAT"               # etalon golden/fixture (regula ETALON)
    if _re_param_cota.search(_lin):
        return "ACCEPTAT"               # parametru de generator pur, prin design
    return "GRI"                        # literal de productie ne-atasat, cu temei cunoscut
_gri_reg = {"ACCEPTAT": [], "GRI": [], "ROSU": []}
for _r2, _d2, _f2 in os.walk(BAZA_PY):
    if "venv" in _r2 or "/." in _r2 or "_arhiva" in _r2 or "/static" in _r2 or "/duk" in _r2:
        continue
    if os.path.relpath(_r2, BAZA_PY) not in (".", "core"):
        continue
    for _f in _f2:
        if not _f.endswith(".py") or _f in _TVA_EXCLUSE:
            continue
        _rel = os.path.relpath(os.path.join(_r2, _f), BAZA_PY)
        for _i, _ln in enumerate(open(os.path.join(_r2, _f), encoding="utf-8", errors="replace"), 1):
            _st = _ln.strip()
            if _st.startswith("#"):
                continue
            _md = _re_tva_dec.search(_ln)
            _mi = _re_tva_int.search(_ln) if "cota" in _ln.lower() else None
            if not (_md or _mi):
                continue
            _val = _md.group(0) if _md else _mi.group(0)
            _clasa = _clasa_cota(_rel, _st)
            if _clasa is None:
                continue
            _sem, _temei = _TVA_TEMEI.get(_val, ("necunoscut", "???"))
            if _temei == "???":
                _clasa = "ROSU"          # fara temei identificabil -> RISC
            _gri_reg[_clasa].append((_rel, _i, _val, _sem, _temei))
_n_gri = len(_gri_reg["GRI"]); _n_rosu = len(_gri_reg["ROSU"])
if _n_gri > GRI_BASELINE or _n_rosu:
    rap["cota_gri_rosu"] = []
    if _n_gri > GRI_BASELINE:
        rap["cota_gri_rosu"].append(("REGRESIE-GRI", _n_gri, "base=%d" % GRI_BASELINE,
            "cota GRI noua (%d > %d) - ataseaza temeiul sau ia din common.cota" % (_n_gri, GRI_BASELINE)))
    for _h in _gri_reg["ROSU"]:
        rap["cota_gri_rosu"].append(("ROSU-RISC", _h[1], _h[0],
            "cota %s fara temei identificabil (=???) - RISC, cerceteaza la sursa" % _h[2]))
print("\n### REGISTRU GRI COTA (verde/acceptat/gri/rosu):")
print("  ACCEPTAT %d (golden/fixture + parametri generator, temei cunoscut - NU datorie) | "
      "GRI %d (baseline %d) | ROSU %d%s" % (len(_gri_reg["ACCEPTAT"]), _n_gri, GRI_BASELINE,
      _n_rosu, "  <== BLOCHEAZA" if (_n_gri > GRI_BASELINE or _n_rosu) else ""))
for _h in _gri_reg["GRI"]:
    print("  GRI   %s:%d  %-5s %-28s %s" % (_h[0], _h[1], _h[2], _h[3], _h[4]))
for _h in _gri_reg["ROSU"]:
    print("  ROSU  %s:%d  %-5s %-28s temei=??? RISC" % (_h[0], _h[1], _h[2], _h[3]))
if _n_gri < GRI_BASELINE:
    print("  -> grii reparate: coboara GRI_BASELINE la %d in verificator." % _n_gri)

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
