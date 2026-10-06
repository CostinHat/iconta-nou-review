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
        raise ValueError("%s: %r nu e o dată din calendar. Aștept forma AAAA-LL-ZZ, cu o zi care "
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
    """Campuri obligatorii per linie -> [{camp, eticheta, mesaj}]. Obligatorii: denumire (nevida) +
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
    baza = Decimal(0)
    tva = Decimal(0)
    for l in linii:
        b = Decimal(str(l["cantitate"])) * Decimal(str(l["pret_unitar"]))
        t = b * Decimal(str(l["cota_tva"])) / Decimal(100)
        baza += b
        tva += t
    return {"total": _q(baza + tva), "tva": _q(tva)}


# ============================================================
#  CREARE — DB
# ============================================================
from core import curs_bnr


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


def creeaza_factura(conn, numar, data_emitere, directie, linii,
                    client_id=None, tert_nume=None, tert_cui=None, tert_adresa=None,
                    data_scadenta=None, moneda="RON", status="emisa",
                    categorie_331=None, data_faptului_generator=None, taxare_inversa=False,
                    tert_platitor_tva=None, tert_tara="RO", tip_operatiune="normal",
                    furnizor_tva_incasare=False, tert_pf=False, tip="factura", axa_ic=None,
                    curs=None, data_curs=None, curs_sursa=None, cota_la_data=None,
                    bon_fiscal_nr=None, bon_fiscal_data=None):
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
    if not linii:
        raise ValueError("factura trebuie să aibă cel puțin o linie")
    cere_cod_partener(tert_cui, tert_pf, tert_nume)
    for _l in linii:
        if _l.get("cota_tva") is None:
            raise ValueError("Linia %r nu are cotă de TVA. Completează cota pe linie — 0 (scutit) "
                             "e o valoare validă, dar absența nu se poate ghici."
                             % (_l.get("descriere") or "",))
    if directie not in DIRECTII:
        raise ValueError("Direcția facturii trebuie să fie 'emisă' sau 'primită'.")
    _bon_nr, _bon_data = _marca_bon(directie, tip, bon_fiscal_nr, bon_fiscal_data, data_emitere)
    # [probare invalid lot 2, 03.09.2026] Cele trei refuzuri de mai jos au înlocuit, în ordine:
    # un `500` pe o dată inexistentă în calendar, o factură cu cota de TVA 99% acceptată ȘI
    # contabilizată (4427 = 99 lei), și un al doilea document cu un număr deja folosit.
    _d_emitere = _data_ceruta("data emiterii", data_emitere)
    _d_scadenta = _data_ceruta("data scadenței", data_scadenta)
    # [comanda Costin 05.10.2026 pct.4] scadența se stabilește pe formular și alimentează scadențarul; înaintea emiterii n-are sens
    if _d_scadenta is not None and _d_emitere is not None and _d_scadenta < _d_emitere:
        # refuz de FORMĂ, fără temei normativ: o scadență anterioară emiterii e o dată imposibilă, nu o regulă fiscală
        raise ValueError(MESAJ_SCADENTA_INAINTE_DE_EMITERE)
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
            _cur.execute("SELECT id FROM facturi WHERE numar=%s AND directie='emisa' LIMIT 1",
                         (numar,))
            _existent = _cur.fetchone()
        if _existent:
            raise ValueError(
                "Numărul %s e deja pe factura #%s. Două documente emise cu același număr rup "
                "secvența cerută de %s. Dacă documentul dinainte e greșit, se stornează — nu se "
                "reia numărul." % (numar, _existent[0], NUMEROTARE_SECVENTIALA))
    # [B1 D300] campuri de clasificare/temporizare. tip_operatiune distinge avansul (exigibil la
    # emitere, art.282 alin.2 lit.b); furnizor_tva_incasare doar pe PRIMITE (deducere amanata la
    # plata, art.297 alin.2). Fara default tacit peste o valoare invalida -> refuz cu mesaj clar.
    tert_tara_v = (tert_tara or "RO").strip().upper() or "RO"
    # [R186, 16.09.2026] AXA bunuri/servicii, ÎNGHEȚATĂ pe document. Nomenclatorul vine din
    # `migrare_axa_ic.AXE`, nu scris aici: a doua definiție a aceluiași nomenclator e începutul unei
    # divergențe. `None` e a TREIA stare — „nedeclarată" —, nu un implicit: pentru operațiunile
    # interne axa n-are sens, iar pentru facturile istorice nu se știe. O valoare din afara
    # nomenclatorului e REFUZATĂ aici, nu lăsată pe seama constrângerii din bază: refuzul trebuie să
    # ajungă la om cu numele câmpului.
    from core.migrare_axa_ic import AXE as _AXE
    axa_v = (str(axa_ic).strip().lower() or None) if axa_ic is not None else None
    if axa_v is not None and axa_v not in _AXE:
        raise ValueError("Axa operațiunii intracomunitare poate fi doar %s (primit: %r). Ea se "
                         "înregistrează PE document și nu se mai schimbă după introducere."
                         % (" sau ".join(_AXE), axa_ic))
    tip_op_v = (tip_operatiune or "normal").strip().lower() or "normal"
    if tip_op_v not in ("normal", "avans", "regularizare_avans"):
        raise ValueError("Tipul operațiunii %r nu e recunoscut. Alege: normal, avans sau "
                         "regularizare de avans." % tip_operatiune)
    # [A3, 17.09.2026] Statusul e din NOMENCLATOR, nu text liber. Până azi `FacturaIn.status` trecea
    # nevalidat prin `creeaza_factura`; o valoare inventată ar fi intrat în bază și ar fi decis tăcut
    # includerea în declarații (clauza de status compară cu lista nedeclarabilelor). Refuzul numește câmpul.
    from core import nomenclator_status_factura as _nsf_creare
    _status_v = (status or _nsf_creare.IMPLICITA).strip().lower() or _nsf_creare.IMPLICITA
    if _status_v not in _nsf_creare.STARI:
        raise ValueError("Starea %r nu e recunoscută ca stare de factură. Stări acceptate: %s."
                         % (status, ", ".join(sorted(_nsf_creare.STARI))))
    status = _status_v
    # [EEE1] `tip` intra la INSERT, nu printr-un UPDATE de dupa. Motivul nu e stilistic: nota
    # automata se scrie in ACEEASI tranzactie, iar ea trebuie sa stie daca documentul e factura sau
    # proforma. Cat timp tipul se punea dupa, o proforma ar fi primit nota si abia apoi ar fi devenit
    # proforma.
    tip_v = (tip or "factura").strip().lower() or "factura"
    if tip_v not in ("factura", "proforma", "aviz"):
        raise ValueError("Tipul documentului %r nu e recunoscut. Alege: factură, proformă sau aviz."
                         % tip)
    furnizor_incasare_v = bool(furnizor_tva_incasare)
    if furnizor_incasare_v and directie != "primita":
        raise ValueError("TVA la încasare la furnizor se poate bifa doar pe facturile primite "
                         "— pe cele emise nu se aplică.")
    t = totaluri_din_linii(linii)
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
        _total_lei_v = _q(t["total"] * _curs_v)
        _tva_lei_v = _q(t["tva"] * _curs_v)
    else:
        _curs_v = _dcurs_v = _sursa_v = _total_lei_v = _tva_lei_v = None
        try:
            _c_auto, _dc_auto, _s_auto = curs_bnr.curs_pentru(conn, _moneda_v, _d_emit_lei)
            _curs_v, _dcurs_v, _sursa_v = Decimal(str(_c_auto)), _dc_auto, _s_auto
            _total_lei_v, _tva_lei_v = _q(t["total"] * _curs_v), _q(t["tva"] * _curs_v)
        except Exception:
            pass   # valută fără curs disponibil: NULL, semnalat la contare/declarație (nu se inventează)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO facturi (client_id, numar, data_emitere, data_scadenta, "
            "total, tva, status, moneda, directie, tert_nume, tert_cui, tert_adresa, "
            "categorie_331, data_faptului_generator, taxare_inversa, tert_platitor_tva, "
            "tert_tara, tip_operatiune, furnizor_tva_incasare, tip, axa_ic, "
            "curs_bnr, tva_lei, total_lei, data_curs, curs_sursa, "  # [A1] lei la INSERT
            "bon_fiscal_nr, bon_fiscal_data, "   # [decizia A 02.10] factura emisă pe baza bonului fiscal
            # [punctul 3, 03.10.2026] … și ÎNCASATĂ: HG 1/2016 pct.97 alin.(1) „facturile emise și achitate pe bază de bonuri
            # fiscale”. Fără asta rămânea „neîncasată”: notificarea de scadență (emailul pleacă la CLIENT) o trata ca
            # restanță, scadențarul la fel, iar ecranul oferea „Emite chitanță” — încasare dublă.
            "platita_la) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            "%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (client_id, numar, data_emitere, data_scadenta, t["total"], t["tva"],
             status, moneda, directie, tert_nume, tert_cui, tert_adresa,
             categorie_331 or None, data_faptului_generator or None, bool(taxare_inversa),
             tert_platitor_tva, tert_tara_v, tip_op_v, furnizor_incasare_v, tip_v, axa_v,
             _curs_v, _tva_lei_v, _total_lei_v, _dcurs_v, _sursa_v, _bon_nr, _bon_data,
             _bon_data if _bon_nr else None))
        factura_id = cur.fetchone()[0]
        for l in linii:
            cur.execute(
                "INSERT INTO factura_linii (factura_id, descriere, um, cantitate, "
                "pret_unitar, cota_tva, articol_id, cont_venit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (factura_id, l["descriere"], l.get("um", "buc"),
                 l["cantitate"], l["pret_unitar"], l["cota_tva"], l.get("articol_id"),
                 (l.get("cont_venit") or None)))  # #11 cont venit pe linie (auto din denumire, editabil)
    _redeschide_luna(conn, data_emitere)   # [cap.23] evidenta lunii s-a schimbat -> luna se redeschide
    out = {"ok": True, "factura_id": factura_id,
           "total": float(t["total"]), "tva": float(t["tva"])}
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
            "nota automată se scrie doar pentru facturi EMISE de tip factură; documentul ăsta e "
            "%s / %s" % (directie, tip),
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
                    unde="factura #%s" % factura_id,
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
        raise ValueError("luna invalidă: %r (aștept 1-12)" % (luna,))
    if an is not None and not (1990 <= an <= 2100):
        raise ValueError("an invalid: %r (aștept 1990-2100)" % (an,))
    if directie is not None and directie not in DIRECTII:
        raise ValueError("direcție necunoscută: %r (direcțiile facturii: %s)"
                         % (directie, ", ".join(DIRECTII)))
    if limit is not None and limit < 0:
        raise ValueError("limit invalid: %r (aștept un număr pozitiv, sau nimic pentru tot)"
                         % (limit,))
    if offset is not None and offset < 0:
        raise ValueError("offset invalid: %r (aștept un număr pozitiv sau 0)" % (offset,))
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
    where = (" WHERE " + " AND ".join(cond)) if cond else ""
    limitclause = ""
    if limit is not None:
        limitclause = " LIMIT %s OFFSET %s"; val += [limit, offset]
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, numar, data_emitere, directie, total, tva, status, "
            "moneda, tert_nume, tert_cui, tert_adresa, tip, transformat_in_id, storno_din_id "
            "FROM facturi" + where +
            " ORDER BY data_emitere DESC, id DESC" + limitclause, val)
        out = [dict(r) for r in cur.fetchall()]
        _cu_stare_contare(cur, out)
        return out


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
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, client_id, numar, serie, data_emitere, data_scadenta, total, tva, "   # [05.10.2026] seria pe PDF (art.319 lit.a)
            "status, moneda, directie, tert_nume, tert_cui, tert_adresa, "
            "tert_tara, tip_operatiune, furnizor_tva_incasare, "
            "taxare_inversa, categorie_331, axa_ic, tert_platitor_tva, data_faptului_generator, "  # [A4] clasificarea storno-ului
            "curs_bnr, tva_lei, total_lei, data_curs, curs_sursa, storno_din_id, tip, transformat_in_id, "
            "link_plata, platita_la, plata_confirmata_de, "  # [R43] marca de simulare
            "bon_fiscal_nr, bon_fiscal_data, "   # [decizia A 02.10] factura emisă pe baza bonului fiscal
            "(SELECT numar FROM facturi f2 WHERE f2.id = facturi.transformat_in_id) AS transformat_in_numar "
            "FROM facturi WHERE id = %s",
            (factura_id,))
        f = cur.fetchone()
        if not f:
            return None
        f = dict(f)
        cur.execute(
            "SELECT id, descriere, um, cantitate, pret_unitar, cota_tva, cont_venit "
            "FROM factura_linii WHERE factura_id = %s ORDER BY id", (factura_id,))
        f["linii"] = [dict(r) for r in cur.fetchall()]
        _cu_stare_contare(cur, [f])
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


def _luna_facturii(conn, factura_id):
    with conn.cursor() as cur:
        cur.execute("SELECT data_emitere FROM facturi WHERE id = %s", (factura_id,))
        r = cur.fetchone()
    return r[0] if r else None


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
    from core import contare_facturi as _cf
    with _cf.cursor_dict(conn) as cur:
        # [05.10.2026] Aceeași clasă ca nota legată: `efactura_trimiteri` / `efactura_primite` țin factura printr-o cheie
        # fără `ON DELETE`, deci ștergerea cădea cu o eroare brută de bază. Factura legată de SPV tot nu se șterge — istoricul
        # cu ANAF rămâne —, dar refuzul e numit și spune ieșirea.
        cur.execute("SELECT id, stare FROM efactura_trimiteri WHERE factura_id = %s ORDER BY id DESC LIMIT 1", (factura_id,))
        trim = cur.fetchone()
        cur.execute("SELECT id_mesaj_anaf FROM efactura_primite WHERE factura_id = %s LIMIT 1", (factura_id,))
        prim = cur.fetchone()
        n = _cf.contare_existenta(cur, "", factura_id)
        legate = _cf.note_cu_cheia(cur, "", factura_id)
    if trim:
        raise _cf.RefuzContare(
            "LEGATA_DE_SPV",
            "Factura are o trimitere în e-Factura (#%d, stare „%s”) și nu se mai șterge: istoricul trimiterii către ANAF se "
            "păstrează. Corecția se face prin storno — un al doilea document." % (trim["id"], trim["stare"]),
            detalii={"efactura_trimitere_id": trim["id"], "stare": trim["stare"], "iesire": "storno"})
    if prim:
        raise _cf.RefuzContare(
            "LEGATA_DE_SPV",
            "Factura a venit din SPV (mesajul ANAF %s) și nu se șterge: e documentul furnizorului, păstrat așa cum a fost "
            "primit." % prim["id_mesaj_anaf"],
            detalii={"id_mesaj_anaf": prim["id_mesaj_anaf"], "iesire": "fara_stergere"})
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
            "Factura are o notă legată care nu e de contare (#%d, %s, %s) — o plată sau o încasare. "
            "Dezleag-o întâi: potrivirea rămâne consemnată pe linia de extras, iar factura redevine "
            "neîncasată." % (_n0["id"], _n0.get("sursa") or "fără sursă", _n0.get("status") or "?"),
            detalii={"inregistrare_id": _n0["id"], "status_nota": _n0.get("status"),
                     "iesire": "dezleaga_nota"})
    if n:
        raise _cf.RefuzContare(
            "ARE_NOTA_DE_CONTARE",
            "Factura are notă contabilă (#%d) și nu se mai șterge: o notă ștearsă lasă o gaură în "
            "evidență. Corecția unei facturi contabilizate se face prin STORNO — un al doilea "
            "document, care își produce propria notă." % n["id"],
            detalii={"inregistrare_id": n["id"], "iesire": "storno"})
    _d = _luna_facturii(conn, factura_id)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM facturi WHERE id = %s", (factura_id,))
        sterse = cur.rowcount
    if sterse:
        _redeschide_luna(conn, _d)
    return {"ok": sterse > 0}


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
    return {"lipsuri_firma": lipsuri, "forma_propusa": forma, "forma_propusa_sursa": sursa,
            "serie_lipsa": not serie_facturi(conn),   # [06.10.2026 §6.1] nu blochează: refuzul o cere și o setează pe loc
            # [lotul 07.10 pct.18] scadența PROPUSĂ pe formular (editabilă): zilele și temeiul vin de aici, nu din ecran
            "scadenta_zile": SCADENTA_PROPUSA[0], "scadenta_temei": str(SCADENTA_PROPUSA[1]),
            "mesaj_lipsuri": _cs.mesaj_la_deschidere(lipsuri, forma, sursa),
            "cote_permise": sorted({int(c) if int(c) == c else float(c) for c in permise}, reverse=True) if permise else None}


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


def seteaza_numerotare(conn, serie=None, numar_start=None):
    """Configureaza seria + numarul de start (continuitate cu istoricul).
    Se apeleaza o data; dupa, numarul se auto-incrementeaza la emitere."""
    # [probare invalid lot 2, 03.09.2026] Trei valori treceau cu `200 {"ok": true}`:
    # `serie="   "` ștergea seria firmei în tăcere (`strip() or None`), `numar_start=-5` intra
    # ca atare, iar `numar_start=100` dădea contorul înapoi peste numere deja emise — următoarea
    # factură ar fi purtat un număr existent. Probat: după el, emiterea prin API a produs
    # documentul „100", fără serie.
    with conn.cursor() as _cur:
        _cur.execute("SELECT serie_factura, urmator_numar_factura FROM firma_profil LIMIT 1")
        _acum = _cur.fetchone() or (None, None)
    seturi, val = [], []
    if serie is not None:
        if not str(serie).strip():
            return {"ok": False, "mesaj": "Seria e goală (numai spații). Nu se poate ghici dacă "
                                          "ai vrut s-o ștergi sau ai greșit tastarea, iar seria "
                                          "firmei e pe documentele deja emise."}
        seturi.append("serie_factura = %s"); val.append(serie.strip())
    if numar_start is not None:
        try:
            _n = int(numar_start)
        except (TypeError, ValueError):
            return {"ok": False, "mesaj": "Numărul de start: %r nu e un număr întreg." % (numar_start,)}
        if _n < 1:
            return {"ok": False, "mesaj": "Numărul de start trebuie să fie cel puțin 1; am primit "
                                          "%s. Numerotarea documentelor pornește de la 1, nu de la "
                                          "zero sau de la un număr negativ (%s)."
                                          % (_n, NUMEROTARE_SECVENTIALA)}
        _urm = _acum[1]
        if _urm is not None and _n < _urm:
            return {"ok": False, "mesaj": "Numărul de start %s e sub cel la care a ajuns seria "
                                          "(%s). Dat înapoi, următoarea factură ar primi un număr "
                                          "deja emis, iar secvența cerută de %s s-ar rupe. Un "
                                          "număr mai mare sau egal se acceptă."
                                          % (_n, _urm, NUMEROTARE_SECVENTIALA)}
        seturi.append("urmator_numar_factura = %s"); val.append(_n)
    if not seturi:
        return {"ok": False, "mesaj": "Nu ai trimis nici seria, nici numărul de "
                                      "start, deci n-am ce schimba în numerotarea "
                                      "facturilor."}
    seturi.append("numerotare_configurata = true")  # numerotare_configurata_v1
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET " + ", ".join(seturi), val)
    return {"ok": True}


def _potriveste_linii(conn, linii, platitor_tva=True):
    """Pentru fiecare linie fara cota_tva, o potriveste (nomenclator/AI) si o
    salveaza in nomenclator. Determina si contul de venit PE LINIE din denumire
    (#11: marfa->707/produse->701/serviciu->704, OMFP 1802/2014), editabil ulterior.
    Intoarce liniile cu cota + cont_venit completate."""
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
                                    platitor_tva=platitor_tva)
            if r.get("cota_tva") is None:
                # auto-match esuat (AI indisponibil/nedeterminat): intrare incompleta, NU cota 21
                raise ValueError("cota TVA nedeterminata pentru %r: nomenclatorul/AI nu a putut "
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
                    rez = cote_tva.potriveste_cota(linie.get("descriere", ""), platitor_tva=platitor_tva)
                    tip = rez.get("tip") if rez.get("ok") else None
                    if tip:
                        cont = _fc.VENIT.get(tip)
                except Exception:
                    cont = None
            # nivel 3: BLOCARE (simetric cu blocajul de cota TVA), NU cadere tacuta pe default.
            if cont is None:
                raise ValueError(
                    "cont de venit nedeterminat pentru %r: denumirea nu se incadreaza clar "
                    "(marfa/produse/servicii) si AI e indisponibil/nedeterminat. Declara "
                    "cont_venit explicit pe linie." % (linie.get("descriere") or "",))
            linie["cont_venit"] = cont
        out.append(linie)
    return out


def emite_factura(conn, linii, client_id=None, tert_nume=None, tert_cui=None, tert_adresa=None,
                  data_emitere=None, data_scadenta=None, moneda="RON",
                  platitor_tva=True, status="de_preluat", curs_manual=None, tip="factura",
                  tert_tara="RO", tip_operatiune="normal", tert_pf=False,
                  data_curs_manual=None, curs_manual_de=None, axa_ic=None,
                  bon_fiscal_nr=None, bon_fiscal_data=None, tert_platitor_tva=None, pleaca_marfa=None):
    """
    Emite o factura noua (directie=emisa):
      - potriveste cota pe liniile fara cota (nomenclator/AI)
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

    linii = _potriveste_linii(conn, linii, platitor_tva=platitor_tva)
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
        if _dcm > _d:
            raise ValueError(
                "Data cursului (%s) e după data facturii (%s). Se folosește ultimul curs comunicat "
                "PÂNĂ la data facturii — unul de după ea n-avea cum să fie cunoscut atunci."
                % (_dcm.isoformat(), _d.isoformat()))
        if not (curs_manual_de or "").strip():
            raise ValueError(
                "Cursul introdus manual se consemnează cu autorul lui. Fără el, peste șase luni "
                "nimeni nu poate spune cine a ales cifra cu care s-a calculat TVA-ul.")
        _curs, _dcurs, _sursa = float(curs_manual), _dcm, "manual"
        _urma_manual = (curs_manual_de.strip(), _dt.datetime.now(_dt.timezone.utc))
    else:
        try:
            _c, _dc, _s = curs_bnr.curs_pentru(conn, moneda, _d)
            _curs, _dcurs, _sursa = float(_c), _dc, _s
        except curs_bnr.CursPreaVechi as _pv:
            # Emiterea AUTOMATĂ se oprește — dar facturarea nu se blochează: refuzul își numește
            # ieșirea, iar cursul găsit merge cu el, ca omul să vadă de la ce pornește. Nimic n-a fost
            # scris încă (cursul se verifică înaintea creării), dar `_potriveste_linii` a putut salva
            # în nomenclator — rollback ca înainte.
            conn.rollback()
            return {"ok": False, "cod": "CURS_PREA_VECHI", "moneda": moneda,
                    "data": _d.isoformat(), "data_curs_gasit": _pv.data_curs.isoformat(),
                    "curs_gasit": str(_pv.curs), "vechime_zile": _pv.vechime_zile,
                    "prag_zile": _pv.prag_zile, "mesaj": str(_pv),
                    "iesire": {"camp": "curs_manual",
                               "cere": ["curs_manual", "data_curs_manual"],
                               "cum": "Introdu cursul de mână, cu data la care a fost comunicat. "
                                      "Se consemnează cine l-a introdus și când."}}
        except curs_bnr.MonedaNecotata as _mn:
            # Moneda nu exista: nu e o intarziere, deci nu se ofera nici „reincearca", nici
            # „curs manual" — al doilea ar baga factura in contabilitate pe o moneda inventata.
            conn.rollback()
            return {"ok": False, "cod": "MONEDA_NECOTATA", "moneda": moneda,
                    "data": _d.isoformat(), "mesaj": str(_mn)}
        except curs_bnr.CursIndisponibil:
            # nu emit factura in valuta fara curs valid; nimic comis, semnalez frontend-ului
            conn.rollback()
            return {"ok": False, "cod": "CURS_INDISPONIBIL",
                    "moneda": moneda, "data": _d.isoformat(),
                    "mesaj": "Cursul BNR nu e disponibil momentan."}

    r = creeaza_factura(conn, numar, data_emitere, "emisa", linii, tert_platitor_tva=tert_platitor_tva,   # [05.10.2026 pct.5]
                        client_id=client_id, tert_nume=tert_nume, tert_cui=tert_cui, tert_adresa=tert_adresa,
                        data_scadenta=data_scadenta, moneda=moneda, status=status,
                        tert_tara=tert_tara, tip_operatiune=tip_operatiune, tip=tip,
                        axa_ic=axa_ic,   # [R186] axa, INGHETATA pe document
                        # [A1] cursul emiterii intra ÎN creare, deci nota automată e în lei. RON→None
                        # (creeaza pune cursul 1); valută→cursul calculat mai sus.
                        curs=(None if (moneda or "RON").upper() == "RON" else _curs),
                        data_curs=_dcurs, curs_sursa=_sursa,
                        bon_fiscal_nr=bon_fiscal_nr, bon_fiscal_data=bon_fiscal_data)   # [decizia A 02.10]
    _fid = r["factura_id"]
    # setez seria pe factura. [C1] contorul a fost DEJA incrementat atomic de `_rezerva_numar` la
    # inceput — nu se mai incrementeaza aici (dublul increment ar sari numere).
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET serie = %s WHERE id = %s", (serie, _fid))
        if _urma_manual:
            cur.execute("UPDATE facturi SET curs_manual_de=%s, curs_manual_la=%s WHERE id=%s",
                        (_urma_manual[0], _urma_manual[1], _fid))

    _tva_lei = round(float(r["tva"]) * _curs, 2)
    _total_lei = round(float(r["total"]) * _curs, 2)
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
    return r


def storneaza(conn, factura_id):
    """
    Creeaza o factura de stornare: copie a originalului cu cantitati NEGATIVE,
    numar nou din aceeasi serie, referinta la original (storno_din_id).
    Intoarce {ok, factura_id, numar, ...} sau ridica ValueError.
    """
    orig = detalii_factura(conn, factura_id)
    if not orig:
        raise ValueError("factura de stornat nu exista")
    if orig.get("directie") != "emisa":
        raise ValueError("se storneaza doar facturi emise")
    # linii negate
    linii_neg = []
    for l in orig.get("linii", []):
        linii_neg.append({
            "descriere": "STORNO: " + (l.get("descriere") or ""),
            "um": l.get("um", "buc"),
            "cantitate": -abs(float(l.get("cantitate", 0))),
            "pret_unitar": float(l.get("pret_unitar", 0)),
            "cota_tva": float(l["cota_tva"]),
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
                        cota_la_data=orig.get("data_emitere"))  # [3i] cota validata pe data operatiunii de baza (art.282(9))
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET serie = %s, storno_din_id = %s WHERE id = %s",
                    (serie, factura_id, r["factura_id"]))
        # [C1] contorul a fost incrementat atomic de `_rezerva_numar`; nu se mai incrementeaza aici.
    r["numar"] = numar
    r["storno_din_id"] = factura_id
    return r
