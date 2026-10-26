"""
core/facturi_api.py — facturi în schema unui tenant: listă, creare, detalii, ștergere.
Rulează pe conexiunea deja poziționată pe schema tenantului (get_conn(schema)).

total/tva se CALCULEAZĂ pe server din linii (o singură sursă de adevăr — clientul
nu poate trimite sume incoerente cu liniile). Calculul e PUR (testabil fără DB).

Convenție (confirmată din d300._segmente: baza = total - tva):
  total = Σ(cantitate × preț) + Σ(TVA)   -> include TVA
  tva   = Σ(cantitate × preț × cotă/100)
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP

from core.common import (NUMEROTARE_SECVENTIALA, Temei,
                         cote_tva_in_vigoare as _cote_tva_in_vigoare)

REGULI = "2026.1"
MODUL = "facturi_api"


COD_INTREABA_MARFA = "INTREABA_PLEACA_MARFA"
MESAJ_INTREABA_MARFA = "Răspunde la întrebare: pleacă marfa acum? (Da: se descarcă gestiunea; Nu: numai evidența fiscală)"
#: [lotul 12, C84, decizia Costin 12.3 pct.7] întrebarea dovezii transportului la livrarea intracomunitară de bunuri (răspunsul „Nu” emite,
#: cu avertisment — `intracomunitar.AVERTISMENT_LIC_FARA_DOVADA`)
COD_INTREABA_DOVADA = "INTREABA_DOVADA_TRANSPORT"


def poarta_marfa_ceruta(tip, linii, bon_fiscal_nr=None):
    """[304 / C63] Când se întreabă „Pleacă marfa acum?”: la FACTURĂ (nu proformă / aviz) cu o linie pe articol de stoc, care nu e emisă
    din bon fiscal (marfa a ieșit cu bonul, deci nu se mai descarcă). O singură condiție pentru toate drumurile care emit o factură:
    formularul (`uc_tenants.facturi_emite`) și transformarea proformei / avizului (`uc_tenants.proforma_transforma`)."""
    return tip == "factura" and any(l.get("articol_id") for l in linii) and not str(bon_fiscal_nr or "").strip()


class LiniiIncomplete(ValueError):
    """[cap.24/cap.6] Linii de factura fara denumire sau cu cantitate<=0 -> erori PER-LINIE field-keyed
    {camp, eticheta} (id-uri DOM em-l{i}-*, i = pozitia in lista PRIMITA). Backendul e autoritatea de validare
    per-linie; frontendul NU tine oglinda. Ruta o converteste intr-un 422 care poarta lista `campuri`."""
    def __init__(self, campuri):
        self.campuri = campuri
        super().__init__("Linii incomplete: " + "; ".join(x["eticheta"] for x in campuri))


#: Direcțiile posibile ale unei facturi. Erau scrise de două ori — o dată ca refuz în
#: `creeaza_factura` și o dată deloc în `lista_facturi`, care tăcea pe orice altă valoare și
#: întorcea lista goală. O singură sursă: filtrul respinge exact ce respinge și crearea.
DIRECTII = ("emisa", "primita")


def _data_ceruta(camp, valoare):
    """Data unui câmp, ca `date`, sau `ValueError` care spune CARE câmp și CE s-a primit.

    Până azi `data_emitere` mergea neatinsă până în `INSERT`, iar Postgres refuza `2026-02-31`
    cu o eroare de driver — contabilul primea `500 Internal Server Error`, adică nimic. O zi
    care nu există în calendar e o greșeală de tastare, nu o cădere de sistem."""
    import datetime as _d
    if valoare is None or valoare == "":
        return None
    if isinstance(valoare, _d.date):
        return valoare
    try:
        return _d.date.fromisoformat(str(valoare).strip())
    except ValueError:
        raise ValueError("%s: %r nu e o dată din calendar. Se așteaptă forma AAAA-LL-ZZ, cu o zi care "
                         "există în luna aia." % (camp, valoare))


def _cota_necunoscuta(linii, la_data):
    """Prima linie a cărei cotă de TVA nu exista în lege la data facturii, ca `(linie, cota,
    cote_permise, temeiuri)`; `None` dacă toate se recunosc SAU dacă nu se poate ști.

    **Nu confunda „e invalidă" cu „n-am putut verifica"**: dacă registrul de cote nu acoperă
    perioada facturii, `cote_tva_in_vigoare` întoarce `None`, iar aici nu se refuză nimic. Un
    refuz pe necunoaștere ar bloca introducerea unei facturi vechi corecte."""
    if la_data is None:
        return None   # fara data facturii nu se poate sti ce cote erau atunci — deci nu se refuza
    permise, temeiuri = _cote_tva_in_vigoare(la_data)
    if permise is None:
        return None
    for l in linii:
        c = l.get("cota_tva")
        if c is None:
            continue
        try:
            v = Decimal(str(c))
        except Exception:
            v = None
        if v is None or v not in permise:
            return l, c, permise, temeiuri
    return None


def _numar_ro(v):
    """Numarul in forma romaneasca (virgula zecimala), fara zecimale inutile — ca sa nu apara
    „-99999999.0" intr-un mesaj citit de un om."""
    s = ("%.3f" % v).rstrip("0").rstrip(".")
    return s.replace(".", ",")


def linii_campuri_lipsa(linii, prefix="em-l"):
    """Campuri obligatorii per linie -> [{camp, eticheta, mesaj}]. Obligatorii: denumire (nevida) + pret unitar (06.10.2026) +
    cantitate > 0. id camp = {prefix}{i}-{camp}, i = pozitia in lista. prefix parametrizat ca acelasi
    contract sa serveasca emitere (em-l) + facturi-recurente (fr-l) FARA a duplica criteriile (o
    singura sursa de adevar, cap.24 regula 4).

    [R139, 04.09.2026] FIECARE CAMP ISI POARTA MOTIVUL. Pana azi functia intorcea doar `eticheta`
    („Linia 1: cantitate"), iar `api.js` o foloseste ca mesaj cand nu primeste unul
    (`x.mesaj || x.eticheta`, api.js:41). Consecinta, masurata apasand: langa caseta cantitatii,
    care CONTINEA `-99999999`, contabilul citea „Linia 1: cantitate" — numele campului pe care
    tocmai se uita, si nimic despre ce e gresit cu el. Iar rezumatul de deasupra spunea
    „**Completeaza** liniile", desi campul era completat: aplicatia numea alta problema decat cea
    reala. *Un refuz care spune CARE camp, dar nu CE e gresit, indeplineste jumatate din cerinta
    campaniei — si jumatatea care lipseste e chiar cea care il ajuta pe om.*

    Cele doua cauze se DEOSEBESC, fiindca au remedii diferite: un camp gol se completeaza, o
    cantitate negativa se corecteaza. Numele functiei ramane `..._lipsa` — asa o cheama cei doi
    apelanti si cele patru garzi ale ei —, dar ce intoarce nu mai e „ce lipseste", ci „ce nu e bun".
    """
    lipsa = []
    for i, l in enumerate(linii):
        n = i + 1
        d = l.get("descriere")
        if d is None or str(d).strip() == "":
            lipsa.append({"camp": "%s%d-descriere" % (prefix, i),
                          "eticheta": "Linia %d: denumire" % n,
                          "mesaj": "Denumirea liniei e obligatorie pe factură. Scrie ce se facturează."})
        brut = l.get("cantitate")
        try:
            val = float(brut or 0)
        except (TypeError, ValueError):
            val = None
        if val is None:
            m = "Cantitatea nu e un număr. Scrie o cantitate mai mare decât zero."
        elif val == 0:
            m = "Cantitatea lipsește. Scrie o cantitate mai mare decât zero."
        elif val < 0:
            m = ("Cantitatea e negativă (%s). Pe o factură de emis cantitatea trebuie să fie mai mare "
                 "decât zero; pentru o stornare se emite o factură de corecție." % _numar_ro(val))
        else:
            m = None
        if m:
            lipsa.append({"camp": "%s%d-cantitate" % (prefix, i),
                          "eticheta": "Linia %d: cantitate" % n, "mesaj": m})
        # [comanda Costin 06.10.2026 pct.1b] „Un preț pe care nu l-a ales nimeni nu se propune: câmp gol și obligatoriu.”
        # Până azi linia fără preț intra cu 0 (implicitul `LinieEmitereIn.pret_unitar = 0` și `|| 0` din ecran) — o factură
        # cu o valoare pe care n-a scris-o nimeni. 0 SCRIS de om rămâne permis; lipsa (None / gol) se refuză lângă câmp.
        p = l.get("pret_unitar")
        if p is None or str(p).strip() == "":
            lipsa.append({"camp": "%s%d-pret_unitar" % (prefix, i), "eticheta": "Linia %d: preț unitar" % n,
                          "mesaj": "Prețul unitar lipsește. Scrie prețul liniei; nu se presupune niciunul."})
    return lipsa


def _q(x):
    """Rotunjește la 2 zecimale (ca numeric(12,2)), ROUND_HALF_UP."""
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ============================================================
#  CALCUL totaluri — PUR
# ============================================================
def totaluri_din_linii(linii):
    """
    linii: listă de dict cu cantitate, pret_unitar, cota_tva.
    Întoarce {"total": Decimal, "tva": Decimal} (total include TVA).
    """
    # [lotul 11, decizia Costin 10.3: „Rotunjirea TVA: o singură regulă pe toată aplicația, cea cerută de validatorul e-Factura.”] TVA-ul
    # scris pe factură = regula unică (`core/tva_calcul.py`, EN 16931 BR-DEC-23 / BR-S-08 / BR-CO-17 / BR-CO-14): pe COTĂ, din suma valorilor
    # nete ale liniilor (la ban), rotunjit o dată — același ca pe PDF, în XML-ul e-Factura și pe nota contabilă. Înainte: Σ cantitate × preț
    # × cotă nerotunjit pe toată factura, rotunjit la total (pe mai multe cote putea diferi cu un ban de XML).
    from core import tva_calcul as _tc
    t = _tc.totaluri(linii)
    return {"total": _q(t["total"]), "tva": _q(t["tva"])}


def sume_lei(t, curs):
    """(tva_lei, total_lei) ale facturii cu totalurile `t` (`totaluri_din_linii`) la cursul `curs`. O SINGURĂ definiție a conversiei,
    pentru ce se scrie pe factură (`creeaza_factura`), ce întoarce emiterea și ce arată formularul înainte de emitere (lotul 10, pct.7g).
    CF art.319 alin.(20) lit.j): factura cuprinde „suma taxei colectate, exprimate în lei”; rotunjirea fiscală e aritmetică (ROUND_HALF_UP,
    deficiența 280), nu `round()`."""
    c = Decimal(str(curs))
    return _q(Decimal(str(t["tva"])) * c), _q(Decimal(str(t["total"])) * c)


def curs_automat(conn, moneda, data_factura):
    """Cursul BNR cu care se emite AUTOMAT o factură în `moneda` cu data `data_factura`: (curs, data_curs, sursa) — sau refuzul, ca dict
    `{ok: False, cod, mesaj, …}` (nimic scris). O singură definiție pentru emitere (`emite_factura`) și pentru previzualizarea din formular
    (`previzualizare_lei`, lotul 10, pct.7g: „cursul BNR și TVA-ul în lei nu se văd înainte de emitere”): formularul arată exact cursul pe
    care îl va folosi emiterea. Alegerea cursului e a lui `curs_bnr.curs_pentru` (cel mai recent curs comunicat de BNR ÎNAINTEA zilei facturii — HG 1/2016 pct.35 alin.(1) —, în
    pragul de vechime); CF art.290 alin.(2): „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a
    României [...] valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză”."""
    try:
        return curs_bnr.curs_pentru(conn, moneda, data_factura)
    except curs_bnr.CursPreaVechi as _pv:
        # Emiterea AUTOMATĂ se oprește — dar facturarea nu se blochează: refuzul își numește ieșirea, iar cursul găsit merge cu el, ca
        # omul să vadă de la ce pornește.
        return {"ok": False, "cod": "CURS_PREA_VECHI", "moneda": moneda,
                "data": data_factura.isoformat(), "data_curs_gasit": _pv.data_curs.isoformat(),
                "curs_gasit": str(_pv.curs), "vechime_zile": _pv.vechime_zile,
                "prag_zile": _pv.prag_zile, "mesaj": str(_pv),
                "iesire": {"camp": "curs_manual",
                           "cere": ["curs_manual", "data_curs_manual"],
                           "cum": "Introdu cursul de mână, cu data la care a fost comunicat. "
                                  "Se consemnează cine l-a introdus și când."}}
    except curs_bnr.MonedaNecotata as _mn:
        # Moneda nu exista: nu e o intarziere, deci nu se ofera nici „reincearca", nici
        # „curs manual" — al doilea ar baga factura in contabilitate pe o moneda inventata.
        return {"ok": False, "cod": "MONEDA_NECOTATA", "moneda": moneda,
                "data": data_factura.isoformat(), "mesaj": str(_mn)}
    except curs_bnr.CursIndisponibil:
        return {"ok": False, "cod": "CURS_INDISPONIBIL",
                "moneda": moneda, "data": data_factura.isoformat(),
                "mesaj": "Cursul BNR nu e disponibil momentan."}


def previzualizare_lei(conn, moneda, data_factura, linii=None):
    """[lotul 10, comanda 10.2 pct.7g] „Factură în valută: cursul BNR și TVA-ul în lei nu se văd înainte de emitere.” Ce va scrie emiterea,
    fără să scrie nimic: cursul (`curs_automat`, același ca la emitere), data lui și, pentru liniile date (cantitate, preț, cotă), TVA-ul și
    totalul în lei (`totaluri_din_linii` + `sume_lei`, aceleași ca la `creeaza_factura`). `linii=None` (cota încă nestabilită pe o
    linie): numai cursul. Refuzul cursului se întoarce ca atare (ok False, cu mesajul): formularul îl arată, emiterea îl va spune la
    fel."""
    c = curs_automat(conn, moneda, data_factura)
    if isinstance(c, dict):
        return c
    curs, data_curs, sursa = c
    out = {"ok": True, "moneda": moneda, "curs": str(curs), "data_curs": data_curs.isoformat(), "sursa": sursa,
           "vechime_zile": (data_factura - data_curs).days}
    if linii is not None:
        t = totaluri_din_linii(linii)
        tva_lei, total_lei = sume_lei(t, curs)
        out.update({"tva": str(t["tva"]), "total": str(t["total"]), "tva_lei": str(tva_lei), "total_lei": str(total_lei)})
    return out


# ============================================================
#  CREARE — DB
# ============================================================
from core import curs_bnr
from core import eticheta_nota as _et
from core import chei_unice as _chei   # [lotul 10, C73 / U2] numărul documentului dublat în cursă -> refuz numit, nu 500


# ─────────────────────────────────────────── CODUL DE PARTENER (prag 2, 23.08.2026)
# NORMA: Codul fiscal art. 319 alin. (20) cere pe factura codul de identificare fiscala al
# beneficiarului. Pana azi `tert_cui` era default de parametru (`None`) si NIMIC nu-l verifica -
# nici prezenta, nici cifra de control. Masurat: 2 din 42 de facturi fara cod, una catre un SRL,
# intrata PRIN APLICATIE (status `de_preluat`, produs de `emite_factura`).
#
# DE CE PRAG 2 SI NU O SEMNALARE (decizia lui Costin, 23.08): o factura fara CUI de partener
# NU INTRA IN D394 si nu se poate corela in VIES. Nu e o coloana goala, e o DECLARATIE INCOMPLETA
# la prima firma reala. Iar un CUI lipsa nu se poate completa retroactiv de nimeni altcineva decat
# cel care a emis factura - deci momentul e introducerea, nu un raport de mai tarziu.
#
# EXCEPTIA e EXPLICITA, nu dedusa: `tert_pf=True` spune ca partenerul e persoana fizica fara cod de
# identificare fiscala. Nu se ghiceste din nume si nici din lipsa codului - a ghici ar readuce exact
# tacerea pe care o inlocuim.
def cere_cod_partener(tert_cui, tert_pf=False, tert_nume=None):
    """Ridica daca lipseste codul de partener si nu s-a declarat persoana fizica."""
    if tert_pf:
        return None
    cod = (tert_cui or "").strip()
    if cod:
        return cod
    cine = (" (%s)" % tert_nume.strip()) if (tert_nume or "").strip() else ""
    raise ValueError(
        "Factura nu se poate salva fără codul fiscal al partenerului%s. Completează-l, sau bifează "
        "că partenerul e persoană fizică fără cod fiscal. Fără el, factura nu intră în D394 și nu "
        "se poate corela în VIES, iar codul nu mai poate fi completat mai târziu de altcineva decât "
        "cel care a emis-o (Cod fiscal art. 319 alin. 20)." % cine)


MESAJ_SCADENTA_INAINTE_DE_EMITERE = ("Data scadenței e înaintea datei emiterii — factura nu poate fi scadentă înainte să "
                                     "existe. Alege o scadență egală sau după data emiterii.")

