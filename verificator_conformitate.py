# verificator_conformitate.py — v2: AUDIT COMPLET DE CONFORMITATE (Design System)
# /opt/iconta/venv/bin/python3 verificator_conformitate.py
# v2 adauga: BANI (sume afisate fara formator), SPATIERE (Total0,00), MENIURI (dialecte),
# CULORI_HARDCODATE (stiluri inline in afara tokenilor), ETICHETE (campuri doar cu placeholder)
import re, os
_RAD = os.path.dirname(os.path.abspath(__file__))   # rădăcina depozitului, din fișierul însuși (C35)

BAZA = os.path.join(_RAD, "static/js/ecrane")

CUVINTE = ["inca", "raspuns", "adauga", "sterge", "stergi", "cauta", "fara",
           "numar", "incarca", "gaseste", "banca", "plata", "pastreaza",
           "creeaza", "urmator", "dispozitie", "noua", "incasare", "asteapta", "asteptare",
           "genereaza", "blocheaza", "deblocheaza", "valideaza", "editeaza", "salveaza", "renunta",
           "astazi", "productia", "sesizari", "prioritatile"]
RE_CUV = re.compile(r'[">\s(](' + "|".join(CUVINTE) + r')[\s.,:!?<")]', re.IGNORECASE)
CLASE_BUTON_OK = {"buton-primar", "buton-secundar", "buton-sters", "buton-verde",
                  "buton-mic", "btn-link", "btn-nav", "buton-activ", "ajutor-btn"}
# componente structurale si selectoare de optiune — limbaj propriu, nu butoane de actiune (Design System v1.1)
CLASE_COMPONENTA_OK = {"firme-optiune", "cab-card", "acces-card", "meniu-card", "sub-inapoi",
                       "firme-inapoi", "rap-tab", "ac-per", "mig-dec", "vf-opt", "sa-asist",
                       "val-btn", "mf-font-opt", "mf-culoare-opt", "pagina-card-buton",
                       "pagina-bara-acces", "pacm-x", "acces-x", "rec-modal-x", "pf-frand", "func-card"}  # func-card = selector card grupa (F203), ca cab-card/acces-card/meniu-card
# culori-token permise inline (semafor canonic + entitate + fir)
ZEBRA_INTERZISE = {"#fdeef2", "#eaf2fb", "#f4f7fb", "#f7f8fa"}  # alternante vechi, inlocuite de STANDARD_ZEBRA
CULORI_OK = {"#1d7a4d", "#c9961f", "#ff3b30", "#1d4ed8", "#5b6b7c", "#1d3a5f", "#8a97a5", "#e11d1d"}

fisiere = {}
# [ds_frontend_integral_v1] verificatorul acopera TOT frontendul, nu doar ecrane/: static/js/*.js
# (app.js/navigator.js/sesiune.js/api.js) intra sub aceleasi reguli DS. api.js = SURSA canonica
# (esc/ICOANE/paleta culori) -> exceptata la regulile de registru (redef-esc/strip-html/icoane/culoare_card_hex).
_DIRS_FRONTEND = [BAZA, os.path.join(_RAD, "static/js")]
for _d in _DIRS_FRONTEND:
    for f in sorted(os.listdir(_d)):
        if f.endswith(".js") and ".bak" not in f and f not in fisiere:
            with open(os.path.join(_d, f), encoding="utf-8") as h:
                fisiere[f] = h.read()

rap = {k: [] for k in ["hex_semafor", "culoare_card_hex", "diacritice", "precompletari", "butoane", "entitate_in_titlu",
                        "dialog_browser", "bani_neformatati", "spatiere", "culori_hardcodate",
                        "etichete_lipsa", "input_contrast", "antet", "camp_dialect", "mig_text", "input_neconform", "fmt_local", "data_dialect", "data_bruta", "icoane_local", "font_inline", "radius_inline", "card_inline", "checkbox_dialect", "caseta_info", "stare_goala", "poarta_inline",
                        "esc_local", "caseta_atentie", "backend_ui_brut", "verdict_colapsat", "default_fiscal_tacit", "card_regim", "import_versiune", "verdict_paritate", "mirror_campuri_lipsa", "filtrare_inainte_validare", "stare_goala_eroare", "clasif_select"]}
meniuri = {}

for nume, t in fisiere.items():
    linii = t.split("\n")
    for i, lin in enumerate(linii, 1):
        # [ds_frontend_integral_v1] nu se flagueste cod COMENTAT (linie intreaga // sau /* * <!--);
        # cod comentat nu e comportament livrat (evita fals-pozitive pe marcaje ca "// alert() INTERZIS").
        if lin.strip().startswith(("//", "/*", "*", "<!--")):
            continue
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
        # MIRROR_CAMPURI_LIPSA (cap.24 pct.4): frontendul NU tine o a doua functie de campuri-lipsa care
        # oglindeste validarea backend (oglinda drifteaza - dovedit valoare_fara_tva). Validarea per-camp pe
        # randuri = backend; frontendul consuma raspunsul de eroare (cap.6). e-Transport + emitere = EXCEPTIE
        # declarata pana la batch 3 (ca test_g10_eroare_langa_camp / lista G10-A).
        # cap.24: G10 NU mai are exceptii dupa batch 3b (e-Transport 3a + emitere 3b restructurate).
        if re.search(r"(function\s+|const\s+|let\s+|var\s+)[A-Za-z0-9_]*[Cc]ampuri[A-Za-z0-9_]*[Ll]ipsa", lin):
            rap["mirror_campuri_lipsa"].append((nume, i, "", lin.strip()[:66]))
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
        # [lotul 12, 184] și cu argument cu punct / indice (`String(r.luna)`, `String(b.dataset.luna)`), nu numai un nume simplu
        if re.search(r'String\([\w.\[\]"]+\)\.padStart\(2, ?"0"\)\}/\$\{', lin):
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
        if (re.search(r'\bfunction\s+esc\s*\(', lin) or re.search(r'\b(?:const|let|var)\s+esc\s*=', lin)) and nume != "api.js":
            rap["esc_local"].append((nume, i, "redef-esc", lin.strip()[:60]))
        # ESC_LOCAL extins v3 (cap.10): STRIP inline de caractere HTML (.replace(/[...<>&...]/,...)) ca sanitizare
        # ad-hoc in loc de esc canonic. NU e XSS (scoate <>), dar e DATA-LOSSY (scoate & din nume: "A&B"->"AB") si
        # o a doua sursa de sanitizare. Prinde orice clasa de caractere care contine TOATE din <>& (robust la
        # reordonare/caractere extra). api.js (sursa canonica) e in static/js/, nescanat -> fara auto-flag.
        for _ms in re.finditer(r'\.replace\(\s*/\[([^\]]*)\]/', lin):
            if all(ch in _ms.group(1) for ch in "<>&") and nume != "api.js":  # api.js = corpul esc canonic
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
            if not re.search(r'_bani|toLocaleString|fmt|bani\(|pretUnitar\(', expr):   # pretUnitar = costul unitar canonic (DS cap.4 v2.69)
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
        # INPUT_NECONFORM (decizie Costin 11.08): orice <input>/<select> NORMAL fara .camp-input.
        # DS 2.1: input/select normale poarta EXCLUSIV .camp-input. Extinde MIG_TEXT la TOATA clasa
        # (.pr-input/.asi-per-sel/em-*-input/dlg-input etc.). Exclus tipuri ne-text.
        for _tm in re.finditer(r"<(input|select)\b([^>]*?)/?>", lin):
            _at = _tm.group(2)
            _ty = re.search(r'type="(\w+)"', _at)
            if _ty and _ty.group(1) in ("checkbox", "radio", "hidden", "file", "submit", "button", "range", "color"):
                continue
            if "camp-input" not in _at:
                rap["input_neconform"].append((nume, i, "", lin.strip()[:66]))
        # CLASIF_SELECT (DS cap.28, A12b): un <select> de CLASIFICARE per-linie pe un ecran de validare
        # a documentelor importate (marcat prin clasa `pr-dest`) trebuie sa poarte `aria-label`
        # (regula 1: control accesibil, criteriul fiscal in .camp-ajutor). `.camp-input` e deja cerut
        # de INPUT_NECONFORM; aici se adauga aria-label, pe care INPUT_NECONFORM nu-l verifica.
        for _cs in re.finditer(r"<select\b([^>]*\bpr-dest\b[^>]*)>", lin):
            if "aria-label" not in _cs.group(1):
                rap["clasif_select"].append((nume, i, "fara-aria", lin.strip()[:66]))
        # INPUT_NECONFORM prin createElement (decizie Costin 11.08 seara, inchide gaura tag-urilor
        # literale): input/select construit programatic (document.createElement) fara .camp-input in
        # fereastra (linia + urmatoarele 4, unde se seteaza className/classList/setAttribute).
        _ce = re.search(r"""createElement\(\s*['"](input|select)['"]""", lin)
        if _ce and "camp-input" not in " ".join(linii[i - 1:i + 4]):
            rap["input_neconform"].append((nume, i, "createElement", lin.strip()[:66]))
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
            if nume != "api.js":  # api.js = dictionarul ICOANE canonic (sursa), nu duplicat local
                rap["icoane_local"].append((nume, i, "", lin.strip()[:60]))
        # FONT_INLINE: font-size cu valoare literala inline (px/em) in loc de var(--text-*) sau clasa .tip-*
        for fm in re.finditer(r'font-size:\s*([0-9.]+(?:px|em|rem))', lin):
            rap["font_inline"].append((nume, i, fm.group(1), lin.strip()[:56]))
        # HEX_SEMAFOR: culori de semafor literale in loc de var(--rosu-semafor)/var(--galben)/var(--verde). Exceptii: definitia tokenilor si gradientul dot:
        if re.search(r'#(ff3b30|c9961f|1d7a4d|9aa3b2|3a4250)\b', lin, re.I) and '--rosu-semafor:' not in lin and '--galben:' not in lin and '--verde:' not in lin and '--gri-semafor:' not in lin and '--gri-fundal-semafor:' not in lin and 'dot:' not in lin:
            rap["hex_semafor"].append((nume, i, "", lin.strip()[:66]))
        # CULOARE_CARD_HEX: bg:/fg: cu hex literal pe carduri in loc de ...CULORI_CARD.cheie (exceptie: semafor control.js, are dot:)
        if re.search(r'\b(bg|fg)\s*:\s*"#', lin) and 'dot:' not in lin and nume != "api.js":
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
BAZA_PY = _RAD
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
BAZA_JS = os.path.join(_RAD, "static/js")
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

# [P7 · valul use-case, 13.09.2026] Cele trei felii de mai jos (`_verificari_contabile`,
# `_construieste_contabil`, `VC_FARA_SEVERITATE`) sunt despre MUNCA verdictului, nu despre protocol —
# iar munca a plecat din `main.py` in `core/uc_*.py`. Se citeste sursa STRATULUI DE APLICATIE, cap la
# cap: altfel taietura iese goala si verificatorul raporteaza „n-am putut extrage", ceea ce e corect
# ca semnal, dar despre instrument, nu despre cod.
import sys as _sys_uc
if BAZA_PY not in _sys_uc.path:
    _sys_uc.path.insert(0, BAZA_PY)
from core import scan_sql_efectiv as _efectiv_uc  # noqa: E402
_main_src = _efectiv_uc.sursa_aplicatie()
# chei PRODUSE: dict-ul `rezultat = {...}` din _verificari_contabile + orice rezultat["x"] = ...
# Nu din sursa lipita: acolo `def _verificari_contabile` apare de DOUA ori — invelisul din
# `main.py`, care n-are corp, si munca din `core/uc_comun.py`. Accesorul da functia CU CORP.
_vf = _efectiv_uc.sursa_functiei("_verificari_contabile") or ""
_produse = set()
_mrez = re.search(r'rezultat\s*=\s*\{(.*?)\n    \}', _vf, re.S)
if _mrez:
    _produse |= set(re.findall(r'"(\w+)"\s*:', _mrez.group(1)))
_produse |= set(re.findall(r'rezultat\[\s*"(\w+)"\s*\]\s*=', _vf))
# chei PLIATE in contabil (severitate): vc.get("x") + tuplul (cheie, eticheta) din _construieste_contabil
_cc = _efectiv_uc.sursa_functiei("_construieste_contabil") or ""
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

_BRAND_STATIC = os.path.join(_RAD, "static")
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
GRI_BASELINE = 0   # PRAG (nu ratchet) de la 01.08.2026: cele 2 GRI (main.py bucketing OCR) atasate la common.cota. Regula 01.08 (ciclul>ratchet): la 0, orice GRI nou BLOCHEAZA.
_re_tva_dec = re.compile(r"(?<![\w.])0\.(?:21|19|11)(?![\w])")
_re_tva_int = re.compile(r"(?<![\w.])(?:21|19|11)(?![\w.%])")
# `scan_constante.py` intra aici 21.08.2026, in aceeasi clasa cu verificator_conformitate.py si
# cote_tva.py: nu e cod fiscal, e un INSTRUMENT DE MASURA care citeaza cote ca exemple in proza
# ("ca `art. 21` sa nu treaca drept cota 21"). N-are si nu poate avea logica de cota - orice 21 din
# el e text despre masuratoare. Alternativa era rescrierea prozei ca sa ocoleasca regexul, adica
# exact felul de ajustare care face un gard sa para verde fara sa se fi schimbat nimic.
# `denumiri_randuri.py` intra 19.10.2026 (comanda 8.2, deficienta 379): e GENERAT din textul ordinelor ANAF (`scripts/denumiri_randuri.py`,
# garda `core/test_denumiri_randuri.py`) — „taxabile cu cota 11%” e denumirea oficiala a randului D300, nu o cota folosita la calcul.
_TVA_EXCLUSE = {"common.py", "verificator_conformitate.py", "cote_tva.py", "scan_constante.py",
                "d406.py", "d300.py", "d300_reconciliere.py", "d301.py", "d390.py", "d394.py", "amef_import.py",
                "export_winmentor.py", "denumiri_randuri.py"}
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
_re_ref_deficienta = re.compile(r"deficien\w*\s+(?:nr\.\s*)?(?:21|19|11)(?![\w.%])", re.I)
def _clasa_cota(_fis, _lin):
    if "alin" in _lin.lower():          # referinta legala in docstring ("alin. 11") - nu e o cota
        return None
    # [lotul 12] numarul unei deficiente din registru („ca la cota de pe linia facturii (deficiența 21, …)”) - nu e o cota;
    # o cota 21 adevarata pe acelasi rand ramane prinsa doar daca apare a doua oara (vezi `_re_tva_int` pe restul randului)
    if _re_ref_deficienta.search(_lin) and not _re_tva_int.search(_re_ref_deficienta.sub("", _lin)) \
            and not _re_tva_dec.search(_lin):
        return None
    if "test" in _fis:
        return "ACCEPTAT"               # etalon golden/fixture (regula ETALON)
    if _re_param_cota.search(_lin):
        return "ACCEPTAT"               # parametru de generator pur, prin design
    return "GRI"                        # literal de productie ne-atasat, cu temei cunoscut
_gri_reg = {"ACCEPTAT": [], "GRI": [], "ROSU": [], "EXCLUS": []}
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
            # [lotul 11] comentariul de la capătul liniei nu e cod (ca linia-comentariu de mai sus): „# [lotul 11, …]” lângă un câmp
            # „cota” se citea drept cota 11 (12 fals pozitive). Separatorul e cel PEP 8 (două spații + „# ”), deci un „#” din șir rămâne.
            _ln = re.split(r"\s{2,}#\s", _ln, 1)[0]
            _md = _re_tva_dec.search(_ln)
            _mi = _re_tva_int.search(_ln) if "cota" in _ln.lower() else None
            if not (_md or _mi):
                continue
            _val = _md.group(0) if _md else _mi.group(0)
            _clasa = _clasa_cota(_rel, _st)
            if _clasa is None:
                _gri_reg["EXCLUS"].append((_rel, _i, _val, "referinta (alin. / nr. deficientei), nu cota"))
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
_n_acc = len(_gri_reg["ACCEPTAT"]); _n_excl = len(_gri_reg["EXCLUS"])
_n_tot = _n_acc + _n_gri + _n_rosu + _n_excl
print("  TOTAL scanat %d = ACCEPTAT %d + GRI %d + ROSU %d + EXCLUS %d%s" % (
      _n_tot, _n_acc, _n_gri, _n_rosu, _n_excl,
      "  <== BLOCHEAZA" if (_n_gri > GRI_BASELINE or _n_rosu) else ""))
print("  ACCEPTAT = etalon golden/fixture + parametri generator (temei cunoscut, NU datorie) | "
      "GRI baseline %d | EXCLUS = referinta legala alin. in docstring (nu e cota)" % GRI_BASELINE)
for _h in _gri_reg["GRI"]:
    print("  GRI    %s:%d  %-5s %-28s %s" % (_h[0], _h[1], _h[2], _h[3], _h[4]))
for _h in _gri_reg["ROSU"]:
    print("  ROSU   %s:%d  %-5s %-28s temei=??? RISC" % (_h[0], _h[1], _h[2], _h[3]))
for _h in _gri_reg["EXCLUS"]:
    print("  EXCLUS %s:%d  %-5s %s" % (_h[0], _h[1], _h[2], _h[3]))
if _n_gri < GRI_BASELINE:
    print("  -> grii reparate: coboara GRI_BASELINE la %d in verificator." % _n_gri)

# --- GARD TEMEI STRUCTURAT (common.COTE): fiecare valoare fiscala poarta un Temei structurat
# (act/nr/an/art/alin/lit/data_in/data_out/url), nu string liber. Structurat = grep-abil la o
# schimbare de lege + data_out (garda de EXPIRARE, mecanismul principal de deriva - nu exista API
# legislativ RO fiabil). Ratchet: baseline = intrari INCA cu temei string (0 dupa etapa 2); orice
# intrare noua cu string in loc de Temei -> BLOCHEAZA.
TEMEI_BASELINE = 0
try:
    from core.common import COTE as _COTE, Temei as _Temei
    _cote_string = []
    for _nume, _intrari in _COTE.items():
        for _e in _intrari:
            if not isinstance(_e[2], _Temei):
                _cote_string.append((_nume, 0, "string", "temei nestructurat - foloseste common.Temei(act/nr/an/...)"))
    if len(_cote_string) > TEMEI_BASELINE:
        rap["temei_nestructurat"] = _cote_string
    print("")
    print("### GARD TEMEI STRUCTURAT (common.COTE):")
    print("  intrari COTE cu temei string (nestructurat): %d (baseline %d)%s" % (
        len(_cote_string), TEMEI_BASELINE,
        "  <== BLOCHEAZA" if len(_cote_string) > TEMEI_BASELINE else ""))
except Exception as _etemei:
    print("")
    print("### GARD TEMEI STRUCTURAT: NEVERIFICAT (import COTE esuat: %s)" % _etemei)

# --- GARD NIVEL_SURSA (ETAPA 2 Model de temei, 01.08): fiecare Temei din COTE poarta nivel_sursa
# (MO/REDARE/INTERPRETARE_OFICIALA/PRACTICA) - gri-ul (verificat la MO vs dedus din pliant) incape in
# STRUCTURA, nu intr-un comentariu. text_citat (verbatim) obligatoriu DOAR la nivel_sursa=MO (proba).
# PRAG 0: orice Temei fara nivel_sursa valid, sau MO fara text_citat, BLOCHEAZA.
try:
    from core.common import COTE as _CO, Temei as _Tm
    _ns_lipsa, _mo_fara_text = [], []
    for _nm, _intr in _CO.items():
        for _din, _v, _t in _intr:
            _ns = getattr(_t, "nivel_sursa", None)
            if _ns not in _Tm.NIVELE_SURSA:
                _ns_lipsa.append("%s@%s" % (_nm, _din))
            elif _ns == "MO" and not getattr(_t, "text_citat", None):
                _mo_fara_text.append("%s@%s" % (_nm, _din))
    if _ns_lipsa or _mo_fara_text:
        rap["nivel_sursa"] = ([("FARA-NIVEL", 0, x, "Temei COTE fara nivel_sursa valid") for x in _ns_lipsa] +
                              [("MO-FARA-TEXT", 0, x, "nivel_sursa=MO fara text_citat (proba verbatim)") for x in _mo_fara_text])
    print("")
    print("### GARD NIVEL_SURSA (COTE, PRAG 0):")
    print("  temeiuri fara nivel_sursa: %d | MO fara text_citat: %d%s" % (
        len(_ns_lipsa), len(_mo_fara_text), "  <== BLOCHEAZA" if (_ns_lipsa or _mo_fara_text) else ""))
except Exception as _ens:
    print("")
    print("### GARD NIVEL_SURSA: NEVERIFICAT (%s)" % _ens)

# --- GARD MARKERI TEMEI PE FUNCTII (lista EXPLICITA, 01.08.2026): criteriul STRUCTURAL (functie cu
# literal Decimal("0.NN") SAU care cheama cota()) MINTE in ambele sensuri - masurat: 57 functii prinse,
# ~18 fals-pozitive (helper-e de rotunjire _q/bani/_dec cu Decimal("0.01")) + 2 fals-negative din lista
# reala (calcul_cm, plafon_diurna). Un proxy sintactic nu separa regula fiscala de rotunjire (avertismentul
# lui Costin). Solutia ONESTA = lista INTRETINUTA MANUAL a functiilor care APLICA o regula fiscala cu
# logica proprie (scara degresiva, prorata, plafonare, contributii); gardul cere marker "TEMEI:" in
# docstring DOAR pe ele. PRAG 0: orice functie din lista fara marker BLOCHEAZA. LIMITA DECLARATA: nu se
# auto-detecteaza - o functie fiscala noua se ADAUGA aici + primeste marker (nu "cand vine clusterul").
_TEMEI_FUNCTII = [
    ("core/salarizare.py", "deducere_personala"),
    ("core/salarizare.py", "calcul_salariu"),
    ("core/salarizare.py", "procent_cm"),
    ("core/salarizare.py", "taxe_cm"),
    ("core/salarizare.py", "calcul_cm"),
    ("core/salarizare.py", "calcul_cm_cod10"),
]
try:
    import ast as _ast_tf
    _tf_fara, _tf_lipsa = [], []
    for _rel, _fn in _TEMEI_FUNCTII:
        _cale = os.path.join(BAZA_PY, _rel)
        if not os.path.exists(_cale):
            _tf_lipsa.append((_rel, _fn)); continue
        _tree = _ast_tf.parse(open(_cale, encoding="utf-8").read())
        _gasit = False
        for _n in _ast_tf.walk(_tree):
            if isinstance(_n, _ast_tf.FunctionDef) and _n.name == _fn:
                _gasit = True
                _doc_tf = _ast_tf.get_docstring(_n) or ""
                if "TEMEI:" not in _doc_tf or "nivel_sursa" not in _doc_tf:
                    _tf_fara.append((_rel, _fn))
                break
        if not _gasit:
            _tf_lipsa.append((_rel, _fn))
    if _tf_fara or _tf_lipsa:
        rap["temei_functii"] = (
            [("FARA-MARKER", 0, "%s::%s" % (r, f), "functie fiscala din lista fara marker TEMEI: in docstring") for r, f in _tf_fara] +
            [("FUNCTIE-LIPSA", 0, "%s::%s" % (r, f), "functie din _TEMEI_FUNCTII negasita - actualizeaza lista") for r, f in _tf_lipsa])
    print("")
    print("### GARD MARKERI TEMEI PE FUNCTII (lista explicita, PRAG 0):")
    print("  functii sub gard: %d | fara marker: %d | negasite: %d%s" % (
        len(_TEMEI_FUNCTII), len(_tf_fara), len(_tf_lipsa),
        "  <== BLOCHEAZA" if (_tf_fara or _tf_lipsa) else ""))
    for _r, _f in _tf_fara:
        print("  FARA MARKER: %s::%s" % (_r, _f))
    for _r, _f in _tf_lipsa:
        print("  NEGASITA: %s::%s" % (_r, _f))
except Exception as _etf:
    print("")
    print("### GARD MARKERI TEMEI PE FUNCTII: NEVERIFICAT (%s)" % _etf)


# --- GARD VERSIONARE FORMULE (PAS 4, 01.08.2026): fiecare functie care APLICA o regula fiscala (scara,
# prorata, plafonare, split, procent pe conditie - NU doar citeste o cota) trebuie sa fie un DISPECER pe
# la_data: corpul cheama alege_varianta(_VARIANTE_*, ...). Cotele erau deja period-aware (cota); formulele
# devin period-aware asa - o schimbare de regula se adauga ca varianta datata, nu 'if data'. Fara gard,
# urmatoarea functie de regula scrisa e iar single-body si o adeverinta/rectificativa pe o luna TRECUTA o
# recalculeaza cu regula de AZI (bugul campaniei). Ratchet adus la PRAG 0 in aceeasi campanie (toate cele 13
# convertite 01.08). PRAG 0: orice functie din lista fara dispecer BLOCHEAZA. LIMITA DECLARATA: lista
# INTRETINUTA MANUAL (ca _TEMEI_FUNCTII - proxy sintactic "e regula fiscala?" minte); o functie de regula
# noua se ADAUGA aici + primeste dispecer. Nu prinde o functie de regula NEtrecuta pe lista (acelasi
# compromis constient ca la markeri).
VERSIONARE_BASELINE = 0
_VERSIONARE_FUNCTII = [
    ("core/salarizare.py", "deducere_personala"),
    ("core/salarizare.py", "calcul_salariu"),
    ("core/salarizare.py", "procent_cm"),
    ("core/salarizare.py", "taxe_cm"),
    ("core/salarizare.py", "calcul_cm"),
    ("core/salarizare.py", "calcul_cm_cod10"),
    ("core/deconturi.py", "plafon_diurna"),
    ("core/sponsorizari.py", "plafon_credit"),
    ("core/sponsorizari.py", "credit_sponsorizare"),
    ("core/motor.py", "rezerva_legala"),
    ("core/contracte_speciale.py", "calcul_zilier"),
    ("core/tva_marja.py", "vanzare_marja"),
    ("core/tva_marja_turism.py", "marja_turism_special"),
]
try:
    import ast as _ast_vf
    _vf_fara, _vf_lipsa = [], []
    for _rel, _fn in _VERSIONARE_FUNCTII:
        _cale = os.path.join(BAZA_PY, _rel)
        if not os.path.exists(_cale):
            _vf_lipsa.append((_rel, _fn)); continue
        _tree = _ast_vf.parse(open(_cale, encoding="utf-8").read())
        _gasit = False
        for _n in _ast_vf.walk(_tree):
            if isinstance(_n, _ast_vf.FunctionDef) and _n.name == _fn:
                _gasit = True
                _are = False
                for _cc in _ast_vf.walk(_n):
                    if isinstance(_cc, _ast_vf.Call):
                        _cf = _cc.func
                        if ((getattr(_cf, "attr", None) == "alege_varianta" or getattr(_cf, "id", None) == "alege_varianta")
                                and _cc.args and isinstance(_cc.args[0], _ast_vf.Name)
                                and _cc.args[0].id.startswith("_VARIANTE")):
                            _are = True
                            break
                if not _are:
                    _vf_fara.append((_rel, _fn))
                break
        if not _gasit:
            _vf_lipsa.append((_rel, _fn))
    _vf_viol = len(_vf_fara) + len(_vf_lipsa)
    if _vf_viol > VERSIONARE_BASELINE:
        rap["versionare_formule"] = (
            [("FARA-DISPECER", 0, "%s::%s" % (r, f), "functie de regula fara dispecer alege_varianta(_VARIANTE_*, la_data)") for r, f in _vf_fara] +
            [("FUNCTIE-LIPSA", 0, "%s::%s" % (r, f), "functie din _VERSIONARE_FUNCTII negasita - actualizeaza lista") for r, f in _vf_lipsa])
    print("")
    print("### GARD VERSIONARE FORMULE (dispecer pe la_data, PRAG %d):" % VERSIONARE_BASELINE)
    print("  functii de regula: %d | fara dispecer: %d | negasite: %d%s" % (
        len(_VERSIONARE_FUNCTII), len(_vf_fara), len(_vf_lipsa),
        "  <== BLOCHEAZA" if _vf_viol > VERSIONARE_BASELINE else ""))
    for _r, _f in _vf_fara:
        print("  FARA DISPECER: %s::%s" % (_r, _f))
    for _r, _f in _vf_lipsa:
        print("  NEGASITA: %s::%s" % (_r, _f))
