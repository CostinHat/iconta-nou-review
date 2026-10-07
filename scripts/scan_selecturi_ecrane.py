# -*- coding: utf-8 -*-
"""scripts/scan_selecturi_ecrane.py — FAPT_FISCAL_NECERUT în ecranele SCRISE DE MÂNĂ (în afara registrului Operațiunilor).

Comanda Costin 07.10.2026: „Extinde regula la ecranele scrise de mână, cu clasificarea celor 82”. Regula (DS cap.17): un select a cărui
valoare e fapt fiscal (schimbă nota, baza, impozitul sau conținutul unei declarații către ANAF) nu vine ales de ecran — pornește cu
„— alege —” (`ALEGE` / `alegeDacaLipseste` din `static/js/api.js`) și handlerul care trimite îl cere (`cereAlegerile`). Un select
ne-fiscal (filtru, navigare, setare tehnică) rămâne, cu motivul. O singură implementare, două porți: `core/test_selecturi_ecrane.py`
și regula `FAPT_FISCAL_NECERUT` din `verificator_conformitate.py`.

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
CONFLICT = "CONFLICT_DS"

_D = "conținutul declarației către ANAF"
#: Clasificarea celor 82 (măsurate pe 11f8c2ed: select fără opțiune goală în markup) — `fișier:locator` -> (clasa, motivul).
CLASIFICARE = {
    "asistenti.js:data-per": (NEFISCAL, "filtrul de perioadă al jurnalului de activitate al asistentului — afișare, nicio scriere"),
    "date_firma.js:df-activitate_exceptata_amef": (EXISTENTA, "arată valoarea STOCATĂ; coloana e NOT NULL DEFAULT false (migrarea D394 Î2) — implicitul e în schemă, nu în ecran (decizie cerută: schema)"),
    "date_firma.js:vf-${c.k}": (EXISTENTA, "builderul vectorului fiscal pune „— alege —” pe regim / plătitor TVA / operațiuni IC când lipsesc, iar periodicitatea are opțiunea goală; inreg_art317 arată valoarea stocată (NOT NULL DEFAULT false — implicit în schemă)"),
    "date_firma.js:df-cont_venit": (EXISTENTA, "arată preferința STOCATĂ; coloana are DEFAULT '707' — implicitul e în schemă (decizie cerută: schema)"),
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
    "declaratii.js:d318-drec": (FISCAL, "cerere inițială / rectificativă D318 (venea „inițială”) — " + _D),
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
    "emitere_ecran.js:em-moneda": (FISCAL, "moneda facturii (venea „RON”) — baza și TVA în lei"),
    "emitere_ecran.js:em-tara": (FISCAL, "țara partenerului (venea „RO”) — regimul de TVA și rândul D300"),
    "emitere_ecran.js:em-tipop": (FISCAL, "operațiune normală / avans / regularizare (venea „normală”) — nota și D300"),
    "emitere_ecran.js:em-tip": (FISCAL, "factură / proformă / aviz (venea „Factura”) — documentul fiscal emis"),
    "etransport_ecran.js:${id}": (FISCAL, "helperul `sel` al eTransport (tipul operațiunii, județele de încărcare/descărcare, scopul bunului — venea „101”) — notificarea către ANAF"),
    "facturi_ecran.js:pr-dest": (CONFLICT, "destinația TVA pe linie: DS cap.28 pct.2 cere „default sigur, explicit … `selected` în markup”, iar DS cap.17 „fără preselecție” — două decizii care se contrazic; rămâne până decide Costin"),
    "facturi_ecran.js:fr-moneda": (FISCAL, "moneda facturii recurente (venea „RON”) — baza și TVA"),
    "firme.js:fn-tip": (FISCAL, "tipul firmei SRL / PFA (venea „SRL”) — partida dublă / simplă; DS cap.17 îl numește între faptele decisive"),
    "firme.js:sn-${id}": (FISCAL, "helperul formularului «Salariat nou» (tipul normei) — D112"),
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
}

#: selecturile construite prin HELPERE (un singur `<select` în helper, mai multe câmpuri): locatorii ceruți la trimitere
HELPERE = {
    "etransport_ecran.js:${id}": ["et-tip", "s-judet", "f-judet", "b-cod_scop"],
    "firme.js:sn-${id}": ["sn-tip_norma"],
}


#: selecturi cu markup GOL, umplute la rulare: cheie -> expresia care trebuie să existe în fișier (umplerea începe cu „— alege —”)
DINAMICE = {
    "rip_ecran.js:r-cat": r"selCat\.innerHTML = ALEGE \+",
}


#: [07.10.2026] Al treilea loc al aceluiași implicit: STAREA INIȚIALĂ a formularelor-panou din `declaratii.js` (obiectul `S`). Un
#: select cu `alegeDacaLipseste(d.x)` arată „— alege —” numai dacă `x` pornește nul — altfel ecranul „răspunde” din stare (probat:
#: D230 venea „Un an”, D208 „Teren”, D110 „Regularizare”, D318 „DE”/„A”, deși markup-ul avea „— alege —”).
STARE_INITIALA = {
    "d230": ["valabilitate_distribuire"], "d223": ["categ_venit", "forma_org", "det_venit"], "d208": ["tip_imobil"],
    "d221": ["forma_org", "optiune"], "d603": ["exceptare"], "d110": ["d_temei"], "d398": ["moes_voes_imp"],
    "d318": ["refunding_country", "d_rec", "owner_type"],
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
            if not v or v.group(1).strip() != "null":
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
    if fisiere is None:
        for d, k in stare_initiala_incalcata(_citeste("static/js/ecrane/declaratii.js")):
            out.append(("declaratii.js:%s.%s" % (d, k), "fapt fiscal cu valoare în starea inițială (ecranul răspunde în locul omului)"))
        for k in sorted(set(CLASIFICARE) - vazute):
            out.append((k, "clasificat, dar selectul nu mai există — scoate-l din CLASIFICARE"))
    return out


if __name__ == "__main__":
    import collections
    print(collections.Counter(c for c, _m in CLASIFICARE.values()))
    for k, ce in masoara():
        print("%-48s %s" % (k, ce))