#: [lotul 10, C73 / U2] cheile unice ale numărului documentului (`tenant_template.sql`): factura emisă (serie + număr) și borderoul
#: de achiziție (număr + an)
CHEI_NUMAR = ("facturi_numar_emisa_uniq", "facturi_borderou_numar_an_uniq")


def _refuz_numar_dublat(cur, numar, directie, tip, data_emitere):
    """[lotul 10, C73 / U2] Refuzul numit al numărului deja purtat de alt document — UN text, la verificarea dinaintea scrierii și la
    cursa dintre două salvări (chemat după întoarcerea la savepoint). `CheieDublata` (deci `ValueError`) sau None (nimic găsit)."""
    from core import pdf_util as _pu   # [258] documentul existent numit prin numărul și data lui, nu prin id
    if directie == "emisa":
        # [lotul 12, 252] aceeași mulțime ca cheia `facturi_numar_emisa_uniq`: fără facturile deschise preluate (numerele programului vechi)
        from core import nomenclator_status_factura as _nsf
        cur.execute("SELECT data_emitere FROM facturi WHERE numar=%s AND directie='emisa' AND " + _nsf.clauza_fara_sold_preluat(None)
                    + " LIMIT 1", (numar,))
        r = cur.fetchone()
        if r:
            return _chei.CheieDublata(
                "Numărul %s e deja pe factura emisă din %s. Două documente emise cu același număr rup "
                "secvența cerută de %s. Dacă documentul dinainte e greșit, se stornează — nu se "
                "reia numărul." % (numar, _pu.data_ro(r[0]), NUMEROTARE_SECVENTIALA), valoare=numar)
    elif tip == "borderou":
        from core import documente_interne as _di
        r = _di.borderou_cu_numarul(cur, "", numar, data_emitere)
        if r:
            return _chei.CheieDublata(
                "Numărul %s e deja al borderoului din %s (%s), salvat între timp de altă cerere. Nimic nu s-a scris: lasă câmpul gol, "
                "iar aplicația dă numărul următor, sau scrie alt număr." % (r[0], _pu.data_ro(r[1]), r[2] or "vânzător fără nume"),
                valoare=numar, camp="op-numar")
    return None


class FacturaRefuzata(ValueError):
    """[lotul 11, deficiența 440] Refuzurile de formă ale unei facturi, TOATE deodată. E `ValueError` (orice apelant care îl prindea ca
    text îl prinde la fel, iar `str(e)` le spune pe toate, rând cu rând); `detaliu()` = {mesaj, erori_campuri} pentru ecranul care pune
    fiecare eroare lângă câmpul ei (`camp` = numele din cerere: `linii[0].cota_tva`, `data_scadenta`, …)."""

    def __init__(self, erori):
        self.erori_campuri = [{"camp": c, "mesaj": m} for c, m in erori]
        super().__init__(erori[0][1] if len(erori) == 1 else
                         "Factura nu s-a salvat:\n" + "\n".join("— " + m for _c, m in erori))

    def detaliu(self):
        return {"mesaj": str(self), "erori_campuri": list(self.erori_campuri)}


def creeaza_factura(conn, numar, data_emitere, directie, linii,
                    client_id=None, tert_nume=None, tert_cui=None, tert_adresa=None,
                    data_scadenta=None, moneda="RON", status="emisa",
                    categorie_331=None, data_faptului_generator=None, taxare_inversa=False,
                    tert_platitor_tva=None, tert_tara="RO", tip_operatiune="normal",
                    furnizor_tva_incasare=False, tert_pf=False, tip="factura", axa_ic=None,
                    curs=None, data_curs=None, curs_sursa=None, cota_la_data=None,
                    bon_fiscal_nr=None, bon_fiscal_data=None, tert_oras=None, tert_judet=None, serie=None):
    """
    Inserează factura + liniile, într-o tranzacție. total/tva calculate din linii.
    Întoarce {ok, factura_id, total, tva}.

    [A1, 17.09.2026] CONVERSIA ÎN LEI E PAS OBLIGATORIU AL CREĂRII. `total_lei/tva_lei/curs_bnr` se
    scriu AICI, la INSERT, pentru ORICE factură — RON primește cursul 1 prin lege. Punctul e unic
    (toate emiterile trec prin `creeaza_factura`: emitere, storno, transformare proformă, `POST
    /facturi` primite), deci nicio factură nu mai ajunge în carte sau în declarație fără să fi trecut
    prin curs. Pentru valută, cursul vine de la apelant (`emite_factura` îl calculează cu logica lui
    de manual/auto/refuz); dacă nu vine, se încearcă auto o dată — iar dacă nici așa, `curs_bnr` rămâne
    `NULL`, factura se creează dar contarea o refuză (nu se ghicește 1). Nota automată (care rulează la
    capătul acestei funcții) vede deja sumele în lei.
    """
    cere_cod_partener(tert_cui, tert_pf, tert_nume)
    # [lotul 11, deficiența 440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp”]
    # Refuzurile de FORMĂ ale documentului (liniile și cota FIECĂREI linii, direcția, datele, axa, tipul operațiunii, starea, tipul
    # documentului) se ADAUGĂ și pleacă o dată (`FacturaRefuzata`, un `ValueError`: apelanții care prindeau `ValueError` îl prind la fel,
    # iar `str(e)` le spune pe toate). Înainte, prima oprea tot — bucla cotei se oprea la prima linie fără cotă.
    _er = []
    if not linii:
        _er.append(("linii", "factura trebuie să aibă cel puțin o linie"))
    for _i, _l in enumerate(linii or []):
        if _l.get("cota_tva") is None:
            _er.append(("linii[%d].cota_tva" % _i, "Linia %r nu are cotă de TVA. Completează cota pe linie — 0 (scutit) "
                                                   "e o valoare validă, dar absența nu se poate ghici." % (_l.get("descriere") or "",)))
    if directie not in DIRECTII:
        _er.append(("directie", "Direcția facturii trebuie să fie 'emisă' sau 'primită'."))
    # [probare invalid lot 2, 03.09.2026] Cele trei refuzuri de mai jos au înlocuit, în ordine:
    # un `500` pe o dată inexistentă în calendar, o factură cu cota de TVA 99% acceptată ȘI
    # contabilizată (4427 = 99 lei), și un al doilea document cu un număr deja folosit.
    _d_emitere = _d_scadenta = None
    try:
        _d_emitere = _data_ceruta("data emiterii", data_emitere)
    except ValueError as e:
        _er.append(("data_emitere", str(e)))
    try:
        _d_scadenta = _data_ceruta("data scadenței", data_scadenta)
    except ValueError as e:
        _er.append(("data_scadenta", str(e)))
    # [comanda Costin 05.10.2026 pct.4] scadența se stabilește pe formular și alimentează scadențarul; înaintea emiterii n-are sens
    if _d_scadenta is not None and _d_emitere is not None and _d_scadenta < _d_emitere:
        # refuz de FORMĂ, fără temei normativ: o scadență anterioară emiterii e o dată imposibilă, nu o regulă fiscală
        _er.append(("data_scadenta", MESAJ_SCADENTA_INAINTE_DE_EMITERE))
    # [IC2, 16.09.2026] axa operațiunii intracomunitare — o valoare din afara nomenclatorului e REFUZATĂ aici, cu numele câmpului
    from core.migrare_axa_ic import AXE as _AXE
    axa_v = (str(axa_ic).strip().lower() or None) if axa_ic is not None else None
    if axa_v is not None and axa_v not in _AXE:
        _er.append(("axa_ic", "Axa operațiunii intracomunitare poate fi doar %s (primit: %r). Ea se "
                              "înregistrează pe document și nu se mai schimbă după introducere." % (" sau ".join(_AXE), axa_ic)))
    tip_op_v = (tip_operatiune or "normal").strip().lower() or "normal"
    if tip_op_v not in ("normal", "avans", "regularizare_avans"):
        _er.append(("tip_operatiune", "Tipul operațiunii %r nu e recunoscut. Alege: normal, avans sau "
                                      "regularizare de avans." % tip_operatiune))
    # [A3, 17.09.2026] Statusul e din NOMENCLATOR, nu text liber. Până azi `FacturaIn.status` trecea
    # nevalidat prin `creeaza_factura`; o valoare inventată ar fi intrat în bază și ar fi decis tăcut
    # includerea în declarații (clauza de status compară cu lista nedeclarabilelor). Refuzul numește câmpul.
    from core import nomenclator_status_factura as _nsf_creare
    _status_v = (status or _nsf_creare.IMPLICITA).strip().lower() or _nsf_creare.IMPLICITA
    if _status_v not in _nsf_creare.STARI:
        _er.append(("status", "Starea %r nu e recunoscută ca stare de factură. Stări acceptate: %s."
                              % (status, ", ".join(sorted(_nsf_creare.STARI)))))
    # [EEE1] `tip` intra la INSERT, nu printr-un UPDATE de dupa (nota automata, in aceeasi tranzactie, trebuie sa stie tipul)
    tip_v = (tip or "factura").strip().lower() or "factura"
    if tip_v not in ("factura", "proforma", "aviz", "borderou"):
        _er.append(("tip", "Tipul documentului %r nu e recunoscut. Alege: factură, proformă sau aviz." % tip))
    elif tip_v == "borderou" and directie != "primita":   # [401] borderoul e numai al achiziției de la persoana fizică — refuz de FORMA
        _er.append(("tip", "Borderoul de achiziție e documentul cumpărării de la o persoană fizică: numai pe achiziție."))
    furnizor_incasare_v = bool(furnizor_tva_incasare)
    if furnizor_incasare_v and directie != "primita":
        _er.append(("furnizor_tva_incasare", "TVA la încasare la furnizor se poate bifa doar pe facturile primite "
                                             "— pe cele emise nu se aplică."))
    if _er:
        raise FacturaRefuzata(_er)
    _bon_nr, _bon_data = _marca_bon(directie, tip, bon_fiscal_nr, bon_fiscal_data, data_emitere)
    # [3i · CF art. 282 alin. (9)] la evenimentele art. 287 (storno, reducere de pret) taxa e
    # exigibila la data evenimentului (data_emitere = azi), dar COTELE APLICABILE sunt aceleasi
    # ca ale operatiunii de baza. cota_la_data muta DOAR verificarea cotei pe data operatiunii de
    # baza; exigibilitatea (data_emitere) ramane azi. Fara ea, storno-ul unei facturi de 19%
    # (emisa inainte de 01.08.2025) verifica 19% contra cotelor de azi {0,11,21} si o respinge.
    _cota_ref = _data_ceruta("data cotei de baza", cota_la_data) if cota_la_data else _d_emitere
    _rea = _cota_necunoscuta(linii, _cota_ref)
    if _rea is not None and (directie == "emisa" or (tert_tara or "RO").strip().upper() == "RO"):
        # Numai pe ce ține de legea română: pe o factură PRIMITĂ dintr-un alt stat, cota lui e
        # legitimă și n-avem de unde ști lista lui. Limita e declarată, nu ascunsă.
        _l, _c, _permise, _temeiuri = _rea
        raise ValueError(
            "Linia %r are cota de TVA %s%%, care nu există în legea română la data facturii (%s). "
            "Cotele de atunci: %s. Temei: %s."
            % (_l.get("descriere") or "", _c, _d_emitere.isoformat() if _d_emitere else "azi",
               ", ".join("%s%%" % _f for _f in sorted(_permise)),
               "; ".join(sorted({str(_t) for _t in _temeiuri}))))
    if directie == "emisa" and any(Decimal(str(_l.get("cota_tva"))) != 0 for _l in linii):
        # [lot 19 pct.4d, 02.10.2026] Emitentul NEplătitor de TVA nu poate purta taxa pe factură: CF art.310 alin.(10)
        # lit.b) — persoana care aplică regimul special de scutire „nu are voie să menționeze taxa pe factură sau pe alt
        # document”. Punctul e unic (toate emiterile trec pe aici), deci garda acoperă emiterea, storno-ul și transformarea
        # proformei. Profil fără statut (NULL) = plătitor, ca `uc_comun._platitor_tva_firma` (fără default tăcut nou).
        with conn.cursor() as _cur:
            _cur.execute("SELECT platitor_tva FROM firma_profil WHERE id = 1")
            _pf = _cur.fetchone()
        if _pf is not None and _pf[0] is False:
            _l = next(_l for _l in linii if Decimal(str(_l.get("cota_tva"))) != 0)
            _e = ValueError(
                "Firma nu e plătitoare de TVA, deci factura nu poate purta TVA: linia %r are cota %s%%. "
                "Cota pe liniile unui neplătitor e 0 (CF art.310 alin.(10) lit.b): persoana în regim special de "
                "scutire „nu are voie să menționeze taxa pe factură sau pe alt document”)."
                % (_l.get("descriere") or "", _l.get("cota_tva")))
            # motivul ca DATĂ (cod + temei + linia), ca refuzul să se poată verifica fără a citi fraza
            _e.cod, _e.temei, _e.linie = "EMITENT_NEPLATITOR_TVA", "CF art.310 alin.(10) lit.b)", _l.get("descriere")
            raise _e
    _avert_emitere = []   # [lotul 12, C157] avertismentele emiterii (nu refuzuri), în răspuns: `avertismente`
    if directie == "emisa":
        # [274b, decizia Costin 16.10.2026] categoria de TVA pe orice linie cu 0% (core/categorii_tva): la neplătitor „O”, automat; la
        # plătitor aleasă, altfel refuz numit (punct UNIC: emiterea, stornarea, proforma transformată, vânzarea IC, API-ul, magazinul,
        # facturile recurente). O linie cu taxare inversă (art.331) pune taxarea inversă pe factură, cu categoria produsului (D394).
        # [lotul 12, C156 / C157, decizia Costin 12.3 pct.3] și înregistrarea art.317 a neplătitorului: prestarea către clientul din alt stat
        # membru primește „taxare inversă” și codul RO art.317 (înregistrat) sau avertismentul emiterii (neînregistrat) — `_avert_emitere`
        from core import categorii_tva as _ct
        with conn.cursor() as _cur:
            _cur.execute("SELECT platitor_tva, inreg_art317 FROM firma_profil WHERE id = 1")
            _pft = _cur.fetchone()
        _rele = _ct.verifica_linii(linii, None if _pft is None else _pft[0], tert_tara, art317=None if _pft is None else _pft[1],
                                   tert_cui=tert_cui)
        if _rele:
            _e = ValueError(" ".join(r["mesaj"] for r in _rele))
            _e.cod, _e.campuri = _rele[0]["cod"], _rele
            raise _e
        # [17.10.2026] axa facturii (bunuri / servicii) vine din categoriile liniilor: din ea se iau D390 (L / P) și D300 (rd.1 / rd.3)
        _axa_cat = _ct.axa_facturii(linii)
        if _axa_cat:
            if axa_ic and str(axa_ic).strip().lower() != _axa_cat:
                _e = ValueError("Axa facturii (%s) nu se potrivește cu categoria liniilor (%s)." % (axa_ic, _axa_cat))
                _e.cod = "AXA_CATEGORIE"
                raise _e
            axa_ic = _axa_cat
        elif not axa_ic:
            # [lotul 12, C154] la neplătitor categoria liniilor („neplatitor”, O) n-are axă: axa vine din felul liniilor (contul de venit),
            # altfel serviciul către clientul din UE intra în D390 ca livrare de bunuri (L), nu ca prestare (P). Axa dată de apelant
            # (prestarea din Operațiuni, `uc_tenants.vanzare_ic`; stornarea, cu axa originalului) rămâne a lui.
            axa_ic = _ct.axa_neplatitor(linii, tert_tara)
        if _pft is not None and not any("categorie_istoric" in _l for _l in linii):   # stornarea (marca ei) nu e o prestare nouă
            _avert_emitere = _ct.avertismente_emitere(_pft[0], _pft[1], (str(axa_ic or "").strip().lower() or None), tert_tara, tert_cui)
        if any(_l.get("categorie_tva") == "taxare_inversa" for _l in linii):
            taxare_inversa = True
            from core import produse_api as _pa   # [lotul 11, 449, patch B/P4] categoriile D394, cu cerealele pe codul NC
            if categorie_331 and categorie_331 not in _pa.coduri_331():
                _e = ValueError("Categoria produsului %r nu e una din D394 (%s)." % (
                    categorie_331, ", ".join(e for e, _c in sorted(_pa.coduri_331().values()))))
                _e.cod = "CATEGORIE_331_NECUNOSCUTA"
                raise _e
            if not categorie_331:
                _e = ValueError("Factura are linii cu taxare inversă (art.331): alege categoria produsului (D394 o declară cu codul ei).")
                _e.cod, _e.campuri = "CATEGORIE_331_DE_COMPLETAT", [{"camp": "em-c331", "eticheta": "Categoria produsului (art.331)",
                                                                     "mesaj": "Alege categoria produsului cu taxare inversă (art.331)."}]
                raise _e
    if directie == "emisa":
        # [Lot 19 defect 12, 03.10.2026] Legea 31/1990 art.74 alin.(3): factura unui SRL menționează capitalul social, a
        # unui SA/SCA capitalul subscris și cel vărsat. Punct UNIC (orice emitere trece pe aici: ecranul, storno,
        # proforma transformată, bonul). Decizia lui Costin: refuz, cu ce lipsește și trimitere la Date firmă.
        from core import capital_social as _cs
        with conn.cursor() as _cur:
            _cur.execute("SELECT tip_firma, forma_juridica, capital_subscris, capital_varsat FROM firma_profil WHERE id = 1")
            _r = _cur.fetchone()
        if _r is not None:
            _lips = _cs.lipsa({"tip_firma": _r[0], "forma_juridica": _r[1], "capital_subscris": _r[2],
                               "capital_varsat": _r[3]})
            if _lips:
                raise _cs.refuz(_lips)
    if directie == "emisa" and numar:
        with conn.cursor() as _cur:
            _refuz = _refuz_numar_dublat(_cur, numar, directie, tip, data_emitere)
        if _refuz:
            raise _refuz
    # [B1 D300] campuri de clasificare/temporizare. tip_operatiune distinge avansul (exigibil la
    # emitere, art.282 alin.2 lit.b); furnizor_tva_incasare doar pe PRIMITE (deducere amanata la
    # plata, art.297 alin.2). Fara default tacit peste o valoare invalida -> refuz cu mesaj clar.
    tert_tara_v = (tert_tara or "RO").strip().upper() or "RO"
    # [R186, 16.09.2026] AXA bunuri/servicii, ÎNGHEȚATĂ pe document. Nomenclatorul vine din
    # `migrare_axa_ic.AXE`, nu scris aici: a doua definiție a aceluiași nomenclator e începutul unei
    # divergențe. `None` e a TREIA stare — „nedeclarată" —, nu un implicit. Axa, tipul operațiunii, starea (A3, din nomenclator),
    # tipul documentului (EEE1) și TVA la încasare la furnizor sunt validate SUS, împreună cu celelalte refuzuri de formă
    # ([lotul 11, 440] `FacturaRefuzata`); aici rămân valorile normalizate. Axa se normalizează DUPĂ derivarea din categoria liniilor
    # (`axa_ic = _axa_cat`, mai sus), ca înainte.
    axa_v = (str(axa_ic).strip().lower() or None) if axa_ic is not None else None
    status = _status_v
    t = totaluri_din_linii(linii)
    if directie == "primita" and tip_v == "factura":
        # [lotul 12, C73.1, comanda Costin 12.2 pct.6] aceeași factură de furnizor (furnizor + număr, `factura_primita_dublura`) nu intră a
        # doua oară: Operațiuni (necorporală, taxare inversă, intracomunitară) și `POST /facturi` trec toate pe aici. Nimic scris.
        from core import factura_primita_dublura as _fpd, repo_facturi as _rf_d
        with conn.cursor() as _cur:
            _ex = _rf_d.primite_cu_aceeasi_cheie(_cur, None, tert_cui, tert_nume, serie, numar, negativ=t["total"] < 0)
        if _ex:
            raise _fpd.refuz(_ex)
    # [A1] Conversia în lei, calculată O DATĂ, la creare. RON → curs 1 (total_lei=total). Valută:
    # cursul dat de apelant, altfel o încercare auto; pe eșec rămâne NULL (factura există, dar
    # contarea o refuză și declarațiile o exclud — nu se ghicește 1).
    _moneda_v = (moneda or "RON").strip().upper() or "RON"
    _d_emit_lei = _d_emitere or _data_ceruta("data emiterii", data_emitere)
    if _moneda_v == "RON":
        _curs_v, _dcurs_v, _sursa_v = Decimal(1), _d_emit_lei, "ron"
        _total_lei_v, _tva_lei_v = t["total"], t["tva"]
    elif curs is not None:
        _curs_v = Decimal(str(curs))
        _dcurs_v = data_curs or _d_emit_lei
        _sursa_v = curs_sursa or "manual"
        _tva_lei_v, _total_lei_v = sume_lei(t, _curs_v)   # [lotul 10, 7g] aceeași conversie ca în formular
    else:
        _curs_v = _dcurs_v = _sursa_v = _total_lei_v = _tva_lei_v = None
        try:
            _c_auto, _dc_auto, _s_auto = curs_bnr.curs_pentru(conn, _moneda_v, _d_emit_lei)
            _curs_v, _dcurs_v, _sursa_v = Decimal(str(_c_auto)), _dc_auto, _s_auto
            _tva_lei_v, _total_lei_v = sume_lei(t, _curs_v)
        except Exception:
            pass   # valută fără curs disponibil: NULL, semnalat la contare/declarație (nu se inventează)
    with conn.cursor() as cur:
        # [lotul 10, 428, decizia Costin „Bifă pe client”] beneficiarul afiliat (CF art.282 alin.(6) lit.d): „livrările de bunuri/prestările
        # de servicii pentru care beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26” nu intră în
        # sistemul TVA la încasare. Bifa clientului se ÎNGHEAȚĂ pe factura emisă la emitere (o bifă schimbată mâine nu mută regimul unei
        # facturi de ieri); motorul (`tva_incasare.motiv_excludere`) o citește de pe factură.
        from core import clienti_api as _cl
        _afiliat_v = directie == "emisa" and _cl.client_afiliat(cur, client_id, tert_cui)
        # [lotul 10, C73 / U2] numărul emis (`facturi_numar_emisa_uniq`) și numărul borderoului (`facturi_borderou_numar_an_uniq`) sunt
        # unici în bază. Verificarea de mai sus (și cea a borderoului, în use-case) ține cererile una după alta; două salvări simultane cu
        # același număr treceau amândouă, iar a doua cădea aici cu 500. Acum ACELAȘI refuz numit (ValueError -> 422 la toți apelanții).
        with _chei.refuza_dublura(cur, CHEI_NUMAR, lambda cur, e: _refuz_numar_dublat(cur, numar, directie, tip_v, data_emitere)):
            cur.execute(
                "INSERT INTO facturi (client_id, numar, data_emitere, data_scadenta, "
                "total, tva, status, moneda, directie, tert_nume, tert_cui, tert_adresa, "
                "categorie_331, data_faptului_generator, taxare_inversa, tert_platitor_tva, "
                "tert_tara, tip_operatiune, furnizor_tva_incasare, tip, axa_ic, "
                "tert_oras, tert_judet, "   # [274b] localitatea / regiunea clientului (adresa de livrare a livrării intracomunitare în XML)
                "curs_bnr, tva_lei, total_lei, data_curs, curs_sursa, "  # [A1] lei la INSERT
                "bon_fiscal_nr, bon_fiscal_data, "   # [decizia A 02.10] factura emisă pe baza bonului fiscal
                # [punctul 3, 03.10.2026] … și ÎNCASATĂ: HG 1/2016 pct.97 alin.(1) „facturile emise și achitate pe bază de bonuri
                # fiscale”. Fără asta rămânea „neîncasată”: notificarea de scadență (emailul pleacă la CLIENT) o trata ca
                # restanță, scadențarul la fel, iar ecranul oferea „Emite chitanță” — încasare dublă.
                "platita_la, beneficiar_afiliat, "
                # [lotul 11, 443] seria ÎNAINTEA contării de la creare (`_conteaza_la_creare`): scrisă după, nota emiterii ieșea „Contare
                # factura F61” (`_descriere` citea factura fără serie) — core/test_lot11_n_443_existente.py
                "serie) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
                "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (client_id, numar, data_emitere, data_scadenta, t["total"], t["tva"],
                 status, moneda, directie, tert_nume, tert_cui, tert_adresa,
                 categorie_331 or None, data_faptului_generator or None, bool(taxare_inversa),
                 tert_platitor_tva, tert_tara_v, tip_op_v, furnizor_incasare_v, tip_v, axa_v,
                 (tert_oras or "").strip() or None, (tert_judet or "").strip() or None,
                 _curs_v, _tva_lei_v, _total_lei_v, _dcurs_v, _sursa_v, _bon_nr, _bon_data,
                 _bon_data if _bon_nr else None, bool(_afiliat_v), serie))
            factura_id = cur.fetchone()[0]
        for l in linii:
            cur.execute(
                "INSERT INTO factura_linii (factura_id, descriere, um, cantitate, "
                "pret_unitar, cota_tva, articol_id, cont_venit, categorie_tva, valoare_neta) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (factura_id, l["descriere"], l.get("um", "buc"),
                 l["cantitate"], l["pret_unitar"], l["cota_tva"], l.get("articol_id"),
                 (l.get("cont_venit") or None),  # #11 cont venit pe linie (auto din denumire, editabil)
                 (l.get("categorie_tva") if directie == "emisa" else None),   # [274b] categoria liniei cu 0%
                 # [lotul 11, C86] valoarea netă a liniei, când apelantul o dă (stornarea unei facturi venite din XML: −BT-131); NULL = cant. × preț
                 l.get("valoare_neta")))
    _redeschide_luna(conn, data_emitere)   # [cap.23] evidenta lunii s-a schimbat -> luna se redeschide
    out = {"ok": True, "factura_id": factura_id,
           "total": float(t["total"]), "tva": float(t["tva"]), "avertismente": _avert_emitere}
    out["contare"] = _conteaza_la_creare(conn, factura_id, directie, tip_v)
    return out