except Exception as _evf:
    print("")
    print("### GARD VERSIONARE FORMULE: NEVERIFICAT (%s)" % _evf)


# --- GARD BLOCAJ MOTIVAT PE COTE DE REGULA (PAS 3, 01.08.2026): orice cota citita de o functie de regula
# fiscala, cu data_in mai TARZIE decat common.DATA_START_SISTEM (podeaua datelor de calcul salarial), trebuie
# sa produca un blocaj MOTIVAT (common.PerioadaIndisponibila, tag PERIOADA_BLOCATA -> handler main.py -> 423)
# cand e ceruta pentru o perioada din [podea, data_in), NU o exceptie bruta (500/traceback in UI). Fara asta,
# o adeverinta/rectificativa pentru o luna in care functia are ALTFEL date (ex. 2025: salariu_minim exista,
# plafon_facilitate nu) crapa cu traceback la contabil. Mecanismul e CENTRAL (cota() ridica PerioadaIndisponibila
# pentru orice pre-data) -> gardul PROBEAZA runtime ca fiecare cota de regula late-start produce chiar blocajul
# motivat. PRAG 0: orice cota de regula late-start care ridica ALTCEVA (exceptie bruta) BLOCHEAZA. Ratchet daca
# apar restante. Cotele care rup un calcul FRECVENT (nu doar retroactiv) - vezi nota tva_redusa in DECIZII/GARZI.
BLOCAJ_MOTIVAT_BASELINE = 0
try:
    from core import common as _cm_bm, graf_temei as _gt_bm
    _graf_bm = _gt_bm.construieste_graf()
    _cote_regula = set()
    for _rel, _fn in _VERSIONARE_FUNCTII:          # cotele citite de cele 13 reguli (direct + prin variante)
        for _cand in (_fn, "_%s_2018" % _fn, "_%s_core" % _fn):
            if _cand in _graf_bm:
                _cote_regula |= _graf_bm[_cand]["cote"]
    _bm_restante, _bm_late = [], []
    for _k in sorted(_cote_regula):
        if _k not in _cm_bm.COTE:
            continue
        _start = min(_r[0] for _r in _cm_bm.COTE[_k])
        if _start <= _cm_bm.DATA_START_SISTEM:
            continue                                # acoperita de la podea in jos - nu rupe in range-ul suportat
        _bm_late.append((_k, _start))
        try:
            _cm_bm.cota(_k, _cm_bm.DATA_START_SISTEM)   # < _start -> TREBUIE sa ridice blocaj motivat
            _bm_restante.append((_k, "NU RIDICA"))
        except _cm_bm.PerioadaIndisponibila:
            pass                                    # corect: blocaj motivat
        except Exception as _ex_bm:
            _bm_restante.append((_k, "exceptie bruta: %s" % type(_ex_bm).__name__))
    if len(_bm_restante) > BLOCAJ_MOTIVAT_BASELINE:
        rap["blocaj_motivat"] = [("EXCEPTIE-BRUTA", 0, "%s (%s)" % (_k, _m),
            "cota de regula late-start fara blocaj motivat - crapa cu traceback in UI") for _k, _m in _bm_restante]
    print("")
    print("### GARD BLOCAJ MOTIVAT PE COTE DE REGULA (PRAG %d):" % BLOCAJ_MOTIVAT_BASELINE)
    print("  cote de regula late-start (data_in > %s): %d | fara blocaj motivat: %d%s" % (
        _cm_bm.DATA_START_SISTEM.isoformat(), len(_bm_late), len(_bm_restante),
        "  <== BLOCHEAZA" if len(_bm_restante) > BLOCAJ_MOTIVAT_BASELINE else ""))
    for _k, _st in _bm_late:
        print("  LATE-START: %-34s start=%s  (blocaj motivat pt [%s, %s))" % (
            _k, _st.isoformat(), _cm_bm.DATA_START_SISTEM.isoformat(), _st.isoformat()))
    for _k, _m in _bm_restante:
        print("  RESTANTA: %s (%s)" % (_k, _m))
except Exception as _ebm:
    print("")
    print("### GARD BLOCAJ MOTIVAT PE COTE DE REGULA: NEVERIFICAT (%s)" % _ebm)


# --- GARD PERIOADA CONFIRMATA (cap.23 DS, 02.08.2026): un calcul care depinde de o PERIOADA confirmabila
# (azi: pontaj, prin tichete) trebuie sa verifice confirmarea (perioada.e_confirmat) si sa blocheze motivat
# (PerioadaNeconfirmata) cand nu e confirmata - altfel "prezent = fara rand" trece tacut o luna necompletata.
# Criteriul structural ("ce calcul depinde de perioada?") e semantic -> LISTA EXPLICITA intretinuta manual (ca
# _TEMEI_FUNCTII). PRAG 0: o functie din lista fara verificarea confirmarii BLOCHEAZA. LIMITA: o functie noua
# dependenta de perioada se ADAUGA aici (nu se auto-detecteaza). Controlul UI foloseste primitivele canonice
# (buton-verde/confirmaCaseta/semafor) - pazit de regulile vizuale existente (HEX_SEMAFOR, BUTOANE).
# (fisier, functie, semnale acceptate pt "perioada neconfirmata" - pe langa e_confirmat obligatoriu)
# [#1/#3] stat_plata NU mai blocheaza TOT statul (deadlock: 423 omora ecranul -> butonul Pontaj inaccesibil
# -> pontajul nu se putea confirma). Semnaleaza per-salariat prin flag pontaj_neconfirmat (tichete=0) SAU
# blocheaza motivat. d112.pull ramane BLOCAJ HARD (o DECLARATIE nu se depune pe o luna necompletata).
_PERIOADA_FUNCTII = [
    ("core/stat_plata_api.py", "stat_plata", ("PerioadaNeconfirmata", "pontaj_neconfirmat")),
    ("core/d112.py", "pull", ("PerioadaNeconfirmata",)),
]
try:
    import ast as _ast_pf
    _pf_fara, _pf_lipsa = [], []
    for _rel, _fn, _semnale in _PERIOADA_FUNCTII:
        _cale = os.path.join(BAZA_PY, _rel)
        if not os.path.exists(_cale):
            _pf_lipsa.append((_rel, _fn)); continue
        _tree = _ast_pf.parse(open(_cale, encoding="utf-8").read())
        _gasit = _are = False
        for _n in _ast_pf.walk(_tree):
            if isinstance(_n, _ast_pf.FunctionDef) and _n.name == _fn:
                _gasit = True
                _refs = set()
                for _x in _ast_pf.walk(_n):
                    _v = getattr(_x, "attr", None) or getattr(_x, "id", None)
                    if _v:
                        _refs.add(_v)
                    if isinstance(_x, _ast_pf.Constant) and isinstance(_x.value, str):
                        _refs.add(_x.value)   # flag-uri contractuale (ex. "pontaj_neconfirmat") sunt string keys
                if "e_confirmat" in _refs and any(_sg in _refs for _sg in _semnale):
                    _are = True
                break
        if not _gasit:
            _pf_lipsa.append((_rel, _fn))
        elif not _are:
            _pf_fara.append((_rel, _fn))
    if _pf_fara or _pf_lipsa:
        rap["perioada_confirmata"] = (
            [("FARA-VERIFICARE", 0, "%s::%s" % (r, f), "calcul dependent de perioada fara e_confirmat+PerioadaNeconfirmata") for r, f in _pf_fara] +
            [("FUNCTIE-LIPSA", 0, "%s::%s" % (r, f), "functie din _PERIOADA_FUNCTII negasita - actualizeaza lista") for r, f in _pf_lipsa])
    print("")
    print("### GARD PERIOADA CONFIRMATA (lista explicita, PRAG 0):")
    print("  calcule dependente de perioada: %d | fara verificarea confirmarii: %d | negasite: %d%s" % (
        len(_PERIOADA_FUNCTII), len(_pf_fara), len(_pf_lipsa),
        "  <== BLOCHEAZA" if (_pf_fara or _pf_lipsa) else ""))
    for _r, _f in _pf_fara:
        print("  FARA VERIFICARE: %s::%s" % (_r, _f))
except Exception as _epf:
    print("")
    print("### GARD PERIOADA CONFIRMATA: NEVERIFICAT (%s)" % _epf)


# --- GARD IZOLARE TENANTI (structural, CODEBASE-WIDE): orice ruta cu {tenant_id} in path care
# deschide get_conn TREBUIE sa rezolve accesul - prin auth_api.schema_tenant SAU printr-un RESOLVER
# (functie al carei corp cheama schema_tenant SAU scopeaza public.tenants pe accounting_firm_id/
# user_tenants, ex. _api_schema pt API-key). Enumereaza rutele din TOT codebase-ul (@<var>.<verb>),
# nu doar main.py @app - ca sa nu taca la migrarea spre APIRouter / fisiere separate. META-GARD:
# semnaleaza un APIRouter definit dar nemontat (rute posibil neverificate). Ratchet: baseline 0.
IZOLARE_BASELINE = 0
def analiza_izolare(rad):
    """Analiza gardului de IZOLARE TENANTI, extrasa ca FUNCTIE (23.08.2026).

    Logica e neschimbata; singura diferenta e ca primeste radacina in loc s-o ia din BAZA_PY. De ce:
    datoria din 31.07.2026 (core/test_datorie.py) spune ca *instrumentul care masoara conformitatea nu
    e el insusi masurat* - verificatorul produsese 13 FALS-POZITIVE prin propriul bug (regexul de rute
    rata `async def`), iar un gard cu fals-pozitive se dezactiveaza si moare, unul cu fals-NEGATIVE
    tace pe un leak real. Ca sa poata fi testat pe FIXTURI known-good / known-bad, analiza trebuie sa
    fie apelabila pe o radacina oarecare - altfel testul ar reimplementa logica, adica logica paralela.

    Intoarce: {gap, resolveri, route_files, router_defs, meta}.
    """
    _iz_files = []
    for _r, _d, _fs in os.walk(rad):
        if any(_x in _r for _x in ("venv", "/.", "_arhiva", "/static", "/duk", "node_modules")):
            continue
        for _f in _fs:
            if _f.endswith(".py") and not _f.startswith("test_"):
                _iz_files.append(os.path.join(_r, _f))
    _redefn = re.compile(r"(\s*)(?:async )?def (\w+)\(")
    _reroute = re.compile(r"\s*@(\w+)\.(get|post|put|delete|patch)\(")
    _reredef = re.compile(r"\s*(?:async )?def ")
    _repath = re.compile(r"@\w+\.\w+\(.([^\"]+)")
    _redn = re.compile(r"(?:async )?def (\w+)")

    # [P7 · valul D4, 13.09.2026] Corpul unei functii include si sursa functiilor de DEPOZIT pe
    # care le cheama prin `_repo.` — un singur pas, numai catre `core/repo_*.py`. Fara asta, dupa
    # ce valul a mutat instructiunile, doua rute `/api/v1/firme/{tenant_id}/…` au aparut ca
    # LEAK-POTENTIAL desi rezolvarea de acces era neatinsa: se mutase, nu disparuse.
    _iz_depozit = {}
    _dir_repo = os.path.join(rad, "core")
    if os.path.isdir(_dir_repo):
        for _fr in sorted(os.listdir(_dir_repo)):
            if not (_fr.startswith("repo_") and _fr.endswith(".py")):
                continue
            _sr = open(os.path.join(_dir_repo, _fr), encoding="utf-8").read().split("\n")
            _poz = [(_i, _ln[4:_ln.index("(")]) for _i, _ln in enumerate(_sr)
                    if _ln.startswith("def ") and "(" in _ln]
            for _q, (_i, _nm) in enumerate(_poz):
                _sf = _poz[_q + 1][0] if _q + 1 < len(_poz) else len(_sr)
                _iz_depozit.setdefault(_nm, []).append("\n".join(_sr[_i:_sf]))

    def _cu_depozit(_bd):
        _extra = [_s for _nm, _lst in _iz_depozit.items() if ("_repo.%s(" % _nm) in _bd
                  for _s in _lst]
        return _bd + ("\n" + "\n".join(_extra) if _extra else "")

    def _iz_resolver(_bd):
        _bd = _cu_depozit(_bd)
        return ("schema_tenant" in _bd or
                ("public.tenants" in _bd and ("accounting_firm_id" in _bd or "user_tenants" in _bd)))

    _resolveri = set()
    _route_files = []
    _router_defs = []
    for _p in _iz_files:
        _src = open(_p, encoding="utf-8").read()
        _ls = _src.split("\n")
        _ds = []
        for _i, _l in enumerate(_ls):
            _m = _redefn.match(_l)
            if _m:
                _ds.append((_i, _m.group(2), len(_m.group(1))))
        _ds.append((len(_ls), "__end__", 0))
        for _k in range(len(_ds) - 1):
            _j = _k + 1
            while _j < len(_ds) and _ds[_j][2] > _ds[_k][2]:
                _j += 1
            # `analiza_izolare` e UNEALTA, nu cod de aplicatie: contine "schema_tenant" in
            # predicatul ei si s-ar numara singura ca resolver (183 -> 184) dupa ce a fost
            # extrasa in functie. Taietura e pe NUME, nu pe fisier: excluderea intregului
            # `verificator*` ar fi scos si doi resolveri numarati dinainte (183 -> 181), adica
            # ar fi schimbat comportamentul in loc sa-l pastreze.
            if _ds[_k][1] == "analiza_izolare":
                continue
            if _iz_resolver("\n".join(_ls[_ds[_k][0]:_ds[_j][0]])):
                _resolveri.add(_ds[_k][1])
        if _reroute.search(_src):
            _route_files.append(_p)
        for _mm in re.finditer(r"(\w+)\s*=\s*APIRouter\(", _src):
            _router_defs.append((_p, _mm.group(1)))
    _iz_gap = []
    for _p in _route_files:
        _ls = open(_p, encoding="utf-8").read().split("\n")
        _starts = []
        for _i, _l in enumerate(_ls):
            if _reroute.match(_l):
                _j = _i + 1
                while _j < len(_ls) and not _reredef.match(_ls[_j]):
                    _j += 1
                _starts.append((_i, _j))
        _starts.append((len(_ls), len(_ls)))
        for _k in range(len(_starts) - 1):
            _deci, _defi = _starts[_k]
            _decs = "\n".join(_ls[_deci:_defi]); _b = "\n".join(_ls[_defi:_starts[_k+1][0]])
            if "{tenant_id}" not in _decs:
                continue
            _dm = _redn.search(_b); _dn = _dm.group(1) if _dm else ""
            _atinge = "get_conn(" in _b
            _ok = _iz_resolver(_b) or any(_rr in _b for _rr in _resolveri if _rr and _rr != _dn)
            if _atinge and not _ok:
                _pm = _repath.search(_decs)
                _iz_gap.append((os.path.basename(_p), _pm.group(1) if _pm else "?", _dn or "?"))
    _allsrc = "\n".join(open(_p, encoding="utf-8").read() for _p in _iz_files)
    _meta = [(os.path.basename(_pf), _rv) for _pf, _rv in _router_defs
             if ("include_router(%s" % _rv) not in _allsrc]
    return {"gap": _iz_gap, "resolveri": _resolveri, "route_files": _route_files,
            "router_defs": _router_defs, "meta": _meta}


try:
    _rez_iz = analiza_izolare(BAZA_PY)
    _iz_gap = _rez_iz["gap"]
    _resolveri = _rez_iz["resolveri"]
    _route_files = _rez_iz["route_files"]
    _router_defs = _rez_iz["router_defs"]
    _meta = _rez_iz["meta"]
    if len(_iz_gap) > IZOLARE_BASELINE or _meta:
        rap["izolare_fara_acces"] = (
            [("LEAK-POTENTIAL", 0, _pp, "ruta {tenant_id} atinge DB fara acces in %s: %s" % (_ff, _dd)) for _ff, _pp, _dd in _iz_gap]
            + [("META-ROUTER", 0, _ff, "APIRouter %s definit dar nemontat - rute posibil neverificate" % _rv) for _ff, _rv in _meta])
    print("")
    print("### GARD IZOLARE TENANTI (codebase-wide: %d fisiere-rute, %d resolveri, %d routere):" % (
        len(_route_files), len(_resolveri), len(_router_defs)))
    print("  rute {tenant_id} care ating DB fara acces: %d (baseline %d)%s" % (
        len(_iz_gap), IZOLARE_BASELINE, "  <== BLOCHEAZA" if (len(_iz_gap) > IZOLARE_BASELINE or _meta) else ""))
    for _ff, _pp, _dd in _iz_gap:
        print("  GAP %-42s %s (%s)" % (_pp, _dd, _ff))
    for _ff, _rv in _meta:
        print("  META APIRouter %s NEMONTAT (%s)" % (_rv, _ff))
except Exception as _eiz:
    print("")
    print("### GARD IZOLARE TENANTI: NEVERIFICAT (%s)" % _eiz)

# --- GARD CONTRACT GENERATOARE dXXX (A1, 31.07.2026): fiecare modul core/dNNN.py cu `def genereaza`
# TREBUIE sa expuna contractul uniform - pull(), erori_generare(), calcul_dNNN(), build_xml(),
# genereaza(conn, schema, perioada, ...). Pasul 4 din CICLUL DE NECONFORMITATE: fara gard, al zecelea
# generator nu respecta contractul. Ratchet: NECONFORM poate doar SCADEA (baseline 9 la start; coboara
# pe masura ce se converteste fiecare modul; la 0, orice modul neconform BLOCHEAZA).
CONTRACT_BASELINE = 2   # [06.10.2026, lotul 07.10] d112 convertit (pasul D1): 3 -> 2
try:
    _dgen = []
    for _f in sorted(os.listdir(os.path.join(BAZA_PY, "core"))):
        _mm = re.match(r"^(d\d+)\.py$", _f)
        if not _mm:
            continue
        _src = open(os.path.join(BAZA_PY, "core", _f), encoding="utf-8").read()
        if not re.search(r"\ndef genereaza\(conn, schema", _src):
            continue
        _nm = _mm.group(1)
        _lips = []
        if not re.search(r"\ndef pull\(", _src):
            _lips.append("pull")
        if not re.search(r"\ndef erori_generare\(", _src):
            _lips.append("erori_generare")
        if not re.search(r"\ndef calcul_%s\(" % _nm, _src):
            _lips.append("calcul_%s" % _nm)
        if not re.search(r"\ndef build_xml\(", _src):
            _lips.append("build_xml")
        if not re.search(r"\ndef genereaza\(conn, schema, perioada", _src):
            _lips.append("genereaza(perioada)")
        if _lips:
            _dgen.append((_nm, _lips))
    _n_neconf = len(_dgen)
    if _n_neconf > CONTRACT_BASELINE:
        rap["contract_dXXX"] = [("NECONFORM", 0, _nm, "lipsesc din contract: " + ", ".join(_lp)) for _nm, _lp in _dgen]
    print("")
    print("### GARD CONTRACT GENERATOARE dXXX (uniform):")
    print("  module neconforme: %d (baseline %d)%s" % (
        _n_neconf, CONTRACT_BASELINE, "  <== BLOCHEAZA" if _n_neconf > CONTRACT_BASELINE else ""))
    for _nm, _lp in _dgen:
        print("  NECONFORM %-6s lipsesc: %s" % (_nm, ", ".join(_lp)))
    if _n_neconf < CONTRACT_BASELINE:
        print("  -> module convertite: coboara CONTRACT_BASELINE la %d in verificator." % _n_neconf)
except Exception as _ectr:
    print("")
    print("### GARD CONTRACT GENERATOARE: NEVERIFICAT (%s)" % _ectr)

# --- GARD POARTA BAZEI NULE (A, 31.07.2026): fiecare generator de declaratie (criteriu COMPORTAMENTAL
# `def genereaza(conn, schema`, NU nume dNNN - altfel bilant/S1003/S1005 era ratat) TREBUIE sa expuna
# erori_generare(). Fara ea, o declaratie depusa la ANAF poate iesi pe profil incomplet fara semnal.
# PRAG (nu ratchet): baseline 0 - nu exista motiv sa lipseasca vreodata. Separat de contract (siguranta
# != uniformitate).
BAZANULA_BASELINE = 0
try:
    _bn_lipsa = []
    _bn_n = 0
    for _f in sorted(os.listdir(os.path.join(BAZA_PY, "core"))):
        if not _f.endswith(".py") or _f.startswith("test_") or _f == "declaratii_api.py":
            continue
        _src = open(os.path.join(BAZA_PY, "core", _f), encoding="utf-8").read()
        if not re.search(r"\ndef genereaza\(conn, schema", _src):
            continue
        _bn_n += 1
        if not re.search(r"\ndef erori_generare\(", _src):
            _bn_lipsa.append(_f)
    if len(_bn_lipsa) > BAZANULA_BASELINE:
        rap["baza_nula_poarta"] = [("FARA-POARTA", 0, _f, "generator fara erori_generare - poate iesi pe profil incomplet") for _f in _bn_lipsa]
    print("")
    print("### GARD POARTA BAZEI NULE (generatoare de declaratii):")
    print("  generatoare fara erori_generare: %d din %d (baseline %d)%s" % (
        len(_bn_lipsa), _bn_n, BAZANULA_BASELINE, "  <== BLOCHEAZA" if len(_bn_lipsa) > BAZANULA_BASELINE else ""))
    for _f in _bn_lipsa:
        print("  FARA POARTA: %s" % _f)
except Exception as _ebn:
    print("")
    print("### GARD POARTA BAZEI NULE: NEVERIFICAT (%s)" % _ebn)

# --- GARD E1 / E2 (DS cap.26 si cap.27, 28.08.2026): cele doua reguli de ecran, pe STRUCTURA.
#
# E1 - un atribut al aceleiasi entitati tinut in DOUA locuri: nodul de randare care declara perechea
#      (`data-e1`) trebuie sa NUMEASCA sursa care produce efectul si sa nu taca despre niciuna. O
#      sursa pe care ecranul n-o are se DECLARA lipsa (`data-e1-absent`), nu se trece sub tacere.
#      PRAG 0, nu clichet: un nod declarat pe jumatate e chiar defectul din care s-a scris regula
#      (F1 - caseta de alegere a denumirii spunea ca eticheta din portofoliu pleaca in documente).
#
# E2 - un act cu efect asupra unei entitati se incheie cu o confirmare vizibila. CLICHET, nu prag:
#      4 din 7 acte de nivel firma se termina azi in tacere, iar repararea lor e R82, nu tura asta.
#
# DE CE NU AICI CIFRELE: sursa unica e core/scan_ecran_reguli.py, citita si de core/test_reguli_ecran.py.
# Doua clichete pe acelasi lucru se pot desparti in tacere - lectia R62 („regula era in doua locuri
# si diferita"). Verificatorul afiseaza si blocheaza; nu tine numar propriu.
rap["e1_pereche_incompleta"] = []
rap["e2_act_fara_confirmare"] = []
try:
    import sys as _sys_ser
    if BAZA_PY not in _sys_ser.path:
        _sys_ser.path.insert(0, BAZA_PY)
    from core import scan_ecran_reguli as _ser
    _e1_nec, _e1_ner = _ser.scaneaza_e1()
    _e1_declarate = sum(len(_ser.perechi_pe_ecran(open(_c, encoding='utf-8').read()))
                        for _c in _ser._fisiere_ecran())
    for _f, _l, _k, _cod, _m in _e1_nec:
        rap["e1_pereche_incompleta"].append((_f, _l, _k, _m))
    for _k in _e1_ner:
        rap["e1_pereche_incompleta"].append(
            ("REGISTRU", 0, _k, "pereche declarata in PERECHI pe care niciun ecran n-o mai arata"))
    _e2_fara, _e2_toate = _ser.scaneaza_e2()
    if len(_e2_fara) > _ser.CLICHET_E2_FARA_CONFIRMARE:
        for _f, _l, _a, _r in _e2_fara:
            rap["e2_act_fara_confirmare"].append((_f, _l, _a, _r))
    if len(_e2_toate) != _ser.CLICHET_E2_ACTE:
        rap["e2_act_fara_confirmare"].append(
            ("REGISTRU", 0, "ANTI-VACUU",
             "clasa actelor de nivel firma are %d membri, nu %d - o ruta redenumita ar goli clasa"
             % (len(_e2_toate), _ser.CLICHET_E2_ACTE)))
    print("")
    print("### GARD E1 (DS cap.26 — doua nume distincte, si care produce efectul):")
    print("  noduri care declara o pereche: %d · neconforme: %d (prag 0)%s" % (
        _e1_declarate, len(_e1_nec), "  <== BLOCHEAZA" if _e1_nec else ""))
    for _f, _l, _k, _c, _m in _e1_nec:
        print("  NECONFORM %-30s %5d  [%s] %s" % (_f, _l, _k, _m))
    print("  perechi din registru nerandate: %d %s" % (len(_e1_ner), _e1_ner or ""))
    print("### GARD E2 (DS cap.27 — actul se incheie cu o confirmare vizibila):")
    print("  acte de nivel firma fara confirmare: %d din %d (clichet %d din %d)%s" % (
        len(_e2_fara), len(_e2_toate), _ser.CLICHET_E2_FARA_CONFIRMARE, _ser.CLICHET_E2_ACTE,
        "  <== BLOCHEAZA" if len(_e2_fara) > _ser.CLICHET_E2_FARA_CONFIRMARE else ""))
    for _f, _l, _a, _r in _e2_fara:
        print("  TACUT  %-30s %5d  %-9s %s" % (_f, _l, _a, _r))
    if not _e2_fara:
        print("  toate actele de nivel firma confirma vizibil (R82 inchisa 28.08.2026)")
    if len(_e2_fara) < _ser.CLICHET_E2_FARA_CONFIRMARE:
        print("  -> a scazut la %d: coboara CLICHET_E2_FARA_CONFIRMARE in core/scan_ecran_reguli.py"
              % len(_e2_fara))
