# -*- coding: utf-8 -*-
"""scripts/scan_selecturi_ecrane.py — FAPT_FISCAL_NECERUT în ecranele SCRISE DE MÂNĂ (în afara registrului Operațiunilor).

Comanda Costin 07.10.2026: „Extinde regula la ecranele scrise de mână, cu clasificarea celor 82”, CORECTATĂ în lotul 07.10 B (A.1):
  · preselecția e PERMISĂ când valoarea (a) e cazul uzual sau se deduce din date (țara din CUI, regimul din profil, moneda RON),
    (b) se vede pe ecran înainte de confirmare și (c) se poate schimba — clasa `PRESELECTAT`, cu criteriul scris în motiv;
  · e INTERZISĂ pentru un fapt situațional pe care aplicația nu-l poate ști (Da/Nu situaționale, categoria sau temeiul dintr-o
    declarație, tipul imobilului, valabilitatea, opțiuni de regim alese de contribuabil): acolo „— alege —” (`ALEGE` /
    `alegeDacaLipseste` / `selectDaNu` din `static/js/api.js`) și handlerul care trimite îl cere (`cereAlegerile`) — clasa `FISCAL`.
Un DA/NU situațional nu e căsuță de bifat (nebifată = „Nu” ales de ecran): e `selectDaNu`; fiecare căsuță din ecrane e în
`CASUTE`, cu motivul. Input-urile cu valoare pusă de ecran sunt în `INPUTURI`, cu motivul. O singură implementare, două porți:
`core/test_selecturi_ecrane.py` și regula `FAPT_FISCAL_NECERUT` din `verificator_conformitate.py`.

Ce măsoară: fiecare `<select` din `static/js` (fără vendor și fără `operatiuni_ecran.js`, care are motorul și garda lui), identificat
prin `fișier:locator` (id-ul, altfel prima clasă proprie, altfel atributul `data-*`). Un select e conform dacă markup-ul lui are o
opțiune goală (literal, `ALEGE`, `alegeDacaLipseste`, sau un builder cu `value=""`) ȘI — când e fapt fiscal reparat — handlerul îl cere;
altfel trebuie să fie în `CLASIFICARE`, cu clasa și motivul. LIMITE, declarate: identificarea e lexicală (un select construit
altfel decât prin `<select` nu se vede); „cerut de handler” = locatorul apare într-un apel `cereAlegerile(...)` din același fișier.
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FISCAL = "FISCAL_REPARAT"
NEFISCAL = "NEFISCAL"
EXISTENTA = "VALOARE_EXISTENTA"
BUILDER = "ARE_GOL_IN_BUILDER"
PRESELECTAT = "PRESELECTAT_PERMIS"     # DS cap.17 corectat: (a) uzual/dedus, (b) vizibil, (c) schimbabil — criteriul în motiv
LA_FOLOSIRE = "CERUT_LA_PRIMA_FOLOSIRE"  # „— alege —” când e neales; salvarea îl lasă nul, refuzul vine la prima folosire relevantă

_D = "conținutul declarației către ANAF"
#: Clasificarea celor 82 (măsurate pe 11f8c2ed: select fără opțiune goală în markup) — `fișier:locator` -> (clasa, motivul).
CLASIFICARE = {
    "asistenti.js:data-per": (NEFISCAL, "filtrul de perioadă al jurnalului de activitate al asistentului — afișare, nicio scriere"),
    "date_firma.js:df-activitate_exceptata_amef": (LA_FOLOSIRE, "exceptarea AMEF (OUG 28/1999 art.2) — coloana fără implicit (core/migrare_fapte_date_firma.py); neleasă se cere la prima chitanță fără factură și la D394 cu chitanțe fără cotă (`activitati_amef.refuz_nedeclarata`)"),
    "date_firma.js:vf-${c.k}": (EXISTENTA, "builderul vectorului fiscal pune „— alege —” pe regim / plătitor TVA / operațiuni IC (obligatorii) și pe inreg_art317 (`neales`, fără implicit în schemă — cerut la D301), iar periodicitatea are opțiunea goală"),
    "date_firma.js:df-cont_venit": (EXISTENTA, "arată preferința STOCATĂ; „cont_venit_implicit 707 rămâne” (decizia Costin, lotul 07.10 B A.3) — contul e o sugestie vizibilă și schimbabilă, ca la Operațiuni"),
    "declaratii.js:dec-tip": (NEFISCAL, "navigare: ce declarație se pregătește; alegerea se vede și se confirmă cu «Continuă», nu se trimite tacit"),
    "declaratii.js:dec-trim": (NEFISCAL, "navigare: trimestrul de lucru (cel din antet), confirmat cu «Continuă»"),
    "declaratii.js:dec-luna": (NEFISCAL, "navigare: luna de lucru (cea din antet), confirmată cu «Continuă»"),
    "declaratii.js:dec-recl": (EXISTENTA, "arată clasificarea CURENTĂ a operațiunii D390 (calculată din date); schimbarea se salvează pe loc, nu e un implicit"),
    "declaratii.js:man-tip": (FISCAL, "tipul rândului manual D390 (A/P/S/T/R) — " + _D),
    "declaratii.js:d301-tip": (FISCAL, "tipul operațiunii D301 — " + _D),
    "declaratii.js:d301-valuta": (FISCAL, "valuta operațiunii D301 (venea „EUR”) — " + _D),
    "declaratii.js:d301-cota": (FISCAL, "cota TVA a operațiunii D301 — baza și TVA declarate"),
    "declaratii.js:d710-cod": (FISCAL, "codul obligației rectificate D710 — " + _D),
    "declaratii.js:d307-tip": (FISCAL, "tipul operațiunii D307 — " + _D),
    "declaratii.js:d177-tip": (FISCAL, "tipul beneficiarului D177 — " + _D),
    "declaratii.js:d200-categ": (FISCAL, "categoria de venit D200 — impozitul declarat"),
    "declaratii.js:d230-valab": (FISCAL, "valabilitatea redirecționării D230 (venea „Un an”) — " + _D),
    "declaratii.js:d223-categ": (FISCAL, "categoria de venit D223 — " + _D),
    "declaratii.js:d223-forma": (FISCAL, "forma de organizare D223 — " + _D),
    "declaratii.js:d223-det": (FISCAL, "determinarea venitului D223 (real / normă) — baza impozitului"),
    "declaratii.js:d208-tip": (FISCAL, "tipul imobilului D208 (venea „Teren”) — " + _D),
    "declaratii.js:d208-bci": (FISCAL, "cota de impozit D208 (venea „3”) — impozitul declarat"),
    "declaratii.js:d221-forma": (FISCAL, "forma de organizare D221 (venea „1 — individual”) — " + _D),
    "declaratii.js:d221-opt": (FISCAL, "opțiunea normă / sistem real D221 (venea „0”) — baza impozitului"),
    "declaratii.js:d603-exc": (FISCAL, "categoria de exceptare CASS D603 (venea „2”) — contribuția declarată"),
    "declaratii.js:d110-temei": (FISCAL, "regularizare / cerere de restituire D110 (venea „Regularizare”) — " + _D),
    "declaratii.js:d110-cod": (FISCAL, "codul obligației D110 — " + _D),
    "declaratii.js:d398-moes": (FISCAL, "regimul special D398 — " + _D),
    "declaratii.js:d398-sup": (FISCAL, "bunuri / servicii D398 — " + _D),
    "declaratii.js:d398-trade": (FISCAL, "felul comerțului D398 — " + _D),
    "declaratii.js:d398-vrt": (FISCAL, "tipul cotei (standard / redusă) D398 — TVA declarat pentru statul de consum"),
    "declaratii.js:d318-tara": (FISCAL, "statul de rambursare D318 — " + _D),
    "declaratii.js:d318-drec": (PRESELECTAT, "(a) uzual: cererea inițială — aceeași regulă ca bifa „Rectificativă” nebifată de la celelalte 17 declarații; (b) vizibil în formular; (c) se schimbă pe „rectificativă”, care cere numărul de referință"),
    "declaratii.js:d204-forma": (FISCAL, "forma de organizare D204 (structura ANAF pct.24: 1 asociere fără personalitate juridică / 2 entitate în regim de transparență fiscală) — pleca „1” fără câmp; " + _D),
    "declaratii.js:d208-mod": (FISCAL, "modalitatea de transfer D208 (structura ANAF v1.0.0 poz.22: 1 vânzare-cumpărare / 2 moștenire / 3 donație / 4 altă) — pleca „1” fără câmp; " + _D),
    "declaratii.js:d318-ownt": (FISCAL, "tipul titularului D318 (venea „A”) — " + _D),
    "declaratii.js:d318-fel": (FISCAL, "achiziție / import D318 — " + _D),
    "declaratii.js:d318-ffztara": (FISCAL, "țara furnizorului D318 (venea țara de rambursare) — " + _D),
    "declaratii.js:d212-exccass": (FISCAL, "excepția de la baza minimă CASS D212 — contribuția declarată („nicio excepție” rămâne o alegere, nu implicit)"),
    "declaratii.js:d212-n-forma": (FISCAL, "forma de organizare (normă) D212 — " + _D),
    "declaratii.js:d212-v-cat": (FISCAL, "categoria venitului D212 — impozitul declarat"),
    "declaratii.js:d212-v-det": (FISCAL, "determinarea venitului net D212 (forfetar / real) — baza impozitului"),
    "declaratii.js:d212-v-forma": (FISCAL, "forma de organizare D212 — " + _D),
    "declaratii.js:d212-s-cat": (FISCAL, "categoria venitului din străinătate D212 — impozitul declarat"),
    "declaratii.js:d212-s-det": (FISCAL, "determinarea venitului net din străinătate D212 — baza impozitului"),
    "declaratii.js:d212-s-tipjoc": (FISCAL, "felul jocului de noroc D212 — impozitul declarat"),
    "declaratii.js:d207-tip": (FISCAL, "tipul venitului nerezidentului D207 — impozitul declarat"),
    "declaratii.js:d207-act": (FISCAL, "actul normativ aplicat (Cod / convenție) D207 — cota declarată"),
    "declaratii.js:d300-rand": (FISCAL, "rândul manual D300 — " + _D),
    "emitere_ecran.js:em-moneda": (PRESELECTAT, "(a) uzual: RON — numit în comandă; (b) vizibil lângă total; (c) se schimbă din listă (nota cursului BNR apare)"),
    "emitere_ecran.js:em-tara": (PRESELECTAT, "(a) DEDUS din CUI-ul partenerului (`taraDinCui`: prefixul statului, CUI numeric -> RO); (b) vizibil la «Clasificare TVA (D300)»; (c) se schimbă din listă"),
    "emitere_ecran.js:em-tipop": (PRESELECTAT, "(a) uzual: operațiunea normală — avansul și regularizarea sunt excepțiile; (b) vizibil; (c) se schimbă din listă"),
    "emitere_ecran.js:em-tip": (PRESELECTAT, "(a) uzual: factura — ecranul e «Emite factură»; (b) vizibil lângă buton; (c) se schimbă pe proformă / aviz"),
    "etransport_ecran.js:${id}": (FISCAL, "helperul `sel` al eTransport (tipul operațiunii, județele de încărcare/descărcare, scopul bunului — venea „101”) — notificarea către ANAF"),
    "facturi_ecran.js:pr-dest": (PRESELECTAT, "(a) uzual: „taxabilă” (deducere integrală) — DS cap.28 pct.2, acum în acord cu cap.17; (b) vizibil pe fiecare linie; (c) se schimbă pe scutită / mixtă"),
    "facturi_ecran.js:fr-moneda": (PRESELECTAT, "(a) uzual: RON — ca la emitere; (b) vizibil; (c) se schimbă din listă"),
    "firme.js:fn-tip": (FISCAL, "tipul firmei SRL / PFA (venea „SRL”) — partida dublă / simplă; DS cap.17 îl numește între faptele decisive"),
    "firme.js:sn-${id}": (FISCAL, "helperul formularului «Salariat nou» (tipul normei; DA/NU-urile declarația pentru copii, funcția de bază, scutirea de contribuția minimă — prin `selectDaNu`) — D112"),
    "firme.js:pj-sel": (EXISTENTA, "pontajul e INFORMATIV (DECIZII 17.07, F135): „prezent” = lipsa unei excepții, prin modelul de date; selectul arată starea reală a zilei"),
    "firme.js:ad-tip": (FISCAL, "tipul contractului pe adeverință (venea „nedeterminată”)"),
    "firme.js:rg-mediu": (NEFISCAL, "mediul REGES (test / producție) — setare tehnică a conexiunii, nu fapt fiscal"),
    "firme.js:cadou-ev": (FISCAL, "evenimentul tichetelor cadou (venea „Paște”) — decide neimpozabilul de 300 lei"),
    "firme.js:ed-norma": (FISCAL, "tipul normei la corectarea salariatului (venea „întreagă” și când lipsea) — D112"),
    "firme.js:susp${i}-tip": (FISCAL, "tipul suspendării (rândul nou venea „CFP”) — D112"),
    "firme.js:tr-art": (BUILDER, "builderul `optArts` începe cu „— alege articolul —”"),
    "firme.js:rc-art": (BUILDER, "builderul `optArts` începe cu „— alege articolul —”"),
    "firme.js:fc-luna": (NEFISCAL, "filtrul fișei contului (luna / tot anul) — afișare"),
    "firme.js:fc-cont": (BUILDER, "builderul `optCont` începe cu „— alege contul —”"),
    "firme.js:jm-tip": (NEFISCAL, "ce jurnal de marjă (second-hand / turism) se afișează — vedere, nicio scriere"),
    "firme.js:rf-var": (NEFISCAL, "ce variantă a registrului de evidență fiscală se afișează — vedere"),
    "firme.js:rf-categorie": (FISCAL, "categoria venitului în registrul de evidență fiscală (PF) — impozitul"),
    "firme.js:rf-mod_venit_net": (FISCAL, "modul de stabilire a venitului net (PF) — baza impozitului"),
    "firme.js:ri-moment": (NEFISCAL, "momentul registrului-inventar afișat — vedere"),
    "firme.js:r3-fel": (NEFISCAL, "care registru art.321 se afișează — vedere"),
    "firme.js:bl-tip": (FISCAL, "S1005 / S1003 (venea „S1005”) — situațiile financiare depuse"),
    "firme.js:c-cat": (FISCAL, "categoria dispoziției de casă — nota contabilă"),
    "firme.js:je-centru": (BUILDER, "builderul `optCentru` începe cu „— centru —” (centrul de cost e opțional)"),
    "firme.js:rg-dir": (NEFISCAL, "registratura documentelor: direcția intrare / ieșire — fără efect contabil sau fiscal"),
    "flux_concediu.js:cm-cod": (FISCAL, "codul indemnizației de concediu medical — indemnizația și D112"),
    "pachete.js:pac-luna": (NEFISCAL, "navigare: luna pachetului lunar afișat — vedere, nicio scriere"),
    "rip_ecran.js:r-tip": (FISCAL, "încasare / plată în registrul de încasări și plăți — venitul / cheltuiala"),
    "rip_ecran.js:r-cat": (FISCAL, "categoria operațiunii RIP — deductibilitatea"),
    "rip_ecran.js:r-met": (FISCAL, "numerar / bancă în registrul de încasări și plăți — contul de trezorerie"),
    "api.js:?": (BUILDER, "`selectDaNu` (lotul 07.10 B): „— alege —” când nu există valoare salvată; locurile care îl folosesc sunt cerute prin `danu_necerute`"),
}

#: selecturile construite prin HELPERE (un singur `<select` în helper, mai multe câmpuri): locatorii ceruți la trimitere
HELPERE = {
    "etransport_ecran.js:${id}": ["et-tip", "s-judet", "f-judet", "b-cod_scop"],
    "firme.js:sn-${id}": ["sn-tip_norma", "sn-declaratie_copii", "sn-functie_baza", "sn-scutit_contrib_minim"],
}


#: selecturi cu markup GOL, umplute la rulare: cheie -> expresia care trebuie să existe în fișier (umplerea începe cu „— alege —”)
DINAMICE = {
    "rip_ecran.js:r-cat": r"selCat\.innerHTML = ALEGE \+",
}


#: [07.10.2026] Al treilea loc al aceluiași implicit: STAREA INIȚIALĂ a formularelor-panou din `declaratii.js` (obiectul `S`). Un
#: select cu `alegeDacaLipseste(d.x)` arată „— alege —” numai dacă `x` pornește nul — altfel ecranul „răspunde” din stare (probat:
#: D230 venea „Un an”, D208 „Teren”, D110 „Regularizare”, D318 „DE”/„A”, deși markup-ul avea „— alege —”).
STARE_INITIALA = {
    "d230": ["valabilitate_distribuire"], "d223": ["categ_venit", "forma_org", "det_venit"], "d208": ["tip_imobil", "mod_transfer"],
    "d221": ["forma_org", "optiune"], "d603": ["exceptare"], "d110": ["d_temei"], "d398": ["moes_voes_imp", "e_int"],
    "d318": ["refunding_country", "owner_type", "currency"], "d204": ["categ_venit", "forma_org"], "d212": ["din_rip"],
}


def stare_initiala_incalcata(js):
    """[(declarație, cheie)] pentru faptele care NU pornesc nule în starea inițială `S` a ecranului Declarații."""
    out = []
    for d, chei in STARE_INITIALA.items():
        m = re.search(r"\n    %s: \{" % d, js)
        if not m:
            out.append((d, "<obiectul de stare lipsește>"))
            continue
        bloc = js[m.end():]
        urm = re.search(r"\n    (?://|d\d+[a-z]?: \{|\})", bloc)
        bloc = bloc[:urm.start() if urm else 2000]
        for k in chei:
            v = re.search(r"\b%s: ([^,}\n]+)" % k, bloc)
            if not v or v.group(1).strip() not in ("null", '""'):   # nul sau text gol (D318 moneda)
                out.append((d, k))
    return out


def _citeste(p):
    return io.open(os.path.join(RAD, p), encoding="utf-8").read()


def _fisiere():
    out = []
    for d, _s, fs in os.walk(os.path.join(RAD, "static/js")):
        if "vendor" in d.split(os.sep):
            continue
        for f in sorted(fs):
            if f.endswith(".js") and f != "operatiuni_ecran.js":
                out.append(os.path.relpath(os.path.join(d, f), RAD))
    return sorted(out)


def _locator(seg):
    m = re.search(r'\bid="([^"]+)"', seg)
    if m:
        return m.group(1)
    m = re.search(r'class="camp-input ([a-z][a-z0-9-]*)', seg)
    if m:
        return m.group(1)
    m = re.search(r'\bdata-([a-z-]+)\b(?!=)', seg)
    return "data-" + m.group(1) if m else "?"


def _norm(x):
    return re.sub(r"\$\{[^}]*\}", "", x).lstrip("#")


def selecturi(fisiere=None):
    """[(cheie fișier:locator, fișier, linie, segment)] pentru fiecare `<select` din ecranele scrise de mână."""
    out = []
    for p in (fisiere or _fisiere()):
        s = _citeste(p) if isinstance(p, str) else p[1]
        nume = p if isinstance(p, str) else p[0]
        for m in re.finditer(r"<select\b", s):
            seg = s[m.start():m.start() + 700]
            e = seg.find("</select>")
            seg = seg[:e if e > 0 else 700]
            out.append(("%s:%s" % (os.path.basename(nume), _locator(seg)), nume, s[:m.start()].count("\n") + 1, seg, s))
    return out


def are_gol(seg, s):
    """Markup-ul are o opțiune goală? — literal, `ALEGE`, `alegeDacaLipseste(`, sau un builder (`${x}` / `' + x`) definit cu value=""."""
    if re.search(r'value=["\']{2}|value=\\"\\"|\bALEGE\b|alegeDacaLipseste\(', seg):
        return True
    for v in set(re.findall(r"\$\{(\w+)[}(]", seg)) | set(re.findall(r"' \+ (\w+) \+", seg)):
        d = re.search(r"(?:const|let)\s+%s\s*=\s*([^\n]*)" % re.escape(v), s)
        if d and re.search(r'value=["\']{2}|value=\\"\\"|\bALEGE\b', d.group(1)):
            return True
    return False


def cerute(s):
    """Locatorii (normalizați) ceruți de `cereAlegerile(...)` într-un fișier."""
    out = set()
    for m in re.finditer(r"cereAlegerile\([^,]+,\s*(.+?)\)\)", s):
        out |= {_norm(x) for x in re.findall(r'["`]#?([^"`]+)["`]', m.group(1))}
    return out


def danu_necerute(fisiere=None):
    """[(cheie, ce)] — un `selectDaNu(...)` (DA/NU situațional) pe care handlerul fișierului nu-l cere prin `cereAlegerile`."""
    out = []
    for p in (fisiere or _fisiere()):
        s = _citeste(p) if isinstance(p, str) else p[1]
        nume = os.path.basename(p if isinstance(p, str) else p[0])
        for m in re.finditer(r"selectDaNu\(\s*[`'\"]id=\\?\"([^\"\\]+)\\?\"", s):
            cheie = "%s:%s" % (nume, m.group(1))
            ceruti = HELPERE.get(cheie) or [_norm(m.group(1))]
            lips = [c for c in ceruti if _norm(c) not in cerute(s)]
            if lips:
                out.append((cheie, "DA/NU situațional pe care handlerul nu-l cere (`cereAlegerile`): %s" % lips))
    return out


#: [lotul 07.10 B] CĂSUȚELE de bifat din ecrane — o căsuță nebifată răspunde „Nu”. Fiecare e aici, cu motivul; un DA/NU
#: situațional (fapt pe care aplicația nu-l poate ști) NU e căsuță, e `selectDaNu` (13 convertite: funcția de bază, declarația
#: pentru copii, scutirea de contribuția minimă, CM continuare / spitalizare / program național, TVA la încasare la furnizor,
#: acordul D177, e_int D398, RIP / cota forfetară / CAS-CASS străinătate D212).
_REC = "tipul declarației: „Rectificativă” nebifată = declarația inițială, cazul uzual (DS cap.17 corectat, (a)-(c)); se vede și se bifează"
CASUTE = {
    **{"declaratii.js:d%s-rec" % d: _REC for d in ("311", "307", "107", "177", "200", "201", "204", "223", "216", "208", "221", "104",
                                                    "114", "110", "212", "207")},
    "declaratii.js:d307-anul": "tipul declarației D307: „corectată după anularea rezervei verificării” e excepția, ca rectificativa; bifată cere temeiul",
    "declaratii.js:d318-annual": "(a) uzual: cererea anuală (1 ian – 31 dec), coerentă cu lunile 1–12; (b) vizibilă; (c) debifată cere lunile",
    "declaratii.js:d600-cas": "D600 se depune NUMAI pentru opțiunea CAS: nebifată, generarea se refuză („Bifează cel puțin CAS”) — nu pleacă niciun „Nu”",
    "facturi_ecran.js:sc-optin": "opțiunea de notificări a scadențarului — setare a aplicației, nu fapt fiscal",
    "setari.js:cmp-preg": "drepturi de utilizator în cabinet — setare de acces, nu fapt fiscal",
    "setari.js:cmp-val": "idem",
    "setari.js:cmp-dep": "idem",
    "asistenti.js:asi-pregati": "drepturi ale asistentului — setare de acces",
    "asistenti.js:asi-valida": "idem",
    "asistenti.js:data-tid": "firmele alocate asistentului — setare de acces",
    "asistenti.js:data-perm": "drepturi pe firmă ale asistentului — setare de acces",
    "login.js:reg-termeni": "acceptarea termenilor — consimțământ; nebifată, înregistrarea se refuză",
    "migrare.js:data-i": "ce rânduri găsite se importă — selecție de lucru, fiecare rând e vizibil",
    "admin.js:sel-bifa": "selecție în administrare — nu fapt fiscal",
    "firme.js:data-fid": "ce facturi se alocă plății — selecție de lucru vizibilă, suma alocată se vede",
    "validat.js:val-sel": "ce note se validează deodată (retest 08.10 pct.3) — selecție de lucru vizibilă; fiecare notă trece prin aceeași validare",
    "validat.js:val-sel-toate": "selectează toate notele din listă — selecție de lucru, nu fapt fiscal",
}


def _locator_casuta(seg):
    m = re.search(r'\bid="([^"]+)"', seg)
    if m:
        return m.group(1)
    m = re.search(r'class="([a-z][a-z0-9-]*)"', seg)
    if m:
        return m.group(1)
    m = re.search(r'\bdata-([a-z]+)=', seg)
    return "data-" + m.group(1) if m else "?"


def casute(fisiere=None):
    """[(cheie fișier:locator, linie)] pentru fiecare căsuță de bifat din ecranele scrise de mână."""
    out = []
    for p in (fisiere or _fisiere() + ["static/js/ecrane/operatiuni_ecran.js"]):
        s = _citeste(p) if isinstance(p, str) else p[1]
        nume = os.path.basename(p if isinstance(p, str) else p[0])
        for m in re.finditer(r'<input\b[^>]*type="checkbox"[^>]*>', s):
            out.append(("%s:%s" % (nume, _locator_casuta(m.group(0))), s[:m.start()].count("\n") + 1))
    return out


#: [lotul 07.10 B] INPUT-URI cu valoare pusă de ecran (literal sau `|| "x"` în `value=`) — fiecare cu motivul, după regula corectată.
INPUTURI = {
    "declaratii.js:d603-tara": "(a) uzual: contribuabilul D603 rezident în România („RO”); (b) vizibil; (c) se scrie alt cod de țară",
    "declaratii.js:d318-li": "(a) uzual: cererea pe an întreg — luna 1; apare numai când cererea NU e anuală, deci e vizibilă și se schimbă",
    "declaratii.js:d318-ls": "idem — luna 12",
    "produse_ecran.js:pr-um": "(a) uzual: unitatea „buc”; (b) vizibilă; (c) se schimbă — unitatea nu schimbă nota, baza sau impozitul",
    "firme.js:sn-cont-transport": "cont contabil sugerat (401) la NIR, vizibil și modificabil — aceeași regulă ca la conturile din Operațiuni",
    "firme.js:sn-cont-taxe": "cont contabil sugerat (446) la NIR, vizibil și modificabil — idem",
    "declaratii.js:d398-cur": "VALOARE FIXĂ, nu alegere: CF art.314 alin.(10) / art.315 alin.(12) / art.315^2 alin.(22) — „Declarația specială de TVA se întocmește în euro” (readonly)",
}


def inputuri_precompletate(fisiere=None):
    """[(cheie, linie)] — `<input` cu valoare pusă de ecran: literal (`value="x"`) sau fallback (`|| "x"` / `|| n`) în `value=`."""
    out = []
    for p in (fisiere or _fisiere()):
        s = _citeste(p) if isinstance(p, str) else p[1]
        nume = os.path.basename(p if isinstance(p, str) else p[0])
        for m in re.finditer(r"<input\b[^>]*>", s):
            seg = m.group(0)
            if re.search(r'type="(?:checkbox|radio|hidden|button|submit|file)"', seg):
                continue
            v = re.search(r'value="([^"]*)"', seg)
            lit = v and v.group(1) and "${" not in v.group(1) and not v.group(1).startswith("'")
            fb = re.search(r'value="[^>]*\|\| ?(?:"[^"]+"|[1-9][0-9]*)\)', seg)
            if lit or fb:
                out.append(("%s:%s" % (nume, _locator_casuta(seg)), s[:m.start()].count("\n") + 1))
    # `inp(id, eticheta, valoare || "x", …)` — helperul de input din declaratii.js
    s = _citeste("static/js/ecrane/declaratii.js")
    for m in re.finditer(r'inp\("([a-z0-9-]+)", [^\n]*?, [^,\n]*\|\| ?(?:"[^"]+"|[1-9][0-9]*), ', s):
        out.append(("declaratii.js:%s" % m.group(1), s[:m.start()].count("\n") + 1))
    return out


def masoara(fisiere=None):
    """Încălcările: [(cheie, ce)]. Goală = conform."""
    out, vazute = [], set()
    for cheie, nume, linie, seg, s in selecturi(fisiere):
        vazute.add(cheie)
        cl = CLASIFICARE.get(cheie)
        gol = are_gol(seg, s) or (cheie in DINAMICE and re.search(DINAMICE[cheie], s) is not None)
        if cl is None and not gol:
            out.append((cheie, "select fără „— alege —” și neclasificat (linia %d)" % linie))
        if cl and cl[0] == FISCAL:
            if not gol:
                out.append((cheie, "fapt fiscal fără „— alege —” (linia %d)" % linie))
            ceruti = HELPERE.get(cheie) or [_norm(cheie.split(":", 1)[1])]
            lips = [c for c in ceruti if _norm(c) not in cerute(s)]
            if lips:
                out.append((cheie, "fapt fiscal pe care handlerul nu-l cere (`cereAlegerile`): %s" % lips))
        if cl and cl[0] == BUILDER and not gol:
            out.append((cheie, "builderul nu mai are opțiunea goală (linia %d)" % linie))
        if cl and cl[0] == LA_FOLOSIRE and not gol:
            out.append((cheie, "fapt cerut la prima folosire fără „— alege —” când e neales (linia %d)" % linie))
        if cl and cl[0] == PRESELECTAT and are_gol(seg, s):
            out.append((cheie, "clasificat preselectat permis, dar markup-ul are „— alege —” — clasificarea nu mai corespunde (linia %d)" % linie))
    if fisiere is None:
        for d, k in stare_initiala_incalcata(_citeste("static/js/ecrane/declaratii.js")):
            out.append(("declaratii.js:%s.%s" % (d, k), "fapt fiscal cu valoare în starea inițială (ecranul răspunde în locul omului)"))
        for k in sorted(set(CLASIFICARE) - vazute):
            out.append((k, "clasificat, dar selectul nu mai există — scoate-l din CLASIFICARE"))
        out += danu_necerute()
        vz = set()
        for k, linie in casute():
            vz.add(k)
            if k not in CASUTE:
                out.append((k, "căsuță de bifat neclasificată (linia %d): un DA/NU situațional se cere cu `selectDaNu`, nu cu o căsuță nebifată" % linie))
        out += [(k, "clasificată, dar căsuța nu mai există — scoate-o din CASUTE") for k in sorted(set(CASUTE) - vz)]
        vz = set()
        for k, linie in inputuri_precompletate():
            vz.add(k)
            if k not in INPUTURI:
                out.append((k, "input cu valoare pusă de ecran, neclasificat (linia %d) — fapt situațional: gol și cerut; uzual/dedus: în INPUTURI cu motivul" % linie))
        out += [(k, "clasificat, dar input-ul nu mai e precompletat — scoate-l din INPUTURI") for k in sorted(set(INPUTURI) - vz)]
    return out


if __name__ == "__main__":
    import collections
    print(collections.Counter(c for c, _m in CLASIFICARE.values()))
    for k, ce in masoara():
        print("%-48s %s" % (k, ce))