def _marca_bon(directie, tip, bon_nr, bon_data, data_emitere):
    """Marca „emisă pe baza bonului fiscal” (HG 1/2016 pct.97 alin.(1): „conform bon fiscal nr./data”): numărul ȘI data
    bonului, doar pe o FACTURĂ EMISĂ, cu bonul cel târziu în ziua facturii (HG 479/2003 anexa art.2: factura se eliberează
    „la data eliberării bonului fiscal”). Întoarce (nr, data) sau (None, None)."""
    nr = str(bon_nr or "").strip()
    if not nr and not bon_data:
        return None, None
    if not nr or not bon_data:
        raise ValueError("Factura emisă pe baza bonului fiscal cere și numărul, și data bonului (HG 1/2016 pct.97 "
                         "alin.(1): mențiunea „conform bon fiscal nr./data”).")
    if directie != "emisa" or (tip or "factura") != "factura":
        raise ValueError("Marca „emisă pe baza bonului fiscal” se pune doar pe o factură emisă.")
    d_bon = _data_ceruta("data bonului fiscal", bon_data)
    import datetime as _dt
    d_fact = _data_ceruta("data emiterii", data_emitere) if data_emitere else _dt.date.today()
    if d_bon > d_fact:
        raise ValueError("Bonul fiscal (%s) nu poate fi după factura emisă pe baza lui (%s)." % (d_bon, d_fact))
    return nr, d_bon


def _conteaza_la_creare(conn, factura_id, directie, tip):
    """[EEE1 / R87] Nota contabila a facturii EMISE se scrie in ACELASI act cu emiterea.

    DE CE AICI, si nu in ruta: `creeaza_factura` e punctul UNIC prin care trec toate emiterile
    aplicatiei — `POST /facturi`, `POST /facturi/emite`, stornarea si transformarea proformei o
    cheama pe toate. Legat de o singura ruta, decizia R36 ar fi fost adevarata doar pe un drum din
    patru. *Masurat prin citire, nu presupus: `emite_factura` si `storneaza` cheama chiar functia
    asta.*

    DE CE NUMAI `emisa`: la primita, faptul economic nu e sosirea documentului, ci recunoasterea
    cheltuielii — nota se scrie la `/valideaza` (R88, decizia din 29.08.2026).

    ROLLBACK COMPLET, ca la NIR: nu se comite nimic aici. Daca emiterea cade mai tarziu — curs BNR
    indisponibil, de pilda —, nota cade cu ea. **Nu exista factura fara nota, si nici nota fara
    factura.**

    UN REFUZ NU E O EROARE. `RefuzContare` opreste NOTA, nu emiterea: factura se creeaza oricum, iar
    motivul pleaca in raspuns. Altfel o factura perfect valida n-ar mai putea fi emisa dintr-un motiv
    de contabilitate — iar semnalul ca lipseste nota exista deja, in verdictul de TVA (R35).

    CE NU ACOPERA, DECLARAT (ZZ4 cere ca absenta sa fie scrisa, nu deduse): facturile intrate prin
    `main._factura_din_parsat` — importul din SPV si incarcarea manuala de XML — NU trec pe aici, ci
    printr-un INSERT propriu. O factura EMISA care se intoarce din SPV a fost emisa in alta parte;
    pentru ea, sosirea documentului nu e faptul economic. Ramane necontata si vizibila ca atare in
    verdictul de TVA.
    """
    from core import contare_facturi as _cf
    from core import afirmatii as _af
    if directie != "emisa" or tip != "factura":
        return {"stare": "neaplicabil", "afirmatie": _af.afirmatie(
            "absenta_observatie", "CONTARE_NEAPLICABILA",
            "nota automată se scrie doar pentru facturile emise; documentul acesta nu e o factură emisă "
            "(%s / %s)" % (directie, tip),
            surse_consultate=["facturi.directie", "facturi.tip"])}
    try:
        with _cf.cursor_dict(conn) as cur:
            return _cf.contabilizeaza(cur, "", factura_id, automat=True)
    except _cf.RefuzContare as e:
        if e.cod == "EMISA_DIN_BON":
            # nu e o neconformitate: factura din bon nu e un fapt economic nou (decizia A 02.10)
            return {"stare": "neaplicabil", "afirmatie": _af.afirmatie(
                "absenta_observatie", e.cod, e.mesaj, surse_consultate=["facturi.bon_fiscal_nr"])}
        return {"stare": "refuzata", "cod": e.cod, "detalii": e.detalii,
                "afirmatie": _af.afirmatie(
                    "neconformitate", e.cod, e.mesaj,
                    unde=_eticheta_factura(conn, factura_id),
                    regula="nota automată se scrie doar când toate intrările ei sunt cunoscute")}


# ============================================================
#  LISTĂ — DB
# ============================================================
def lista_facturi(conn, an=None, luna=None, directie=None, limit=None, offset=0):
    """Lista facturilor (antet), filtrabilă pe an/lună/direcție. limit=None -> tot istoricul
    (folosit intern de alte module: verificatoare, D390 etc.); UI foloseste limit pentru paginare."""
    import psycopg2.extras as _E
    # [probare invalid lot 2, 03.09.2026] Trei feluri de a nu răspunde, toate reparate aici:
    # `luna=13` construia intervalul „2026-13-01 … 2026-14-01" și pica în driver (`500`);
    # `limit=-5` ajungea în `LIMIT -5`, refuzat de Postgres (`500`); iar `directie=lateral`
    # întorcea `200` cu listă goală — „nu există facturi așa" arăta identic cu „direcția asta
    # nu există", exact clasa scoasă din `GET /coada` în lotul 1.
    if luna is not None and not (1 <= luna <= 12):
        raise ValueError("luna invalidă: %r (se așteaptă 1-12)" % (luna,))
    if an is not None and not (1990 <= an <= 2100):
        raise ValueError("an invalid: %r (se așteaptă 1990-2100)" % (an,))
    if directie is not None and directie not in DIRECTII:
        raise ValueError("direcție necunoscută: %r (direcțiile facturii: %s)"
                         % (directie, ", ".join(DIRECTII)))
    if limit is not None and limit < 0:
        raise ValueError("limit invalid: %r (se așteaptă un număr pozitiv, sau nimic pentru tot)"
                         % (limit,))
    if offset is not None and offset < 0:
        raise ValueError("offset invalid: %r (se așteaptă un număr pozitiv sau 0)" % (offset,))
    cond, val = [], []
    if an is not None and luna is not None:
        inceput = "%04d-%02d-01" % (an, luna)
        sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
        cond.append("data_emitere >= %s AND data_emitere < %s"); val += [inceput, sfarsit]
    elif an is not None:
        cond.append("data_emitere >= %s AND data_emitere < %s")
        val += ["%04d-01-01" % an, "%04d-01-01" % (an + 1)]
    if directie is not None:
        cond.append("directie = %s"); val.append(directie)
    # [lotul 12, 252] facturile deschise preluate nu sunt facturi ale firmei din iConta.eu: stau în scadențar, în potrivirea băncii /
    # casei / compensărilor, nu în „Istoric facturi” (și nici la cititorii interni ai listei: verificatoare, D390)
    from core import nomenclator_status_factura as _nsf
    cond.append(_nsf.clauza_fara_sold_preluat(None))
    where = (" WHERE " + " AND ".join(cond)) if cond else ""
    limitclause = ""
    if limit is not None:
        limitclause = " LIMIT %s OFFSET %s"; val += [limit, offset]
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            # [lotul 11, 443] `serie` pentru afișarea separată în Istoric („F6 nr. 1”, `numarCuSerie`), nu numărul lipit
            "SELECT id, numar, serie, data_emitere, directie, total, tva, total_lei, tva_lei, status, "
            "COALESCE(taxare_inversa, false) AS taxare_inversa, "   # [lotul 13, 546] totalul de plată al facturii primite cu taxare inversă
            "moneda, tert_nume, tert_cui, tert_adresa, tip, transformat_in_id, storno_din_id, platita_la, data_faptului_generator, tert_tara "
            "FROM facturi" + where +
            " ORDER BY data_emitere DESC, id DESC" + limitclause, val)
        out = [dict(r) for r in cur.fetchall()]
        _cu_total_de_plata(out)
        _cu_stare_contare(cur, out)
        _cu_stare_incasare(cur, out)
        _cu_stare_spv(cur, out)   # [lotul 6 pct.5b, 275]
        return out