except Exception as _e_ser:
    rap["e1_pereche_incompleta"].append(("verificator", 0, "EROARE", "gard E1/E2: " + str(_e_ser)))

# --- GARD VERDICT RUTE (S1, 28.08.2026 — decizia (c) la R80): GRI NU SE FALSIFICA IN VERDE.
#
# Detectorul de apelanti (R70) avea doua raspunsuri — „are apelant" si „n-are". Cele 45 de rute pe
# care ancora literala nu le identifica (R80) cadeau, PRIN CONSTRUCTIE, in primul: ancora lor apare
# peste tot, deci verificarea „toate bucatile sunt in JS" e mereu adevarata. Orbirea se citea VERDE.
#
# Principiul, din DECIZII 15.07.2026 (filozofia control_incrucisat): *gri nu se falsifica in verde*.
# De azi fiecare ruta primeste unul din patru verdicte, si GRI se numara SEPARAT, aici, in raportul
# portii — nu se topeste in ACCEPTAT.
#
# CLICHET, nu prag: 45 e orbirea de azi, iar (a) si (b) din R80 sunt DEFERATE. Blocheaza numai
# cresterea, si orice ROSU.
# [lotul 12, 12.2, 24.10.2026] 7 -> 11: segmentul `facturi` a trecut pragul de 40 (41 de referinte de ruta, ultima din emitere_ecran.js, 304);
# au orbit GET/POST /tenants/{id}/facturi si GET/DELETE /tenants/{id}/facturi/{factura_id}. Cauza, la `_CLICHET` in core/test_ancore_rute.py.
RUTE_GRI_CLICHET = 11   # 45 -> 49 -> 7 in aceeasi zi (30.08.2026): a doua mutare e REPARATIA R80 —
                        # ancora a devenit SEGMENT DE CALE, nu cuvant. Cauza, la `_CLICHET` in
                        # core/test_ancore_rute.py.
rap["rute_verdict"] = []
try:
    import sys as _sys_rv
    if os.path.join(BAZA_PY, "scripts") not in _sys_rv.path:
        _sys_rv.path.insert(0, os.path.join(BAZA_PY, "scripts"))
    if BAZA_PY not in _sys_rv.path:
        _sys_rv.path.insert(0, BAZA_PY)
    from scan_ancore_rute import rezumat as _rezumat_rute
    _rv_total, _rv = _rezumat_rute()
    print("")
    print("### GARD VERDICT RUTE (R70/R80 — gri nu se falsifica in verde):")
    print("  TOTAL rute %d = ACCEPTAT %d + GRI %d + ROSU %d + EXCLUS %d  (clichet GRI %d)%s" % (
        _rv_total, _rv["ACCEPTAT"], _rv["GRI"], _rv["ROSU"], _rv["EXCLUS"], RUTE_GRI_CLICHET,
        "  <== BLOCHEAZA" if (_rv["ROSU"] or _rv["GRI"] > RUTE_GRI_CLICHET) else ""))
    print("  GRI = detectorul nu poate afirma nimic despre ele. NU sunt verzi.")
    if _rv["ROSU"]:
        rap["rute_verdict"].append(("rute", 0, "ROSU",
                                    "%d rute fara apelant si nedeclarate" % _rv["ROSU"]))
    if _rv["GRI"] > RUTE_GRI_CLICHET:
        rap["rute_verdict"].append(("rute", 0, "GRI",
                                    "orbirea a crescut de la %d la %d"
                                    % (RUTE_GRI_CLICHET, _rv["GRI"])))
    if _rv["GRI"] < RUTE_GRI_CLICHET:
        print("  -> orbirea a scazut la %d: coboara RUTE_GRI_CLICHET (si cifra din R80)."
              % _rv["GRI"])
except Exception as _e_rv:
    rap["rute_verdict"].append(("verificator", 0, "EROARE", "gard verdict rute: " + str(_e_rv)))

print("=" * 92)
print("RAPORT DE CONFORMITATE v2 — Design System")
print("=" * 92)
# --- FILTRARE_INAINTE_VALIDARE (cap.24 regula 2, 08.08.2026): `linii` (variabila SAU cheie de payload)
# construit printr-un `.filter(...)` = lista trimisa != lista randata -> un rand incomplet dispare tacit.
# Backendul e poarta autoritara per-linie (cap.24 regula 4 / cap.6 mecanism A); frontendul NU filtreaza
# randuri inainte de validare. Multi-linie (prinde si `const linii =\n  .filter(`). FARA EXCEPTII: cele 4
# ecrane purtatoare (emitere + e-Transport 3a/3b; facturi-recurente + retete a771f25; NIR + inventar azi) conforme.
_re_r2 = re.compile(r"(?:\blinii:\s*|\b(?:const|let|var)\s+linii\s*=\s*)[^;]{0,140}?\.filter\(", re.S)
for _nume, _t in fisiere.items():
    for _m in _re_r2.finditer(_t):
        _ln = _t[:_m.start()].count("\n") + 1
        rap["filtrare_inainte_validare"].append((_nume, _ln, "", " ".join(_t[_m.start():_m.start()+70].split())))

# --- STARE_GOALA_EROARE (cap.6 v2.13, 09.08.2026): un catch (EROARE de incarcare) randat prin .stare-goala.
# stare-goala = CONTINUT (lista cu 0 randuri: gol+cauza+iesire), NU mesaj de eroare (DS cap.6). Eroarea de
# load merge la .ecran-nota / arataMesaj. Multi-linie (catch { ... stare-goala). Frontend integral.
_re_sge = re.compile(r"catch\s*(?:\([^)]*\))?\s*\{[^{}]{0,220}?stare-goala", re.S)
for _nume, _t in fisiere.items():
    for _m in _re_sge.finditer(_t):
        _ln = _t[:_m.start()].count("\n") + 1
        rap["stare_goala_eroare"].append((_nume, _ln, "", " ".join(_t[_m.start():_m.start()+70].split())))

# --- GARD SCROLL PAGINI PUBLICE (DS cap.22 §7): shell-urile publice folosesc scroll de document.
#     Nu mostenesc html,body{overflow-y:hidden} (app/landing). Marcheaza html+body cu .pagina-publica,
#     iar stil.css readuce overflow-y:auto pe .pagina-publica. Fara asta pagina se taie la primul ecran
#     si componentele de sub fold par "text simplu". Mutatia care il probeaza: scoate clasa dintr-un shell
#     public sau override-ul din stil.css -> aceasta lista devine nevida -> TOTAL > 0 -> poarta rosie.
rap["scroll_public"] = []
try:
    _css_sp = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
    _main_sp = open(os.path.join(BAZA_PY, "main.py"), encoding="utf-8").read()
    if re.search(r"html\s*,\s*body\s*\{[^}]*overflow-y\s*:\s*hidden", _css_sp) and \
       not re.search(r"\.pagina-publica[^{]*\{[^}]*overflow-y\s*:\s*auto", _css_sp):
        rap["scroll_public"].append(("static/stil.css", 0, "scroll",
            "html,body overflow-y:hidden fara override .pagina-publica:auto (DS cap.22 §7)"))
    for _sh in ("_GHID_PAGINA", "_TERMENI_PAGINA"):
        _msp = re.search(_sh + r'\s*=\s*"""(.*?)"""', _main_sp, re.S)
        if not _msp:
            rap["scroll_public"].append(("main.py", 0, _sh, "shell public negasit - nu pot verifica .pagina-publica"))
            continue
        _blk = _msp.group(1)
        _ok_html = re.search(r'<html[^>]*class="[^"]*pagina-publica', _blk)
        _ok_body = re.search(r'<body[^>]*class="[^"]*pagina-publica', _blk)
        if not (_ok_html and _ok_body):
            rap["scroll_public"].append(("main.py", 0, _sh,
                "shell public fara .pagina-publica pe html+body (DS cap.22 §7) -> se taie la primul ecran"))
except Exception as _e_sp:
    rap["scroll_public"].append(("verificator", 0, "EROARE", "gard scroll_public: " + str(_e_sp)))

# --- GARD SCROLL DESKTOP (DS cap.22 §7, deficiența 321, 18.10.2026): cu html,body{overflow-y:hidden}, shell-ul aplicației
#     (`.desktop`, navigator.js) derulează EL ÎNSUȘI: înălțime fixă (100dvh) + overflow-y:auto. Fără asta, ce trece sub ecran
#     (cardurile „Primii pași” împing „De depus” / „Firme” în jos) nu se mai ajunge cu rotița. Mutația: scoate overflow-y:auto
#     sau pune min-height în loc de height pe `.desktop` -> lista nevidă -> TOTAL > 0.
rap["scroll_desktop"] = []
try:
    _css_sd = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
    if re.search(r"html\s*,\s*body\s*\{[^}]*overflow-y\s*:\s*hidden", _css_sd):
        _decl_sd = " ".join(m.group(1) for m in re.finditer(r"(?m)^\.desktop\s*\{([^}]*)\}", _css_sd))
        if not (re.search(r"(?<![-\w])height\s*:\s*100dvh", _decl_sd) and re.search(r"overflow-y\s*:\s*auto", _decl_sd)):
            rap["scroll_desktop"].append(("static/stil.css", 0, ".desktop",
                "shell-ul aplicației fără height:100dvh + overflow-y:auto, sub html,body{overflow-y:hidden} -> rotița nu derulează (321)"))
except Exception as _e_sd:
    rap["scroll_desktop"].append(("verificator", 0, "EROARE", "gard scroll_desktop: " + str(_e_sd)))

# --- GARD BARA ANTET FIXA (DS cap.2, lotul 8 — comanda Costin 7.3 pct.3, 18.10.2026): antetul aplicației (`.bara-antet`: bara de sus,
#     bara de stare cu „Versiune nouă”, bara 3) e copilul lui `.desktop`, care derulează el însuși (321): fără `position: sticky; top: 0`
#     pe `.desktop > .bara-antet`, anunțul „Versiune nouă” iese din ecran la derulare. Mutația: scoate regula -> TOTAL > 0.
rap["bara_antet_fixa"] = []
try:
    _css_ba = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
    _decl_ba = " ".join(m.group(1) for m in re.finditer(r"(?m)^\.desktop\s*>\s*\.bara-antet\s*\{([^}]*)\}", _css_ba))
    if not (re.search(r"position\s*:\s*sticky", _decl_ba) and re.search(r"(?<![-\w])top\s*:\s*0", _decl_ba)):
        rap["bara_antet_fixa"].append(("static/stil.css", 0, ".bara-antet",
            "antetul aplicației nu e sticky sus în `.desktop` -> bara de stare („Versiune nouă”) iese din ecran la derulare"))
except Exception as _e_ba:
    rap["bara_antet_fixa"].append(("verificator", 0, "EROARE", "gard bara_antet_fixa: " + str(_e_ba)))

# --- TINTA BIFEI (DS cap.2, decizia Costin 02.10.2026 — DECIZII „Căsuțele .set-bifa rămân de 16px"): căsuța
#     are 16px, ținta de clic e ETICHETA `<label class="set-bifa">`, care trebuie să rămână >= 24px (WCAG 2.5.8 AA).
#     Premisa deciziei se ține prin `min-height` pe regula globală; fără ea, o micșorare de padding/font coboară
#     ținta sub prag fără să se aprindă nimic. Mutația care o probează: scoate `min-height` din `.set-bifa` (sau
#     pune 20px) -> lista nevidă -> TOTAL > 0 -> poarta roșie.
rap["tinta_bifa"] = []
try:
    _css_tb = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
    _mtb = re.search(r"(?m)^\.set-bifa\s*\{([^}]*)\}", _css_tb)
    _mh = re.search(r"min-height\s*:\s*(\d+)px", _mtb.group(1)) if _mtb else None
    if not _mtb:
        rap["tinta_bifa"].append(("static/stil.css", 0, "set-bifa", "regula globala .set-bifa negasita (DS cap.2)"))
    elif not _mh or int(_mh.group(1)) < 24:
        rap["tinta_bifa"].append(("static/stil.css", 0, "set-bifa",
            ".set-bifa fara min-height >= 24px: tinta de clic (eticheta) poate cobori sub 24px (DS cap.2, WCAG 2.5.8)"))
except Exception as _e_tb:
    rap["tinta_bifa"].append(("verificator", 0, "EROARE", "gard tinta_bifa: " + str(_e_tb)))

# --- MESAJ_PE_RANDURI (DS cap.6 v2.89, retestul Costin 12.10.2026, deficiența 238): un refuz cu un rând pe cont (`\n`) se citește rând
#     cu rând numai dacă zonele de mesaj păstrează rândurile. Mutația care o probează: `white-space: normal` pe `.msg-eroare` -> lista
#     nevidă -> TOTAL > 0 -> poarta roșie.
rap["mesaj_pe_randuri"] = []
try:
    _css_mr = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
    # [lotul 11, 440, g2] + casetele care afișează textul serverului (`e.mesaj`) și `.pe-randuri` (caseta refuzului dintr-o clasă de
    # proză), declarate ÎMPREUNĂ într-o regulă comună (global-first) — de aceea `.cls` se caută și ca element al unei liste de selectori,
    # iar oricare regulă a clasei cu `pre-line` ajunge. Gardul pe locurile din JS: core/test_lot11_g2_pre_line.py
    for _cls in ("msg-eroare", "msg-avert", "msg-info", "msg-ok", "dec-eroare",   # [lotul 11, 440] caseta refuzului generării
                 "dec-avert-cap", "pacm-mail", "cp-mesaj", "val-lipsa", "anunt-text", "mig-eroare", "cf-semnal", "rn-mesaj",
                 "pe-randuri"):
        _mm = [_m for _m in re.finditer(r"(?m)^(?:[^{}\n]*,\s*)?\.%s\s*(?:,[^{}]*)?\{([^}]*)\}" % _cls, _css_mr)
               if re.search(r"white-space\s*:\s*pre-line", _m.group(1))]
        if not _mm:
            rap["mesaj_pe_randuri"].append(("static/stil.css", 0, _cls,
                ".%s fara white-space: pre-line — un mesaj cu un rand pe element s-ar citi pe un singur rand (DS cap.6 v2.89)" % _cls))
except Exception as _e_mr:
    rap["mesaj_pe_randuri"].append(("verificator", 0, "EROARE", "gard mesaj_pe_randuri: " + str(_e_mr)))

# --- GHID_ACTUALIZAT (DS cap.22 v2.90, comanda Costin 13.10.2026 pct.2c): fiecare ghid public poartă data ultimei actualizări sub titlu
#     (`.ghid-actualizat`, generată de `public_ghid`), cu tokenii textului secundar. Mutația care o probează: scoate `ghid-actualizat` din
#     `public_ghid` (main.py) sau regula din stil.css -> lista nevidă -> TOTAL > 0 -> poarta roșie.
rap["ghid_actualizat"] = []
try:
    _css_ga = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
    _mga = re.search(r"(?m)^\.ghid-actualizat\s*\{([^}]*)\}", _css_ga)
    if not _mga or not re.search(r"font-size\s*:\s*var\(--text-desc\)", _mga.group(1)) or not re.search(r"color\s*:\s*var\(--gri\)", _mga.group(1)):
        rap["ghid_actualizat"].append(("static/stil.css", 0, "ghid-actualizat",
            ".ghid-actualizat lipsa sau fara tokenii textului secundar (--text-desc, --gri) (DS cap.22 v2.90)"))
    _main_ga = open(os.path.join(BAZA_PY, "main.py"), encoding="utf-8").read()
    _fga = re.search(r"(?ms)^def public_ghid\(.*?(?=^def |^@app)", _main_ga)
    if not _fga or 'class="ghid-actualizat">Actualizat la ' not in _fga.group(0):
        rap["ghid_actualizat"].append(("main.py", 0, "public_ghid",
            "public_ghid nu mai pune „Actualizat la …” (.ghid-actualizat) sub titlul ghidului (DS cap.22 v2.90)"))
except Exception as _e_ga:
    rap["ghid_actualizat"].append(("verificator", 0, "EROARE", "gard ghid_actualizat: " + str(_e_ga)))

# --- DIALOG_FARA_INCHIDERE (DS cap.9 v2.64, comanda Costin 04.10.2026): orice fereastră suprapusă creată în JS se
#     închide prin mecanismul unic `inchidereDialog` (X în antet + Esc), SAU poartă pe linia creării marcajul
#     `fereastra-de-lucru: doar X` (fereastra cu câmpuri — Esc nu aruncă un formular). Instanța: bun-venitul se
#     închidea numai de la butonul de la capătul listei. Mutația care o probează: scoate apelul `inchidereDialog`
#     din `ecranBunVenit` (ansamblu.js) -> lista nevidă -> TOTAL > 0 -> poarta roșie.
rap["dialog_fara_inchidere"] = []
_re_ov = re.compile(r"""\.className\s*=\s*["'`]([^"'`]*overlay[^"'`]*)["'`]""")
for _nume, _t in fisiere.items():
    for _m in _re_ov.finditer(_t):
        _ln = _t[:_m.start()].count("\n") + 1
        _linie = _t[_t.rfind("\n", 0, _m.start()) + 1:_t.find("\n", _m.end())]
        if "fereastra-de-lucru:" in _linie:
            continue
        if "inchidereDialog(" in _t[_m.end():_m.end() + 2500]:
            continue
        rap["dialog_fara_inchidere"].append((_nume, _ln, _m.group(1)[:14],
            "fereastra suprapusa fara inchidereDialog (X + Esc) si fara marcaj fereastra-de-lucru (DS cap.9)"))

# --- HIDDEN_CU_DISPLAY (DS cap.2 v2.74, lotul 07.10 pct.20, comanda Costin 06.10.2026): un element `hidden` nu se vede.
#     (1) regula globală `[hidden] { display: none !important; }` stă în stil.css; (2) niciun șablon JS nu pune pe același
#     element `hidden` și `style="…display:…"` („NIR nou”, Casa ×2, Încasări/plăți stăteau deschise). Mutația care o
#     probează: `style="display:block;…"` pus la loc pe `#sn-zona` (firme.js) SAU regula globală scoasă -> TOTAL > 0.
rap["hidden_cu_display"] = []
_re_hid = re.compile(r"""<[a-z][^<>]*\shidden(?:\s|>|=)[^<>]*style\s*=\s*["'][^"']*\bdisplay\s*:|<[a-z][^<>]*style\s*=\s*["'][^"']*\bdisplay\s*:[^"']*["'][^<>]*\shidden(?:\s|>|=)""")
for _nume, _t in fisiere.items():
    for _m in _re_hid.finditer(_t):
        rap["hidden_cu_display"].append((_nume, _t[:_m.start()].count("\n") + 1, "hidden",
            "element `hidden` cu `display` inline: ascunderea nu se aplică (DS cap.2 v2.74)"))
try:
    _css_h = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
    if not re.search(r"^\[hidden\]\s*\{\s*display:\s*none\s*!important;\s*\}", _css_h, re.M):
        rap["hidden_cu_display"].append(("stil.css", 0, "[hidden]", "lipsește regula globală [hidden]{display:none!important} (DS cap.2 v2.74)"))
except Exception as _e_hid:
    rap["hidden_cu_display"].append(("stil.css", 0, "EROARE", "gard hidden: " + str(_e_hid)))

# --- MESAJ_FARA_ADUCERE_IN_VEDERE (DS cap.6 v2.74, lotul 07.10 pct.3): mesajul de după un buton se aduce în vedere — UN
#     mecanism, în api.js: `aduInVedere`, chemat de `arataMesaj` / `eroareCamp` / `confirmaCaseta`, plus observatorul pe
#     `SELECTOR_MESAJ`. Orice clasă de casetă de după-buton folosită în ecrane (`caseta-poarta`, `em-curs-box`) e în selector.
#     Mutația care o probează: `aduInVedere(el)` scos din `arataMesaj` SAU `.caseta-poarta` scos din SELECTOR_MESAJ -> TOTAL > 0.
rap["mesaj_fara_aducere_in_vedere"] = []
try:
    _api = fisiere.get("api.js", "")
    _fn = lambda nume: (re.search(r"export function %s\([^)]*\)\s*\{(.*?)\n\}" % nume, _api, re.S) or [None, ""])[1]
    if "export function aduInVedere(" not in _api:
        rap["mesaj_fara_aducere_in_vedere"].append(("api.js", 0, "aduInVedere", "lipsește aduInVedere (DS cap.6 v2.74)"))
    for _h in ("arataMesaj", "eroareCamp", "confirmaCaseta"):
        if "aduInVedere(" not in _fn(_h):
            rap["mesaj_fara_aducere_in_vedere"].append(("api.js", 0, _h, "%s nu aduce mesajul în vedere (DS cap.6 v2.74)" % _h))
    _sel = (re.search(r'SELECTOR_MESAJ\s*=\s*"([^"]+)"', _api) or [None, ""])[1]
    if "MutationObserver" not in _api or "SELECTOR_MESAJ" not in _api.split("MutationObserver", 1)[-1][:600]:
        rap["mesaj_fara_aducere_in_vedere"].append(("api.js", 0, "observator", "observatorul pe SELECTOR_MESAJ lipsește (DS cap.6 v2.74)"))
    # [lotul 12, deficiența 45] textul scris DIRECT într-o zonă de mesaj existentă (`rez.textContent = …`, clasa pusă după) — observatorul
    # trebuie să vadă și textul schimbat și clasa, nu numai nodurile adăugate. Mutația: `characterData: true` scos din `.observe(` -> TOTAL > 0.
    _obs = (re.search(r"new MutationObserver\(.*?\.observe\(document\.documentElement,\s*\{([^}]*)\}", _api, re.S) or [None, ""])[1]
    if not all(k in _obs for k in ("characterData: true", "attributes: true", "childList: true")):
        rap["mesaj_fara_aducere_in_vedere"].append(("api.js", 0, "observator", "observatorul nu vede textul scris direct într-o zonă de mesaj "
                                                    "(characterData / attributes) (DS cap.6 v2.74, deficiența 45)"))
    for _cls in ("caseta-poarta", "em-curs-box", "msg-eroare", "msg-avert"):
        if any(re.search(r'class="[^"]*\b%s\b' % _cls, _t) for _n, _t in fisiere.items() if _n != "api.js") and "." + _cls not in _sel:
            rap["mesaj_fara_aducere_in_vedere"].append(("api.js", 0, _cls, "clasa de casetă .%s lipsește din SELECTOR_MESAJ (DS cap.6 v2.74)" % _cls))
except Exception as _e_mv:
    rap["mesaj_fara_aducere_in_vedere"].append(("api.js", 0, "EROARE", "gard mesaj in vedere: " + str(_e_mv)))

# --- REFUZ_ECRAN_FARA_BUTON (DS cap.6 v2.74, lotul 07.10 pct.2): orice ținta `ecran` pusă de server într-un refuz are
#     ecran-destinație în `ecran_destinatie.js` (ECRANE), iar api.js pune butonul (`_butonSpreEcran`) pe drumurile de refuz.
#     Mutația care o probează: `date_firma` scos din ECRANE SAU apelul `_butonSpreEcran(eroare, cale)` scos din `_cere` -> TOTAL > 0.
rap["refuz_ecran_fara_buton"] = []
try:
    _ed = fisiere.get("ecran_destinatie.js", "")
    _chei_ecr = set(re.findall(r"^\s{2}([a-z_]+):\s*\{", _ed, re.M))
    _emise = set()
    for _r, _ds, _fs in os.walk(os.path.join(BAZA_PY, "core")):
        for _f in _fs:
            if _f.endswith(".py") and not _f.startswith("test_"):
                _src = open(os.path.join(_r, _f), encoding="utf-8").read()
                _emise |= set(re.findall(r"""\becran\s*=\s*["']([a-z_]+)["']""", _src))
                _emise |= set(re.findall(r"""\.ecran\s*=\s*(?:[^\n]*,\s*)?["']([a-z_]+)["']""", _src))
    for _e in sorted(_emise - {"numerotare"} - _chei_ecr):   # „numerotare”: refuzul seriei se rezolvă PE LOC, în emitere
        rap["refuz_ecran_fara_buton"].append(("ecran_destinatie.js", 0, _e, "ținta de refuz `%s` n-are ecran-destinație (DS cap.6 v2.74)" % _e))
    # numai APELURILE (`_butonSpreEcran(eroare, cale);`), nu și definiția — prima formă le număra pe amândouă și rămânea
    # verde cu un drum lipsă (prins de mutație, 06.10.2026)
    if len(re.findall(r"(?<!function )_butonSpreEcran\(eroare, cale\);", fisiere.get("api.js", ""))) < 2:
        rap["refuz_ecran_fara_buton"].append(("api.js", 0, "_butonSpreEcran", "refuzul cu `ecran` nu primește butonul pe ambele drumuri (DS cap.6 v2.74)"))
except Exception as _e_re:
    rap["refuz_ecran_fara_buton"].append(("verificator", 0, "EROARE", "gard refuz ecran: " + str(_e_re)))

# --- PRET_SAU_ARTICOL_NEALES (DS cap.24 v2.75, comanda Costin 06.10.2026 pct.1b/1c): „un preț pe care nu l-a ales nimeni nu
#     se propune”. (1) un preț citit dintr-un câmp nu se transformă în 0 când câmpul e gol (`parseFloat(…value) || 0` pe o linie
#     cu `pret`); (2) rândul nou nu poartă preț (`linieNoua = () => ({ … pret_unitar: 0 …})`); (3) rândul nou nu se leagă de
#     primul articol (`articol_id: arts[0]`); (4) orice listă de articole (`<option value="${a.id}"`) are opțiunea goală
#     înaintea ei; (5) emiterea: denumirea scrisă de mână dezleagă articolul și golește propunerea. Mutația care o probează:
#     `pret_unitar: 0` repus în rândul nou al facturii recurente SAU opțiunea goală scoasă din `optArts` SAU dezlegarea scoasă
#     din `emitere_ecran.js` -> TOTAL > 0. LIMITA: (1) vede citirea pe O linie (`.value` / `val(` + `|| 0` + `pret`); un preț
#     citit într-o variabilă pe o linie și apărat cu `|| 0` pe alta nu se vede.
rap["pret_sau_articol_neales"] = []
try:
    for _nume, _t in fisiere.items():
        for _i, _ln in enumerate(_t.split("\n"), 1):
            if (re.search(r"pret", _ln, re.I) and re.search(r"(?:parseFloat|Number)\(", _ln) and re.search(r"\|\|\s*0\b", _ln)
                    and re.search(r"\.value\b|\bval\(", _ln)):
                rap["pret_sau_articol_neales"].append((_nume, _i, "|| 0", "prețul gol devine 0 (DS cap.24 v2.75)"))
        for _m in re.finditer(r"linieNoua\s*=\s*\(\)\s*=>\s*\(\{[^}]*\bpret_unitar:\s*0\b", _t):
            rap["pret_sau_articol_neales"].append((_nume, _t[:_m.start()].count("\n") + 1, "pret_unitar: 0", "rândul nou poartă un preț (DS cap.24 v2.75)"))
        for _m in re.finditer(r"articol_id:\s*arts\[0\]", _t):
            rap["pret_sau_articol_neales"].append((_nume, _t[:_m.start()].count("\n") + 1, "arts[0]", "rândul nou legat de primul articol (DS cap.24 v2.75)"))
        for _m in re.finditer(r'<option value="\$\{a\.id\}"', _t):
            # [07.10.2026] `${ALEGE}` (api.js) E opțiunea goală canonică (`<option value="" data-alege …>`, DS cap.17): o listă care
            # pornește cu ea e conformă — fără asta, gardul lexical respingea exact forma pe care o cere DS-ul
            _fer = _t[max(0, _m.start() - 300):_m.start()]
            if '<option value=""' not in _fer and "${ALEGE}" not in _fer:
                rap["pret_sau_articol_neales"].append((_nume, _t[:_m.start()].count("\n") + 1, "option", "lista de articole fără opțiunea goală (DS cap.24 v2.75)"))
    _em = fisiere.get("emitere_ecran.js", "")
    if "golestePropunerea(l, pret, um);" not in _em or not re.search(r"dataset\.den[^\n]*l\.articol_id = null", _em):
        rap["pret_sau_articol_neales"].append(("emitere_ecran.js", 0, "denumire", "denumirea scrisă de mână nu dezleagă articolul / nu golește propunerea (DS cap.24 v2.75)"))