#: [lotul 6 pct.5b, 275] starea în SPV, pe înțelesul contabilului, din ultima trimitere a facturii (`efactura_trimiteri.stare`)
STARE_SPV = {None: "netrimisa", "pregatit": "netrimisa", "eroare_upload": "netrimisa", "incarcat": "trimisa", "in_prelucrare": "trimisa",
             "investigatie": "trimisa", "ok": "acceptata", "nok": "respinsa"}


def termen_spv(data_emitere, data_fapt_generator=None):
    """OUG 120/2021 art.10 alin.(7) (anaf_surse/oug_120_2021.txt): „Termenul-limită pentru transmiterea facturilor în sistemul național
    privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile
    lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015 [...]. Calculul
    termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71” — termenul începe a doua zi; zilele lucrătoare,
    fără sâmbete, duminici și sărbători legale (`scadente.e_zi_lucratoare`, Codul muncii art.139). Cu faptul generator cunoscut, al
    doilea capăt: 5 zile lucrătoare după 15 ale lunii următoare faptului generator (CF art.319 alin.(16)); se ia cel mai devreme."""
    import datetime as _dt
    from core.scadente import e_zi_lucratoare

    def _plus5(d):
        n = 0
        while n < 5:
            d += _dt.timedelta(days=1)
            if e_zi_lucratoare(d):
                n += 1
        return d
    de = data_emitere if hasattr(data_emitere, "year") else _dt.date.fromisoformat(str(data_emitere)[:10])
    t = _plus5(de)
    if data_fapt_generator:
        fg = data_fapt_generator if hasattr(data_fapt_generator, "year") else _dt.date.fromisoformat(str(data_fapt_generator)[:10])
        limita_emitere = _dt.date(fg.year + 1, 1, 15) if fg.month == 12 else _dt.date(fg.year, fg.month + 1, 15)
        t = min(t, _plus5(limita_emitere))
    return t


def spv_obligatorie(tert_tara, tert_cui):
    """[deficiența 307, comanda Costin 17.10.2026 7.2 pct.6, verificat la sursă] Factura emisă se transmite OBLIGATORIU în RO e-Factura
    numai către un client stabilit în România sau înregistrat în scopuri de TVA în România. OUG 120/2021 art.10 alin.(1): „În relația
    comercială B2B, între persoane impozabile stabilite în România [...] pentru livrările de bunuri și prestările de servicii care au locul
    livrării/prestării în România [...] emitentul facturii electronice are obligația de transmitere”; alin.(1^1) (de la 01.01.2026, OUG
    89/2025): și către „persoane impozabile nestabilite, dar înregistrate în scopuri de TVA în România” (text din
    `anaf_surse/oug_120_2021.html`). Clientul din alt stat, cu cod de TVA al lui (F1A5, Irlanda: serviciu cu locul prestării la client,
    CF art.278 alin.(2)) nu intră în niciunul — fără obligație, deci fără termenul de 5 zile."""
    tara = (tert_tara or "RO").strip().upper() or "RO"
    cod = (tert_cui or "").strip().upper()
    return tara == "RO" or cod.startswith("RO") or (cod.isdigit() and bool(cod))


def _cu_stare_spv(cur, facturi):
    """[lotul 6 pct.5b, 275] „«Istoric facturi» și detaliul arată starea în SPV: netrimisă / trimisă / acceptată / respinsă, cu termenul de 5
    zile lucrătoare.” Pe facturile EMISE de tip factură (proforma, avizul nu pleacă în e-Factura): `stare_spv` = {stare, termen,
    depasit, eroare}. O singură definiție pentru listă și detaliu; starea vine din ultima trimitere (`efactura_trimiteri`)."""
    from core.common import azi_ro as _azi
    ids = [f["id"] for f in facturi if f.get("directie") == "emisa" and (f.get("tip") or "factura") == "factura"]
    for f in facturi:
        f["stare_spv"] = None
        f["din_efactura"] = None
    if not ids:
        return
    # [lotul 11, C86] factura EMISĂ venită din XML-ul e-Factura (`/import-efactura`; `facturi.xml` îl scrie numai importul — discriminatorul
    # din `efactura_trimitere.refuz_din_efactura`) e transmisă în SPV de cine a emis-o: nu e „netrimisă”, n-are termen și nu se trimite din
    # aplicație — `din_efactura` = eticheta de pe ecran, în locul butonului „Trimite în SPV”
    from core import efactura_trimitere as _eft
    cur.execute("SELECT id FROM facturi WHERE id = ANY(%s) AND xml IS NOT NULL", (ids,))
    din_xml = {(r["id"] if isinstance(r, dict) else r[0]) for r in cur.fetchall()}
    cur.execute("SELECT DISTINCT ON (factura_id) factura_id, stare, error_message FROM efactura_trimiteri "
                "WHERE factura_id = ANY(%s) ORDER BY factura_id, id DESC", (ids,))
    ultima = {}
    for r in cur.fetchall():
        k = r["factura_id"] if isinstance(r, dict) else r[0]
        ultima[k] = (r["stare"], r["error_message"]) if isinstance(r, dict) else (r[1], r[2])
    azi = _azi()
    for f in facturi:
        if f["id"] not in ids or not f.get("data_emitere"):
            continue
        st, err = ultima.get(f["id"], (None, None))
        if f["id"] in din_xml:
            f["din_efactura"] = _eft.ETICHETA_DIN_EFACTURA
            if st is None:   # nicio trimitere din aplicație: nici „netrimisă”, nici termen (o trimitere veche, dacă există, rămâne arătată)
                continue
        stare = STARE_SPV.get(st, "netrimisa")
        if not spv_obligatorie(f.get("tert_tara"), f.get("tert_cui")):
            # [307] clientul nu e stabilit și nu e înregistrat în scopuri de TVA în România: transmiterea nu e obligatorie, deci nici termen
            f["stare_spv"] = {"stare": stare, "termen": None, "depasit": False, "obligatorie": False,
                              "eroare": err if stare in ("respinsa", "netrimisa") and st else None, "stare_tehnica": st}
            continue
        termen = termen_spv(f["data_emitere"], f.get("data_faptului_generator"))
        f["stare_spv"] = {"stare": stare, "termen": termen.isoformat(), "depasit": stare == "netrimisa" and azi > termen,
                          "obligatorie": True, "eroare": err if stare in ("respinsa", "netrimisa") and st else None, "stare_tehnica": st}


def _cu_total_de_plata(facturi):
    """[lotul 13, 546] `total_de_plata` (în moneda facturii) și `tva_taxare_inversa` (TVA-ul determinat de beneficiar, care nu se plătește
    furnizorului — CF art.331 alin.(3)) pe fiecare factură, pentru ecran (`facturi.total_de_plata`, aceeași definiție ca starea de plată)."""
    from core import facturi as _fc_tp
    for f in facturi:
        f["total_de_plata"] = str(_fc_tp.total_de_plata(f, f.get("total"), f.get("tva")))
        f["tva_taxare_inversa"] = str(f.get("tva") or 0) if _fc_tp.fara_tva_de_plata(f) else None


def _cu_stare_incasare(cur, facturi):
    """[retest 08.10, completarea pct.1, comanda Costin] „starea de încasare (încasată / parțial / neîncasată) trebuie să fie vizibilă
    pe factură și în lista «Istoric facturi»” — F1A3, încasată integral prin CHF1-1, arăta numai „contabilizată”. O SINGURĂ definiție
    pentru listă și detaliu: încasat = chitanțele nenulate ale facturii (`chitante.factura_id`) + plățile legate de factură
    (`inregistrari.factura_id`, nu contarea: 411x pe credit la emisă, 401x pe debit la primită — reconcilierea bancară, casa);
    `platita_la` (pus de chitanța integrală, de bonul stins) = încasare integrală declarată. Comparat cu totalul în lei.
    `stare_incasare` = {stare: incasata | partial | neincasata | stornata, incasat, total[, stornat]}; None la proformă / aviz / storno."""
    from decimal import Decimal as _D
    from core import facturi as _fc_tp
    from core import sume_lei as _sl
    from core import nomenclator_status_factura as _nsf
    # [lotul 12, 252] și factura deschisă preluată are stare de încasare (`TIPURI_CU_INCASARE`): banca, casa, compensarea o sting
    ids = [f["id"] for f in facturi if (f.get("tip") or "factura") in _nsf.TIPURI_CU_INCASARE and not f.get("storno_din_id")]
    for f in facturi:
        f["stare_incasare"] = None
    if not ids:
        return
    # [lotul 6 pct.3a, 278] chitanța se numără aici numai dacă nota ei NU e legată de factură: de la lotul 6 nota chitanței stinge factura
    # (`inregistrari.factura_id`, numărată mai jos) — altfel aceeași încasare ar intra de două ori
    cur.execute("SELECT c.factura_id, COALESCE(SUM(c.suma), 0) FROM chitante c WHERE c.factura_id = ANY(%s) AND NOT c.anulata "
                "AND NOT EXISTS (SELECT 1 FROM inregistrari i WHERE i.id = c.inregistrare_id AND i.factura_id = c.factura_id) "
                "GROUP BY c.factura_id", (ids,))
    incasat = {(r["factura_id"] if isinstance(r, dict) else r[0]): _D(str(r["coalesce"] if isinstance(r, dict) else r[1]))
               for r in cur.fetchall()}
    # [lotul 10, 428, decizia „Construiesc acum”] „fiecare compensare stinge cele două facturi”: nota compensării (401 = 4111) e legată
    # de AMBELE prin `compensari` (`compensari_api.legaturi`, sursa unică a legăturii notă–factură), nu prin `inregistrari.factura_id`
    from core import compensari_api as _cz
    cur.execute("SELECT lg.factura_id, COALESCE(SUM(l.suma), 0) FROM " + _cz.legaturi() + " lg JOIN inregistrari i ON i.id = lg.inregistrare_id "
                "JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "JOIN facturi f ON f.id = lg.factura_id WHERE lg.factura_id = ANY(%s) AND i.sursa IS DISTINCT FROM 'facturi' "
                "AND ((f.directie = 'emisa' AND l.cont_credit LIKE '411%%') OR (f.directie = 'primita' AND l.cont_debit LIKE '401%%')) "
                "GROUP BY lg.factura_id", (ids,))
    for r in cur.fetchall():
        k = r["factura_id"] if isinstance(r, dict) else r[0]
        incasat[k] = incasat.get(k, _D(0)) + _D(str(r["coalesce"] if isinstance(r, dict) else r[1]))
    # [deficiența 416] stornările facturii (în lei, negative): stornată integral -> „stornata” (nu „neîncasată”: nu mai e nimic de
    # încasat, deci nici scadențar, nici notificare — aceeași definiție, `repo_facturi.SQL_STORNARI`, acolo); parțial -> rămasul e totalul
    cur.execute("SELECT storno_din_id, COALESCE(SUM(COALESCE(total_lei, total)), 0) FROM facturi WHERE storno_din_id = ANY(%s) "
                "GROUP BY storno_din_id", (ids,))
    stornat = {(r["storno_din_id"] if isinstance(r, dict) else r[0]): _D(str(r["coalesce"] if isinstance(r, dict) else r[1]))
               for r in cur.fetchall()}
    from core import repo_facturi as _rf_st   # [416] toleranța stornării, lângă SQL_STORNARI
    for f in facturi:
        if f["id"] not in ids:
            continue
        # [lotul 12, 468, clasa „lei comparați cu euro”] totalul în LEI: `total_lei` (scris la creare) când factura îl are — lista „Istoric
        # facturi” nu citește `tva_lei` / `curs_bnr`, iar `antet_lei` cădea atunci pe totalul în valută, comparat cu încasările în lei
        # (o factură de 1.000 EUR cu 2.000 lei încasați ieșea „încasată”)
        try:
            total = _D(str(f["total_lei"])) if f.get("total_lei") is not None else _sl.antet_lei(f)[0]
            tva_lei = _D(str(f["tva_lei"])) if f.get("tva_lei") is not None else _sl.antet_lei(f)[1]
        except _sl.LipsaCurs:
            total, tva_lei = _D(str(f.get("total") or 0)), _D(str(f.get("tva") or 0))
        # [lotul 13, 546] factura primită cu taxare inversă: TVA-ul de pe antet e al beneficiarului (CF art.331 alin.(3)), nu se plătește
        # furnizorului — totalul de plată e baza (`facturi.total_de_plata`, aceeași definiție peste tot)
        total = _fc_tp.total_de_plata(f, total, tva_lei)
        st = stornat.get(f["id"], _D(0))
        if st and total + st <= _D(str(_rf_st.TOLERANTA_STORNATA)):
            f["stare_incasare"] = {"stare": "stornata", "incasat": "%.2f" % incasat.get(f["id"], _D(0)), "total": "%.2f" % total,
                                   "stornat": "%.2f" % -st}
            continue
        total = total + st
        inc = incasat.get(f["id"], _D(0))
        stare = ("incasata" if (f.get("platita_la") or (total > 0 and inc >= total - _D("0.005")))
                 else ("partial" if inc > 0 else "neincasata"))
        f["stare_incasare"] = {"stare": stare, "incasat": "%.2f" % (total if (f.get("platita_la") and inc < total) else inc),
                               "total": "%.2f" % total, **({"stornat": "%.2f" % -st} if st else {})}


def _cu_stare_contare(cur, facturi):
    """[05.10.2026, comanda Costin pct.7] Starea spune adevărul: `nota_contare` (id, stare, dată) și `contabilizata` = nota de
    contare VALIDATĂ — nu „există orice notă cu cheia” (ciorna și încasarea treceau drept contabilizare)."""
    from core import contare_facturi as _cf
    st = _cf.stare_contare(cur, "", [f["id"] for f in facturi])
    for f in facturi:
        f["nota_contare"] = st.get(f["id"])
        f["contabilizata"] = bool(f["nota_contare"] and f["nota_contare"]["status"] == "validata")


# ============================================================
#  DETALII — DB
# ============================================================
def detalii_factura(conn, factura_id):
    """O factură cu liniile ei, sau None."""
    import psycopg2.extras as _E
    from core import repo_facturi as _rf   # [417] SQL_STORNO_DIN
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, client_id, numar, serie, data_emitere, data_scadenta, total, tva, "   # [05.10.2026] seria pe PDF (art.319 lit.a)
            "status, moneda, directie, tert_nume, tert_cui, tert_adresa, "
            "tert_tara, tip_operatiune, furnizor_tva_incasare, tert_oras, tert_judet, "   # [306] adresa clientului străin
            "taxare_inversa, categorie_331, axa_ic, tert_platitor_tva, data_faptului_generator, "  # [A4] clasificarea storno-ului
            "curs_bnr, tva_lei, total_lei, data_curs, curs_sursa, storno_din_id, tip, transformat_in_id, "
            "link_plata, platita_la, plata_confirmata_de, "  # [R43] marca de simulare
            "bon_fiscal_nr, bon_fiscal_data, "   # [decizia A 02.10] factura emisă pe baza bonului fiscal
            "(SELECT numar FROM facturi f2 WHERE f2.id = facturi.transformat_in_id) AS transformat_in_numar, "
            "(SELECT serie FROM facturi f2 WHERE f2.id = facturi.transformat_in_id) AS transformat_in_serie, "   # [lotul 12, C196] seria separat, ca în Istoric
            + _rf.SQL_STORNO_DIN.format(s="", a="facturi") +   # [417] factura stornată, pentru trimiterea de pe PDF
            " FROM facturi WHERE id = %s",
            (factura_id,))
        f = cur.fetchone()
        if not f:
            return None
        f = dict(f)
        cur.execute(
            "SELECT id, descriere, um, cantitate, pret_unitar, cota_tva, cont_venit, categorie_tva, "
            "articol_id, "   # [C63] articolul de stoc al liniei: proforma / avizul îl trec pe factură, cu „Pleacă marfa acum?”
            "valoare_neta "   # [lotul 11, C82] BT-131 de pe factura importată: valoarea liniei pe ecran și pe PDF (NULL = cantitate × preț)
            "FROM factura_linii WHERE factura_id = %s ORDER BY id", (factura_id,))
        f["linii"] = [dict(r) for r in cur.fetchall()]
        _cu_total_de_plata([f])   # [lotul 13, 546]
        # [deficiența 306] detaliul arată categoria de TVA a liniei cu 0% (eticheta ei), nu numai „0%”; codul și adresa clientului ca pe PDF
        from core import categorii_tva as _ct, factura_pdf as _fp
        for l in f["linii"]:
            l["categorie_tva_eticheta"] = (_ct.CATEGORII.get(l.get("categorie_tva")) or {}).get("eticheta")
        f["tert_cod_eticheta"], f["tert_cod"] = _fp.cod_fiscal_pe_factura(f.get("tert_cui"), f.get("tert_platitor_tva"), f.get("tert_tara"))
        f["tert_adresa_completa"] = _fp.adresa_tert(f.get("tert_adresa"), f.get("tert_oras"), f.get("tert_judet"), f.get("tert_tara"))
        _cu_stare_contare(cur, [f])
        _cu_stare_incasare(cur, [f])
        _cu_stare_spv(cur, [f])   # [lotul 6 pct.5b, 275]
        # [lotul 10, comanda 10.2 pct.7e, deficiența 417] „pe ecranul de detaliu al facturii de stornare nu apare trimiterea la factura
        # inițială (pe PDF apare)”: aceeași mențiune ca pe PDF (`facturi.mentiune_storno`, CF art.330 alin.(1) lit.b), una singură
        from core import facturi as _fc
        f["mentiune_storno"] = _fc.mentiune_storno(f)
        # [lotul 10, deficiența 428] factura emisă în sistemul TVA la încasare (regimul la DATA ei) poartă mențiunea CF art.319 alin.(20)
        # lit.p) pe PDF; aceeași definiție ca pe nota de contare (4428) și în XML-ul e-Factura
        from core import tva_incasare as _tvi
        f["tva_la_incasare"] = f.get("directie") == "emisa" and _tvi.regim(cur, None, f) == _tvi.REGIM_INCASARE
        # [lotul 10, 10.2 pct.7e — clasa lui 417: „pe PDF apare”, pe detaliu nu] celelalte mențiuni de pe PDF, din aceleași funcții:
        # „TVA la încasare” (CF art.319 alin.(20) lit.p) și „conform bon fiscal nr./data” (HG 1/2016 pct.97 alin.(1))
        f["mentiuni"] = [m for m in ((_tvi.MENTIUNE if f["tva_la_incasare"] else None),
                                     (_fc.mentiune_bon(f) if _fc.e_din_bon_fiscal(f) else None)) if m]
        if f.get("directie") == "emisa":
            # [lotul 12, C156; clasa 417] și mențiunile TVA de pe PDF (`factura_pdf.mentiuni_tva`: scutirea neplătitorului, motivele
            # categoriilor, „taxare inversă”), iar la prestarea IC a neplătitorului înregistrat art.317 codul RO de pe PDF (`cod_emitent`)
            cur.execute("SELECT platitor_tva, cui FROM firma_profil WHERE id = 1")
            _pr = cur.fetchone()
            _pr = {"platitor_tva": _pr["platitor_tva"], "cui": _pr["cui"]} if _pr else {}
            _art317 = (["Codul de TVA al firmei pe această factură (art.317): %s" % _fp.cod_emitent(_pr, f["linii"])[1]]
                       if _ct.cod_tva_art317(_pr.get("platitor_tva"), f["linii"]) else [])
            f["mentiuni"] = _art317 + _fp.mentiuni_tva(False if _pr.get("platitor_tva") is False else None, f["linii"],
                                                       f.get("tert_tara")) + f["mentiuni"]
        # [419] ce a plecat din magazie cu factura (ieșirile vii): stornarea întreabă dacă se întoarce
        from core import pdf_util as _pdfu, stocuri_cv_api as _cv
        f["iesiri_stoc"] = [{"articol": m["denumire"], "cantitate": str(m["cantitate"]), "cantitate_text": _pdfu.cantitate(m["cantitate"], m["um"]),
                             "valoare": str(m["valoare"])} for m in _cv.iesiri_facturii(cur, None, factura_id)] \
            if f.get("directie") == "emisa" and not f.get("storno_din_id") else []
    return f


# ============================================================
#  ȘTERGERE — DB (liniile cad prin CASCADE)
# ============================================================
def _redeschide_luna(conn, data_emitere):
    """[cap.23, 21.08.2026] Orice modificare a evidenței facturilor DE-CONFIRMĂ luna. O închidere care
    supraviețuiește unei modificări ar afirma „evidența lunii e completă" despre alte date decât cele
    pe care cineva le-a văzut când a închis — exact „verde e o afirmație". Simetric cu `pontaj.seteaza`.
    Conexiunea e pe schema tenantului (search_path), ca restul modulului."""
    if not data_emitere:
        return
    d = data_emitere
    if isinstance(d, str):
        import datetime as _dt
        try:
            d = _dt.date.fromisoformat(d[:10])
        except ValueError:
            return
    from core import perioada as _per
    _per.deconfirma(conn, "", d.year, d.month, "facturi")


def _eticheta_factura(conn, factura_id):
    """[258] „Factură FCT12 din 05.10.2026” — cum o vede omul (`eticheta_nota.factura`), nu id-ul intern."""
    with conn.cursor() as cur:
        return _et.factura(cur, "", factura_id)


def _luna_facturii(conn, factura_id):
    with conn.cursor() as cur:
        cur.execute("SELECT data_emitere FROM facturi WHERE id = %s", (factura_id,))
        r = cur.fetchone()
    return r[0] if r else None


def refuza_sold_preluat(tip):
    """[lotul 12, deficiența 252] PUNCTUL UNIC al refuzului: o acțiune de document fiscal (stornare, ștergere, PDF, e-mail, SPV, contare,
    transformare) pe o factură deschisă preluată -> ValueError cu `nomenclator_status_factura.MESAJ_SOLD_PRELUAT`."""
    from core import nomenclator_status_factura as _nsf
    if _nsf.e_sold_preluat(tip):
        e = ValueError(_nsf.MESAJ_SOLD_PRELUAT)
        e.cod = "SOLD_PRELUAT"
        raise e


def sterge_factura(conn, factura_id):
    """Șterge factura (liniile cad automat prin ON DELETE CASCADE).

    [EEE2] **REFUZĂ MOTIVAT dacă factura are notă de contare.** Până azi ștergerea nu verifica nimic,
    iar cheia străină `inregistrari_factura_id_fkey` n-are `ON DELETE` — deci trecea *de cele mai
    multe ori* doar fiindcă majoritatea facturilor n-aveau notă (28 din 41, măsurat). Cu note
    automate, fiecare factură are una, iar ștergerea ar fi început să pice cu o eroare brută de bază
    în loc de un refuz explicat. **Automatizarea nu creează problema — o face vizibilă la fiecare
    ștergere.**

    O notă de **plată** nu blochează ștergerea: nu e evidența facturii, e a încasării. Aceeași
    distincție ca la idempotență, din același loc (`contare_facturi.contare_existenta`).

    Varianta aleasă de Costin (29.08.2026) e (i) — refuz + trimitere la storno. Respinse: (ii)
    ștergerea notei odată cu factura — *o notă ștearsă e o gaură în evidență, nu o corecție* —, și
    (iii) ștergerea condiționată de starea ciornă, care ar face comportamentul să depindă de un pas
    de validare pe care omul nu-l are în minte când apasă „șterge"."""
    from core import contare_facturi as _cf, nomenclator_status_factura as _nsf_sp
    with _cf.cursor_dict(conn) as cur:
        # [lotul 12, 252] factura deschisă preluată se schimbă numai prin reimportul soldurilor pe parteneri (totalul ei e al partenerului)
        cur.execute("SELECT tip FROM facturi WHERE id = %s", (factura_id,))
        _t = cur.fetchone()
        if _t and _nsf_sp.e_sold_preluat(_t["tip"]):
            raise _cf.RefuzContare("SOLD_PRELUAT", _nsf_sp.MESAJ_SOLD_PRELUAT)
        # [05.10.2026] Aceeași clasă ca nota legată: `efactura_trimiteri` / `efactura_primite` țin factura printr-o cheie
        # fără `ON DELETE`, deci ștergerea cădea cu o eroare brută de bază. Factura legată de SPV tot nu se șterge — istoricul
        # cu ANAF rămâne —, dar refuzul e numit și spune ieșirea.
        cur.execute("SELECT id, stare FROM efactura_trimiteri WHERE factura_id = %s ORDER BY id DESC LIMIT 1", (factura_id,))
        trim = cur.fetchone()
        cur.execute("SELECT id_mesaj_anaf FROM efactura_primite WHERE factura_id = %s LIMIT 1", (factura_id,))
        prim = cur.fetchone()
        n = _cf.contare_existenta(cur, "", factura_id)
        legate = _cf.note_cu_cheia(cur, "", factura_id)
        # [258] notele se numesc în refuz cum le arată Registrul jurnal, nu prin id-ul intern
        et_n = _et.nota(cur, "", n["id"]) if n else None
        et_legata = _et.nota(cur, "", legate[0]["id"]) if legate else None
        cur.execute("SELECT numar FROM nir WHERE factura_id = %s LIMIT 1", (factura_id,))
        nir_legat = cur.fetchone()
        from core import compensari_api as _cz
        compensata = _cz.ale_facturii(cur, "", factura_id)
        cur.execute("SELECT directie, COALESCE(tip, 'factura') AS tip, serie, numar FROM facturi WHERE id = %s", (factura_id,))
        _fp_ = cur.fetchone()
        # [lotul 13, deficiența 547] factura PRIMITĂ introdusă greșit, cu notele ei (cele ale facturii: contarea, nota taxării inverse)
        # încă ciornă — nimic din ea n-a intrat în evidență, deci se șterge cu notele ei; o notă validată, o plată, stocul, SPV-ul o opresc
        primita_ciorna = bool(_fp_ and _fp_["directie"] == "primita" and _fp_["tip"] == "factura" and legate
                              and all(x["status"] == "ciorna" and x.get("sursa") == "facturi" for x in legate))
        stoc_primita = None
        if primita_ciorna:
            cur.execute("SELECT count(*) AS n FROM miscari_stoc WHERE factura_id = %s", (factura_id,))
            stoc_primita = cur.fetchone()["n"]
    if compensata:
        # [lotul 10, 428] aceeași clasă ca NIR-ul legat: `compensari` ține factura printr-o cheie fără `ON DELETE` — refuzul o numește
        raise _cf.RefuzContare(
            "COMPENSATA",
            "Factura e stinsă (total sau parțial) prin %s și nu se șterge. Ștergi întâi compensarea — nota ei ciornă, din Registrul "
            "jurnal — sau corectezi prin storno." % (compensata[0][2] or "ordinul de compensare"),
            detalii={"document": compensata[0][2], "iesire": "storno"})
    if nir_legat:
        # [decizii 07.10 pct.2] NIR-ul legat își ia costul din factură (scrie numai adaosul și TVA neexigibilă): fără factură,
        # 371 ar rămâne cu adaosul unei mărfi fără cost. Cheia `nir_factura_fk` n-are `ON DELETE` — refuzul o numește.
        raise _cf.RefuzContare(
            "LEGATA_DE_NIR",
            "Factura e legată de NIR-ul %s, care își ia costul din ea, și nu se șterge. Corecția se face prin storno — un al "
            "doilea document." % nir_legat["numar"], detalii={"nir_numar": nir_legat["numar"], "iesire": "storno"})
    if trim:
        raise _cf.RefuzContare(
            "LEGATA_DE_SPV",
            "Factura are o trimitere în e-Factura (stare „%s”) și nu se mai șterge: istoricul trimiterii către ANAF se "
            "păstrează. Corecția se face prin storno — un al doilea document." % trim["stare"],
            detalii={"efactura_trimitere_id": trim["id"], "stare": trim["stare"], "iesire": "storno"})
    if prim:
        raise _cf.RefuzContare(
            "LEGATA_DE_SPV",
            "Factura a venit din SPV (mesajul ANAF %s) și nu se șterge: e documentul furnizorului, păstrat așa cum a fost "
            "primit." % prim["id_mesaj_anaf"],
            detalii={"id_mesaj_anaf": prim["id_mesaj_anaf"], "iesire": "fara_stergere"})
    if primita_ciorna:
        return _sterge_primita_cu_notele_ciorna(conn, factura_id, legate, stoc_primita, _fp_)
    if not n and legate:
        # GĂSIT DE PROPRIA GARDĂ, la prima rulare, și nu era în comandă: cheia străină blochează
        # ștergerea pentru ORICE notă legată, nu doar pentru o contare. O notă de PLATĂ n-ar trebui
        # să apere factura de ștergere — dar `inregistrari_factura_id_fkey` n-are `ON DELETE`, deci
        # o blochează oricum, cu o eroare brută de bază. EEE2 cere ca ștergerea să nu mai pice așa;
        # refuzul acoperă și clasa asta, cu ALT cod și ALT motiv, fiindcă **ieșirea e alta**:
        # aici dezlegi nota, nu stornezi factura.
        # Mesajul NUMEȘTE starea notei, fiindcă de ea depinde dacă ieșirea există. O ciornă se
        # poate șterge (patru-ochi n-a fost consumat); o notă VALIDATĂ nu — `jurnal_api.sterge`
        # refuză orice notă care nu e ciornă, iar rută de dezlegare nu există. Pe portofoliul de
        # azi, toate cele 3 facturi din clasa asta au nota VALIDATĂ, deci nu se pot șterge deloc.
        # Restanța e deschisă (R90); mesajul nu are voie s-o ascundă promițând o ieșire inexistentă.
        # [R90, varianta (a)] Ieșirea EXISTĂ de azi și se numește: nota se dezleagă, explicit, prin
        # actul ei. Până azi mesajul trimitea într-un zid pentru o notă validată — `jurnal_api.sterge`
        # refuză orice notă care nu e ciornă, iar dezlegare nu era. *Un refuz care numește o ieșire
        # inexistentă e mai rău decât unul care spune «nu se poate».*
        _n0 = legate[0]
        raise _cf.RefuzContare(
            "ARE_NOTA_LEGATA",
            "Factura are o notă legată care nu e de contare (nota %s, %s, %s) — o plată sau o încasare. "
            "Dezleag-o întâi: potrivirea rămâne consemnată pe linia de extras, iar factura redevine "
            "neîncasată." % (et_legata, _n0.get("sursa") or "fără sursă", _n0.get("status") or "?"),
            detalii={"inregistrare_id": _n0["id"], "status_nota": _n0.get("status"),
                     "iesire": "dezleaga_nota"})
    if n:
        raise _cf.RefuzContare(
            "ARE_NOTA_DE_CONTARE",
            "Factura are notă contabilă (nota %s) și nu se mai șterge: o notă ștearsă lasă o gaură în "
            "evidență. Corecția unei facturi contabilizate se face prin STORNO — un al doilea "
            "document, care își produce propria notă." % et_n,
            detalii={"inregistrare_id": n["id"], "iesire": "storno"})
    # [Retestul plasei 09.10.2026, regula a (R6) — CF art.330 alin.(1)] o factură EMISĂ nu se șterge, nici fără notă: se corectează prin
    # stornare. Baza o refuză oricum (`trg_regula_factura_emisa`); aici refuzul e numit, cu ieșirea lui, din aceeași sursă a stărilor.
    from core import nomenclator_status_factura as _nsf
    from core.pdf_util import serie_nr as _pu_serie_nr
    with conn.cursor() as cur:
        cur.execute("SELECT directie, COALESCE(tip, %s), COALESCE(status, %s), serie, numar FROM facturi WHERE id = %s",
                    (_nsf.TIP_IMPLICIT, _nsf.IMPLICITA, factura_id))
        _f = cur.fetchone()
    if _f and _f[0] == "emisa" and _f[1] == _nsf.TIP_IMPLICIT and _f[2] not in _nsf.STERGIBILE:
        raise _cf.RefuzContare(
            "FACTURA_EMISA",
            "Factura %s e emisă, deci nu se șterge: se corectează prin factură de stornare (CF art.330 alin.(1))."
            % _pu_serie_nr(_f[3], _f[4]),   # [lotul 11, 443] „F1A nr. 3”, nu „F1AF1A3” (seria lipită peste numărul care o poartă)
            detalii={"iesire": "storno"})
    _d = _luna_facturii(conn, factura_id)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM facturi WHERE id = %s", (factura_id,))
        sterse = cur.rowcount
    if sterse:
        _redeschide_luna(conn, _d)
    return {"ok": sterse > 0}


#: [lotul 13, 547] refuzul ștergerii facturii primite care a adus marfă în stoc (fișa de magazie are deja intrarea)
MESAJ_PRIMITA_CU_STOC = ("Factura %s a adus marfă în stoc (%s în fișa de magazie) și nu se șterge de aici: fișa ar rămâne cu marfa unei "
                         "facturi care nu mai există. Respinge nota facturii din „De validat” (stocul ei se stornează) sau corectează "
                         "factura prin stornare.")