except Exception as _e_pa:
    rap["pret_sau_articol_neales"].append(("verificator", 0, "EROARE", "gard pret/articol neales: " + str(_e_pa)))

# --- ID_INTERN_TASTABIL (DS cap.24 v2.76, decizia Costin 07.10.2026, C4): o entitate a firmei se alege din LISTĂ, nu tastându-i
#     ID-ul intern. Vede registrul `C("…_id", "…", "numar"|"text")` din ecrane și orice `<input>` cu id `…-…_id` de tip number/text.
#     Mutația care o probează: `C("mijloc_fix_id", "ID mijloc fix", "numar", …)` pus la loc -> TOTAL > 0. LIMITA: un câmp de ID cu
#     alt nume (fără sufixul `_id`) nu se vede.
rap["id_intern_tastabil"] = []
for _nume, _t in fisiere.items():
    for _m in re.finditer(r'C\("([a-z_]*_id)", "[^"]*", "(?:numar|text)"', _t):
        rap["id_intern_tastabil"].append((_nume, _t[:_m.start()].count("\n") + 1, _m.group(1), "ID intern tastat — alegerea din listă (DS cap.24 v2.76)"))
    for _m in re.finditer(r'<input[^>]*type="(?:number|text)"[^>]*id="[a-z]+-[a-z_]*_id"', _t):
        rap["id_intern_tastabil"].append((_nume, _t[:_m.start()].count("\n") + 1, "input", "ID intern tastat — alegerea din listă (DS cap.24 v2.76)"))

# --- FAPT_FISCAL_NECERUT (DS cap.17 v2.77, comanda Costin 07.10.2026, „Cele 33 de chei”): o cheie care e fapt fiscal (schimbă nota,
#     baza sau impozitul) se cere în formularul Operațiunilor EXPLICIT, fără preselecție; una strict tehnică rămâne în afara
#     ecranului, cu motivul scris. Același instrument ca `core/test_formulare_operatiuni_campuri.py` — o singură implementare, două
#     porți. Mutația care o probează: câmpul „Accize” pus la loc opțional -> TOTAL > 0.
rap["fapt_fiscal_necerut"] = []
try:
    import sys as _sys_ff
    _sys_ff.path.insert(0, os.path.join(BAZA_PY, "scripts"))
    import scan_formulare_operatiuni as _sfo
    for _k_ff, _ce_ff in _sfo.masoara():
        rap["fapt_fiscal_necerut"].append(("operatiuni_ecran.js", 0, _k_ff, _ce_ff + " (DS cap.17 v2.77)"))
    # [07.10.2026, „Ecranele scrise de mână”] aceeași regulă în afara registrului Operațiunilor (DS cap.17 v2.78): un fapt fiscal
    # ales dintr-o listă pornește cu „— alege —” și e cerut de handler; restul selecturilor, clasificate cu motiv.
    import scan_selecturi_ecrane as _sse
    for _k_ff, _ce_ff in _sse.masoara():
        rap["fapt_fiscal_necerut"].append((_k_ff.split(":", 1)[0], 0, _k_ff, _ce_ff + " (DS cap.17 v2.79)"))
except Exception as _e_ff:
    rap["fapt_fiscal_necerut"].append(("verificator", 0, "EROARE", "gard fapt_fiscal_necerut: " + str(_e_ff)))

# --- COADA_UN_SINGUR_DRUM (DS cap.24 v2.76, comanda Costin 07.10.2026, C1/C2/C3/C11): trimiterea în coadă trece numai prin
#     `coada_trimite.js` (corpul generării, refuzul real, confirmarea atenționărilor DUK). Mutația care o probează: un
#     `api.post("/coada", …)` scris de mână în declaratii.js -> TOTAL > 0.
rap["coada_un_singur_drum"] = []
for _nume, _t in fisiere.items():
    if _nume == "coada_trimite.js":
        continue
    for _m in re.finditer(r'api\.post\(\s*["\'`]/coada["\'`]', _t):
        rap["coada_un_singur_drum"].append((_nume, _t[:_m.start()].count("\n") + 1, "/coada", "trimitere în coadă în afara lui trimiteInCoada (DS cap.24 v2.76)"))
if "export async function trimiteInCoada(" not in fisiere.get("coada_trimite.js", ""):
    rap["coada_un_singur_drum"].append(("coada_trimite.js", 0, "trimiteInCoada", "drumul comun al cozii lipsește (DS cap.24 v2.76)"))

# --- ACTIUNE_REFUZATA_NEMARCATA (DS cap.9 v2.64, decizia Costin 04.10.2026: „orice acțiune refuzată rolului nu se
#     afișează”). Un apel JS la o rută restrânsă cere elementul marcat `data-actiune` (poarta din `drepturi.js` îl ascunde
#     celui refuzat), iar unde handlerul se poate lega de element, marcajul stă pe ACEL element. Același instrument ca
#     `core/test_drepturi_ui.py` (`scripts/scan_drepturi_ui.py`) — o singură implementare, două porți. Mutația care o
#     probează: `data-actiune` scos de pe butonul „Adaugă firma” -> lista nevidă -> TOTAL > 0 -> poarta roșie.
rap["actiune_refuzata_nemarcata"] = []
try:
    import sys as _sys_ar
    _sys_ar.path.insert(0, os.path.join(BAZA_PY, "scripts"))
    import scan_drepturi_ui as _sdu
    for _rel, _ln, _act, _g in _sdu.masoara()["lipsa"]:
        rap["actiune_refuzata_nemarcata"].append((_rel.replace("static/js/", ""), _ln, "data-actiune",
            "apel la %s fara data-actiune in fisier (drepturi.js nu-l poate ascunde)" % _act))
    for _rel, _ln, _act, _tag in _sdu.masoara_pe_element()["gresite"]:
        rap["actiune_refuzata_nemarcata"].append((_rel.replace("static/js/", ""), _ln, "data-actiune",
            "elementul legat de apelul %s nu poarta data-actiune: %s" % (_act, _tag[:60])))
    for _rel, _ln, _et in _sdu.butoane_creare_nemarcate():
        rap["actiune_refuzata_nemarcata"].append((_rel.replace("static/js/", ""), _ln, "data-actiune",
            "buton de intrare intr-un formular (%s) fara data-actiune / data-fara-actiune" % _et))
    for _rel, _ln, _act, _tag in _sdu.intrari_in_formular_nemarcate()["nemarcate"]:
        rap["actiune_refuzata_nemarcata"].append((_rel.replace("static/js/", ""), _ln, "data-actiune",
            "buton care deschide formularul %s fara data-actiune / data-fara-actiune" % _act[:60]))
    # [deficiența 262, 15.10.2026] butonul care deschide, prin ALTĂ funcție, un ecran ale cărui acțiuni sunt toate ale administratorului
    for _rel, _ln, _acts, _tag in _sdu.intrari_in_ecrane_doar_admin()["nemarcate"]:
        rap["actiune_refuzata_nemarcata"].append((_rel.replace("static/js/", ""), _ln, "data-actiune",
            "buton spre un ecran numai al administratorului (%s) fara data-actiune / data-fara-actiune" % "|".join(_acts)[:60]))
except Exception as _e_ar:
    rap["actiune_refuzata_nemarcata"].append(("verificator", 0, "EROARE", "gard actiune_refuzata_nemarcata: " + str(_e_ar)))

# --- MESAJ_SERVER_NEESCAPAT (DS cap.10 v2.65, găsit 04.10.2026 la confirmările de drepturi): mesajul unei erori venite de
#     la server (`e.mesaj` / `err.message` / `r.detail`) interpolat într-un șablon HTML trece prin `esc()`. Mesajul
#     poate cita ce a tastat utilizatorul (un nume de firmă, un email) — fără escape, `<` din el devine marcaj. Instanța:
#     13 interpolări neescapate (portal 7, firme 3, cabinet, facturi, Woo). O apariție folosită doar ca TEST de
#     ternar (`e.mesaj ? … : …`) nu se afișează și nu se numără. Limita: vede `${…}` pe o singură linie, cu `<` sau
#     `innerHTML` înaintea lui pe aceeași linie; un mesaj concatenat cu `+` în afara unui șablon nu e văzut.
#     Mutația care o probează: `esc(` scos din jurul `err.mesaj` în portal.js -> lista nevidă -> TOTAL > 0.
rap["mesaj_server_neescapat"] = []
_re_ms = re.compile(r"\$\{([^{}]*\b(?:e|err|ex|er|eroare|error|r|res|raspuns)\b(?:\s*&&\s*\w+)?\.(?:mesaj|message|detail)\b[^{}]*)\}")
for _nume, _t in fisiere.items():
    for _ln, _l in enumerate(_t.split("\n"), 1):
        for _m in _re_ms.finditer(_l):
            _pre = _l[:_m.start()]
            if "<" not in _pre and "innerHTML" not in _pre:
                continue
            _ex = _m.group(1)
            for _p in re.finditer(r"\.(?:mesaj|message|detail)\b", _ex):
                if re.match(r"\s*\?", _ex[_p.end():]):
                    continue
                if "esc(" not in _ex[:_p.start()]:
                    rap["mesaj_server_neescapat"].append((_nume, _ln, "esc",
                        "mesaj de eroare de la server interpolat in HTML fara esc(): " + _m.group(0)[:50]))
                    break

# --- DATE_UTILIZATOR_NEESCAPATE (DS cap.10, C37 — Lotul 5, 15.10.2026): un nume, prenume, email, o denumire sau un mesaj scris de
#     om, pus în HTML (șablon `${…}` sau lipit cu `+` lângă un tag), trece prin `esc()`. Regula din DS exista fără gard; singurul gard
#     pe `esc` (MESAJ_SERVER_NEESCAPAT) vedea numai mesajele de eroare de la server și numai în `${…}` — așa au trecut prenumele din
#     salut, numele din bară, emailurile din portal și mesajele clientului către cabinet. Instrumentul: `scripts/scan_date_neescapate.py`
#     (o singură implementare, două porți: aici și `core/test_date_neescapate.py`), cu limitele scrise acolo. Mutația care o probează:
#     `esc(` scos din salutul din `salut.js` -> lista nevidă -> TOTAL > 0.
rap["date_utilizator_neescapate"] = []
try:
    import sys as _sys_dn
    _sys_dn.path.insert(0, os.path.join(BAZA_PY, "scripts"))
    import scan_date_neescapate as _sdn
    for _f, _ln, _frag in _sdn.toate(BAZA_PY):
        rap["date_utilizator_neescapate"].append((_f, _ln, "esc", "dată scrisă de om pusă în HTML fără esc(): " + _frag[:50]))
except Exception as _e_dn:
    rap["date_utilizator_neescapate"].append(("verificator", 0, "EROARE", "gard date_utilizator_neescapate: " + str(_e_dn)))

# --- NUMERAL_NEACORDAT (DS cap.0, deficiențele 261 / 263 — Lotul 5, 15.10.2026): un număr afișat se acordă cu substantivul prin
#     `cate(n, singular, plural)` (static/js/plural.js, oglinda lui `core/common.cate`): „1 notă”, „2 note”, „20 de note”. Clasa avea
#     ~255 de locuri în JS („1 note”, „1 facturi”, „1 angajați”, „5 absent”), fără niciun gard. Instrumentul: `gaseste_js()` din
#     `core/test_plural_dupa_numar.py` (o singură implementare, două porți: aici și testul), cu excepțiile numite acolo. Mutația care o
#     probează: `${note.length} note` pus înapoi în Registrul jurnal (firme.js) -> lista nevidă -> TOTAL > 0.
rap["numeral_neacordat"] = []
try:
    import sys as _sys_pl
    _sys_pl.path.insert(0, BAZA_PY)
    from core import test_plural_dupa_numar as _tpl
    for _g in _tpl.gaseste_js():
        if not _tpl._exceptat(_g):
            rap["numeral_neacordat"].append((_g[0], _g[1], "cate", "număr cu substantiv la formă fixă, fără cate(): " + str(_g[3])[:50]))
except Exception as _e_pl:
    rap["numeral_neacordat"].append(("verificator", 0, "EROARE", "gard numeral_neacordat: " + str(_e_pl)))

# --- ICOANA_INEXISTENTA (DS cap.13 v2.66, comanda Costin 05.10.2026 pct.5): orice cheie de iconiță folosită într-un ecran
#     (`icon: "x"`, `ICOANE["x"]`, `ICOANE.x`) există în dicționarul canonic `ICOANE` din api.js. `svg(cheie)` desena
#     `ICOANE[cheie] || ""` — o cheie greșită dădea o iconiță GOALĂ, fără eroare („Raportează” și „Raportări” cereau `report`,
#     scos în v2.7). Mutația care o probează: `icon: "suport"` -> `icon: "report"` în asistent.js -> TOTAL > 0.
rap["icoana_inexistenta"] = []
try:
    _api_t = fisiere.get("api.js", "")
    _ii = _api_t.index("export const ICOANE = {")
    _chei_ic = set(re.findall(r"(?m)^\s*([a-z_]+):", _api_t[_ii:_api_t.index("};", _ii)]))
    _re_ic = re.compile(r"""\bicon\s*:\s*["']([a-z_]+)["']|ICOANE\[\s*["']([a-z_]+)["']\s*\]|ICOANE\.([a-z_]+)""")
    for _nume, _t in fisiere.items():
        for _m in _re_ic.finditer(_t):
            _k = _m.group(1) or _m.group(2) or _m.group(3)
            if _k not in _chei_ic:
                rap["icoana_inexistenta"].append((_nume, _t.count("\n", 0, _m.start()) + 1, _k,
                    "cheie de iconita inexistenta in ICOANE (api.js): svg() deseneaza gol (DS cap.13)"))
    if len(_chei_ic) < 15:
        rap["icoana_inexistenta"].append(("api.js", 0, "ICOANE", "dictionarul ICOANE nu s-a putut citi (%d chei)" % len(_chei_ic)))
except Exception as _e_ic:
    rap["icoana_inexistenta"].append(("verificator", 0, "EROARE", "gard icoana_inexistenta: " + str(_e_ic)))

# --- ALEGERE_FIRMA_DUBLA (DS cap.6 v2.66, comanda Costin 05.10.2026 pct.6): alegerea firmei într-un formular e UN control
#     (`<select>` cu „— alege firma —”). Un câmp „Caută firma” în același fișier cu o listă „— alege firma —” = aceeași alegere
#     de două ori (instanța: Pachete lunare). Lista de BIFE a firmelor (asistenți) nu are „— alege firma —”, deci nu intră.
#     Mutația care o probează: câmpul `pac-cauta` repus în pachete.js -> TOTAL > 0.
rap["alegere_firma_dubla"] = []
for _nume, _t in fisiere.items():
    if re.search(r"""placeholder=["']Caut[ăa] firma""", _t) and re.search(r"<option[^>]*>\s*(?:—|\\u2014)\s*alege firma", _t):
        _ln = _t.count("\n", 0, re.search(r"""placeholder=["']Caut[ăa] firma""", _t).start()) + 1
        rap["alegere_firma_dubla"].append((_nume, _ln, "firma", "camp de cautare + lista derulanta pentru aceeasi firma (DS cap.6)"))

# --- MOTIV_DREPT_ABSENT (DS cap.9 v2.66, comanda Costin 05.10.2026 pct.3): poarta din drepturi.js, când ascunde acțiuni într-o
#     zonă, pune nota `.drept-motiv` cu dreptul care lipsește și cine îl acordă. Gardianul cere ca mecanismul să existe și să
#     acopere ferestrele din navigator și overlay-ul poveștii. Comportamentul îl probează `frontend_test/proba_asistent_poveste.py`.
#     Mutația care o probează: `motivInZona` scos din bucla lui aplicaDrepturi -> TOTAL > 0.
rap["motiv_drept_absent"] = []
_dr_t = fisiere.get("drepturi.js", "")
for _cerinta, _rx in (("zona include .fereastra-corp", r'ZONA_MOTIV\s*=\s*"[^"]*\.fereastra-corp'),
                      ("zona include .pacm", r'ZONA_MOTIV\s*=\s*"[^"]*\.pacm\b'),
                      ("aplicaDrepturi pune motivul", r"zone\.forEach\(motivInZona\)"),
                      ("textul numește cine acordă dreptul", r"[ÎL][le] acordă administratorul cabinetului, din ecranul Asistenți")):
    if not re.search(_rx, _dr_t):
        rap["motiv_drept_absent"].append(("drepturi.js", 0, "drept-motiv", "lipseste: %s (DS cap.9 v2.66)" % _cerinta))

# --- PASTRARE_FORMULAR (DS cap.3 v2.67, comanda Costin 05.10.2026 pct.1): „un contabil nu pierde niciodată ce a completat”.
#     Gardianul cere mecanismele care fac asta: navigatorul păstrează ecranul în care s-a tastat (`_dePastrat` la deschide și
#     mergi, `replaceWith(pastrat.corp)` la revenire); api.js reautentifică peste ecran (`ceraReautentificare`) în loc de
#     `sesiune.iesi()` la 401. Comportamentul îl probează `frontend_test/proba_fara_pierdere.py`. Mutația care o probează:
#     `_dePastrat()` scos din `deschide` -> TOTAL > 0.
rap["pastrare_formular"] = []
#     [lotul 11, 445] `_dePastrat(dinRefuz)`: deschiderea dintr-un refuz păstrează formularul și neatins — se numără apelul cu orice
#     argument (definiția + cele două apeluri), nu numai forma fără argument.
for _fis, _cerinta, _rx, _n in (("navigator.js", "păstrarea la deschide și mergi", r"_dePastrat\(", 3),
                                ("navigator.js", "revenirea pune ecranul la loc", r"replaceWith\(pastrat\.corp\)", 1),
                                ("api.js", "401 cu sesiune -> reautentificare peste ecran", r"await ceraReautentificare\(\)", 1)):
    if len(re.findall(_rx, fisiere.get(_fis, ""))) < _n:
        rap["pastrare_formular"].append((_fis, 0, "PASTRARE_FORMULAR", "lipseste: %s (DS cap.3 v2.67)" % _cerinta))

# --- DATA_UTC (DS cap.4 v2.68, 05.10.2026): o dată calendaristică produsă în interfață (valoarea unui câmp de dată, „azi”,
#     un termen calculat) se scrie prin `dataIso(d)` din api.js, în ora LOCALĂ. `toISOString()` convertește în UTC: între 00:00
#     și 03:00 (02:00 iarna) „azi” devine ieri, iar o dată construită la miezul nopții local iese cu o zi mai devreme. Găsit la
#     data implicită a facturii (pct.4 al comenzii „fluxul de factură pe F1”); clasa avea 21 de apariții. Mutația care o
#     probează: `new Date().toISOString().slice(0, 10)` repus în emitere_ecran.js -> TOTAL > 0.
rap["data_utc"] = []
for _fis, _txt in sorted(fisiere.items()):
    for _i, _ln in enumerate(_txt.split("\n"), 1):
        if re.search(r"toISOString\(\)\s*\.\s*(?:slice|substring|substr)\(\s*0\s*,\s*10\s*\)|toISOString\(\)\s*\.\s*split\(\s*[\"']T", _ln):
            rap["data_utc"].append((_fis, _i, "DATA_UTC", _ln.strip()[:90]))

# --- CANTITATE_BRUTA (DS cap.4 v2.69, 05.10.2026, comanda Costin pct.9): o cantitate sau un cost unitar afișat trece prin
#     `cantitate(v, um)` / `pretUnitar(v)` din api.js. Prinde câmpurile de cantitate/CMP interpolate brut într-un șablon
#     (`${a.stoc}`, `esc(l.cantitate)`, `" + a.cmp`). EXCEPTAT: `value="${…}"` (câmp numeric) și payload-ul. Mutația care o
#     probează: `${a.stoc}` repus în opțiunea articolului din firme.js -> TOTAL > 0.
_CAMPURI_CANT = r"(?:stoc|cantitate|cmp|sold_cantitate|faptic|scriptic|nivel_minim|necesar|cant|pret_unitar)"
# [lotul 12] excepția câmpului numeric acoperă și forma scăpată `value="${esc(l.cantitate)}"` (formularul facturii introduse manual, 477)
_RX_CANT = re.compile(r"(?<!value=\")(?<!value=\"\$\{)(?:\$\{\s*|esc\(\s*|[\"'`]\s*\+\s*)[A-Za-z_]\w*\." + _CAMPURI_CANT + r"\s*(?:\}|\))")
rap["cantitate_bruta"] = []
for _fis, _txt in sorted(fisiere.items()):
    if _fis == "api.js":
        continue
    for _i, _ln in enumerate(_txt.split("\n"), 1):
        for _m in _RX_CANT.finditer(_ln):
            rap["cantitate_bruta"].append((_fis, _i, "CANTITATE_BRUTA", _m.group(0)[:60]))

# --- CURS_FORMAT_LOCAL (DS cap.4 v2.101, 22.10.2026, lotul 11, C88): cursul valutar se afișează prin `cursValutar(v)` din api.js,
#     cu precizia BNR (4–6 zecimale). Prinde formatarea locală cu `minimumFractionDigits: 4` (cursul rotunjit la 4 zecimale: HUF
#     „0,0147” în loc de „0,014719”). EXCEPTAT: definiția din api.js (linia cu `maximumFractionDigits: 6`). Mutația care o
#     probează: `Number(r.curs).toLocaleString("ro-RO", { minimumFractionDigits: 4 })` repus în emitere_ecran.js -> TOTAL > 0.
rap["curs_format_local"] = []
for _fis, _txt in sorted(fisiere.items()):
    for _i, _ln in enumerate(_txt.split("\n"), 1):
        if re.search(r"minimumFractionDigits\s*:\s*4\b", _ln) and not (_fis == "api.js" and "maximumFractionDigits: 6" in _ln):
            rap["curs_format_local"].append((_fis, _i, "CURS_FORMAT_LOCAL", _ln.strip()[:90]))

# --- CULOARE_SEMAFOR_TEXT (DS cap.8 v2.70, 05.10.2026): culorile de SEMAFOR (`--galben` #c9961f, `--gri-semafor` #9aa3b2) sunt
#     pentru buline, borduri și fundaluri, nu pentru text: pe alb dau ~2,6:1 și ~2,5:1, sub pragul WCAG 1.4.3 (4,5:1). Textul
#     folosește `--galben-text` / `--gri`. Găsită de axe pe Registrul jurnal („● Ciornă”) și la Bancă („Parțial”, „Contat ✓”),
#     la proba pasului C. Mutația care o probează: `color:var(--galben)` repus pe insigna „Ciornă” -> TOTAL > 0.
#     [DS cap.15 v2.80, 08.10.2026] Aceeași clasă: `--gri-clar` (#8a929e) dă 3,14:1 pe alb (2,84:1 pe fundalul notificării
#     necitite) — e pentru fundaluri / placeholder, nu pentru text; textul secundar e `--gri` (5,91:1). Găsită de axe pe clopoțel
#     (lotul „Deciziile 07.10”). Excepție: `::placeholder`. Mutația: `color: var(--gri-clar)` repus pe `.clopot-cand` -> TOTAL > 0.
_RX_SEMAFOR_TEXT = re.compile(r"(?<![-\w])color\s*:\s*(?:var\(--galben\)|var\(--gri-semafor\)|var\(--gri-clar\)|#c9961f|#9aa3b2|#8a929e|\$\{CUL\.(?:galben|gri)\})", re.I)
rap["culoare_semafor_text"] = []
_surse_css = dict(fisiere)
with open(os.path.join(_RAD, "static/stil.css"), encoding="utf-8") as _h:
    _surse_css["stil.css"] = _h.read()
for _fis, _txt in sorted(_surse_css.items()):
    for _i, _ln in enumerate(_txt.split("\n"), 1):
        if _RX_SEMAFOR_TEXT.search(_ln) and "::placeholder" not in _ln:
            rap["culoare_semafor_text"].append((_fis, _i, "CULOARE_SEMAFOR_TEXT", _ln.strip()[:70]))
# forma INDIRECTĂ: un dicționar / o variabilă / o funcție cu culoare de semafor, folosită apoi ca `color:${…}`. LIMITĂ
# declarată (GARZI 05.10.2026): culoarea transmisă prin PARAMETRU (ex. `cifra(…, "var(--galben)")` -> `color:${accent}`) nu se
# vede — acolo s-a reparat la sursă, iar regula prinde numai forma directă și cele două de mai jos.
_SEM = r'"var\(--(?:galben|gri-semafor|rosu-semafor)\)"'
for _fis, _txt in sorted(fisiere.items()):
    for _m in re.finditer(r"(?:const|let|var)\s+(\w+)\s*=[^;\n]*" + _SEM, _txt):
        if re.search(r"color:\s*\$\{\s*" + _m.group(1) + r"\b", _txt):
            rap["culoare_semafor_text"].append((_fis, _txt[:_m.start()].count("\n") + 1, "CULOARE_SEMAFOR_TEXT", "indirect: " + _m.group(1)))
    for _m in re.finditer(r"function\s+(\w+)\s*\([^)]*\)\s*\{(?:(?!\nfunction)[\s\S]){0,400}?return\s+" + _SEM, _txt):
        if re.search(r"color:\s*\$\{[^}]*\b" + _m.group(1) + r"\(", _txt):
            rap["culoare_semafor_text"].append((_fis, _txt[:_m.start()].count("\n") + 1, "CULOARE_SEMAFOR_TEXT", "indirect: " + _m.group(1) + "()"))