def _sterge_primita_cu_notele_ciorna(conn, factura_id, note, stoc, f):
    """[lotul 13, deficiența 547 — „O factură primită introdusă greșit, cu nota încă nevalidată, nu are niciun buton de anulare sau
    ștergere (nici nota derivată nu se poate șterge)”] Ștergerea facturii PRIMITE ale cărei note (cele scrise de factură, sursa
    `facturi`) sunt toate ciornă: notele (cu liniile lor), operațiunea D301 legată (achiziția intracomunitară, `d301_operatiuni.factura_id`)
    și factura, în aceeași tranzacție. Ciorna nu e evidență (o notă intră în evidență abia validată), deci nu lasă nicio gaură; o notă
    validată, o plată, NIR-ul, SPV-ul și compensarea au refuzurile lor, mai sus. Nota din coada de validare și ciorna altui utilizator se
    refuză numit (`coada_api.nota_la_validare`, regula din bază `DREPT_CIORNA`), nu cu o eroare de bază.
    Temei: OMFP 2634/2015 anexa 1 pct.58 lit.c — „fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui
    document”; documentul introdus greșit nu e al firmei, iar ciorna lui nu a fost înregistrată în contabilitate."""
    from core import contare_facturi as _cf, coada_api as _coada, jurnal_api as _j
    from core.common import cate
    from core.pdf_util import serie_nr as _sn
    eticheta = _sn(f["serie"], f["numar"]) if f else str(factura_id)
    if stoc:
        raise _cf.RefuzContare("PRIMITA_CU_STOC", MESAJ_PRIMITA_CU_STOC % (eticheta, cate(stoc, "mișcare", "mișcări")),
                               detalii={"iesire": "respinge_sau_storno"})
    ids = [x["id"] for x in note]
    with conn.cursor() as cur:
        cur.execute("SELECT current_schema()")
        schema = cur.fetchone()[0]
        for nid in ids:
            if _coada.nota_la_validare(cur, schema, nid):
                raise _cf.RefuzContare(_coada.COD_NOTA_LA_VALIDARE, _coada.mesaj_nota_la_validare(cur, schema, nid))
    _d = _luna_facturii(conn, factura_id)
    try:
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT sterge_primita")
            cur.execute("DELETE FROM d301_operatiuni WHERE factura_id = %s", (factura_id,))
            cur.execute("DELETE FROM inregistrari WHERE id = ANY(%s) AND status = 'ciorna'", (ids,))
            cur.execute("DELETE FROM facturi WHERE id = %s", (factura_id,))
            sterse = cur.rowcount
            cur.execute("RELEASE SAVEPOINT sterge_primita")
    except Exception as e:   # noqa: BLE001 — numai refuzurile din bază se traduc; orice altceva urcă
        motiv = _j._motiv_din_baza(e)
        if motiv is None:
            raise
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT sterge_primita")
        raise _cf.RefuzContare(_j._cod_din_baza(e) or "REFUZ_BAZA", motiv)
    if sterse:
        _redeschide_luna(conn, _d)
    return {"ok": sterse > 0, "note_sterse": len(ids)}


# ============================================================
#  EMITERE — numerotare, emitere, storno  [p103_emitere]
# ============================================================
def numerotare(conn):
    """Citeste serie + urmatorul numar de factura din firma_profil."""
    with conn.cursor() as cur:
        cur.execute("SELECT serie_factura, urmator_numar_factura, numerotare_configurata FROM firma_profil LIMIT 1")
        row = cur.fetchone()
    serie = row[0] if row else None
    urmator = int(row[1]) if row and row[1] is not None else 1
    configurata = bool(row[2]) if row and len(row) > 2 and row[2] is not None else False
    return {"serie": serie, "urmator_numar": urmator, "configurata": configurata}  # numerotare_configurata_v1


def forma_propusa_firma(conn, tenant_id):
    """(forma, sursa) propusă pentru firma fără formă juridică: din denumirea de pe profil, cea din portofoliu și cea primită
    de la ANAF (`public.tenants.nume_anaf`) — numai dacă toate spun același lucru."""
    from core import capital_social as _cs
    with conn.cursor() as cur:
        cur.execute("SELECT nume FROM firma_profil WHERE id = 1")
        p = cur.fetchone()
        cur.execute("SELECT nume, nume_anaf FROM public.tenants WHERE id = %s", (tenant_id,))
        t = cur.fetchone() or (None, None)
    return _cs.forma_propusa(None, *(x for x in ((p or (None,))[0], t[0], t[1]) if x))