# --- GRUP_FIRMA (DS cap.18 v2.71, 05.10.2026, comanda Costin pct.11): cardurile ferestrei firmei stau sub titluri de grup dintr-o
#     SINGURĂ sursă. Cere: (a) `GRUPURI_FIRMA` definit o singură dată în tot frontendul; (b) fiecare card din `meniuFirma`
#     declară `grup` imediat după `regim`, cu o cheie din `GRUPURI_FIRMA`; (c) randarea trece prin `grupeazaCarduri`, nu
#     printr-o grilă plată `vizibile.map`. Mutația care o probează: `grup` scos de pe cardul Facturi -> TOTAL > 0.
rap["grup_firma"] = []
_def_grup = [(f, t.count("const GRUPURI_FIRMA = [")) for f, t in fisiere.items() if "const GRUPURI_FIRMA = [" in t]
if [n for _f, n in _def_grup] != [1]:
    rap["grup_firma"].append(("firme.js", 0, "GRUP_FIRMA", "GRUPURI_FIRMA definit de %s ori (trebuie o dată)" % sum(n for _f, n in _def_grup)))
_ff = fisiere.get("firme.js", "")
_m_gr = re.search(r"const GRUPURI_FIRMA = \[(.*?)\];", _ff, re.S)
_chei_gr = set(re.findall(r'\["([a-z]+)",', _m_gr.group(1))) if _m_gr else set()
for _i, _ln in enumerate(_ff.split("\n"), 1):
    _mc = re.search(r'\{\s*cheie:\s*"([a-z0-9]+)",\s*regim:\s*"[a-z]+",\s*(grup:\s*"([a-z]+)")?', _ln)
    if _mc and (not _mc.group(2) or _mc.group(3) not in _chei_gr):
        rap["grup_firma"].append(("firme.js", _i, "GRUP_FIRMA", "card %r fără grup din GRUPURI_FIRMA" % _mc.group(1)))
if "grupeazaCarduri(vizibile)" not in _ff or "${vizibile.map((o) =>" in _ff:
    rap["grup_firma"].append(("firme.js", 0, "GRUP_FIRMA", "meniuFirma nu randează prin GRUPURI_FIRMA"))

# --- ACTIUNI_RAND_LIBERE (DS cap.9 v2.83, 08.10.2026, comanda Costin „Retest 08.10” pct.13): „acțiunile într-un meniu”. O celulă de
#     tabel cu TREI sau mai multe butoane le ține într-un `<details class="dec-xml"><summary>Acțiuni</summary>`, nu libere pe rând:
#     butoanele libere lățesc coloana până când fereastra derulează lateral și acțiunile ies din vedere (Mijloace fixe F2, ~1700 px).
#     Mutația care o probează: `<details class="dec-xml"><summary>Acțiuni</summary>` scos din mijloace_ecran.js -> TOTAL > 0.
#     LIMITĂ: vede celulele scrise ca `<td …>…</td>` literal într-un șablon; o celulă construită din bucăți (`"<td>" + x`) nu se vede.
rap["actiuni_rand_libere"] = []
for _fis, _txt in sorted(fisiere.items()):
    for _m in re.finditer(r"<td\b[^>]*>(.*?)</td>", _txt, re.S):
        if len(re.findall(r"<button\b", _m.group(1))) >= 3 and "<details" not in _m.group(1):
            rap["actiuni_rand_libere"].append((_fis, _txt[:_m.start()].count("\n") + 1, "ACTIUNI_RAND", _m.group(1).strip()[:60]))

# --- FER_LARG_STRIVIT (DS cap.9 v2.84, 08.10.2026, comanda Costin „Retest 08.10” pct.15): in fereastra larga (corp = coloana flex)
#     niciun copil nu se strange sub continutul lui — altfel continutul curge peste fratii de dedesubt (D406: tabelul „Din ce e
#     facuta declaratia” peste „Vezi XML-ul generat” si „Trimite in coada”) si un <details> inchis care creste lasa goluri mari.
#     Cere: (a) regula generala `.fereastra.fer-larg .fereastra-corp > * { flex-shrink: 0; }`; (b) o regula `.fer-larg` care pune
#     `flex: G 1 …` / `flex-shrink: 1` numai pe zonele care deruleaza ele insele (ZONE_STRANSE). Mutatia care o probeaza:
#     `.fereastra.fer-larg .dec-xml { flex: 1 1 auto; … }` pusa la loc -> TOTAL > 0. LIMITA: vede `stil.css`, nu stilurile inline.
rap["fer_larg_strivit"] = []
_ZONE_STRANSE = {".mig-sold-tabel", ".rap-split", ".pac-text"}
_css = _surse_css["stil.css"]
if not re.search(r"\.fereastra\.fer-larg \.fereastra-corp > \* \{ flex-shrink: 0; \}", _css):
    rap["fer_larg_strivit"].append(("stil.css", 0, "FER_LARG", "lipseste regula generala `.fereastra-corp > * { flex-shrink: 0; }`"))
for _m in re.finditer(r"([^{}]*\.fer-larg[^{}]*)\{([^}]*)\}", _css):
    _sel, _decl = _m.group(1).strip(), _m.group(2)
    if re.search(r"(?<![-\w])flex\s*:\s*\d+\s+1\b|flex-shrink\s*:\s*1\b", _decl) and not any(z in _sel for z in _ZONE_STRANSE):
        rap["fer_larg_strivit"].append(("stil.css", _css[:_m.start(2)].count("\n") + 1, "FER_LARG", _sel[-60:]))

# --- FOCUS_CU_SALT (DS cap.9 v2.86, 09.10.2026, retestul Costin, deficiența 159): „ecranul tot sare: rândul atins urcă”. `.focus()`
#     derulează elementul în CENTRUL zonei când nu se vede întreg (la „Marchează depusă”: 475 px), iar la `<input type="date">`
#     Chromium ignoră chiar și `preventScroll`. Focusul trece prin `api.focusFaraSalt` (ține minte derularea strămoșilor, o reface,
#     apoi `nearest`) sau, unde `api.js` nu se poate importa, prin `.focus({ preventScroll: true })`. Mutația care o probează: un
#     `x.focus()` pus într-un ecran -> TOTAL > 0. LIMITĂ: vede apelurile scrise `.focus(`; un `el["focus"]()` nu se vede.
rap["focus_cu_salt"] = []
for _fis, _txt in sorted(fisiere.items()):
    for _i, _ln in enumerate(_txt.split("\n"), 1):
        if re.search(r"\.focus\((?!\{\s*preventScroll:\s*true\s*\})", _ln.split("//", 1)[0]):
            rap["focus_cu_salt"].append((_fis, _i, "FOCUS", _ln.strip()[:60]))

# --- ANTET_NUMERIC_NOWRAP (DS cap.9 v2.86, 09.10.2026, retestul Costin, deficiența 162): la 1700 px Mijloace fixe derula lateral
#     (scrollWidth 1752 > clientWidth 1604) fiindcă antetele coloanelor numerice nu se rupeau (`white-space: nowrap`: „Amortizat
#     (calculat, până la 09/2026)” 335 px). Pe un rând stau CIFRELE; antetul și nota de sub cifră (`.tip-desc`) se rup. Cere regula
#     `.fd-tabel thead th.fd-td-num, .fd-td-num .tip-desc { white-space: normal; }` în stil.css. Mutația: regula scoasă -> TOTAL > 0.
#     LIMITĂ: vede `stil.css`; un antet numeric cu `white-space: nowrap` inline în șablon nu se vede.
rap["antet_numeric_nowrap"] = []
if not re.search(r"\.fd-tabel thead th\.fd-td-num, \.fd-td-num \.tip-desc \{ white-space: normal; \}", _surse_css["stil.css"]):
    rap["antet_numeric_nowrap"].append(("stil.css", 0, "ANTET_NUM", "lipsește regula: antetul numeric și nota se rup pe rânduri"))

# --- FEREASTRA_SCRIS (DS cap.9 v2.86, 09.10.2026, retestul Costin, deficiența 208): „fereastra și caseta de text prea mici”. Fereastra
#     poveștii (`.pacm`) e un document de scris: înălțimea e a ecranului (`height: calc(100vh - …)`), nu a conținutului — cu povestea
#     goală se strângea la 600 px. Regula e scrisă O SINGURĂ dată (erau două blocuri `.pacm`, 720 px și 900 px, care se contraziceau).
#     Mutația: `height:` scos sau al doilea bloc `.pacm {` pus la loc -> TOTAL > 0. LIMITĂ: vede numai `.pacm`.
# --- ROSU_DOAR_RESTANTA (DS cap.8 v2.87, 10.10.2026, decizia Costin „Roșu înseamnă termen depășit.”, deficiența 220): pe ecranele
#     Control fiscal (control.js, control_verdict.js) o culoare ROȘIE de semafor (`CULORI.rosu`, `cf-rosu`, `pct-rosu`, `cf-termen-rosu`,
#     `--rosu-semafor`) stă numai pe un rând care vorbește de restanțe. Mutația: `cf-galben` din titlul „Declarație vs contabilitate”
#     repus pe `cf-rosu` -> TOTAL > 0. LIMITĂ: culoarea primită prin parametru sau calculată (`CULORI[x]`) nu se vede — acolo
#     `stareAfisata` e păzită de `core/test_rosu_termen_depasit.py`.
rap["rosu_doar_restanta"] = []
_RX_ROSU = re.compile(r"CULORI\.rosu\b|\bcf-rosu\b|\bpct-rosu\b|\bcf-termen-rosu\b|--rosu-semafor")
for _fis in ("control.js", "control_verdict.js"):
    for _i, _ln in enumerate(fisiere.get(_fis, "").split("\n"), 1):
        if _RX_ROSU.search(_ln) and not re.search(r"restan", _ln, re.I) and not _ln.strip().startswith("//"):
            rap["rosu_doar_restanta"].append((_fis, _i, "ROSU_RESTANTA", _ln.strip()[:70]))

# --- SEMAFOR_PATRU_LUMINI (DS cap.8 v2.87, 10.10.2026, aprobat de Costin, deficiența 224): cardul Control fiscal al contabilului-șef și
#     al asistentului randează `semaforPatruLumini(sumar)`, iar `LUMINI_CONTROL` are exact patru stări, în ordinea roșu, galben, verde,
#     gri. Mutația: ordinea `galben` / `rosu` inversată, sau cardul asistentului întors pe `semaforCard` -> TOTAL > 0.
rap["semafor_patru_lumini"] = []
_m_lum = re.search(r"export const LUMINI_CONTROL = \[(.*?)\];", fisiere.get("semafor.js", ""), re.S)
_ord_lum = re.findall(r'\["(\w+)", "pct-', _m_lum.group(1)) if _m_lum else []
if _ord_lum != ["rosu", "galben", "verde", "gri"]:
    rap["semafor_patru_lumini"].append(("semafor.js", 0, "SEMAFOR4", "LUMINI_CONTROL: %s" % _ord_lum))
# [deficiența 224 redeschisă, comanda Costin 12.10.2026] cardul = UN RÂND cu patru buline și numărul fiecăreia, FĂRĂ TEXT
#     (`semaforCardControl`), aceeași înălțime cu celelalte carduri; textul stărilor numai în fereastră (`semaforPatruLumini`). Mutația:
#     cardul întors pe `semaforPatruLumini` (listă cu text), sau un text după număr în `semaforCardControl`, sau `.cab-semafor4--card`
#     înapoi pe coloană -> TOTAL > 0.
for _fis in ("cabinet.js", "asistent.js"):
    _t = fisiere.get(_fis, "")
    _bloc = re.search(r"querySelector\('\[data-cheie=\"control\"\]'\);(.*?)\n\}", _t, re.S)
    if not _bloc or "semaforCardControl(" not in _bloc.group(1) or "semaforPatruLumini(" in _bloc.group(1):
        rap["semafor_patru_lumini"].append((_fis, 0, "SEMAFOR4", "cardul Control fiscal nu randează semaforCardControl (rând fără text)"))
_m_card = re.search(r"export function semaforCardControl\(.*?\n\}", fisiere.get("semafor.js", ""), re.S)
_m_stare = re.search(r'<span class="cab-stare"[^`]*?</span>`', _m_card.group(0), re.S) if _m_card else None
if not _m_stare or not _m_stare.group(0).endswith('<b class="tip-figura">${s[k] || 0}</b></span>`'):
    rap["semafor_patru_lumini"].append(("semafor.js", 0, "SEMAFOR4", "lumina cardului are altceva decât bulina și numărul (text pe card)"))
_m_css4 = re.search(r"(?m)^\.cab-semafor4--card\s*\{([^}]*)\}", open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read())
if not _m_css4 or not re.search(r"flex-direction:\s*row", _m_css4.group(1)):
    rap["semafor_patru_lumini"].append(("stil.css", 0, "SEMAFOR4", ".cab-semafor4--card nu e un rând"))
# [125 + 224, decizia Costin 11.10.2026] fereastra deschisă din card arată ACELEAȘI patru stări, din ACEEAȘI sursă: `control.js` randează
#     `semaforPatruLumini(date.sumar)` și nu mai citește alte cifre de sumar (`contoare`). Mutația: fereastra întoarsă pe contoarele de
#     fapte (`date.contoare`) sau pe alt câmp decât `sumar` -> TOTAL > 0.
_t_cf = fisiere.get("control.js", "")
if "semaforPatruLumini(date.sumar)" not in _t_cf:
    rap["semafor_patru_lumini"].append(("control.js", 0, "SEMAFOR4", "fereastra Control fiscal nu randează semaforPatruLumini(date.sumar)"))
# ... și o PUBLICĂ: cardul se redesenează din citirea ferestrei (`publicaSumarControl` -> ascultătorul din semafor.js), altfel două citiri
#     la momente diferite dau cifre diferite (prins de plasă 11.10). Mutația: apelul scos din control.js sau ascultătorul scos -> TOTAL > 0.
if "publicaSumarControl(date.sumar)" not in _t_cf:
    rap["semafor_patru_lumini"].append(("control.js", 0, "SEMAFOR4", "fereastra nu publică sumarul către card (publicaSumarControl)"))
if not re.search(r'addEventListener\("control-fiscal:sumar"[^;]*semaforCardControl\(e\.detail\)', fisiere.get("semafor.js", ""), re.S):
    rap["semafor_patru_lumini"].append(("semafor.js", 0, "SEMAFOR4", "cardul nu se redesenează din sumarul publicat de fereastră"))
for _m in re.finditer(r"\.contoare\b", _t_cf):
    rap["semafor_patru_lumini"].append(("control.js", _t_cf[:_m.start()].count("\n") + 1, "SEMAFOR4",
                                        "fereastra citește alte cifre decât sumar (contoare)"))

# --- PAGINA_PRINCIPALA_UNA (DS cap.2a v2.88, 12.10.2026, deficiențele 225 + 231, comanda Costin): pagina principală are ACEEAȘI
#     structură la ambele roluri — banda de sus din `salut.js` (`paginaPrincipala` + `legaBenzile`: titlul, data, benzile „Recomandă” și
#     „Suport” una lângă alta), apoi grila de carduri; fără meniu lateral, iar „Suport” / „Recomandă” nu mai sunt carduri în grilă.
#     Mutația: arborele asistentului readus (`asi-arbore`), sau „Suport” înapoi card în DEF (`cheie:"raport"`), sau o pagină cu banda
#     ei proprie (fără `paginaPrincipala(`) -> TOTAL > 0. LIMITĂ: așezarea (benzile deasupra, înălțimile) o măsoară proba în browser
#     (`frontend_test/proba_pagina_principala.py` + `core/test_pagina_principala.py`).
rap["pagina_principala_una"] = []
for _fis, _fn in (("cabinet.js", "randeazaPanou"), ("asistent.js", "desktopAsistent")):
    _t = fisiere.get(_fis, "")
    _m = re.search(r"function " + _fn + r"\(.*?\n\}", _t, re.S)
    _corp = _m.group(0) if _m else ""
    if "paginaPrincipala(" not in _corp or "legaBenzile(" not in _corp:
        rap["pagina_principala_una"].append((_fis, 0, "PAGINA_UNA", "%s nu folosește banda comună (salut.js)" % _fn))
    for _rx, _ce in ((r"asi-arbore|asi-nod|<nav\b", "meniu lateral"), (r"""cheie:\s*["']raport["']|\braport:\s*\{""", "„Suport” card în grilă"),
                     (r"""cheie:\s*["']recomanda["']|\brecomanda:\s*\{""", "„Recomandă” card în grilă")):
        for _mm in re.finditer(_rx, _t):
            rap["pagina_principala_una"].append((_fis, _t[:_mm.start()].count("\n") + 1, "PAGINA_UNA", _ce))
_t_sal = fisiere.get("salut.js", "")
if [x for x in re.findall(r'\{ cheie: "(\w+)", titlu:', _t_sal)] != ["recomanda", "raport"]:
    rap["pagina_principala_una"].append(("salut.js", 0, "PAGINA_UNA", "benzile nu sunt „Recomandă”, „Suport”"))

# --- ETICHETA_PATRU_STARI (DS cap.8 v2.88, 12.10.2026, deficiența 226, comanda Costin): în Control fiscal eticheta stării unei firme
#     (rândul listei, antetul detaliului) e UNA din cele patru stări — `etichetaStare(stare)` = `CULORI[stare].txt`, fără cauză
#     („neconcordanță”) și fără număr („2 nu se pot verifica”); detaliul stă pe rândul de dedesubt. Mutația: `etichetaStare` cu al doilea
#     argument (numărul) sau o etichetă calculată din fapte pe rând -> TOTAL > 0.
rap["eticheta_patru_stari"] = []
_t_cv = fisiere.get("control_verdict.js", "")
_m_es = re.search(r"export function etichetaStare\(([^)]*)\)\s*\{(.*?)\n\}", _t_cv, re.S)
if not _m_es or _m_es.group(1).strip() != "stare" or "CULORI[stare]" not in _m_es.group(2) or "${" in _m_es.group(2):
    rap["eticheta_patru_stari"].append(("control_verdict.js", 0, "ETICHETA4", "etichetaStare nu e numele uneia din cele patru stări"))
_txt4 = re.findall(r'txt:"([^"]+)"', _t_cv)
if _txt4 != ["la zi", "de urmărit", "restanță", "nu se poate verifica"]:
    rap["eticheta_patru_stari"].append(("control_verdict.js", 0, "ETICHETA4", "CULORI.txt: %s" % _txt4))
for _fis in ("control.js", "firme.js"):
    _t = fisiere.get(_fis, "")
    for _mm in re.finditer(r"etichetaStare\(([^)]*)\)", _t):
        if "," in _mm.group(1) or not _mm.group(1).strip().endswith("stare"):
            rap["eticheta_patru_stari"].append((_fis, _t[:_mm.start()].count("\n") + 1, "ETICHETA4", _mm.group(0)[:60]))
    if re.search(r"etichetaRand|neconcordanță[\"`]", _t):
        rap["eticheta_patru_stari"].append((_fis, 0, "ETICHETA4", "etichetă din fapte pe rândul firmei"))

# --- BUTON_DEZACTIVAT (DS cap.1 v2.87, 10.10.2026, deficiența 222): fiecare clasă de buton din set (cap.1, fără modificatorii
#     `buton-mic` / `buton-activ`) are o regulă `:disabled` în stil.css, iar hover-ul ei e `:hover:not(:disabled)`. Mutația:
#     `.buton-secundar:disabled` scos din regula comună -> TOTAL > 0.
rap["buton_dezactivat"] = []
_css_b = open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read()
_set_b = ("buton-primar", "buton-secundar", "buton-text", "buton-sters", "buton-verde", "btn-nav", "btn-link")
for _cl in _set_b:
    if not re.search(r"\." + _cl + r":disabled\b", _css_b):
        rap["buton_dezactivat"].append(("stil.css", 0, "BUTON_DEZACTIVAT", ".%s fără regula :disabled" % _cl))
    for _m in re.finditer(r"\." + _cl + r":hover(?!:not\(:disabled\))", _css_b):
        rap["buton_dezactivat"].append(("stil.css", _css_b[:_m.start()].count("\n") + 1, "BUTON_DEZACTIVAT",
                                        ".%s:hover se aplică și dezactivat" % _cl))

# --- ACTIUNE_FARA_TIP (DS cap.1 v2.87, 10.10.2026, deficiența 222): pe un ecran cu select de tip de declarație (`id="<x>-tip"` cu
#     opțiuni de declarație — `s1005`/`s1003` sau `optiuniTip()`), fiecare buton care trimite în coadă, validează sau descarcă XML-ul
#     din aceeași funcție e legat la `disabled` după tip (la deschidere și la schimbare). Mutația: apelul `legaTip();` scos din
#     ecranBilant -> TOTAL > 0. LIMITĂ: recunoaște
#     selectul de tip după opțiunile lui; un al treilea ecran cu alte coduri de declarație intră în `_TIP_DECL` cu mâna.
rap["actiune_fara_tip"] = []
_TIP_DECL = {"firme.js": ("ecranBilant", "bl-tip", ("bl-val", "bl-xml", "bl-coada"),
                         ('.addEventListener("change", legaTip)', "\n    legaTip();",          # legat la schimbare ȘI la deschidere
                          # [deficiența 228, 12.10.2026] și la coloana „An precedent”: inactive cu motivul lângă ele până e completă
                          'id="bl-actiuni-motiv"', "stareaPrec.motiv", "p.lipsa.length", "motivActiuni.textContent = motiv",
                          "b.disabled = !tip() || !!motiv")),
             "declaratii.js": ("pas1", "dec-tip", ("dec-continua",), ("cont.disabled = !(S.tenant_id && S.tip)",))}
for _fis, (_fn, _sel, _btn, _leg) in _TIP_DECL.items():
    _t = fisiere.get(_fis, "")
    _m = re.search(r"function " + _fn + r"\(.*?\n\}", _t, re.S)
    _corp = _m.group(0) if _m else ""
    if 'id="%s"' % _sel not in _corp or any(_l not in _corp for _l in _leg):
        rap["actiune_fara_tip"].append((_fis, 0, "ACTIUNE_FARA_TIP", "%s: acțiunile nu sunt legate la tipul ales" % _fn))
    for _b in _btn:
        if 'id="%s"' % _b not in _corp:
            rap["actiune_fara_tip"].append((_fis, 0, "ACTIUNE_FARA_TIP", "%s: butonul %s nu mai e în funcție" % (_fn, _b)))
for _fis, _t in fisiere.items():                       # un select nou de tip de declarație, nelistat
    for _m in re.finditer(r'<select id="([a-z]+-tip)"[^>]*>\$\{ALEGE\}\s*<option value="(s10|d[0-9])', _t):
        if (_fis, _m.group(1)) not in {(f, v[1]) for f, v in _TIP_DECL.items()}:
            rap["actiune_fara_tip"].append((_fis, 0, "ACTIUNE_FARA_TIP", "select de tip de declarație nelistat: %s" % _m.group(1)))

# --- BARA_INALTIME_MINIMA (DS cap.2 v2.87, 11.10.2026, deficiența C8): barele aplicației (`.bara`, `.subbara`, `.bara3`,
#     `.subbara--admin`) au înălțime MINIMĂ (`min-height`), nu fixă — un conținut rupt pe rânduri (mesajul lung de pe telefon) le
#     crește, nu iese peste bara vecină și nu-i acoperă butoanele. Mutația: `.subbara { min-height: 40px` înapoi pe `height: 40px` ->
#     TOTAL > 0. LIMITĂ: vede regulile de bază ale celor patru clase din stil.css; un stil inline nu se vede (plasa: test_def_c8).
rap["bara_inaltime_minima"] = []
for _cl in ("bara", "subbara", "bara3", "subbara--admin"):
    for _m in re.finditer(r"(?m)^\." + re.escape(_cl) + r"\s*\{([^}]*)\}", _css_b):
        if re.search(r"(?<![-\w])height\s*:", _m.group(1)):
            rap["bara_inaltime_minima"].append(("stil.css", _css_b[:_m.start()].count("\n") + 1, "BARA_INALTIME_MINIMA",
                                                ".%s cu înălțime fixă" % _cl))
    if not re.search(r"(?m)^\." + re.escape(_cl) + r"\s*\{[^}]*min-height\s*:", _css_b):
        rap["bara_inaltime_minima"].append(("stil.css", 0, "BARA_INALTIME_MINIMA", ".%s fără min-height" % _cl))

# --- FEREASTRA_LOT6 (DS cap.6 + cap.9 v2.92, lotul 6: deficiențele 272, 279, 285): (a) un câmp `readonly` arată needitabil prin regula
#     GLOBALĂ `.camp-input[readonly]`; (b) acțiunea principală și mesajul ei stau în `.bara-fixa` (sticky); (c) rândul de butoane și stări
#     al detaliului facturii se rupe (`.fd-antet-sus` cu `flex-wrap: wrap`); (d) navigatorul lățește singur fereastra mai îngustă decât
#     conținutul ei (`_lateste` -> `fer-tabel`); (e) refuzul de pe rând trece prin `api.refuzPeRand`, nu se lipește de buton. Mutația:
#     oricare din cele cinci scoasă -> TOTAL > 0. LIMITĂ: vede regulile și apelurile, nu așezarea pe ecran (aia o măsoară e2e 285 / 272).
rap["fereastra_lot6"] = []
_css_l6 = _surse_css["stil.css"]
for _sel, _decl, _cod in ((r"\.camp-input\[readonly\]", r"background\s*:", "READONLY_GLOBAL"),
                          (r"\.fereastra-corp \.bara-fixa", r"position\s*:\s*sticky", "BARA_FIXA"),
                          (r"\.fereastra-corp \.bara-fixa:not\(:last-child\)", r"margin-bottom\s*:\s*0", "BARA_NU_ACOPERA"),
                          (r"\.fd-antet-sus", r"flex-wrap\s*:\s*wrap", "RAND_RUPT"),
                          # [lotul 11, 436 afișare — patch-ul subagentului D] caseta de refuz din bara fixă nu trece pe sub antetul lipit
                          # sus: zona de mesaj are cel mult 35vh și derulează ea; elementul adus în vedere se oprește sub antet (DS cap.6 v2.98)
                          (r'\.fereastra-corp \.bara-fixa > \[id\$="-mesaj"\], \.fereastra-corp \.bara-fixa > \[id\$="-msg"\]', r"max-height\s*:\s*35vh", "CASETA_SUB_ANTET"),
                          (r"\.fereastra-corp \*", r"scroll-margin-top\s*:\s*calc\(var\(--rezumat-h", "CASETA_SUB_ANTET")):
    _ml6 = re.search(r"(?m)^" + _sel + r"\s*\{([^}]*)\}", _css_l6)
    if not _ml6 or not re.search(_decl, _ml6.group(1)):
        rap["fereastra_lot6"].append(("stil.css", 0, _cod, "regula %s lipsește sau nu are %s (DS v2.92)" % (_sel, _decl)))
_nav_l6 = open(os.path.join(BAZA_PY, "static", "js", "navigator.js"), encoding="utf-8").read()
# [349, lotul 9 -> lotul 10] cutia previzualizării (`.mig-prev-cutie`) nu mai derulează ea însăși (421/424), deci depășirea ei se vede în
# lățimea corpului: `_prealata` întreabă corpul, iar `_lateste` lățește fereastra și când conținutul e mai lat (285)
if not (re.search(r"const _prealata = \(\) => _corp\.scrollWidth > _corp\.clientWidth \+ 1;", _nav_l6)
        and re.search(r"const _lateste = \(\) => \{[^}]*?_prealata\(\)\)\) f\.classList\.add\(\"fer-tabel\"\)", _nav_l6)):
    rap["fereastra_lot6"].append(("navigator.js", 0, "LATIRE_AUTOMATA", "fereastra nu se mai lățește singură când conținutul e mai lat (DS cap.9 v2.92, 285)"))
# (f) [deficiența 290] eroarea unui formular dispare când câmpul se schimbă: ascultarea unică din `api.js`, în faza de captură
_api_l6 = open(os.path.join(BAZA_PY, "static", "js", "api.js"), encoding="utf-8").read()
for _ev in ("input", "change"):
    if 'document.addEventListener("%s", stergeEroriDupaCorectare, true);' % _ev not in _api_l6:
        rap["fereastra_lot6"].append(("api.js", 0, "ERORI_DUPA_CORECTARE",
                                      "eroarea nu mai dispare la „%s” pe câmp (stergeEroriDupaCorectare, DS cap.6 v2.92)" % _ev))
# (g) [deficiența 410, DS cap.6 v2.93] „NU s-a salvat” lângă butonul apăsat: helperii comuni de refuz (câmp și formular) alimentează
# `refuzSalvare`, iar câmpul corectat iese din listă — un singur mecanism, în `api.js`
for _ancora, _cod_r in (('refuzSalvare({ camp: inp, txt });', "eroareCamp"),
                        ('if (txt && tip === "eroare") refuzSalvare({ mesaj: el });', "arataMesaj"),
                        ('_scoateDinRefuz(c);', "stergeEroriDupaCorectare"),
                        ('box.innerHTML = \'<b>NU s-a salvat.</b><ul class="refuz-salvare-lista"></ul>\';', "textul")):
    if _ancora not in _api_l6:
        rap["fereastra_lot6"].append(("api.js", 0, "REFUZ_SALVARE",
                                      "%s nu mai alimentează lista „NU s-a salvat” de lângă buton (DS cap.6 v2.93, 410)" % _cod_r))
if not re.search(r"(?m)^\.refuz-salvare \{", _css_l6):
    rap["fereastra_lot6"].append(("stil.css", 0, "REFUZ_SALVARE", "regula .refuz-salvare lipsește (DS cap.6 v2.93, 410)"))
# (g2) [deficiența 410] refuzul unei acțiuni (urmat de `return`) e EROARE, nu avertisment: numai eroarea intră în „NU s-a salvat”
for _nume, _t in fisiere.items():
    for _m in re.finditer(r'arataMesaj\([^;]*"avert"\);\s*return;', _t):
        rap["fereastra_lot6"].append((_nume, _t[:_m.start()].count("\n") + 1, "REFUZ_CA_AVERTISMENT",
                                      "refuz afișat ca avertisment: arataMesaj(…, \"eroare\") (DS cap.6 v2.93, 410)"))
# (h) [deficiența 418c, clasa 410, DS cap.27 v2.93] după un act reușit, nicio navigare / redesenare TEMPORIZATĂ care șterge confirmarea
for _nume, _t in fisiere.items():
    for _m in re.finditer(r"setTimeout\(\s*(?:async\s*)?\(\)\s*=>\s*\{?[^;{}]*?(?:nav\.inapoi|nav\.acasa|dupaEmitere|\b(?:randeaza|istoric)\w*\()", _t):
        rap["fereastra_lot6"].append((_nume, _t[:_m.start()].count("\n") + 1, "CONFIRMARE_TEMPORIZATA",
                                      "navigare/redesenare temporizată după act: confirmarea dispare înainte de a fi citită (DS cap.27 v2.93, 418c)"))
# (h2) [C64, DS cap.27 v2.94] confirmarea după o redesenare se pune în zona de mesaj a ecranului refăcut: `await randeaza…(corp, …);`
# urmat de `arataMesaj(corp, …)` scrie mesajul ÎN LOCUL ecranului abia refăcut (fără drum mai departe)
for _nume, _t in fisiere.items():
    for _m in re.finditer(r"await\s+[\w.]+\(\s*corp\b[^;]*\);(?:\s*//[^\n]*)*\s*arataMesaj\(\s*corp\s*,", _t):
        rap["fereastra_lot6"].append((_nume, _t[:_m.start()].count("\n") + 1, "CONFIRMARE_PESTE_ECRAN",
                                      "mesajul după redesenare înlocuiește ecranul refăcut: zona lui de mesaj (DS cap.27 v2.94, C64)"))
for _nume, _t in fisiere.items():
    for _m in re.finditer(r"""insertAdjacentHTML\(\s*["']afterend["'],\s*['"`]<span class="msg-eroare""", _t):
        rap["fereastra_lot6"].append((_nume, _t[:_m.start()].count("\n") + 1, "REFUZ_LIPIT", "refuz lipit de buton: api.refuzPeRand (DS cap.6 v2.92)"))