def pregatire_emitere(conn, tenant_id, la_data):
    """[comanda Costin 05.10.2026 pct.2–3] Ce trebuie știut LA DESCHIDEREA formularului de emitere:
    `lipsuri_firma` (din Date firmă, aceeași regulă ca refuzul de la emitere: `capital_social.lipsa`), `forma_propusa` când forma
    lipsește, și `cote_permise` (procente, cotele în vigoare la data facturii — aceeași sursă ca validarea de la emitere).
    `la_data` e OBLIGATORIE: e data emiterii din formular; o cotă citită „azi” pentru o factură datată altfel ar fi o listă
    validă și falsă (interdicția 3, `core/test_data_curenta.py`)."""
    from core import capital_social as _cs
    with conn.cursor() as cur:
        cur.execute("SELECT tip_firma, forma_juridica, capital_subscris, capital_varsat FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    profil = dict(zip(("tip_firma", "forma_juridica", "capital_subscris", "capital_varsat"), r)) if r else {}
    lipsuri = _cs.lipsa(profil) if profil else []
    forma, sursa = (None, None)
    if lipsuri and not profil.get("forma_juridica"):
        forma, sursa = forma_propusa_firma(conn, tenant_id)
    permise, _t = _cote_tva_in_vigoare(la_data)
    from core import capital_social as _csl
    return {"lipsuri_firma": lipsuri, "forma_propusa": forma, "forma_propusa_sursa": sursa,
            "camp_ecran": _csl.CAMP_LIPSA.get((lipsuri or [None])[0]),   # [retest 08.10, completarea pct.2] butonul, la câmp
            "serie_lipsa": not serie_facturi(conn),   # [06.10.2026 §6.1] nu blochează: refuzul o cere și o setează pe loc
            # [lotul 07.10 pct.18] scadența PROPUSĂ pe formular (editabilă): zilele și temeiul vin de aici, nu din ecran
            "scadenta_zile": SCADENTA_PROPUSA[0], "scadenta_temei": str(SCADENTA_PROPUSA[1]),
            "mesaj_lipsuri": _cs.mesaj_la_deschidere(lipsuri, forma, sursa),
            "cote_permise": sorted({int(c) if int(c) == c else float(c) for c in permise}, reverse=True) if permise else None,
            # [274b] categoriile de TVA ale unei linii cu 0% (core/categorii_tva; goală la neplătitor: „O” e automat) și, pentru
            # taxarea inversă, categoriile produsului (codurile D394, aceeași listă ca la facturile primite, 273c)
            "categorii_tva": _categorii_formular(conn), "categorii_331": _categorii_331()}


def _categorii_formular(conn):
    from core import categorii_tva as _ct
    with conn.cursor() as cur:
        cur.execute("SELECT platitor_tva FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    return _ct.pentru_formular(None if r is None else r[0])


def _categorii_331():
    """[lotul 11, 449, patch B/P4] Bunurile cu taxare inversă pentru formularul de emitere: [{cod, eticheta}] (eticheta din nomenclator)."""
    from core import produse_api as _pa
    return [{"cod": c["cod"], "eticheta": c["eticheta"]} for c in _pa.categorii_331_pentru_ecran()]


#: [lotul 07.10 pct.18, comanda Costin 06.10.2026] „Scadența facturii e goală implicit; aplicația propune o scadență editabilă.”
#: Legea 72/2013 art.3 alin.(3): „Dacă termenul de plată nu a fost prevăzut în contract, dobânda penalizatoare curge de la
#: următoarele termene: a) după 30 de zile calendaristice de la data primirii de către debitor a facturii …” (anaf_surse/
#: legea_72_2013.html). INTERPRETARE CU TEMEI: data primirii nu se cunoaște la emitere; se propune de la data EMITERII (factura
#: pleacă în aceeași zi prin e-Factura). E o propunere pe formular — contractul părților primează, iar omul o schimbă.
#: Alternativa respinsă: 60 de zile (art.5 alin.(1) — plafonul termenului CONTRACTUAL, nu termenul fără contract).
SCADENTA_PROPUSA = (30, Temei("Legea", 72, 2013, art="3", alin="3", lit="a", nivel_sursa="MO", de_cine="Code",
                              verificat_la="2026-10-06", url="anaf_surse/legea_72_2013.html",
                              text_citat="după 30 de zile calendaristice de la data primirii de către debitor a facturii"))


#: [06.10.2026, comanda Costin §6.1] CF art.319 alin.(20) lit.a): factura poartă „numărul de ordine, în baza uneia sau a mai
#: multor serii, care identifică factura în mod unic”. Refuzul e STRUCTURAT (cod + temei + câmp): ecranul de emitere oferă
#: setarea seriei pe loc și emiterea continuă cu factura păstrată. Facturile deja emise nu se ating.
COD_SERIE_LIPSA = "SERIE_LIPSA"
TEMEI_SERIE = "CF art.319 alin.(20) lit.a)"
#: [lotul 10, C74] stornarea anulează valorile facturii corectate — „se emite o factură cu valorile cu semnul minus [...] în care se
#: înscriu numărul și data facturii corectate”: o factură stornată integral nu mai are ce storna, iar o stornare nu se stornează
TEMEI_STORNARE = "CF art.330 alin.(1) lit.b)"
MESAJ_SERIE_LIPSA = ("Factura nu s-a emis: firma n-are serie de facturare. Legea cere ca numărul facturii să fie dat „în baza "
                     "uneia sau a mai multor serii” (CF art.319 alin.(20) lit.a). Stabilește seria și emiterea continuă — "
                     "factura rămâne așa cum ai scris-o; facturile emise deja nu se modifică.")


def verifica_marfa_si_metoda(conn, linii, pleaca_marfa):
    """[06.10.2026, comanda Costin §6.3] Marfa de pe factură (cont de venit 707 sau articol de stoc) se descarcă O SINGURĂ dată,
    după metoda firmei (`core.metoda_stoc`): la cantitativ-valoric pe articol — deci linia de marfă fără articol se refuză pe
    câmp; la global-valoric prin descărcarea lunară — deci ieșirea pe articol de pe factură se refuză; nedeclarată -> refuz
    numit, cu trimitere la Date firmă. Factura din bon (marfa a ieșit cu bonul) și „Nu, doar factură” nu trec pe aici."""
    from core import metoda_stoc as _ms
    marfa = [i for i, l in enumerate(linii) if str(l.get("cont_venit") or "").startswith("707")]
    pe_articol = [i for i, l in enumerate(linii) if l.get("articol_id")]
    if not marfa and not pe_articol:
        return
    with conn.cursor() as cur:
        m = _ms.citeste(cur)
    if m is None:
        raise _ms.refuz(_ms.COD_NEDECLARATA, "Factura nu s-a emis: are marfă, iar metoda de stoc a firmei nu e declarată. "
                        "Declar-o în Date firmă (global-valoric sau cantitativ-valoric) — de ea depinde cum se descarcă "
                        "marfa, o singură dată; factura rămâne așa cum ai scris-o.")
    if m == _ms.CV:
        lipsa = [i for i in marfa if not linii[i].get("articol_id")]
        if lipsa:
            raise LiniiIncomplete([{"camp": "em-l%d-articol" % i,
                                    "eticheta": "Linia %d: alege articolul din stoc (marfă, firma ține stocul cantitativ-valoric)" % (i + 1)}
                                   for i in lipsa])
    elif pe_articol and pleaca_marfa is True:
        raise _ms.refuz(_ms.COD_ALTA, "Factura nu s-a emis: firma ține stocul global-valoric — marfa se descarcă lunar, din "
                        "toate vânzările, nu pe articol. Scoate articolul de pe linie (sau alege „Nu, doar factură”).")


def serie_facturi(conn):
    """Seria de facturare a firmei, sau „” dacă lipsește."""
    with conn.cursor() as cur:
        cur.execute("SELECT serie_factura FROM firma_profil LIMIT 1")
        r = cur.fetchone()
    return str((r[0] if r else "") or "").strip()


def cere_serie(conn):
    """Refuzul §6.1, ÎNAINTE de rezervarea numărului (refuzul nu consumă un număr)."""
    if not serie_facturi(conn):
        e = ValueError(MESAJ_SERIE_LIPSA)
        e.cod, e.temei, e.camp = COD_SERIE_LIPSA, TEMEI_SERIE, "serie"
        raise e


def detaliu_serie_lipsa(e):
    """Corpul refuzului structurat (422): ecranul de emitere citește `cod` și deschide setarea seriei peste factură."""
    from core import afirmatii as _af
    return _af.afirmatie("neconformitate", "factura", str(e), unde="Numerotare facturi", regula=e.temei,
                         cod=e.cod, mesaj=str(e), temei=e.temei, camp=e.camp, ecran="numerotare")


def _rezerva_numar(conn, tip="factura"):
    """[C1, 17.09.2026] Rezervă ATOMIC următorul număr al documentului: `UPDATE ... = +1 RETURNING`
    valoarea DE DINAINTE. UPDATE-ul blochează rândul `firma_profil`, deci două cereri concurente NU mai
    pot citi același număr. Până azi `numerotare` citea fără `FOR UPDATE`, iar incrementul venea într-un
    UPDATE de mai târziu — între citire și scriere, douăsprezece cereri simultane primeau același număr
    (măsurat de audit: numărul 6 pe 3 facturi). Rollback-ul tranzacției anulează și rezervarea, deci un
    eșec ulterior (curs, cotă) nu consumă numărul. Întoarce `(serie, numar_int)`."""
    col = {"factura": "urmator_numar_factura", "proforma": "urmator_numar_proforma",
           "aviz": "urmator_numar_aviz"}[tip]
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET %s = COALESCE(%s, 1) + 1 "
                    "RETURNING serie_factura, %s - 1" % (col, col, col))
        row = cur.fetchone() or (None, 1)
    serie = row[0] if tip == "factura" else ("PF" if tip == "proforma" else "AV")
    numar_int = int(row[1]) if row[1] is not None else 1
    return serie, numar_int


def urmatorul_in_serie(conn, serie):
    """[lotul 13, 542] Primul număr liber al seriei `serie` pe facturile emise: 1 pentru o serie nefolosită, altfel ultimul număr emis în ea
    + 1 (numărul facturii e seria lipită de numărul de ordine: „F2T3” -> 3)."""
    with conn.cursor() as cur:
        cur.execute("SELECT numar FROM facturi WHERE directie = 'emisa' AND COALESCE(tip, 'factura') = 'factura' AND serie = %s", (serie,))
        nr = [str(r[0] if not isinstance(r, dict) else r["numar"]) for r in cur.fetchall()]
    cifre = [int(x[len(serie):]) for x in nr if x.startswith(serie) and x[len(serie):].isdigit()]
    return (max(cifre) + 1) if cifre else 1


def seteaza_numerotare(conn, serie=None, numar_start=None):
    """Configureaza seria + numarul de start (continuitate cu istoricul).
    Se apeleaza o data; dupa, numarul se auto-incrementeaza la emitere."""
    # [probare invalid lot 2, 03.09.2026] Trei valori treceau cu `200 {"ok": true}`:
    # `serie="   "` ștergea seria firmei în tăcere (`strip() or None`), `numar_start=-5` intra
    # ca atare, iar `numar_start=100` dădea contorul înapoi peste numere deja emise — următoarea
    # factură ar fi purtat un număr existent. Probat: după el, emiterea prin API a produs
    # documentul „100", fără serie.
    # [440, comanda Costin 11.1 pct.16] seria și numărul se judecă AMÂNDOUĂ (`ErorileFormularului`), nu la prima greșeală: refuzul
    # are `erori_campuri` cu numele din cerere (`serie`, `numar_start`), iar `mesaj` le spune pe toate
    from core.erori import ErorileFormularului as _Erori
    er = _Erori("Numerotarea nu s-a salvat")
    with conn.cursor() as _cur:
        _cur.execute("SELECT serie_factura, urmator_numar_factura FROM firma_profil LIMIT 1")
        _acum = _cur.fetchone() or (None, None)
    seturi, val = [], []
    # [lotul 13, deficiența 542 — „Seria F2T stabilită la prima factură a pornit de la nr. 2 (contorul vechi), deci F2T1 lipsește și seria are
    # o gaură. Seria nouă pornește de la 1 sau de la numărul ales de contabil.”] Contorul e al SERIEI: o serie nouă (alta decât cea de acum)
    # pornește de la primul număr liber din ea (1, sau după ultima factură emisă vreodată în ea), nu de la contorul seriei vechi. CF art.319
    # alin.(20) lit.a): factura cuprinde „numărul de ordine, în baza uneia sau mai multor serii, care identifică în mod unic factura”.
    _serie_noua = str(serie).strip() if serie is not None and str(serie).strip() else None
    _schimba_seria = _serie_noua is not None and _serie_noua != str(_acum[0] or "").strip()
    _urm = urmatorul_in_serie(conn, _serie_noua) if _schimba_seria else _acum[1]
    if serie is not None:
        if not str(serie).strip():
            er.camp("serie", "Seria e goală (numai spații). Nu se poate ghici dacă "
                             "ai vrut s-o ștergi sau ai greșit tastarea, iar seria "
                             "firmei e pe documentele deja emise.")
        else:
            seturi.append("serie_factura = %s"); val.append(str(serie).strip())
            if _schimba_seria and numar_start is None:
                seturi.append("urmator_numar_factura = %s"); val.append(_urm)
    if numar_start is not None:
        try:
            _n = int(numar_start)
        except (TypeError, ValueError):
            _n = None
            er.camp("numar_start", "Numărul de start: %r nu e un număr întreg." % (numar_start,))
        if _n is None:
            pass
        elif _n < 1:
            er.camp("numar_start", "Numărul de start trebuie să fie cel puțin 1; s-a primit "
                                   "%s. Numerotarea documentelor pornește de la 1, nu de la "
                                   "zero sau de la un număr negativ (%s)."
                                   % (_n, NUMEROTARE_SECVENTIALA))
        elif _urm is not None and _n < _urm:
            er.camp("numar_start", "Numărul de start %s e sub cel la care a ajuns seria "
                                   "(%s). Dat înapoi, următoarea factură ar primi un număr "
                                   "deja emis, iar secvența cerută de %s s-ar rupe. Un "
                                   "număr mai mare sau egal se acceptă."
                                   % (_n, _urm, NUMEROTARE_SECVENTIALA))
        else:
            seturi.append("urmator_numar_factura = %s"); val.append(_n)
    if er:
        return dict(er.detaliu(), ok=False)
    if not seturi:
        return {"ok": False, "mesaj": "Nu ai trimis nici seria, nici numărul de "
                                      "start, deci nu e nimic de schimbat în numerotarea "
                                      "facturilor."}
    seturi.append("numerotare_configurata = true")  # numerotare_configurata_v1
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET " + ", ".join(seturi), val)
    return {"ok": True}


def intrebari_model(conn, linii, platitor_tva=True):
    """[R193, comanda Costin 10.10.2026 pct.2] Faza de CITIRE a emiterii: denumirile pentru care `_potriveste_linii` va avea nevoie
    de răspunsul modelului — linia fără cotă al cărei produs nu e în nomenclator (`produse_api.de_intrebat`), și linia fără cont de
    venit a cărei denumire nu-i spune felul (nivelul 2 de mai jos). Aceeași regulă ca acolo, de-aia stă lângă ea. Apelantul pune
    întrebarea cu pool-ul liber (`cote_tva.intreaba`) și trimite răspunsurile emiterii (`raspunsuri_ai=`).
    Întrebarea pentru cont e `(denumire, True)` la orice emitent: felul venitului (marfă / produs / serviciu) nu depinde de TVA.
    Până pe 10.10.2026 neplătitorul o primea cu `platitor_tva=False`, pe care `potriveste_cota` îl scurtcircuitează la cota 0 fără
    „tip” — deci nivelul 2 al deciziei 64 (22.09) nu rula la el, iar refuzul spunea că „asistentul nu a putut decide”."""
    from core import produse_api
    from core import facturi as _fc
    out = []
    for l in linii or ():
        if not isinstance(l, dict):
            continue   # forma greșită o refuză validarea emiterii, cu mesajul ei
        d = str(l.get("descriere") or "").strip()
        if l.get("cota_tva") is None and platitor_tva:
            out += produse_api.de_intrebat(conn, d)
        if d and not str(l.get("cont_venit") or "").strip() and not _fc.tip_din_denumire(d):
            out.append((d, True))
    return list(dict.fromkeys(out))


def _potriveste_linii(conn, linii, platitor_tva=True, raspunsuri_ai=None):
    """Pentru fiecare linie fara cota_tva, o potriveste (nomenclator/AI) si o
    salveaza in nomenclator. Determina si contul de venit PE LINIE din denumire
    (#11: marfa->707/produse->701/serviciu->704, OMFP 1802/2014), editabil ulterior.
    Intoarce liniile cu cota + cont_venit completate.
    [R193] Raspunsul modelului vine din `raspunsuri_ai` (`intrebari_model` + `cote_tva.intreaba`, inaintea conexiunii); aici nu
    se intreaba modelul. Un raspuns lipsa e cota/contul NEDETERMINAT, cu refuzul de mai jos."""
    from core import produse_api, cote_tva
    from core import facturi as _fc
    # [22.09.2026, DECIZII 64] contul de venit NU mai cade tacit pe default-ul firmei:
    # se clasifica determinist din denumire (nivel 1), apoi AI (nivel 2), apoi se BLOCHEAZA
    # (nivel 3) - simetric cu blocajul de cota TVA. Fallback-ul tacit cv_firma a fost SCOS.
    out = []
    for l in linii:
        linie = dict(l)
        if linie.get("cota_tva") is None and not platitor_tva:
            # [lot 19 pct.4d] emitent neplătitor: cota e 0 prin lege (CF art.310 alin.(10) lit.b)), nu cea din catalog —
            # un produs salvat cândva cu 21% ar fi readus TVA-ul pe o factură care n-are voie să-l poarte.
            linie["cota_tva"] = 0
        if linie.get("cota_tva") is None:
            # creeaza() cauta in nomenclator, altfel AI + salveaza; nu dubleaza
            r = produse_api.creeaza(conn, linie.get("descriere", ""),
                                    um=linie.get("um", "buc"),
                                    pret_unitar=linie.get("pret_unitar", 0),
                                    platitor_tva=platitor_tva, raspunsuri=raspunsuri_ai)
            if r.get("erori_campuri"):   # [lotul 11, 440] produsul refuzat pe date (UM / preț peste coloană), nu „cota nedeterminată”
                raise ValueError(r["mesaj"])
            if r.get("cota_tva") is None:
                # auto-match esuat (AI indisponibil/nedeterminat): intrare incompleta, NU cota 21
                raise ValueError("cota TVA nedeterminată pentru %r: nomenclatorul/AI nu a putut "
                                 "stabili cota. Declara cota explicit pe linie."
                                 % (linie.get("descriere") or "",))
            linie["cota_tva"] = r["cota_tva"]
        # cont de venit pe linie: pastreaza ce a pus contabilul (escape explicit); altfel:
        if not str(linie.get("cont_venit") or "").strip():
            # nivel 1: regula DETERMINISTA pe cuvinte-cheie (marfa->707/produse->701/servicii->704,
            # OMFP 1802/2014). Nu depinde de AI, deci o factura de servicii NU mai primeste tacit 707.
            tip = _fc.tip_din_denumire(linie.get("descriere", ""))
            cont = _fc.VENIT.get(tip) if tip else None
            # nivel 2: AI, cand e disponibil, pentru denumiri fara cuvant-cheie clar
            if cont is None:
                try:
                    rez = cote_tva.raspuns(raspunsuri_ai, linie.get("descriere", ""), True)   # felul venitului nu depinde de TVA
                    tip = rez.get("tip") if rez.get("ok") else None
                    if tip:
                        cont = _fc.VENIT.get(tip)
                except Exception:
                    cont = None
            # nivel 3: BLOCARE (simetric cu blocajul de cota TVA), NU cadere tacuta pe default.
            if cont is None:
                raise ValueError(
                    "Contul de venit pentru %r nu se poate stabili: denumirea nu arată clar dacă e "
                    "marfă, produs sau serviciu, iar asistentul nu a putut decide. Alege "
                    "contul de venit pe linie." % (linie.get("descriere") or "",))
            linie["cont_venit"] = cont
        out.append(linie)
    return out


def emite_factura(conn, linii, client_id=None, intreaba_marfa=False, tert_nume=None, tert_cui=None, tert_adresa=None,
                  data_emitere=None, data_scadenta=None, moneda="RON",
                  platitor_tva=True, status="de_preluat", curs_manual=None, tip="factura",
                  tert_tara="RO", tip_operatiune="normal", tert_pf=False,
                  data_curs_manual=None, curs_manual_de=None, axa_ic=None,
                  bon_fiscal_nr=None, bon_fiscal_data=None, tert_platitor_tva=None, pleaca_marfa=None,
                  raspunsuri_ai=None, categorie_331=None, tert_oras=None, tert_judet=None,
                  intreaba_dovada=False, dovada_transport=None, vies=None):
    """
    Emite o factura noua (directie=emisa):
      - potriveste cota pe liniile fara cota (nomenclator / raspunsurile modelului, cerute INAINTEA conexiunii:
        `intrebari_model` -> `cote_tva.intreaba` -> `raspunsuri_ai=`, R193)
      - numeroteaza automat (serie + urmator_numar din firma_profil)
      - salveaza + incrementeaza contorul
    Intoarce {ok, factura_id, numar, serie, total, tva}.
    """
    # [probare invalid lot 2, 03.09.2026] ORDINEA e reparația: codul de partener se cerea
    # ÎNAINTE de a se uita la linii, deci cine trimitea `linii=[]`, o cantitate negativă sau o
    # monedă inexistentă primea, toți trei, mesajul despre codul fiscal al partenerului — un
    # refuz care numește alt câmp. Aceeași clasă ca „trimestru invalid: None" din lotul 1.
    import datetime
    if not linii:
        raise ValueError("Factura trebuie să aibă cel puțin o linie.")
    _lipsa = linii_campuri_lipsa(linii)   # [cap.24 3b] validare per-linie field-keyed (autoritatea)
    if _lipsa:
        raise LiniiIncomplete(_lipsa)
    cere_cod_partener(tert_cui, tert_pf, tert_nume)
    data_emitere = data_emitere or datetime.date.today().isoformat()

    linii = _potriveste_linii(conn, linii, platitor_tva=platitor_tva, raspunsuri_ai=raspunsuri_ai)   # R193: modelul, întrebat înainte
    # [274b] categoria fiecărei linii cu 0%, pe câmpul ei (em-l{i}-categorie), înainte să se rezerve vreun număr. Marca de stornare
    # istorică (`categorie_istoric`) nu vine niciodată din cerere: o pune numai `storneaza`.
    for _l in linii:
        _l.pop("categorie_istoric", None)
    from core import categorii_tva as _ct
    with conn.cursor() as _cur:   # [lotul 12, C156] înregistrarea art.317 a neplătitorului (categoria prestării IC), ca `creeaza_factura`
        _cur.execute("SELECT inreg_art317 FROM firma_profil WHERE id = 1")
        _r317 = _cur.fetchone()
    _rele = _ct.verifica_linii(linii, platitor_tva, tert_tara, art317=_r317[0] if _r317 else None, tert_cui=tert_cui)
    if not _rele and not categorie_331 and any(_l.get("categorie_tva") == "taxare_inversa" for _l in linii):
        _rele = [{"camp": "em-c331", "eticheta": "Categoria produsului (art.331)", "cod": "CATEGORIE_331_DE_COMPLETAT",
                  "mesaj": "Factura are linii cu taxare inversă (art.331): alege categoria produsului (D394 o declară cu codul ei)."}]
    if _rele:
        raise LiniiIncomplete(_rele)
    if intreaba_marfa and pleaca_marfa is None:
        # [deficiența 304, comanda Costin 17.10.2026 7.2] „refuzul vine abia după «Pleacă marfa acum?»”: întrebarea vine DUPĂ ce liniile și
        # categoriile lor au trecut, nu înainte — un refuz al facturii nu mai așteaptă un răspuns care nu-l schimbă
        _e = ValueError(MESAJ_INTREABA_MARFA)
        _e.cod = COD_INTREABA_MARFA
        raise _e
    _lic = cere_vies(tip, linii)
    _stare_vies = stare_vies(vies) if (_lic and vies is not None) else None
    if _stare_vies == "invalid":
        # [lotul 13, C199 — decizia Costin, verbatim: „C199: cu un cod TVA invalid în VIES se refuză scutirea; factura se emite doar cu TVA
        # românesc. VIES indisponibil = avertisment și reîncercare, nu refuz (550).”] verificarea e pe server, la emitere, înaintea oricărei
        # scrieri și înaintea întrebărilor (răspunsul la ele n-ar schimba refuzul)
        _e = ValueError(MESAJ_VIES_INVALID % (str(tert_cui or "").strip(),))
        _e.cod, _e.camp, _e.temei = COD_VIES_INVALID, "em-cui", "CF art.294 alin.(2) lit.a)"
        raise _e
    if intreaba_dovada and _lic and dovada_transport is None:
        # [lotul 12, C84, decizia Costin 12.3 pct.7] întrebarea, după linii și după „Pleacă marfa acum?”, înaintea oricărei scrieri; răspunsul
        # nu oprește emiterea („avertisment la emitere, nu refuz”)
        from core import intracomunitar as _ic
        _e = ValueError("Răspunde la întrebare: " + _ic.INTREBARE_DOVADA_TRANSPORT)
        _e.cod, _e.intrebare = COD_INTREABA_DOVADA, _ic.INTREBARE_DOVADA_TRANSPORT
        raise _e
    if tip == "factura" and not str(bon_fiscal_nr or "").strip() and pleaca_marfa is not False:
        verifica_marfa_si_metoda(conn, linii, pleaca_marfa)   # [06.10.2026 §6.3] o singură descărcare pe ieșire
    # [C1] rezervare ATOMICĂ a numărului (UPDATE ... +1 RETURNING), nu citire-apoi-increment.
    if tip == "factura":
        cere_serie(conn)   # [06.10.2026 §6.1] CF art.319 alin.(20) lit.a)
        serie, numar_int = _rezerva_numar(conn, "factura")
        numar = f"{serie}{numar_int}" if serie else str(numar_int)
    else:
        serie, numar_int = _rezerva_numar(conn, tip)
        numar = f"{serie}{numar_int}"

    # ---- CURS VALUTAR (art. 290/319 Cod fiscal): [A1] calculat ÎNAINTE de creare și pasat în
    # `creeaza_factura`, ca nota automată (care rulează ÎN creare) să vadă deja sumele în lei. Până
    # azi cursul se aplica printr-un UPDATE de DUPĂ creare — deci nota valutei se scria cu cursul
    # calculat de `creeaza` (auto), nu cu cel manual al emiterii. Ordinea corectă: întâi cursul, apoi
    # documentul și nota lui.
    import datetime as _dt
    if isinstance(data_emitere, str):
        _d = _dt.date.fromisoformat(data_emitere)
    elif isinstance(data_emitere, _dt.date):
        _d = data_emitere
    else:
        _d = _dt.date.today()

    _urma_manual = None            # (cine, cand) — se scrie numai pe calea manuala
    if (moneda or "RON").upper() == "RON":
        _curs, _dcurs, _sursa = 1, _d, "ron"
    elif curs_manual is not None:
        # [R130, decizia lui Costin 04.09.2026] Cursul de mână vine cu DATA LUI, nu cu data
        # facturii. Până azi `data_curs` primea data facturii — adică documentul spunea „curs din
        # 4 septembrie" despre o cifră pe care contabilul o luase din altă zi. Iar „consemnat cine
        # și când" cere un autor: fără el, „manual" e o stare, nu un act.
        _dcm = _data_ceruta("data cursului", data_curs_manual)
        if _dcm is None:
            raise ValueError(
                "Cursul introdus manual are nevoie de data la care a fost comunicat. Fără ea, "
                "factura ar spune că e cursul zilei de emitere, ceea ce nu se știe.")
        from core.pdf_util import data_ro as _data_ro   # DS cap.4: data pentru om
        if _dcm > _d:
            raise ValueError(
                "Data cursului (%s) e după data facturii (%s). Se folosește ultimul curs comunicat "
                "până la data facturii — unul de după ea n-avea cum să fie cunoscut atunci."
                % (_data_ro(_dcm), _data_ro(_d)))
        if not (curs_manual_de or "").strip():
            raise ValueError(
                "Cursul introdus manual se consemnează cu autorul lui. Fără el, peste șase luni "
                "nimeni nu poate spune cine a ales cifra cu care s-a calculat TVA-ul.")
        _curs, _dcurs, _sursa = float(curs_manual), _dcm, "manual"
        _urma_manual = (curs_manual_de.strip(), _dt.datetime.now(_dt.timezone.utc))
    else:
        # [lotul 10, 7g] cursul automat și refuzurile lui: `curs_automat`, aceeași definiție ca previzualizarea din formular
        _ca = curs_automat(conn, moneda, _d)
        if isinstance(_ca, dict):
            # Refuzul (curs prea vechi, monedă necotată, BNR indisponibil): nu se emite fără curs valid. Nimic n-a fost scris încă
            # (cursul se verifică înaintea creării), dar `_potriveste_linii` a putut salva în nomenclator — rollback ca înainte.
            conn.rollback()
            return _ca
        _curs, _dcurs, _sursa = float(_ca[0]), _ca[1], _ca[2]

    r = creeaza_factura(conn, numar, data_emitere, "emisa", linii, tert_platitor_tva=tert_platitor_tva,   # [05.10.2026 pct.5]
                        client_id=client_id, tert_nume=tert_nume, tert_cui=tert_cui, tert_adresa=tert_adresa,
                        data_scadenta=data_scadenta, moneda=moneda, status=status,
                        tert_tara=tert_tara, tip_operatiune=tip_operatiune, tip=tip,
                        axa_ic=axa_ic,   # [R186] axa, INGHETATA pe document
                        categorie_331=categorie_331,   # [274b] categoria produsului la taxarea inversă (D394)
                        tert_oras=tert_oras, tert_judet=tert_judet,   # [274b] adresa de livrare a livrării intracomunitare (XML)
                        # [A1] cursul emiterii intra ÎN creare, deci nota automată e în lei. RON→None
                        # (creeaza pune cursul 1); valută→cursul calculat mai sus.
                        curs=(None if (moneda or "RON").upper() == "RON" else _curs),
                        data_curs=_dcurs, curs_sursa=_sursa,
                        bon_fiscal_nr=bon_fiscal_nr, bon_fiscal_data=bon_fiscal_data,   # [decizia A 02.10]
                        # [10.10.2026] `tert_pf` se oprea aici: `cere_cod_partener` de mai sus il primea, `creeaza_factura` nu, deci
                        # refuza a doua oara partenerul persoana fizica fara cod — orice comanda din magazin (`woocommerce._importa`).
                        tert_pf=tert_pf, serie=serie)   # [lotul 11, 443] seria la INSERT, înaintea contării
    _fid = r["factura_id"]
    # setez seria pe factura. [C1] contorul a fost DEJA incrementat atomic de `_rezerva_numar` la
    # inceput — nu se mai incrementeaza aici (dublul increment ar sari numere).
    with conn.cursor() as cur:
        if _urma_manual:
            cur.execute("UPDATE facturi SET curs_manual_de=%s, curs_manual_la=%s WHERE id=%s",
                        (_urma_manual[0], _urma_manual[1], _fid))

    # [deficiența 280, clasa: rotunjirea fiscală e aritmetică] suma în lei la curs e o sumă NOUĂ: `round()` (la par) greșea pe ,xx5
    # [lotul 10, 7g] aceeași conversie ca la creare și în formular (`sume_lei`)
    _tva_lei, _total_lei = (float(x) for x in sume_lei(r, _curs))
    r["curs_bnr"] = _curs
    r["tva_lei"] = _tva_lei
    r["total_lei"] = _total_lei
    r["curs_sursa"] = _sursa
    # [R130] Data cursului și cât e de vechi ies din rută, nu doar în PDF. *„Sub prag: se
    # folosește, dar cursul și data lui apar pe factură ȘI în răspunsul rutei. Nu se mai tace
    # niciodată."* (Costin, 04.09.2026)
    r["data_curs"] = _dcurs.isoformat() if hasattr(_dcurs, "isoformat") else _dcurs
    r["curs_vechime_zile"] = (_d - _dcurs).days if hasattr(_dcurs, "isoformat") else None
    if _urma_manual:
        r["curs_manual_de"] = _urma_manual[0]
        r["curs_manual_la"] = _urma_manual[1].isoformat()
    r["numar"] = numar
    r["serie"] = serie
    if _stare_vies == "indisponibil":   # [lotul 13, C199 / 550] avertisment, nu refuz: codul se reverifică (ecranul oferă reîncercarea)
        r["avertismente"] = list(r.get("avertismente") or []) + [AVERTISMENT_VIES_INDISPONIBIL % (str(tert_cui or "").strip(),)]
        r["vies_de_reverificat"] = str(tert_cui or "").strip()
    if _lic and dovada_transport is not True:
        # [lotul 12, C84] emisă fără dovada transportului: ce lipsește și ce se întâmplă cu scutirea. [C197] Pe un drum care nu întreabă
        # (`intreaba_dovada=False`, răspunsul lipsă: factura recurentă din cron) avertismentul e tot acolo, cu textul a ce nu se știe
        from core import intracomunitar as _ic
        r["avertismente"] = list(r.get("avertismente") or []) + [
            _ic.AVERTISMENT_LIC_FARA_DOVADA if dovada_transport is False else _ic.AVERTISMENT_LIC_NEINTREBAT]
    return r


#: [lotul 13, C199] livrarea intracomunitară cu codul de TVA al clientului invalid în VIES: refuzul scutirii (CF art.294 alin.(2) lit.a: „către
#: o persoană impozabilă [...] care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale
#: din alt stat membru”)
COD_VIES_INVALID = "VIES_INVALID"
MESAJ_VIES_INVALID = ("Codul de TVA %s al clientului e invalid în VIES, deci livrarea nu e scutită: scutirea livrării intracomunitare cere un "
                      "cod valabil (Cod fiscal art.294 alin.(2) lit.a). Factura se emite cu TVA românesc: alege pe linie cota de TVA în locul "
                      "categoriei „livrare intracomunitară”. Dacă clientul are alt cod, corectează-l și verifică-l din nou.")
#: [lotul 13, C199 / 550] VIES n-a răspuns (serviciul statului membru indisponibil, VIES căzut): nu e un cod invalid — avertisment, nu refuz
AVERTISMENT_VIES_INDISPONIBIL = ("VIES nu a răspuns acum pentru codul %s (serviciul statului membru e indisponibil), deci codul de TVA al "
                                 "clientului nu s-a putut verifica; factura s-a emis cu scutirea. Reverifică codul în VIES înainte de D390: "
                                 "dacă iese invalid, livrarea nu e scutită și factura se corectează prin stornare.")


def cere_vies(tip, linii):
    """[lotul 13, C199] Emiterea cere verificarea în VIES a codului clientului: factura (nu proforma / avizul) cu o linie „livrare
    intracomunitară” (categoria de TVA a liniei cu 0%)."""
    return (tip or "factura") == "factura" and any(_l.get("categorie_tva") == "livrare_ic" for _l in (linii or []))


def stare_vies(v):
    """[lotul 13, C199] Starea răspunsului VIES: „valid” | „invalid” | „indisponibil” (câmpul `stare` al lui `intracomunitar.verifica_vies`,
    lotul 13 — 550). Un răspuns fără `stare` nu e niciodată „invalid”: numai un cod spus invalid de VIES refuză scutirea."""
    if not isinstance(v, dict):
        return "indisponibil"
    st = v.get("stare")
    if st in ("valid", "invalid", "indisponibil"):
        return st
    return "valid" if v.get("valid") else "indisponibil"


def verifica_vies_emitere(cod, tara=None):
    """[lotul 13, C199] VIES pentru emitere, chemat de ruta emiterii ÎNAINTEA conexiunii (ca `vanzare_ic`, P5): răspunsul lui
    `intracomunitar.verifica_vies`, sau `{"stare": "indisponibil"}` dacă serviciul nu răspunde (căderea nu refuză emiterea — 550); detaliul
    căderii merge în jurnalul operatorului."""
    from core import intracomunitar as _ic, observare as _obs
    c = str(cod or "").strip().upper().replace(" ", "")
    if c and not c[:2].isalpha() and tara:   # codul scris fără prefix, cu țara clientului aleasă pe factură
        c = str(tara).strip().upper() + c
    try:
        return _ic.verifica_vies(c)
    except ValueError as e:   # codul nu e un cod de TVA din UE (formă greșită): nu poate fi „valabil” — verdictul, cu motivul lui
        return {"stare": "invalid", "valid": False, "motiv": str(e)}
    except Exception as e:   # noqa: BLE001 — VIES căzut: avertisment la emitere, nu refuz; nu e tăcut (jurnalul operatorului)
        _obs.esec_secundar("vies_emitere", e)
        return {"stare": "indisponibil", "valid": False}


COD_CERE_RETUR = "CERE_RETUR"


def storneaza(conn, factura_id, retur=None):
    """
    Creeaza o factura de stornare: copie a originalului cu cantitati NEGATIVE,
    numar nou din aceeasi serie, referinta la original (storno_din_id).
    Intoarce {ok, factura_id, numar, ...} sau ridica ValueError.

    [deficiența 419] Factura care a descărcat stocul (`iesiri_stoc`) nu se stornează fără răspunsul omului: `retur=True` — marfa se
    întoarce fizic, ieșirile ei se stornează în roșu (`stocuri_cv_api.retur_la_stornare`); `retur=False` — marfa rămâne la client
    (numai corecția valorii), stocul nu se atinge. Fără răspuns: ValueError cu `cod = CERE_RETUR`, nimic scris.
    """
    orig = detalii_factura(conn, factura_id)
    if not orig:
        raise ValueError("factura de stornat nu există")
    refuza_sold_preluat(orig.get("tip"))   # [lotul 12, 252] factura deschisă preluată nu se stornează
    if orig.get("directie") != "emisa":
        raise ValueError("se storneaza doar facturi emise")
    # [lotul 10, 10.2 pct.7f (419): după stornare detaliul se redesenează, deci „Stornează” ar fi oferit din nou pe factura stornată] O
    # factură stornată integral nu se mai stornează: CF art.330 alin.(1) lit.b) — factura „cu valorile cu semnul minus” anulează valorile
    # facturii corectate, deci a doua stornare ar scădea încă o dată o operațiune care nu mai există (D300, 4111, stocul). Nici o
    # stornare nu se stornează (ecranul n-o oferea; ruta o primea). „Stornată” = aceeași definiție ca starea de încasare (416).
    from core.pdf_util import serie_nr as _sn   # [lotul 12, 443.1] factura numită ca în Istoric („F1A nr. 8”), nu cu seria lipită („F1A8”)
    _nr_orig = _sn(orig.get("serie"), orig.get("numar"))
    if orig.get("storno_din_id"):
        raise ValueError("Factura %s e ea însăși o stornare (%s): o stornare nu se stornează la rândul ei (%s)."
                         % (_nr_orig, orig.get("mentiune_storno") or "trimite la factura inițială", TEMEI_STORNARE))
    if (orig.get("stare_incasare") or {}).get("stare") == "stornata":
        with conn.cursor() as cur:
            cur.execute("SELECT serie, numar FROM facturi WHERE storno_din_id = %s ORDER BY id", (factura_id,))
            prin = [_sn(*((r["serie"], r["numar"]) if isinstance(r, dict) else r)) for r in cur.fetchall()]
        raise ValueError("Factura %s e deja stornată integral (prin %s): nu mai rămâne nimic de stornat (%s)."
                         % (_nr_orig, ", ".join(prin) or "o factură de stornare", TEMEI_STORNARE))
    if orig.get("iesiri_stoc") and retur is None:
        _e = ValueError("Factura %s a descărcat din stoc: %s. Marfa se întoarce în stoc (retur) sau rămâne la client (numai corecția "
                        "valorii)? Alege, apoi confirmă stornarea." % (_nr_orig, "; ".join(
                            "%s × %s" % (x["articol"], x["cantitate_text"]) for x in orig["iesiri_stoc"])))
        _e.cod = COD_CERE_RETUR
        raise _e
    # linii negate
    linii_neg = []
    for l in orig.get("linii", []):
        linii_neg.append({
            "descriere": "STORNO: " + (l.get("descriere") or ""),
            "um": l.get("um", "buc"),
            "cantitate": -abs(float(l.get("cantitate", 0))),
            "pret_unitar": float(l.get("pret_unitar", 0)),
            "cota_tva": float(l["cota_tva"]),
            # [274b] corecția aterizează în aceeași categorie (același rând D300, același cod în e-Factura) ca linia stornată; o
            # linie de dinainte de categorie rămâne fără ea, ca originalul (nimic ghicit)
            "categorie_tva": l.get("categorie_tva"),
            "categorie_istoric": l.get("categorie_tva") is None,
            # [lotul 11, C86] linia venită din XML-ul e-Factura poartă BT-131 exact (`valoare_neta`): stornarea o ia negată, nu cantitate × preț
            # (3,333 × 30,15 = 100,49, pe factură 100,50). CF art.330 alin.(1) lit.b): factura de stornare cuprinde „informațiile din factura
            # inițială [...] valorile cu semnul minus” — valorile ei, deci nota, D300, D394, D406 și XML-ul stornării iau exact −100,50
            "valoare_neta": (-Decimal(str(l["valoare_neta"])) if l.get("valoare_neta") not in (None, "") else None),
        })
    cere_serie(conn)   # [06.10.2026 §6.1] storno-ul e tot o factură (CF art.319 alin.(20) lit.a)
    serie, numar_int = _rezerva_numar(conn, "factura")   # [C1] rezervare atomica si la storno
    numar = f"{serie}{numar_int}" if serie else str(numar_int)
    import datetime
    # [A1] Storno-ul unei facturi în valută păstrează CURSUL ORIGINALULUI: corecția e la rata la care
    # s-a înregistrat operațiunea, nu la cursul zilei de stornare. Fără el, `creeaza` ar lua cursul
    # de azi și storno-ul n-ar anula exact suma în lei a facturii inițiale.
    _mon_orig = orig.get("moneda") or "RON"
    _curs_orig = orig.get("curs_bnr")
    # [A4, 17.09.2026] Storno-ul COPIAZĂ clasificarea originalului. Fără ea, `creeaza_factura` cădea
    # pe implicite (`tert_tara="RO"`, `taxare_inversa=False`, axa None), iar storno-ul unei livrări IC
    # devenea o „livrare RO cu cotă 0" neclasificabilă — nu scădea rd.1/rd.13, deci D300 ≠ D390. Cu
    # bazele negate (linii_neg) și aceeași clasificare, storno-ul aterizează pe ACELAȘI rând ca
    # originalul și îl reduce. `data_faptului_generator` se copiază: exigibilitatea corecției urmează
    # faptul original (art. 284).
    r = creeaza_factura(conn, numar, datetime.date.today().isoformat(), "emisa",
                        linii_neg, client_id=orig.get("client_id"),
                        tert_nume=orig.get("tert_nume"), tert_cui=orig.get("tert_cui"), tert_adresa=orig.get("tert_adresa"),
                        # [417, prins pe validatorul FACT1] orașul și județul clientului: fără ele stornarea ieșea cu BR-RO-110 (BT-54)
                        tert_oras=orig.get("tert_oras"), tert_judet=orig.get("tert_judet"),
                        moneda=_mon_orig, status="de_preluat",
                        curs=(None if str(_mon_orig).upper() == "RON" else _curs_orig),
                        data_curs=orig.get("data_curs"), curs_sursa=orig.get("curs_sursa"),
                        tert_tara=(orig.get("tert_tara") or "RO"),
                        taxare_inversa=bool(orig.get("taxare_inversa")),
                        categorie_331=orig.get("categorie_331"),
                        axa_ic=orig.get("axa_ic"),
                        tip_operatiune=(orig.get("tip_operatiune") or "normal"),
                        tert_platitor_tva=orig.get("tert_platitor_tva"),
                        data_faptului_generator=orig.get("data_faptului_generator"),
                        # [decizia A 02.10] storno-ul unei facturi emise pe baza bonului fiscal nu e nici el o vânzare:
                        # moștenește marca, altfel ar scădea din D300 / evidență o vânzare care n-a fost numărată
                        bon_fiscal_nr=orig.get("bon_fiscal_nr"), bon_fiscal_data=orig.get("bon_fiscal_data"),
                        cota_la_data=orig.get("data_emitere"),  # [3i] cota validata pe data operatiunii de baza (art.282(9))
                        serie=serie)   # [lotul 11, 443] seria la INSERT, înaintea contării („Contare factura F1A nr. 11”)
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET storno_din_id = %s WHERE id = %s", (factura_id, r["factura_id"]))
        # [C1] contorul a fost incrementat atomic de `_rezerva_numar`; nu se mai incrementeaza aici.
    r["numar"] = numar
    r["serie"] = serie   # [lotul 12, 443.1] ecranul spune „Storno creat: F1A nr. 16”, nu „F1A16” (`numarCuSerie`)
    r["storno_din_id"] = factura_id
    r["retur"] = []
    if retur and orig.get("iesiri_stoc"):
        from core import stocuri_cv_api as _cv
        # [lotul 11, 451] documentul returului din regula unică `stocuri_cv_api.document_retur` (citit din factura de stornare de
        # mai sus), aceeași cu regenerarea pe uscat a ciornei returului la validare (`ciorne_depasite`)
        r["retur"] = _cv.retur_la_stornare(conn, None, factura_id, r["factura_id"], datetime.date.today(), None)
    return r