# --- FEREASTRA_TABEL (DS cap.9 v2.96; lotul 10, deficiențele 421 și 424 — clasă, toată aplicația). Comanda Costin 10.1 pct.5, verbatim
#     în DECIZII: „Regula: ferestrele cu tabele se deschid aproape pe tot ecranul (cum e deja Balanța de verificare); rezumatul stă fix
#     sus și acțiunea principală fix jos; se derulează doar tabelul din mijloc, niciodată lateral.” Patru coduri, fiecare cu mutația lui:
#     FEREASTRA_TABEL — (a) navigatorul pune singur `fer-tabel` pe fereastra care conține un tabel (`_cuTabel`) și strânge tabelul care
#       nu încape (`fer-strans` / `fer-rupt`); (b) stil.css: fereastra cu tabel are lățimea și înălțimea ecranului (`calc(100vw/100vh -
#       48px)`), corpul ei derulează numai vertical (`overflow-x: hidden`), nicio regulă `fer-tabel` nu mai permite derularea laterală,
#       `.rezumat-fix` e lipit sus, `.mig-prev-cutie` nu mai derulează ea însăși. Mutații: `_cuTabel() || ` scos din navigator; `height:
#       calc(100vh - 48px)` scos; `overflow-x: hidden` -> `overflow-x: auto`; `position: sticky` scos de pe `.rezumat-fix`; `max-height:
#       55vh; overflow: auto` repus pe `.mig-prev-cutie` -> TOTAL > 0 (fiecare, `core/test_lot10_fereastra_tabel.py`).
#     DERULARE_INLINE — niciun `overflow(-x): auto|scroll` scris în stilul inline al unui șablon / șir din static/js (o cutie cu derulare
#       proprie ascunde derularea laterală și de navigator, și de măsurătorile e2e). Mutația: `<div style="overflow-x:auto">` repus în
#       mijloace_ecran.js -> TOTAL > 0.
#     ACTIUNE_TABEL_NEFIXATA — în corpul unei ferestre cu tabel (șablonul pus în `<corp>.innerHTML`, unde `<corp>` e primul parametru al
#       funcției de nivel întâi care randează un `<table` sau cheamă `tabelPrevizualizare(`), un buton care scrie (`data-actiune` POST /
#       PUT / PATCH / DELETE) stă în `.bara-fixa` (jos) sau în `.rezumat-fix` (sus) — nu la capătul conținutului, unde ajungi numai
#       derulând tot tabelul. Nu se cer: butoanele de pe rând (într-o celulă `<td>`, sau cu un `data-…="${…}"` al rândului) și tabelele
#       de machetă (`tabele_macheta`, o listă scrisă ca să poată fi contrazisă). Mutația: `<div class="bara-fixa">` scos de lângă
#       „Înscrie în registru” (firme.js, Registrul-inventar) -> TOTAL > 0.
#       **(v2.97, ZONE)** Lărgită de la `corp.innerHTML` la orice șablon al funcției cu tabel (zona ferestrei: `zona.innerHTML = info +
#       `…``, șablonul unui arrow adăugat după tabel `corpHtml += formular(d)`), cu butonul care scrie stând DUPĂ tabel în același
#       șablon — tabelul fiind `<table`, o variabilă cu tabel `${lista}` sau un producător de tabel (arrow-ul `sectiune` din funcție, o
#       funcție-șablon a fișierului) chemat sau dat ca referință (`.map(sectiune)`). Butonul de DEASUPRA tabelului nu e al ei (îl cere
#       REZUMAT_TABEL_LIPSA). Excepțiile, cu motiv: `actiuni_exceptii`. Mutația: bara scoasă de pe „Adaugă ajustarea” (firme.js) ->
#       TOTAL > 0 (`core/test_lot10_rezumat_fix.py`).
#     LIMITĂ (declarată): vede șabloanele scrise literal; un buton construit din bucăți (`"<button" + …`) sau adus printr-o variabilă
#       (`${ctx.actiuni}`) nu se vede, iar un tabel adus prin variabilă se vede numai dacă variabila e atribuită în aceeași funcție. Nu
#       vede așezarea pe ecran (lățimea reală, butonul în vedere) — aia o măsoară e2e `test_def_421_*` / `test_def_424_*`.
#     REZUMAT_TABEL_LIPSA (DS cap.9 v2.97 pct.5; lotul 10, 421 / 424 — „rezumatul stă fix sus”): orice ecran care desenează un tabel de
#       date (`<table>` care nu e de machetă, sau lista-tabel `.mig-sold-tabel`) în corpul unei ferestre are rezumatul lipit sus
#       (`class="… rezumat-fix …"` într-un șablon al lui). Unitatea e funcția de nivel întâi: „desenează” = are tabelul într-un șablon
#       al ei sau cheamă o funcție-șablon a fișierului (care nu scrie `innerHTML`, ex. `_blocComponente`, `tabelPrevizualizare`) care
#       îl are; „în fereastră” = scrie `….innerHTML =`. Rezumatul poate veni și dintr-o funcție-șablon (`_cadruPrev`, migrare) sau din
#       funcția care o cheamă în ACEEAȘI fereastră (zona desenată de `randeazaFisa` stă sub rezumatul ecranului care o cheamă; un apel
#       de pe un rând cu `deschide(` / `mergi(` deschide altă fereastră și nu acoperă). Excepțiile stau în `rezumat_exceptii`, fiecare
#       cu motivul (formularele cu tabel mic și ecranele „de decis de Costin”, unde rezumatul ar cere mutarea a ce e sub tabel); o
#       excepție rămasă fără obiect (funcția a dispărut, nu mai desenează tabel, sau are acum rezumat) pică și ea. Tot aici (pct.3):
#       lista-tabel `.mig-sold-tabel` nu mai derulează ea însăși în fereastra cu tabel (cu cutia ei de 280 px corpul n-avea ce derula).
#       Mutații: `rezumat-fix` scos din Balanță / din `_cadruPrev`; toate scoase (anti-vacuu); `max-height: none; overflow: clip` scos
#       de pe lista-tabel -> TOTAL > 0 (`core/test_lot10_rezumat_fix.py`). LIMITĂ: vede șabloanele scrise literal și apelurile pe nume
#       din același fișier; un tabel construit din bucăți (`"<tab" + "le"`) sau un ecran deschis din alt fișier peste o funcție-șablon a
#       acestuia nu se văd; nu vede dacă rezumatul e chiar deasupra tabelului — aia o măsoară e2e 421 / 424.
def analiza_fereastra_tabel(css, nav, fisiere):
    """Gărzile ferestrei cu tabel (421 / 424), ca FUNCȚIE PURĂ: primește textele (stil.css, navigator.js, {nume: sursă JS}) și întoarce
    [(fișier, linie, COD, text)]. E funcție, nu cod la nivel de modul, ca `core/test_lot10_fereastra_tabel.py` să cheme logica reală
    pe fragmente sintetice (known-good / known-bad) — o copie a ei în test ar fi logică paralelă."""
    import re as _re
    out = []
    # Tabelele de MACHETĂ (o imagine a documentului tipărit, nu date de citit) nu fac din fereastra lor o „fereastră cu tabel” pentru
    # ACTIUNE_TABEL_NEFIXATA. Lista se scrie, ca să poată fi contrazisă: `mfp-tabel` = previzualizarea modelului de factură (două
    # rânduri de exemplu), lângă controalele modelului — „Salvează” stă în coloana controalelor, nu sub un tabel lung.
    tabele_macheta = {"mfp-tabel"}

    def _sabloane(t):
        """[(start, stop, fel)] ale șabloanelor `…` exterioare (cu tot cu `${…}` imbricate, fel „sablon”) și ale șirurilor '…' / "…" din cod
        (fel „sir”). Comentariile și expresiile regulate se sar: un backtick dintr-un comentariu nu deschide un șablon."""
        spans, i, n, stiva, start, prev = [], 0, len(t), [], None, ""
        while i < n:
            c = t[i]
            top = stiva[-1] if stiva else None
            if top == "T":
                if c == "\\":
                    i += 2
                    continue
                if c == "`":
                    stiva.pop()
                    i += 1
                    if not stiva:
                        spans.append((start, i, "sablon"))
                    prev = "`"
                    continue
                if c == "$" and t[i + 1:i + 2] == "{":
                    stiva.append(0)
                    i += 2
                    prev = "{"
                    continue
                i += 1
                continue
            if c == "/" and t[i + 1:i + 2] == "/":
                j = t.find("\n", i)
                i = n if j < 0 else j
                continue
            if c == "/" and t[i + 1:i + 2] == "*":
                j = t.find("*/", i + 2)
                i = n if j < 0 else j + 2
                continue
            if c in "'\"":
                j = i + 1
                while j < n and t[j] != c and t[j] != "\n":
                    j += 2 if t[j] == "\\" else 1
                if not stiva:
                    spans.append((i, j + 1, "sir"))
                i, prev = j + 1, c
                continue
            if c == "/" and (prev == "" or prev in "(,=:[!&|?{};+-*%<>~^" or _re.search(r"\breturn\s*$", t[max(0, i - 8):i])):
                j, cls = i + 1, False
                while j < n and t[j] != "\n":
                    if t[j] == "\\":
                        j += 2
                        continue
                    if t[j] == "[":
                        cls = True
                    elif t[j] == "]":
                        cls = False
                    elif t[j] == "/" and not cls:
                        break
                    j += 1
                i, prev = j + 1, "/"
                continue
            if c == "`":
                if not stiva:
                    start = i
                stiva.append("T")
                i += 1
                continue
            if isinstance(top, int):
                if c == "{":
                    stiva[-1] += 1
                elif c == "}":
                    if top == 0:
                        stiva.pop()
                        i += 1
                        prev = "}"
                        continue
                    stiva[-1] -= 1
            if not c.isspace():
                prev = c
            i += 1
        return spans

    def _linie(t, p):
        return t[:p].count("\n") + 1

    # (a) navigatorul
    if not _re.search(r'const _cuTabel = \(\) => !!_corp\.querySelector\("table\b[^"]*"\);', nav):
        out.append(("navigator.js", 0, "FEREASTRA_TABEL", "navigatorul nu mai recunoaște singur fereastra care conține un tabel (`_cuTabel`)"))
    if not _re.search(r'const _lateste = \(\) => \{[^}]*?\(_cuTabel\(\) \|\| _prealata\(\)\)\) f\.classList\.add\("fer-tabel"\)', nav):
        out.append(("navigator.js", 0, "FEREASTRA_TABEL", "`_lateste` nu pune `fer-tabel` pe fereastra cu tabel"))
    if not _re.search(r'for \(const treapta of \["fer-strans", "fer-rupt"\]\) \{ if \(!_prealata\(\)\) break; f\.classList\.add\(treapta\); \}', nav):
        out.append(("navigator.js", 0, "FEREASTRA_TABEL", "tabelul care nu încape nu se mai strânge (`fer-strans` / `fer-rupt`): corpul fără derulare laterală l-ar tăia"))

    # (b) stil.css
    def _bloc(sel):
        m = _re.search(r"(?m)^" + _re.escape(sel) + r"\s*\{([^}]*)\}", css)
        return m.group(1) if m else None
    b = _bloc(".fereastra.fer-tabel") or ""
    for decl, ce in ((r"(?<![-\w])width:\s*calc\(100vw - 48px\)", "lățimea ecranului"),
                     (r"(?<![-\w])height:\s*calc\(100vh - 48px\)", "înălțimea ecranului")):
        if not _re.search(decl, b):
            out.append(("stil.css", 0, "FEREASTRA_TABEL", "`.fereastra.fer-tabel` nu mai are %s (DS cap.9 v2.96)" % ce))
    mc = _re.search(r"(?m)^\.fereastra\.fer-tabel \.fereastra-corp[^{]*\{([^}]*)\}", css)
    if not mc or not _re.search(r"overflow-x:\s*hidden", mc.group(1)) or not _re.search(r"overflow-y:\s*auto", mc.group(1)):
        out.append(("stil.css", 0, "FEREASTRA_TABEL", "corpul ferestrei cu tabel nu mai derulează numai vertical (`overflow-x: hidden`)"))
    for m in _re.finditer(r"([^{}]*\bfer-tabel\b[^{}]*)\{([^}]*)\}", css):
        if _re.search(r"overflow(?:-x)?\s*:\s*(?:auto|scroll)", m.group(2)):
            out.append(("stil.css", _linie(css, m.start(2)), "FEREASTRA_TABEL", "derulare laterală permisă: %s" % m.group(1).strip()[-60:]))
    r = _bloc(".fereastra-corp .rezumat-fix") or ""
    if not (_re.search(r"position:\s*sticky", r) and _re.search(r"(?<![-\w])top:\s*-24px", r)):
        out.append(("stil.css", 0, "FEREASTRA_TABEL", "`.rezumat-fix` nu mai e lipit sus (position: sticky; top: -24px)"))
    for m in _re.finditer(r"(?m)^[^{}\n]*\.mig-prev-cutie[^{}]*\{([^}]*)\}", css):
        if _re.search(r"max-height|overflow", m.group(1)):
            out.append(("stil.css", _linie(css, m.start(1)), "FEREASTRA_TABEL", "`.mig-prev-cutie` derulează iar ea însăși (al doilea element care derulează)"))
    # [lotul 10, REZUMAT_TABEL_LIPSA] a doua cutie cu derulare proprie a clasei: lista-tabel `.mig-sold-tabel` (Activitate cabinet)
    ms = _re.search(r"(?m)^\.fereastra\.fer-tabel \.fereastra-corp \.mig-sold-tabel \{([^}]*)\}", css)
    if not ms or not (_re.search(r"max-height:\s*none", ms.group(1)) and _re.search(r"(?<![-\w])overflow:\s*clip", ms.group(1))):
        out.append(("stil.css", 0, "FEREASTRA_TABEL", "lista-tabel `.mig-sold-tabel` derulează iar ea însăși în fereastra cu tabel (DS cap.9 v2.97)"))

    # (c) + (d) șabloanele JS
    re_fn = _re.compile(r"(?m)^(?:export\s+)?(?:async\s+)?function\s+\w+\s*\(\s*(\w*)")
    re_tab = _re.compile(r"<table\b(?![^>]*class=\"[^\"]*\b(?:%s)\b)|tabelPrevizualizare\(" % "|".join(sorted(tabele_macheta)))
    re_btn = _re.compile(r'<button\b[^>]*data-actiune="(?:POST|PUT|PATCH|DELETE)\b[^>]*>')
    re_inl = _re.compile(r"overflow(?:-x)?\s*:\s*(?:auto|scroll)\b")

    def _in_zona(s, p, cls):
        # [lotul 10, ZONE] adâncimea de la deschiderea zonei: zona s-a închis dacă adâncimea ajunge la 0 înaintea butonului. Numărarea
        # simplă (închideri <= deschideri) dădea „în zonă” unui buton pus într-un `<div>` frate rămas deschis după zona închisă.
        q = s.rfind(cls, 0, p)
        if q < 0:
            return False
        adanc = 1
        for m in _re.finditer(r"<(/?)div\b", s[q:p]):
            adanc += -1 if m.group(1) else 1
            if adanc <= 0:
                return False
        return True

    # [lotul 10, ZONE] acțiunile lăsate unde sunt, cu motivul (cheia: fișier, id-ul butonului). O excepție pe care regula n-o mai vede
    # (butonul a dispărut sau a ajuns în bară) pică, ca lista să nu putrezească.
    actiuni_exceptii = {
        ("firme.js", "el-adauga"):
            "formular: în panoul „Prime, sporuri, ore suplimentare” al unui salariat, tabelul elementelor lunii lui (câteva rânduri) stă "
            "deasupra formularului de adăugare; „Adaugă” e în rândul câmpurilor formularului, iar lipirea lui jos ar cere mutarea rândului întreg",
    }
    actiuni_vazute = set()
    # [lotul 11, MESAJ_SUB_TABEL / TOTAL_NEFIXAT] zonele de mesaj lăsate sub tabel, cu motivul (cheia: fișier, id-ul zonei); o excepție
    # fără obiect pică, ca la acțiuni.
    mesaje_exceptii = {
        ("firme.js", "el-msg"):
            "lângă butonul ei: panoul „Prime, sporuri, ore suplimentare” al unui salariat — zona stă sub rândul câmpurilor cu „Adaugă” "
            "(excepția `el-adauga` de la acțiuni), deci lângă butonul care o folosește; tabelul de deasupra e al elementelor lunii lui",
    }
    mesaje_vazute = set()
    re_zona_msg = _re.compile(r'<div\b[^>]*\bid="([\w-]+-(?:mesaj|msg|eroare))"')
    re_total_rand = _re.compile(r"<tr>\s*(?:<td[^>]*>\s*</td>\s*)?<td[^>]*>\s*<b>\s*Total\b")
    for nume, t in sorted(fisiere.items()):
        spans = _sabloane(t)
        for a, z, _f in spans:
            for m in re_inl.finditer(t, a, z):
                out.append((nume, _linie(t, m.start()), "DERULARE_INLINE", t[a:z][max(0, m.start() - a - 30):m.end() - a + 10].strip()[:80]))
        for m in _re.finditer(r"\.style\.overflow(?:X)?\s*=\s*[\"'](?:auto|scroll)", t):
            out.append((nume, _linie(t, m.start()), "DERULARE_INLINE", m.group(0)))
        sabl = [(a, z) for a, z, f in spans if f == "sablon"]
        cod = list(t)
        for a, z in sabl:           # codul fără șabloane (pozițiile rămân): `;` din HTML nu mai încheie o instrucțiune
            cod[a:z] = " " * (z - a)
        cod = "".join(cod)
        fns = [(m.start(), m.group(1) or "corp") for m in re_fn.finditer(t)]
        # funcțiile-șablon ale fișierului care întorc un tabel (nu scriu `innerHTML`): un `${f(…)}` în șablon e un tabel
        prod_fisier = set()
        for (q0, _c), (q1, _y) in zip(fns, fns[1:] + [(len(t), "")]):
            mn = _re.match(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", t[q0:q1])
            if mn and any(q0 <= a < q1 and re_tab.search(t, a, z) for a, z in sabl) and not _re.search(r"\.innerHTML\s*\+?=", cod[q0:q1]):
                prod_fisier.add(mn.group(1))
        for (s0, corp), (s1, _x) in zip([(0, "corp")] + fns, fns + [(len(t), "")]):
            if not re_tab.search(t, s0, s1):
                continue
            # variabilele funcției care țin un tabel: `const tabel = … `<table…`` (instrucțiunea până la șablon, fără `;` între)
            var_tab = set()
            for a, z in sabl:
                if s0 <= a < s1 and re_tab.search(t, a, z):
                    st = max(cod.rfind(";", s0, a), cod.rfind("\n\n", s0, a), s0)
                    mv = _re.search(r"(?:const|let|var)?\s*(\w+)\s*\+?=(?!=)[^=]*$", cod[st:a].replace("\n", " "))
                    if mv:
                        var_tab.add(mv.group(1))
            # [lotul 10, ZONE] producătorii de tabel ai funcției: arrow-urile `const X = (…) =>` al căror șablon are un tabel
            prod = set(prod_fisier)
            for mp in _re.finditer(r"(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>", cod[s0:s1]):
                for a, z in sabl:
                    if a >= s0 + mp.end() and re_tab.search(t, a, z) and not _re.search(r"(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>", cod[s0 + mp.end():a]):
                        prod.add(mp.group(1))
                        break
            adaugate = {m.group(2) for v in var_tab for m in _re.finditer(r"\b(%s)\s*\+=\s*(\w+)\(" % _re.escape(v), cod[s0:s1])}
            for a, z in sabl:
                if not (s0 <= a < s1):
                    continue
                s = t[a:z]
                ma = _re.search(r"(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>\s*$", cod[max(s0, a - 120):a])
                dupa_tabel = bool(ma and ma.group(1) in adaugate)     # șablonul adăugat după tabel (`corpHtml += formular(d)`)
                pozt = [m.start() for m in re_tab.finditer(s)] + [m.start() for v in var_tab for m in _re.finditer(r"\$\{\s*%s\b" % _re.escape(v), s)] \
                    + [m.start() for g in prod for m in _re.finditer(r"(?<![\w.$])%s\b(?=\s*[(),])" % _re.escape(g), s)]
                if not pozt and not dupa_tabel:
                    continue
                for mb in re_btn.finditer(s):
                    p = mb.start()
                    if not dupa_tabel and p < min(pozt):
                        continue                      # butonul de DEASUPRA tabelului: îl cere rezumatul (REZUMAT_TABEL_LIPSA), nu bara
                    if s.rfind("<td", 0, p) > s.rfind("</td>", 0, p) or _re.search(r'\sdata-(?!actiune)[\w-]+="\$\{', mb.group(0)):
                        continue                      # acțiunea unui rând, nu a ecranului
                    if _in_zona(s, p, "bara-fixa") or _in_zona(s, p, "rezumat-fix"):
                        continue
                    idm = _re.search(r'id="([^"]+)"', mb.group(0))
                    if idm and (nume, idm.group(1)) in actiuni_exceptii:
                        actiuni_vazute.add((nume, idm.group(1)))
                        continue
                    out.append((nume, _linie(t, a + p), "ACTIUNE_TABEL_NEFIXATA",
                                "„%s” la capătul conținutului: în .bara-fixa (jos) sau .rezumat-fix (sus) — DS cap.9 v2.96" % (
                                    idm.group(1) if idm else mb.group(0)[:50])))
                # [lotul 11, decizia Costin 10.3: „Totalurile și rezumatul fix, mesajele lângă buton”, DS cap.9 v2.100 pct.7–8]
                # MESAJ_SUB_TABEL — zona de mesaj a ecranului (`id="…-mesaj|-msg|-eroare"`) pusă DUPĂ tabel, în afara barei de jos și a
                # rezumatului: mesajul acțiunii de sus apărea la capătul tabelului, departe de butonul care îl produce (Stocuri `#s-mesaj`,
                # Înregistrare `#ins-cereri-msg`). Zona unui rând (în celulă) nu e a ecranului.
                if not dupa_tabel:
                    for mz in re_zona_msg.finditer(s):
                        p = mz.start()
                        if p < min(pozt) or s.rfind("<td", 0, p) > s.rfind("</td>", 0, p):
                            continue
                        if _in_zona(s, p, "bara-fixa") or _in_zona(s, p, "rezumat-fix"):
                            continue
                        if (nume, mz.group(1)) in mesaje_exceptii:
                            mesaje_vazute.add((nume, mz.group(1)))
                            continue
                        out.append((nume, _linie(t, a + p), "MESAJ_SUB_TABEL",
                                    "zona de mesaj „%s” stă sub tabel, departe de butonul ei: în .rezumat-fix (lângă butoanele de sus) sau "
                                    ".bara-fixa (lângă acțiunea de jos) — DS cap.9 v2.100" % mz.group(1)))
                # TOTAL_NEFIXAT — totalul unui tabel care iese din vedere cât derulezi: rândul „Total” lăsat în `<tbody>` (se lipește jos
                # numai din `<tfoot>`), sau caseta `.fd-totaluri` pusă după tabel în afara `.bara-fixa`.
                for mt in re_total_rand.finditer(s):
                    p = mt.start()
                    if s.rfind("<tbody", 0, p) > max(s.rfind("</tbody>", 0, p), s.rfind("<tfoot", 0, p)):
                        out.append((nume, _linie(t, a + p), "TOTAL_NEFIXAT",
                                    "rândul de total stă în <tbody>: în <tfoot>, ca să rămână jos, în vedere — DS cap.9 v2.100"))
                for mt in _re.finditer(r'class="fd-totaluri\b', s):
                    p = mt.start()
                    if (dupa_tabel or p > min(pozt)) and not _in_zona(s, p, "bara-fixa"):
                        out.append((nume, _linie(t, a + p), "TOTAL_NEFIXAT",
                                    "caseta de totaluri stă după tabel, în afara .bara-fixa: iese din vedere cât derulezi — DS cap.9 v2.100"))

    for (fis, ida), _motiv in sorted(actiuni_exceptii.items()):
        if fis in fisiere and (fis, ida) not in actiuni_vazute:
            out.append((fis, 0, "ACTIUNE_TABEL_NEFIXATA", "excepția „%s” nu mai are obiect: butonul nu mai e la capătul unui tabel" % ida))
    for (fis, idz), _motiv in sorted(mesaje_exceptii.items()):
        if fis in fisiere and (fis, idz) not in mesaje_vazute:
            out.append((fis, 0, "MESAJ_SUB_TABEL", "excepția „%s” nu mai are obiect: zona nu mai stă sub un tabel" % idz))
    # [lotul 11, TOTAL_NEFIXAT, partea de stil] rândul de total se lipește jos în fereastra cu tabel, deasupra barei (`--bara-h`, pus de
    # navigator ca `--rezumat-h`), iar caseta de totaluri din bară stă pe un rând
    mtf = _re.search(r"(?m)^\.fereastra\.fer-tabel \.fereastra-corp \.fd-tabel tfoot td[^{]*\{([^}]*)\}", css)
    if not mtf or not (_re.search(r"position:\s*sticky", mtf.group(1)) and _re.search(r"bottom:\s*calc\(var\(--bara-h", mtf.group(1))):
        out.append(("stil.css", 0, "TOTAL_NEFIXAT", "rândul de total (`tfoot`) nu mai e lipit jos, deasupra barei (`--bara-h`) — DS cap.9 v2.100"))
    if not _re.search(r'_corp\.style\.setProperty\("--bara-h"', nav):
        out.append(("navigator.js", 0, "TOTAL_NEFIXAT", "navigatorul nu mai pune `--bara-h` (înălțimea barei de jos): totalul lipit ar sta sub bară"))

    # (e) REZUMAT_TABEL_LIPSA — rezumatul lipit sus al ferestrei cu tabel (DS cap.9 v2.97 pct.5). Excepțiile se scriu, ca să poată fi
    # contrazise; cheia e (fișier, funcția care desenează tabelul).
    rezumat_exceptii = {
        ("date_firma.js", "randeazaDateFirma"):
            "formular: Date firmă e un formular lung cu patru tabele mici în el (perioadele TVA la încasare, asociații, cesiunile, istoricul); "
            "se derulează formularul, nu un tabel, iar „Salvează” stă deja în bara fixă (DS cap.9 pct.5: rezumatul e ce trebuie văzut cât "
            "derulezi TABELUL)",
        ("operatiuni_ecran.js", "ecranOperatiuni"):
            "formular: tabelul împărțirii dividendului pe asociați e rezultatul câmpurilor de deasupra (câteva rânduri și totalul lor), "
            "iar „Generează nota” stă deja în bara fixă",
        # [lotul 11] cele trei excepții „de decis de Costin” (Tipare, Înregistrare — cererile neconfirmate, Stocuri — situația stocului)
        # au fost decise (DECIZII „Comanda 10.3” pct.4: „Totalurile și rezumatul fix, mesajele lângă buton […]: da, reorganizezi
        # ecranele”) și scoase: ecranele au acum rezumatul lipit sus.
    }
    re_fn_n = _re.compile(r"(?m)^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(")
    re_tab_d = _re.compile(r"<table\b(?![^>]*class=\"[^\"]*\b(?:%s)\b)|class=\"[^\"]*\bmig-sold-tabel\b" % "|".join(sorted(tabele_macheta)))
    re_rez = _re.compile(r"class=\"[^\"]*\brezumat-fix\b")
    for nume, t in sorted(fisiere.items()):
        lit = [(a, z) for a, z, _f in _sabloane(t)]
        fc, prec = [], 0                                       # codul fără comentarii (șabloanele rămân, cu tot cu `${…}`)
        for a, z in lit + [(len(t), len(t))]:
            seg = _re.sub(r"/\*.*?\*/|//[^\n]*", lambda m: _re.sub(r"[^\n]", " ", m.group(0)), t[prec:a], flags=_re.S)
            fc.append(seg + t[a:z])
            prec = z
        fc = "".join(fc)
        defs = [(m.start(), m.group(1)) for m in re_fn_n.finditer(t)]
        fn = {}
        for (s0, n0), (s1, _x) in zip(defs, defs[1:] + [(len(t), "")]):
            texte = " ".join(t[a:z] for a, z in lit if s0 <= a < s1)
            fn[n0] = {"s0": s0, "cod": fc[s0:s1], "tab": bool(re_tab_d.search(texte)), "rez": bool(re_rez.search(texte)),
                      "scrie": bool(_re.search(r"\.innerHTML\s*\+?=(?!=)", fc[s0:s1]))}
        for n0, f in fn.items():
            f["cheama"] = {g for g in fn if g != n0 and _re.search(r"(?<![\w.$])%s\(" % g, f["cod"])}
        sablon = lambda g, cheie: fn[g][cheie] and not fn[g]["scrie"]       # funcție-șablon: întoarce HTML, nu scrie în fereastră
        for f in fn.values():
            f["deseneaza"] = f["tab"] or any(sablon(g, "tab") for g in f["cheama"])
            f["are_rez"] = f["rez"] or any(sablon(g, "rez") for g in f["cheama"])

        def _aceeasi_fereastra(g, n0):                         # g cheamă n0 pe un rând care NU deschide altă fereastră
            return any(not _re.search(r"\b(?:deschide|mergi)\(", fn[g]["cod"][fn[g]["cod"].rfind("\n", 0, m.start()) + 1:
                                                                            (fn[g]["cod"] + "\n").find("\n", m.start())])
                       for m in _re.finditer(r"(?<![\w.$])%s\(" % n0, fn[g]["cod"]))

        def _acoperit(n0, vazut, cu_exceptii=True):
            if n0 in vazut:
                return False
            vazut = vazut | {n0}
            if fn[n0]["are_rez"] or (cu_exceptii and (nume, n0) in rezumat_exceptii):
                return True
            return any(_acoperit(g, vazut, cu_exceptii) for g in fn if n0 in fn[g]["cheama"] and _aceeasi_fereastra(g, n0))

        for n0, f in sorted(fn.items(), key=lambda x: x[1]["s0"]):
            if f["deseneaza"] and f["scrie"] and not _acoperit(n0, set()):
                out.append((nume, _linie(t, f["s0"]), "REZUMAT_TABEL_LIPSA",
                            "„%s” desenează un tabel în fereastră fără rezumatul lipit sus (`.rezumat-fix`) — DS cap.9 v2.97 pct.5" % n0))
        for (fis, n0), motiv in sorted(rezumat_exceptii.items()):
            if fis != nume:
                continue
            if n0 not in fn or not (fn[n0]["deseneaza"] and fn[n0]["scrie"]):
                out.append((nume, 0, "REZUMAT_TABEL_LIPSA", "excepția „%s” nu mai are obiect: funcția nu mai desenează un tabel în fereastră" % n0))
            elif _acoperit(n0, set(), cu_exceptii=False):
                out.append((nume, _linie(t, fn[n0]["s0"]), "REZUMAT_TABEL_LIPSA", "excepția „%s” nu mai are obiect: are acum rezumatul lipit sus" % n0))

    # (f) REZUMAT_CASETA — [lotul 12, comanda Costin 12.2 pct.11, deficiența 621, verbatim: „Balanța: casetele de sus ocupă jumătate din
    #     fereastră, se văd 2–3 rânduri de tabel”; cerința: „Casetele nu mănâncă tabelul (regulă globală, nu doar pe balanță)”] DS cap.9
    #     v2.102: în rezumatul lipit sus (`.rezumat-fix`) stă numai ce trebuie văzut cât derulezi — titlul, perioada, cifrele, butoanele,
    #     zona lor de mesaj, o concluzie pe un rând. O casetă (`.caseta-info` / `.caseta-atentie` / `.caseta-poarta`, sau `${caseta…}` — o
    #     funcție / variabilă care o produce) pusă în rezumat se lipește și ea și ia din fereastră cât ține: stă SUB rezumat (se citește la
    #     deschidere, iar tabelul primește fereastra cât derulezi) sau, ca notă informativă, pliată (`<details class="dec-xml">`, concluzia
    #     în titlu). Mutația care o probează (`core/test_lot12_ui2_rezumat.py`): caseta rulajelor pusă înapoi în rezumatul Balanței -> prinsă.
    #     LIMITĂ: vede șabloanele scrise literal; o casetă ajunsă în rezumat printr-o variabilă cu alt nume (`${sus}` din `_cadruPrev`) nu
    #     se vede — pe aceea o măsoară testul în browser (înălțimea rezumatului, `core/test_lot12_ui2_rezumat.py`).
    re_caseta = _re.compile(r'class="(?:caseta-info|caseta-atentie|caseta-poarta)\b|\$\{\s*caseta\w*')
    for nume, t in sorted(fisiere.items()):
        for a, z, fel in _sabloane(t):
            s = t[a:z]
            if fel != "sablon" or "rezumat-fix" not in s:
                continue
            for mc in re_caseta.finditer(s):
                p = mc.start()
                if not _in_zona(s, p, "rezumat-fix"):
                    continue
                seg = s[s.rfind("rezumat-fix", 0, p):p]
                if seg.rfind("<details") > seg.rfind("</details>"):
                    continue                                  # notă pliată: în rezumat stă numai titlul ei
                out.append((nume, _linie(t, a + p), "REZUMAT_CASETA",
                            "casetă în rezumatul lipit sus: stă sub rezumat sau pliată (`details.dec-xml`) — DS cap.9 v2.102 (621): " + s[p:p + 50].replace("\n", " ")))
    return out

rap["fereastra_tabel"] = analiza_fereastra_tabel(_surse_css["stil.css"], _nav_l6, fisiere)

rap["fereastra_scris"] = []
_blocuri_pacm = re.findall(r"(?m)^\.pacm \{([^}]*)\}", _surse_css["stil.css"])
if len(_blocuri_pacm) != 1 or not re.search(r"(?<![-\w])height:\s*calc\(100vh", _blocuri_pacm[0] if _blocuri_pacm else ""):
    rap["fereastra_scris"].append(("stil.css", 0, "PACM", "%d blocuri `.pacm`, înălțimea ecranului: %s" % (
        len(_blocuri_pacm), bool(_blocuri_pacm and re.search(r"(?<![-\w])height:\s*calc\(100vh", _blocuri_pacm[0])))))


# --- DUPA_GENERARE (DS cap.6 v2.98, lotul 11 — 8c, decizia Costin 10.3: „8c: reparația centrală, cu DS cap. 6 actualizat.”). Clasa,
#     raportul Z (comanda 10.2 pct.8c): „După generare, titlul «Notă generată» e roșu, conturile notei nu se văd, iar «Generează notă»
#     rămâne activ.” Un singur drum: `api.dupaGenerare` (stilul de succes, conturile și sumele, butonul inactiv cu motivul).
#     Mutațiile care o probează (`core/test_lot11_j_verificator.py`, pe fragmente și pe fișierele reale): `butonGenerat(` scos din
#     helper; un buton „Generează …” fără `data-genereaza-nota`; „Notă generată” scris de mână într-un ecran; apelul helperului scos din
#     handlerul butonului -> lista nevidă -> TOTAL > 0.
#     LIMITA, declarată: (1) domeniul îl dă eticheta butonului (`_GENERATOARE`) — un buton nou de generare cu altă etichetă intră numai
#     când e adăugat în listă (sau poartă singur `data-genereaza-nota`); (2) legătura buton -> helper e textuală: un `dupaGenerare(` în
#     cel mult 80 de rânduri după o referință la `#<id>`-ul butonului; nu dovedește că apelul e pe ramura de succes (o dovedesc testele
#     în browser, `core/test_lot11_j_dupa_generare.py`); (3) stornarea facturii nu e aici: se încheie cu confirmarea DS cap.27 (418c).
_GENERATOARE = re.compile(r"Genereaz[ăa] (?:not|amortizar|compensar)|Regenereaz[ăa] amortizar|Desc[ăa]rc[ăa] gestiunea|"
                          r"Finalizeaz[ăa] inventarul|Salveaz[ăa] inventarul|Scrie nota|[ÎI]nlocuie[șş]te ciorna|Recontabilizeaz[ăa]|"
                          r"Reevalueaz[ăa]|Caseaz[ăa]")


def analiza_dupa_generare(fisiere):
    """[(fișier, linie, COD, text)] — funcție PURĂ (primește {nume: sursă JS}), chemată de `core/test_lot11_j_verificator.py` pe
    fragmente known-good / known-bad și pe fișierele reale. Codurile: DUPA_GENERARE_HELPER (helperul unic din api.js nu face ce cere
    regula), GENERARE_NEDECLARATA (buton de generare fără `data-genereaza-nota`), GENERARE_FARA_HELPER (butonul declarat nu trece prin
    `dupaGenerare`), TEXT_GENERAT_DE_MANA („Notă generată” scris în afara helperului — culoarea și conturile ar depinde de ecran)."""
    import re as _re
    out = []
    dec = lambda s: _re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    api = fisiere.get("api.js", "")

    def _corp(nume):
        m = _re.search(r"export function %s\([^)]*\)\s*\{(.*?)\n\}" % nume, api, _re.S)
        return m.group(1) if m else None
    dg, bg = _corp("dupaGenerare"), _corp("butonGenerat")
    if dg is None or bg is None:
        out.append(("api.js", 0, "DUPA_GENERARE_HELPER", "lipsește helperul unic `dupaGenerare` / `butonGenerat` (DS cap.6 v2.98)"))
    else:
        for frag, motiv in (("msg-(eroare|avert|info|ok)", "nu șterge culoarea refuzului de dinainte"),
                            ("caseta-ok", "nu are stilul de succes (.caseta-ok)"),
                            ("liniiNotaHtml(", "nu arată conturile și sumele notei"),
                            ("butonGenerat(", "nu dezactivează butonul de generare")):
            if frag not in dg:
                out.append(("api.js", 0, "DUPA_GENERARE_HELPER", "dupaGenerare %s (DS cap.6 v2.98)" % motiv))
        if "disabled = true" not in bg:
            out.append(("api.js", 0, "DUPA_GENERARE_HELPER", "butonGenerat nu face butonul inactiv (DS cap.6 v2.98)"))
    re_txt = _re.compile(r"\b[Nn]ot[ăa] generat[ăa]\b|\b[Nn]ote generate\b")
    for nume, t in sorted(fisiere.items()):
        linii = t.split("\n")
        if nume != "api.js":
            for i, lin in enumerate(linii, 1):
                if lin.strip().startswith(("//", "/*", "*")):
                    continue
                if re_txt.search(dec(_re.sub(r"\s//\s.*$", "", lin))):
                    out.append((nume, i, "TEXT_GENERAT_DE_MANA", "„Notă generată” în afara helperului: confirmarea trece prin "
                                "`dupaGenerare` (DS cap.6 v2.98)"))
        cheama = [i for i, lin in enumerate(linii) if "dupaGenerare(" in lin and not lin.strip().startswith(("//", "*"))]
        for m in _re.finditer(r"<button\b[^>]*>(?:[^<]|<(?!/button>))*</button>", t):
            tag = m.group(0)
            if tag.startswith("<button") and "data-fara-actiune" in tag:
                continue
            i = t[:m.start()].count("\n") + 1
            if _GENERATOARE.search(dec(tag)) and "data-genereaza-nota" not in tag:
                out.append((nume, i, "GENERARE_NEDECLARATA", "buton de generare fără `data-genereaza-nota` (DS cap.6 v2.98): %s"
                            % _re.sub(r"\s+", " ", dec(tag))[:90]))
            if "data-genereaza-nota" not in tag:
                continue
            mid = _re.search(r'\bid="([\w-]+)"', tag)
            if mid:
                x = mid.group(1)
                refs = [k for k, lin in enumerate(linii) if ("#%s\"" % x) in lin or ("#%s'" % x) in lin]
                # butonul dat helperului: `#x` chiar în apel, sau variabila legată de `querySelector("#x")`. Ecranul care se
                # redesenează fără buton (confirmarea cu `null`) o declară: `data-genereaza-nota="redesenat"` — atunci ajunge apelul
                var = {v for k in refs for v in _re.findall(r"\b(?:const|let)\s+(\w+)\s*=\s*[^;]*#%s[\"']" % _re.escape(x), linii[k])}
                da_butonul = lambda lin: _re.search(r"#%s[\"']" % _re.escape(x), lin.split("dupaGenerare(", 1)[1]) or any(
                    _re.search(r"dupaGenerare\([^,]*,\s*%s\b" % v, lin) for v in var)
                redesenat = 'data-genereaza-nota="redesenat"' in tag
                if not any(r0 <= c <= r0 + 80 and (redesenat or da_butonul(linii[c])) for r0 in refs for c in cheama):
                    out.append((nume, i, "GENERARE_FARA_HELPER", "butonul #%s generează o notă, dar handlerul lui nu cheamă "
                                "`dupaGenerare` (DS cap.6 v2.98)" % mid.group(1)))
            elif not cheama:
                out.append((nume, i, "GENERARE_FARA_HELPER", "buton de generare fără id, iar fișierul nu cheamă `dupaGenerare`"))
    return out


rap["dupa_generare"] = analiza_dupa_generare(fisiere)


# --- TITLU_FARA_DIACRITICE (lotul 11, comanda 11.1 pct.23: „titluri fără diacritice”). Titlurile de ferestre, carduri, secțiuni, coloane,
#     opțiuni și butoane se scriu cu diacritice. Regula `diacritice` de mai sus (CUVINTE) prinde verbe din texte; aici, un DICȚIONAR de
#     cuvinte frecvente din titluri care NU au formă corectă fără diacritice („Inregistrare”, „Iesire”, „Declaratii”…), plus titlul
#     „Factura” scris singur (forma de titlu e „Factură”). Mutația: `<th>Factura</th>` sau `nav.deschide("Iesiri", …)` -> TOTAL > 0.
#     LIMITA: un cuvânt corect și fără diacritice în altă formă („plata”, „luna”, „factura” articulat) nu intră — nu se poate judeca
#     din text; dicționarul crește când se găsește un titlu nou (ca CUVINTE).
_TITLU_FARA_DIACRITICE = frozenset("""inregistrare inregistrari iesire iesiri intrari situatie situatia situatii declaratie declaratia declaratii
    setari notificari notificare operatiuni operatiune incasari incasare plati adeverinta adeverinte balanta evidenta fisa fisier fisiere
    retete reteta productie tranzactii tranzactie asociati salariati contributii inchidere inapoi optiuni optiune pozitii informatii
    ajustari cautare adaugare stergere selectie configuratie actiune actiuni activitati atentie diferente bilant imobilizari compensari
    genereaza salveaza valideaza descarca incarca anuleaza renunta pastreaza sterge adauga inlocuieste chitante chitanta dispozitii
    dispozitie noua lunara initiala scadente judet sfarsit inceput raspuns marfuri achizitii livrari prestari incarcare descarcare
    rectificativa clienti angajati asistenti mentiuni observatii conditii ocupatie banci unitati pret preturi creante numar
    saptamana urmatoarea urmator precedenta curenta neimputabila imputabila justificata mancare bauturi""".split())


def analiza_titluri_diacritice(fisiere):
    """[(fișier, linie, cuvânt, titlu)] — funcție PURĂ, chemată de `core/test_lot11_j_verificator.py`."""
    import re as _re
    out = []
    dec = lambda s: _re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    ctx = [r'\.deschide\(\s*"([^"]+)"', r"\.deschide\(\s*'([^']+)'", r"<h[1-6][^>]*>([^<$]+)", r'\btitlu:\s*"([^"]+)"',
           r'class="[^"]*\b(?:pf-titlu|pf-subtitlu|cf-grup-titlu|cab-card-titlu|cok-titlu)\b[^"]*"[^>]*>([^<$]+)', r"<summary[^>]*>([^<$]+)",
           r"<legend[^>]*>([^<$]+)", r"<th[^>]*>([^<$]+)", r"<option[^>]*>([^<$]+)", r'camp-eticheta"[^>]*>([^<$]+)',
           r"<button[^>]*>([^<$]+)"]
    for nume, t in sorted(fisiere.items()):
        for i, lin in enumerate(t.split("\n"), 1):
            if lin.strip().startswith(("//", "/*", "*")):
                continue
            vazute = set()   # același titlu prins de două tipare (<h2 class="pf-titlu">) se numără o dată
            for p in ctx:
                for m in _re.finditer(p, lin):
                    s = dec(m.group(1)).strip()
                    gasite = ["Factura"] if s == "Factura" else [w for w in _re.findall(r"[A-Za-zĂÂÎȘȚăâîșțşţ]+", s)
                                                                  if w.lower() in _TITLU_FARA_DIACRITICE]
                    for w in gasite:
                        if (m.start(1), w) not in vazute:
                            vazute.add((m.start(1), w))
                            out.append((nume, i, w, "titlul „Factura” -> „Factură”" if s == "Factura" else s[:70]))
    return out


rap["titlu_fara_diacritice"] = analiza_titluri_diacritice(fisiere)


# --- [lotul 11, subagentul U0] cele patru reguli transversale ale comenzii 11.1 (DS v2.99): 440 ERORI_TOATE, 441 DATA_GOLIBILA,
#     443 SERIE_LIPITA, 445 INTOARCERE_DIN_REFUZ. Funcție PURĂ, chemată de `core/test_lot11_u0_verificator.py` pe fragmente și pe
#     fișierele reale. Limita declarată: INTOARCERE_DIN_REFUZ privește mecanismul unic (navigator + `butonSpreEcran`); un buton „Deschide …”
#     scris de mână într-un refuz, care cheamă `nav.deschide` fără `nav.dinRefuz()`, nu se recunoaște static.
#: trimiterea la o EROARE fără textul ei („motivul e mai jos”, „câmpul marcat mai sus”, „(vezi mai sus)”, „motivele mai jos”); nu
#: frazele care descriu conținutul de alături („o vezi mai jos” după o generare, „ce vezi mai sus e numărul de operațiuni”)
_MAI_SUS = r"(?:motivul e|motivele(?: sunt)?|\(vezi|marcat|marcate)\s+(?:de\s+)?mai\s+(?:sus|jos)"


def analiza_lot11_u0(fisiere, css=""):
    """[(fișier, linie, COD, text)]."""
    import re as _re
    out = []
    api, nav = fisiere.get("api.js", ""), fisiere.get("navigator.js", "")
    dest = fisiere.get("ecran_destinatie.js", "")

    def _corp(src, antet):
        m = _re.search(antet + r"[^{]*\{(.*?)\n\}", src, _re.S)
        return m.group(1) if m else ""
    # 440 — mecanismul unic din api.js
    rs, ec = _corp(api, r"export function refuzSalvare\("), _corp(api, r"export function eroareCamp\(")
    if not rs or "motivul e" in rs:
        out.append(("api.js", 0, "ERORI_TOATE", "caseta „NU s-a salvat.” trimite la refuz („motivul e mai sus”) în loc să-i spună textul (440)"))
    if "aria-describedby" not in ec:
        out.append(("api.js", 0, "ERORI_TOATE", "eroareCamp nu leagă eroarea de câmp (aria-describedby, 440)"))
    if "export function arataRefuzul(" not in api or api.count("setTimeout(() => _campuriAutomat(e, declansator), 0)") < 2:
        out.append(("api.js", 0, "ERORI_TOATE", "refuzul serverului nu-și mai pune toate câmpurile (arataRefuzul / _campuriAutomat în cere și cereForm, 440)"))
    # 441 — câmpul de dată opțional se poate goli
    if "export function dataGolibila(" not in api or "_dateGolibileIn(n)" not in api:
        out.append(("api.js", 0, "DATA_GOLIBILA", "câmpurile de dată opționale nu mai primesc „×” (dataGolibila + observator, 441)"))
    if css and not _re.search(r"(?m)^\.data-golibila \{", css):
        out.append(("stil.css", 0, "DATA_GOLIBILA", "regula .data-golibila lipsește (DS cap.6 v2.99, 441)"))
    # 445 — „Deschide X” dintr-un refuz întoarce la formular
    bs = _corp(dest, r"export function butonSpreEcran\(")
    if dest and ("nav.dinRefuz()" not in bs or "titluCurent" not in bs):
        out.append(("ecran_destinatie.js", 0, "INTOARCERE_DIN_REFUZ", "butonSpreEcran nu mai anunță navigatorul (nav.dinRefuz / inapoiLa implicit, 445)"))
    if nav and ("_dePastrat(dinRefuz)" not in nav or "sus.intoarcere && stiva.length > 1 ? nav.inapoi()" not in nav):
        out.append(("navigator.js", 0, "INTOARCERE_DIN_REFUZ", "fereastra din refuz nu mai păstrează formularul / X o aruncă (445)"))
    for nume, t in sorted(fisiere.items()):
        for i, lin in enumerate(t.split("\n"), 1):
            s = lin.strip()
            if s.startswith(("//", "/*", "*")):
                continue
            cod = _re.sub(r"\s//\s.*$", "", lin)
            # 440 — trimiterea fără text la o eroare
            if _re.search(_MAI_SUS, cod, _re.I):
                out.append((nume, i, "ERORI_TOATE", "trimitere „mai sus / mai jos” în locul textului erorii (440): " + s[:80]))
            # 443 — seria lipită de număr (în afara helperului `numarCuSerie`)
            if nume != "api.js" and (_re.search(r"\$\{[^}]*\bserie\w*[^}]*\}\s*-?\s*\$\{[^}]*\b(?:numar|nr|urmator_numar)\w*", cod)
                                     or _re.search(r"\bserie\w*\s*\|\|\s*[\"']{2}\s*\)\s*\+\s*\(?\s*[\w.]*numar", cod)
                                     or _re.search(r"\[\s*[\w.]*serie\w*\s*,\s*[\w.]*numar\w*\s*\]\s*\.filter\(Boolean\)\.join", cod)):
                out.append((nume, i, "SERIE_LIPITA", "seria lipită de număr — numarCuSerie(serie, numar) dă „F6 nr. 1” (443): " + s[:80]))
    return out


rap["lot11_u0"] = analiza_lot11_u0(fisiere, open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read())


def analiza_lot12(fisiere, css=""):
    """[lotul 12] (469) vederea aleasă nu e `disabled`; (617 / 622) notele numai prin tabelul comun; (561 / 596 / C111) tot ce stă pe
    ecranul întreg derulează. [(fișier, linie, COD, text)]."""
    import re as _re
    out = []
    ales = _re.compile(r"\$\{\s*[\w.\[\]\"']+\s*===?\s*[^?}]+\?\s*[\"'`]\s*disabled\s*[\"'`]\s*:\s*[\"'`]{2}\s*\}")
    for nume, t in sorted(fisiere.items()):
        for i, lin in enumerate(t.split("\n"), 1):
            if lin.strip().startswith(("//", "/*", "*")):
                continue
            if ales.search(lin):
                out.append((nume, i, "ALEGERE_DEZACTIVATA", "vederea aleasă marcată `disabled` (DS cap.1, 469): " + lin.strip()[:80]))
    # [lotul 12, comanda Costin 12.2 pct.9 și 12, deficiențele 617 / 622] TABEL_NOTE — notele (Registrul jurnal, „De validat”) se arată
    # NUMAI prin tabelul comun (`ecrane/tabel_note.js`, DS cap.9 v2.102 „Tabelul de note”): CLAUDE.md §9 „situații identice, soluții
    # identice”. Prinde: un rând de notă scris de mână într-un alt fișier (`<… data-nota-id="…">`, forma cardurilor `.pf-frand` de
    # dinainte), cardul de notă din coadă (`randNota`, `ul.sa-jurnal` al ciornelor) și ecranele care nu mai cheamă componenta.
    # Mutația care o probează (`core/test_lot12_ui2_verificator.py`): rândul `.pf-frand data-nota-id` pus înapoi -> prins.
    for nume, t in sorted(fisiere.items()):
        if nume == "tabel_note.js":
            continue
        for i, lin in enumerate(t.split("\n"), 1):
            if lin.strip().startswith(("//", "/*", "*")):
                continue
            if _re.search(r"<\w+\b[^>`]*\sdata-nota-id=", lin):
                out.append((nume, i, "TABEL_NOTE", "rândul unei note scris de mână: notele se arată prin `tabel_note.js` (DS cap.9 v2.102): " + lin.strip()[:80]))
    for nume, cere in (("firme.js", "htmlTabelNote({ pre: \"jn\""), ("validat.js", "htmlTabelNote({ pre: \"val-n\"")):
        if nume in fisiere and cere not in fisiere[nume]:
            out.append((nume, 0, "TABEL_NOTE", "ecranul notelor nu mai folosește tabelul comun (`%s`) — DS cap.9 v2.102" % cere))
    if "validat.js" in fisiere and _re.search(r"function randNota\(|class=\"sa-jurnal\"", fisiere["validat.js"]):
        out.append(("validat.js", 0, "TABEL_NOTE", "„De validat” arată notele altfel decât în tabelul comun (cardul `randNota` / lista `sa-jurnal`) — 622"))
    if css and _re.search(r"html\s*,\s*body\s*\{[^}]*overflow-y\s*:\s*hidden", css):
        app = " ".join(m.group(1) for m in _re.finditer(r"(?m)^#app\s*\{([^}]*)\}", css))
        if not (_re.search(r"(?<![-\w])height\s*:\s*100dvh", app) and _re.search(r"overflow-y\s*:\s*auto", app)):
            out.append(("stil.css", 0, "SCROLL_APP", "#app fără height:100dvh + overflow-y:auto: ecranele puse direct în el nu derulează (DS cap.22 §7, C111)"))
        for sel in (".acces-modal", ".reaut"):
            dec = " ".join(m.group(1) for m in _re.finditer(r"(?m)^%s\s*\{([^}]*)\}" % _re.escape(sel), css))
            if not (_re.search(r"max-height\s*:", dec) and _re.search(r"overflow-y\s*:\s*auto", dec)):
                out.append(("stil.css", 0, "STRAT_INCAPE", "%s fără max-height + overflow-y:auto: fereastra iese din ecran (DS cap.22 §7, C111)" % sel))
    # [lotul 12, C164 — comanda Costin 12.3 pct.4, verbatim: „pe ecranele scunde, antetul detaliului facturii se strânge pe un rând (număr,
    # client, total, stare SPV); acțiunea principală rămâne fixă jos (clasa 285).”] ANTET_SCUND (DS cap.9 v2.103 „Antetul documentului pe
    # ecranul scund”). Prinde: (1) pragul ecranului scund scris în JS (`matchMedia` cu `max-height`) — pragul stă numai în `stil.css`, ca
    # `--antet-scund`; (2) `stil.css` fără media query-ul care pune `--antet-scund: 1`, fără valoarea de bază `0`, sau cu rândul scurt
    # `.fd-antet-scurt` care se poate rupe (fără `flex-wrap: nowrap` + `white-space: nowrap`); (3) un antet de document lipit sus
    # (`fd-antet rezumat-fix`) cu butoane, într-un fișier fără rândul scurt (`fd-antet-scurt`), fără bara acțiunilor (`fd-bara-actiuni`) sau
    # fără `aseazaAntetul(`. Mutațiile care o probează: `core/test_lot12_fe3_verificator.py`.
    for nume, t in sorted(fisiere.items()):
        for i, lin in enumerate(t.split("\n"), 1):
            if lin.strip().startswith(("//", "/*", "*")):
                continue
            if _re.search(r"matchMedia\(\s*[\"'`][^\"'`]*max-height", lin):
                out.append((nume, i, "ANTET_SCUND", "pragul ecranului scund scris în JS: se citește `--antet-scund` din stil.css (DS cap.9 v2.103): "
                            + lin.strip()[:80]))
        for m in _re.finditer(r"fd-antet rezumat-fix", t):
            # șablonul care conține antetul (de la `innerHTML = \`` până la `\`;`) și corpul funcției de după el (până la următoarea funcție)
            st = t.rfind("innerHTML = `", 0, m.start())
            sf = t.find("`;", m.start())
            if st < 0 or sf < 0:
                continue
            sablon = t[st:sf]
            rest = _re.split(r"\n(?:async )?function ", t[sf:], maxsplit=1)[0]
            if "buton-secundar" not in sablon[sablon.find("fd-antet rezumat-fix"):sablon.find("</table>") if "</table>" in sablon else None]:
                continue   # antet fără acțiuni (factura preluată): încape oricum, nu se cere
            lipsa = [x for x, ok in (("rândul scurt `fd-antet-scurt`", "fd-antet-scurt" in sablon),
                                     ("bara acțiunilor `fd-bara-actiuni`", "fd-bara-actiuni" in sablon),
                                     ("așezarea `aseazaAntetul(corp);` după desenare", _re.search(r"(?m)^\s*aseazaAntetul\(corp\);", rest)))
                     if not ok]
            if lipsa:
                out.append((nume, t.count("\n", 0, m.start()) + 1, "ANTET_SCUND",
                            "antetul lipit al documentului, cu acțiuni, fără forma ecranului scund (lipsește %s) — DS cap.9 v2.103"
                            % "; ".join(lipsa)))
    if css:
        if not _re.search(r"@media\s*\(\s*max-height\s*:\s*\d+px\s*\)[^{]*\{\s*:root\s*\{\s*--antet-scund\s*:\s*1\s*;?\s*\}", css):
            out.append(("stil.css", 0, "ANTET_SCUND", "lipsește media query-ul pe înălțime care pune `--antet-scund: 1` (pragul ecranului scund, DS cap.9 v2.103)"))
        if not _re.search(r"(?m)^:root\s*\{\s*--antet-scund\s*:\s*0\s*;?\s*\}", css):
            out.append(("stil.css", 0, "ANTET_SCUND", "lipsește valoarea de bază `:root { --antet-scund: 0; }` (DS cap.9 v2.103)"))
        dec = " ".join(m.group(1) for m in _re.finditer(r"(?m)^\.fd-antet-scurt\s*\{([^}]*)\}", css))
        if not (_re.search(r"flex-wrap\s*:\s*nowrap", dec) and _re.search(r"white-space\s*:\s*nowrap", dec)):
            out.append(("stil.css", 0, "ANTET_SCUND", "rândul scurt `.fd-antet-scurt` se poate rupe pe mai multe rânduri (DS cap.9 v2.103: un rând)"))
    return out


rap["lot12"] = analiza_lot12(fisiere, open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read())


# ── [lotul 13, comanda 13.1, zona DS] Clasele Design System ale comenzii 13.1 — DS cap.1 (675), cap.2a „Acțiunile din ferestre” (673,
# 674, 676), cap.6 „Numerele scrise de om” (655) și „Nimic precompletat care induce în eroare” (504), cap.9 (509). Fiecare cod prinde
# TIPARUL în toate fișierele frontendului (static/js/ecrane + static/js); locurile din fișierele altor zone se raportează, nu se scutesc.
# Mecanismele comune (api.js / navigator.js / stil.css / core/numere.py) sunt verificate că există — fără ele, regula n-are cum fi
# respectată. Mutațiile care le probează: `core/test_lot13_ds_verificator.py` (fragmente rele / bune + fișierele reale).
_L13_SUMA = r"sum[aăe]\b|sumă|valoare|total|baz[aă]\b|pre[tț]\b|sold\b|salariu|brut|avans|diurn|impozit|\blei\b"
_L13_NU_SUMA = r"caut|cont\b|cont |cod|serie|nume|denumire|cui|iban|email|telefon|adres|motiv|document|descriere"


def _l13_sablon_la(t, start):
    """Capătul șablonului care începe la `start` (după backtick), cu `${…}` imbricate sărite."""
    i, d = start, 0
    while i < len(t):
        if t.startswith("${", i):
            d += 1
            i += 2
            continue
        if t[i] == "}" and d > 0:
            d -= 1
        elif t[i] == "`" and d == 0:
            return i
        i += 1
    return len(t)


def _l13_fara_expresii(t):
    """Textul unui șablon fără expresiile `${…}` (cu imbricările lor) — ce e scris literal."""
    out, i, d = [], 0, 0
    while i < len(t):
        if t.startswith("${", i):
            d += 1
            i += 2
            continue
        if d and t[i] == "{":
            d += 1
        elif d and t[i] == "}":
            d -= 1
        elif not d:
            out.append(t[i])
        i += 1
    return "".join(out)


def _l13_expresii(t):
    """[(început, sfârșit, text)] — expresiile `${…}` de pe primul nivel al unui șablon."""
    out, i, d, st = [], 0, 0, None
    while i < len(t):
        if t.startswith("${", i):
            if d == 0:
                st = i + 2
            d += 1
            i += 2
            continue
        if d and t[i] == "{":
            d += 1
        elif d and t[i] == "}":
            d -= 1
            if d == 0:
                out.append((st - 2, i + 1, t[st:i]))
        i += 1
    return out


def _l13_nr_elemente(corp):
    """Câte elemente are o listă JS scrisă literal (conținutul dintre `[` și `]`): virgulele de pe nivelul ei + 1."""
    adanc, n, sir, gol = 0, 0, None, True
    for ch in corp:
        if sir:
            if ch == sir:
                sir = None
            continue
        if ch in "\"'`":
            sir, gol = ch, False
        elif ch in "[({":
            adanc, gol = adanc + 1, False
        elif ch in "])}":
            adanc -= 1
        elif ch == "," and adanc == 0:
            n += 1
        elif not ch.isspace():
            gol = False
    rest = corp.rstrip()
    return 0 if gol else n + (0 if rest.endswith(",") else 1)


def analiza_lot13(fisiere, css="", numere_py=""):
    """[(fișier, linie, COD, text)] — codurile: SUMA_CITITA_BRUT, SUMA_TEXT (655), FEREASTRA_INLINE (673), ACTIUNE_FARA_BUTON (674),
    BUTON_ASCUNS (675), LISTA_SCURTA (676), PRECOMPLETARE (504), GRILA_INLINE (509), CAUTARE_FEREASTRA (681)."""
    import re as _re
    out = []
    api, nav = fisiere.get("api.js", ""), fisiere.get("navigator.js", "")
    ln = lambda t, p: t.count("\n", 0, p) + 1   # noqa: E731
    # ── mecanismele comune
    for cod, ok, ce in (
        ("SUMA_CITITA_BRUT", "export function numarRo(" in api and "export function campNumericRo(" in api and "_campuriNumericeIn(n)" in api
         and "if (gresit) throw gresit;" in api, "api.js: regula `numarRo` / câmpul numeric românesc / oprirea scrierii (655)"),
        ("SUMA_CITITA_BRUT", (not numere_py) or "def numar_ro(" in numere_py, "core/numere.py: oglinda Python `numar_ro` (655)"),
        ("LISTA_SCURTA", "export function alegereButoane(" in api and 'select[data-butoane]' in api and "data-butoane" in
         _re.search(r"export function selectDaNu\([^\n]*\n(?:.*\n){0,8}", api).group(0) if "export function selectDaNu(" in api else False,
         "api.js: butoanele alăturate ale listei scurte (`alegereButoane`, `selectDaNu` cu `data-butoane`) (676)"),
        ("BUTON_ASCUNS", "export function inactiv(" in api and "export function atributeInactiv(" in api and '[aria-disabled="true"]' in api,
         "api.js: butonul inactiv cu motiv (`inactiv` / `atributeInactiv` + oprirea clicului) (675)"),
        ("FEREASTRA_INLINE", '"fer-lucru"' in nav, "navigator.js: fereastra deschisă peste alta e fereastră de lucru (`fer-lucru`) (673)"),
        ("CAUTARE_FEREASTRA", 'puneCautarea(fer.querySelector(".fereastra-antet")' in nav and '"cautare-fereastra"' in nav,
         "navigator.js: căsuța de căutare a funcțiilor în bara de sus a fiecărei ferestre de lucru (681, precizarea 26.10)"),
    ):
        if not ok:
            out.append(("api.js" if "api.js" in ce else ("navigator.js" if "navigator" in ce else "numere.py"), 0, cod, "mecanismul lipsește — " + ce))
    if css:
        if not _re.search(r"\.fereastra\.fer-lucru\s*\{[^}]*height:\s*calc\(100vh - 48px\)", css):
            out.append(("stil.css", 0, "FEREASTRA_INLINE", "lipsește `.fereastra.fer-lucru` cât ecranul (DS cap.2a, 673 / 509)"))
        if not _re.search(r"\.alegere-butoane\s*\{", css) or not _re.search(r"select\.alegere-sursa\s*\{", css):
            out.append(("stil.css", 0, "LISTA_SCURTA", "lipsesc `.alegere-butoane` / `select.alegere-sursa` (DS cap.2a, 676)"))
        if not _re.search(r'\.buton-secundar\[aria-disabled="true"\]', css):
            out.append(("stil.css", 0, "BUTON_ASCUNS", "butonul inactiv cu motiv (`[aria-disabled=\"true\"]`) nu arată inactiv (DS cap.1, 675)"))
    for nume, t in sorted(fisiere.items()):
        linii = t.split("\n")
        for i, lin in enumerate(linii, 1):
            s = lin.strip()
            if s.startswith(("//", "/*", "*")):
                continue
            # 655 — parsator local al textului numeric (punctul de mii devine zecimală: „1.500” -> 1,5)
            if nume != "api.js" and _re.search(r"\.replace\(\s*(?:\"\,\"|',')\s*,\s*(?:\"\.\"|'\.')\s*\)|\.replace\(/,/g?\s*,\s*(?:\"\.\"|'\.')\)", lin) \
                    and (_re.search(r"\b(parseFloat|Number|parseInt)\s*\(", lin) or _re.search(r"\b\w+\s*:\s*[^,;]*\.replace\(", lin)):
                out.append((nume, i, "SUMA_CITITA_BRUT", "text numeric citit cu un parsator local — `numarRo` (api.js) sau câmpul numeric (DS cap.6, 655): " + s[:80]))
            # 509 — grilă de câmpuri scrisă inline (câmpuri împrăștiate, etichete pe rânduri diferite): `.grila-campuri` / `.grila-doc`
            if _re.search(r"style=\"[^\"]*display:\s*grid", lin) and _re.search(r"<input|<select|<textarea|class=\"camp\"",
                                                                                   "\n".join(linii[i - 1:i + 8])):
                out.append((nume, i, "GRILA_INLINE", "grilă de câmpuri inline — `.grila-campuri` / `.grila-doc` (DS cap.9, 509): " + s[:80]))
        # 655 — câmp de sumă de tip text, fără tastatura numerică (nu trece prin mecanism)
        for m in _re.finditer(r"<input\b[^>]*>", t):
            tag = m.group(0)
            ty = _re.search(r'\btype="([\w-]+)"', tag)
            if (ty and ty.group(1) != "text") or _re.search(r"\breadonly\b|\bdisabled\b|inputmode=\"(decimal|numeric)\"", tag):
                continue
            eticheta = " ".join(_re.findall(r'(?:\bid|aria-label|placeholder|title)="([^"]*)"', tag))
            if _re.search(_L13_SUMA, eticheta, _re.I) and not _re.search(_L13_NU_SUMA, eticheta, _re.I):
                out.append((nume, ln(t, m.start()), "SUMA_TEXT", "câmp de sumă de tip text: `type=\"number\"` sau `inputmode=\"decimal\"` (DS cap.6, 655): "
                            + tag[:80]))
            # 504 — valoare scrisă în câmp, gata aleasă (contul 446, țara RO, UM buc)
            v = _re.search(r'\bvalue="([^"\'$]+)"', tag)
            if v and v.group(1).strip():
                out.append((nume, ln(t, m.start()), "PRECOMPLETARE", "câmp precompletat cu „%s” — rămâne gol (DS cap.6, 504): %s" % (v.group(1), tag[:70])))
        for m in _re.finditer(r"<input\b[^>]*>", t):
            tag = m.group(0)
            if _re.search(r'\btype="(hidden|checkbox|radio|button|submit|file|date|month|time|color|range)"', tag):
                continue
            # 504 — valoare implicită ascunsă în șablon (`value="${esc(x || "RO")}"`, `value="${esc(c.sugestie)}"`)
            if _re.search(r'value="(?:\$\{|\'\s*\+)[^"]*(?:\|\|\s*(?:"[^"]+"|\'[^\']+\'|\d+)|sugestie)', tag):
                out.append((nume, ln(t, m.start()), "PRECOMPLETARE", "valoare implicită pusă în câmp — rămâne gol (DS cap.6, 504): " + tag[:80]))
            # 504 — „valoare gri”: indiciul arată ca o valoare (21, 0,00, DE, 446) — se scrie „ex. …” sau nimic
            p = _re.search(r'placeholder="([^"]*)"', tag)
            if p:
                pv = p.group(1).strip()
                eticheta_scurta = pv in ("UM", "CUI", "CNP", "TVA", "NIR", "CAEN", "COR", "IBAN", "BIC")   # numele câmpului, nu o valoare
                if _re.search(r"sugestie", pv) or (not eticheta_scurta and _re.fullmatch(r"[-+]?\d[\d.,]*\s*(%|lei|RON)?|[A-Z]{2,3}|\d{3,}|\d\d\.\d\d\.\d{4}", pv)):
                    out.append((nume, ln(t, m.start()), "PRECOMPLETARE", "indiciul gri arată ca o valoare („%s”) — „ex. …” sau nimic (DS cap.6, 504): %s"
                                % (pv, tag[:60])))
        # 673 — o acțiune din fereastră care scrie un formular într-o zonă a ferestrei (bandă, card), în loc de o fereastră nouă
        # [lotul 13, zona fact] și formularul INSERAT (`zona.insertAdjacentHTML("afterbegin", `…<input …`)`) — chitanța din detaliul facturii
        # stătea așa, nevăzută de detector
        for m in _re.finditer(r"([\w$]+(?:\.querySelector\([^()]*\)|\.getElementById\([^()]*\))?)\.(?:innerHTML\s*=\s*|insertAdjacentHTML\(\s*\x22[a-z]+\x22\s*,\s*)`", t):
            sf = _l13_sablon_la(t, m.end())
            tpl = t[m.end():sf]
            if not _re.search(r"<input\b(?![^>]*\breadonly\b)|<select|<textarea|<form\b", tpl):
                continue   # un rezultat cu un câmp de copiat (numai citire) nu e un formular
            ant = t[max(0, m.start() - 3000):m.start()]
            k = ant.rfind('addEventListener("click"')
            if k < 0 or ant[k:].count("{") - ant[k:].count("}") <= 0:
                continue
            x = m.group(1)
            sub = "querySelector" in x or "getElementById" in x
            if not sub:
                dec = list(_re.finditer(r"(?:const|let|var)\s+%s\s*=\s*([^;\n]+)" % _re.escape(x.split(".")[0]), t[:m.start()]))
                sub = bool(dec) and bool(_re.search(r"querySelector|getElementById", dec[-1].group(1)))
            if sub:
                out.append((nume, ln(t, m.start()), "FEREASTRA_INLINE", "acțiunea deschide un formular în pagină (`%s.innerHTML`) — fereastră nouă, "
                            "`nav.deschide` (DS cap.2a, 673)" % x[:30]))
        # 674 — text pe care se dă clic: `<details>` închis care ascunde date / un formular („▸ Compoziția netului”) și elementele de
        # text făcute clicabile (`cursor:pointer`, `role="button"`, `onclick`); excepția: meniul „Acțiuni” al rândului (cap.9 v2.83)
        for m in _re.finditer(r"<details\b([^>]*)>(.*?)</details>", t, _re.S):
            if _re.search(r"\bopen\b", m.group(1)):
                continue
            sm = _re.search(r"<summary[^>]*>(.*?)</summary>", m.group(2), _re.S)
            st = _re.sub(r"<[^>]+>|\$\{[^}]*\}", "", sm.group(1) if sm else "").strip()
            if st in ("Acțiuni", "Ac\\u021biuni"):
                continue
            if _re.search(r"<table|<input|<select|<textarea|<button", m.group(2)):
                out.append((nume, ln(t, m.start()), "ACTIUNE_FARA_BUTON", "„%s” se deschide cu clic pe text — buton care deschide fereastra (DS cap.2a, 674)"
                            % st[:60]))
        for m in _re.finditer(r"<(div|span|td|tr|li|p|img|h\d|section)\b([^>]*)>", t):
            if _re.search(r"cursor:\s*pointer|role=\"button\"|\bonclick=", m.group(2)):
                out.append((nume, ln(t, m.start()), "ACTIUNE_FARA_BUTON", "<%s> clicabil — acțiunea e un buton (DS cap.2a, 674): %s"
                            % (m.group(1), m.group(2).strip()[:60])))
        # 675 — butonul unei acțiuni care dispare când nu se aplică (în loc să stea inactiv, cu motivul)
        for m in _re.finditer(r"\?\s*(`|')\s*(<button\b(?:[^`'$]|\$\{[^}]*\})*?)\1\s*:\s*(\"\"|''|``)", t):
            b = m.group(2)
            if not _re.search(r'class="[^"]*\b(buton-primar|buton-secundar|buton-sters|buton-verde|btn-link)\b', b):
                continue
            out.append((nume, ln(t, m.start()), "BUTON_ASCUNS", "butonul dispare când nu se aplică — stă inactiv, cu motivul (`atributeInactiv`, "
                        "DS cap.1, 675): " + _re.sub(r"\s+", " ", b)[:70]))
        # 676 — listă derulantă cu cel mult 6 opțiuni (scrise în șablon sau dintr-o listă fixă a fișierului)
        for m in _re.finditer(r"<select\b([^>]*)>(.*?)</select>", t, _re.S):
            atr, corp = m.group(1), m.group(2)
            if _re.search(r"\bdata-butoane\b|\bmultiple\b|data-lista=", atr):
                continue
            # opțiunile scrise în șablon (nu cele dintr-un `${….map(…)}`); „— alege —” nu e o opțiune
            static = _l13_fara_expresii(corp)
            reale = [tx for atr_o, tx in _re.findall(r"<option\b([^>]*)>([^<]*)", static)
                     if "data-alege" not in atr_o and not _re.search(r"alege|se încarcă|se incarca", tx, _re.I)]
            # o listă ÎNCHISĂ primită de un desenator comun (registrul Operațiunilor `c.optiuni`, e-Transport `optiuni`): butoanele le pune
            # mecanismul, cât lista are cel mult 6 opțiuni — desenatorul pune `data-butoane` o dată, pentru toate
            if _re.search(r"\boptiuni\.map\(", corp):
                out.append((nume, ln(t, m.start()), "LISTA_SCURTA", "listă închisă (`optiuni`) desenată fără `data-butoane` — butoanele alăturate le pune "
                            "mecanismul până la 6 opțiuni (DS cap.2a, 676)"))
                continue
            n = len(reale)
            for mm in _re.finditer(r"(?:\$\{|'\s*\+)\s*([A-Z_][A-Z0-9_]*)\.map\(", corp):
                defs = [d for d in _re.finditer(r"(?:const|let)\s+%s\s*=\s*\[(.*?)\];" % _re.escape(mm.group(1)), t, _re.S)
                        if d.start() < m.start()]   # definiția cea mai apropiată de dinaintea listei (același nume, în alt ecran)
                dm = defs[-1] if defs else None
                if not dm:
                    n = 99
                    break
                n += _l13_nr_elemente(dm.group(1))
            # opțiunile vin din date (firme, conturi, salariați, o variabilă a ecranului): lista lungă rămâne listă. Se judecă expresiile
            # de pe primul nivel al corpului listei: „— alege —”, o listă fixă a fișierului (`NUME.map`), o expresie în tagul sau în
            # eticheta unei opțiuni scrise literal nu fac lista dinamică; orice altă expresie, da
            dinamica = False
            for a0, b0, ex in _l13_expresii(corp):
                if _re.match(r"\s*(ALEGE|alegeDacaLipseste\(|[A-Z_][A-Z0-9_]*\.map\()", ex):
                    continue
                inainte = corp[:a0]
                if inainte.rfind("<option") > inainte.rfind(">") or _re.search(r"<option\b[^>]*>\s*$", inainte):
                    continue
                dinamica = True
                break
            if dinamica or _re.search(r"'\s*\+\s*(?![A-Z_][A-Z0-9_]*\.map|ALEGE)\w", corp):
                continue
            if 0 < n <= 6:
                out.append((nume, ln(t, m.start()), "LISTA_SCURTA", "listă cu %d opțiuni — butoane alăturate: `data-butoane` (DS cap.2a, 676)" % n))
    return out


rap["lot13"] = analiza_lot13(fisiere, open(os.path.join(BAZA_PY, "static", "stil.css"), encoding="utf-8").read(),
                             open(os.path.join(BAZA_PY, "core", "numere.py"), encoding="utf-8").read())

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
