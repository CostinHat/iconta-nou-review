# -*- coding: utf-8 -*-
"""R59 — reevaluarea ajunge pe registrul care conduce amortizarea, SI in declaratie.

DE UNDE VINE. `CONFORMITATE.md` R59, deschisa 26.08.2026 si MASURATA pe declaratie la 16.09.2026
(etapa 2, lotul I, lantul 7): ruta `POST /tenants/{id}/reevaluare-imobilizare` scria o nota ciorna
corecta si **nu atingea `mijloace_fixe`** — deci evidenta contabila purta reevaluarea, iar
`AcquisitionAndProductionCostsEnd` din sectiunea Assets a D406 declara costul VECHI. Doua evidente
despre acelasi activ.

CRITERIUL DE INCHIDERE, largit de Costin pe 16.09.2026 **INAINTE** de reparatie, si de-aia proba
are DOUA afirmatii, nu una:
  (1) coloana din registru (`mijloace_fixe.valoare`) urca la valoarea reevaluata;
  (2) `AcquisitionAndProductionCostsEnd` din Assets o declara.
*Scris dupa, criteriul s-ar fi potrivit pe ce a iesit.*

CE APARA, dincolo de cele doua cifre:
  * MOMENTUL — ruta produce o CIORNA; registrul se misca la VALIDAREA notei, nu inainte. Proba
    masoara si starea INTERMEDIARA: dupa ruta si inainte de validare, registrul e NEATINS. Fara
    acest capat, o reparatie care ar urca valoarea direct din ciorna ar trece la fel de verde.
  * BAZA DE AMORTIZARE — reevaluarea nu urca doar o coloana, TAIE durata in etape (OMFP 1802/2014
    pct.111-116, metoda valorii nete: amortizarea cumulata se ELIMINA). O reparatie care ar urca
    doar `valoare` ar face motorul sa recalculeze amortizarea pe valoarea NOUA de la PIF-ul
    ORIGINAL — o cifra pe care evidenta n-a inregistrat-o niciodata.
  * IDEMPOTENTA — o a doua validare a aceleiasi note nu urca valoarea a doua oara.

CE NU DEMONSTREAZA, declarat: corectitudinea prezentarii SAF-T a anului de reevaluare dincolo de
cele doua cifre din criteriu (cum se raporteaza eliminarea amortizarii cumulate intre
`BookValueBegin` si `BookValueEnd`) — cere o sursa ANAF pe care n-am confruntat-o la sursa; e
consemnata ca restanta, nu presupusa aici.
"""
from __future__ import annotations

import os
import sys
from datetime import date
from decimal import Decimal

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import d406_active as _d406          # noqa: E402
from core import migrare_reevaluare as _mig    # noqa: E402
from core import repo_mijloace_fixe as _rmf    # noqa: E402
from core import repo_reevaluari as _rr        # noqa: E402

SCH = "tenant_proba_r59"

# Scenariul, DECLARAT (cifrele se pot reface cu creionul):
#   activ 3.000 lei, rezidual 0, durata 60 de luni, liniar, PIF 15.01.2026  -> rata veche 50,00
#   reevaluare la 20.03.2026, valoare justa 3.500
#     amortizare cumulata la 20.03 = 2 luni (feb, mar) x 50 = 100,00
#     valoare neta = 2.900 ; diferenta = 600 ; linii: 2813=2131 100 · 2131=105 600
#   dupa aplicare: valoare bruta 3.500, durata ramasa 60-2 = 58  -> rata noua 3.500/58 = 60,34
VALOARE = Decimal("3000")
DNF = 60
PIF = date(2026, 1, 15)
DATA_REEV = date(2026, 3, 20)
JUSTA = Decimal("3500")
RATA_VECHE = Decimal("50.00")
AM_LA_REEV = Decimal("100.00")
RATA_NOUA = Decimal("60.34")          # 3500 / 58, ROUND_HALF_UP


# `xml_asset` intoarce un FRAGMENT cu prefix `nsSAFT:` si fara declaratia spatiului de nume; se
# inveleste ca sa poata fi PARSAT. Se aserteaza pe ELEMENTE, nu pe siruri: un
# `"<X>3500.00</X>" in xml` ar trece si daca elementul ar ajunge sub alt parinte, si ar cadea la o
# schimbare de spatii albe care nu schimba nimic. METODA §23.
_NS = "mfp:anaf:dgti:d406:declaratie:v1"


def _valuation(fragment):
    """{nume_element: text} din `<Valuation>`-ul unui `<Asset>`."""
    import xml.etree.ElementTree as ET
    rad = ET.fromstring('<r xmlns:nsSAFT="%s">%s</r>' % (_NS, fragment))
    val = rad.find(".//{%s}Valuation" % _NS)
    assert val is not None, "fragmentul n-are <Valuation> — s-a schimbat structura, nu cifra"
    return {e.tag.split("}")[-1]: (e.text or "") for e in val}


def _mf(reevaluari=()):
    return {"cod": "MF-R59", "denumire": "Utilaj proba R59",
            "cont_imobilizare": "2131", "cont_amortizare": "2813",
            "valoare": JUSTA if reevaluari else VALOARE, "rezidual": Decimal("0"),
            "dnf_luni": DNF, "data_pif": PIF, "metoda": "liniara",
            "reevaluari": list(reevaluari)}


_REEV = ({"data": DATA_REEV, "valoare_bruta_veche": VALOARE,
          "amortizare_eliminata": AM_LA_REEV, "valoare_justa": JUSTA},)


# ─────────────────────────── motorul, fara baza de date ───────────────────────────

def test_fara_reevaluari_motorul_e_NESCHIMBAT():
    """Calibrare pe directia tacuta: fara reevaluari aplicate, nimic nu se misca.

    Un motor care s-ar comporta altfel pe activul obisnuit ar fi mutat defectul, nu l-ar fi reparat
    — iar cele ~4.000 de active fara reevaluare sunt tocmai cazul care nu trebuie atins.
    """
    mf = _mf()
    assert _d406._mf_la(mf, date(2026, 12, 31))[0] is mf, \
        "fara reevaluari `_mf_la` intoarce alt obiect — exista o a doua cale pentru cazul obisnuit"
    assert _d406.amortizare_luna(mf, 2026, 2) == RATA_VECHE
    assert _d406.amortizat_la_data(mf, DATA_REEV)["amortizat"] == AM_LA_REEV
    assert _d406.calc_asset(mf, 2026)["apreciere"] == Decimal("0.00")


def test_amortizarea_cumulata_de_dinaintea_reevaluarii_e_cea_care_SE_ELIMINA():
    """Cifra pe care ruta o pune pe linia `2813 = 2131` — OMFP 1802/2014 pct.111-116."""
    assert _d406.amortizat_la_data(_mf(), DATA_REEV)["amortizat"] == AM_LA_REEV


def test_dupa_reevaluare_amortizarea_PORNESTE_DE_LA_ZERO_pe_valoarea_justa():
    """Metoda valorii nete: cumulata s-a eliminat, deci de la data reevaluarii se amortizeaza
    valoarea JUSTA pe durata RAMASA. Fara etapa, motorul ar da 3.500/60 de la PIF-ul din ianuarie
    — o amortizare pe care n-a inregistrat-o nicio nota."""
    mf = _mf(_REEV)
    assert _d406.amortizare_luna(mf, 2026, 3) == Decimal("0.00"), \
        "luna reevaluarii se amortizeaza inca o data pe etapa noua — a fost deja in cei 100 eliminati"
    assert _d406.amortizare_luna(mf, 2026, 4) == RATA_NOUA
    # aprilie..decembrie = 9 luni pe rata noua; cumulata NU mai poarta cei 100 eliminati
    assert _d406.amortizat_la_data(mf, date(2026, 12, 31))["amortizat"] == RATA_NOUA * 9
    assert _d406.amortizat_la_data(mf, DATA_REEV)["amortizat"] == Decimal("0.00")


def test_bornele_anului_se_calculeaza_pe_ETAPE_DIFERITE():
    """Un activ mai vechi, reevaluat in cursul anului: 31.12.<an-1> e pe valoarea VECHE.

    E greseala pe care am facut-o construind: prima forma intorcea activul neatins pentru datele
    dinaintea primei reevaluari, deci borna de deschidere se calcula pe valoarea de DUPA.
    """
    mf = dict(_mf(_REEV))
    mf["data_pif"] = date(2025, 1, 15)
    ef, _ = _d406._mf_la(mf, date(2025, 12, 31))
    assert Decimal(str(ef["valoare"])) == VALOARE, \
        "borna de deschidere citeste valoarea de DUPA reevaluare (%s)" % ef["valoare"]


def test_anul_reevaluarii_declara_APRECIEREA_si_costul_de_DESCHIDERE():
    """`cost_begin` = `cost_end` intr-un an in care valoarea s-a schimbat ar fi o afirmatie falsa
    despre soldul de deschidere — exact felul de cifra pe care R59 il numeste."""
    mf = dict(_mf(_REEV))
    mf["data_pif"] = date(2025, 1, 15)          # achizitionat inainte, ca `cost_begin` sa conteze
    v = _d406.calc_asset(mf, 2026)
    assert v["cost_begin"] == VALOARE
    assert v["cost_end"] == JUSTA
    assert v["apreciere"] == JUSTA - VALOARE


def test_amortizarea_ANULUI_e_suma_ratelor_lunare_nu_diferenta_bornelor():
    """In anul reevaluarii, diferenta bornelor ar scadea o ELIMINARE din cheltuiala si ar putea
    iesi negativa. Ce se raporteaza e cheltuiala anului — adica exact ce inregistreaza nota lunara
    de amortizare (6811 = 28xx). *Un singur motor pentru declaratie si evidenta.*"""
    mf = dict(_mf(_REEV))
    mf["data_pif"] = date(2025, 1, 15)
    v = _d406.calc_asset(mf, 2026)
    lunar = sum((_d406.amortizare_luna(mf, 2026, l) for l in range(1, 13)), Decimal("0.00"))
    assert v["depr_period"] == lunar
    assert v["depr_period"] > 0, "cheltuiala anului a iesit <= 0 — bornele s-au scazut din nou"


def test_reevaluare_peste_o_durata_EPUIZATA_se_REFUZA_nu_se_fabrica():
    """Durata ramasa dupa o reevaluare tarzie vine din raportul evaluatorului (OMFP 1802 pct.113).
    Registrul n-o poate deriva — deci se ridica, nu se ghiceste o durata «rezonabila»."""
    mf = dict(_mf(_REEV))
    mf["dnf_luni"] = 2                       # cele doua luni erau deja toata durata
    # Pe TIPUL exceptiei, nu pe un cuvant din mesaj: motivul refuzului trebuie asertat (un test care
    # accepta orice refuz nu apara motivul), dar un `"evaluatorului" in str(e)` ar pazi formularea,
    # nu regula. De-aia refuzul poarta clasa lui. METODA §23.
    with pytest.raises(_d406.DurataEpuizata):
        _d406.amortizare_luna(mf, 2026, 4)
    # si ramane un `ValueError`, ca apelantii care il prind deja sa nu se schimbe
    assert issubclass(_d406.DurataEpuizata, ValueError)


def test_o_reevaluare_NEAPLICATA_nu_atinge_amortizarea():
    """`_reev_aplicate` primeste doar randuri APLICATE (depozitul filtreaza `aplicata_la`), dar
    garda cere si ca lipsa cheii sa insemne «niciuna», nu «necunoscut tratat ca da»."""
    mf = _mf()
    mf.pop("reevaluari")
    assert _d406._reev_aplicate(mf) == []
    assert _d406.amortizare_luna(mf, 2026, 4) == RATA_VECHE


# ─────────────────────────── lantul, pe schema efemera ───────────────────────────

def _db():
    try:
        from core import db
        db.init_pool()
        return db
    except Exception:
        return None


@pytest.fixture
def schema():
    db = _db()
    if not db:
        pytest.skip("fara db.env local")
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)
            c.execute('CREATE SCHEMA "%s"' % SCH)
            c.execute('CREATE TABLE "%s".mijloace_fixe (id integer GENERATED ALWAYS AS IDENTITY '
                      'PRIMARY KEY, cod text, denumire text NOT NULL, cont_imobilizare text, '
                      'cont_amortizare text, valoare numeric NOT NULL DEFAULT 0, rezidual numeric '
                      "DEFAULT 0, dnf_luni integer NOT NULL DEFAULT 12, data_pif date, metoda text "
                      "DEFAULT 'liniara', activ boolean DEFAULT true, creat_la timestamptz DEFAULT now())" % SCH)
        # Tabelul `reevaluari` se ia din MIGRARE, nu se rescrie aici: o a doua definitie a aceluiasi
        # DDL s-ar desparti tacut de prima, iar proba ar trece pe o schema care nu exista nicaieri.
        _mig.aplica(conn, SCH)
    try:
        yield db
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as c:
                c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)


def _activ(db):
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".mijloace_fixe (cod, denumire, cont_imobilizare, '
                      "cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda) "
                      "VALUES ('MF-R59','Utilaj proba R59','2131','2813',%%s,0,%%s,%%s,'liniara') "
                      "RETURNING id" % SCH, (VALOARE, DNF, PIF))
            return c.fetchone()[0]


def _valoarea(db, mid):
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('SELECT valoare FROM "%s".mijloace_fixe WHERE id=%%s' % SCH, (mid,))
            return Decimal(str(c.fetchone()[0]))


def test_LANT_ciorna_nu_misca_registrul_validarea_il_misca(schema):
    """Cele DOUA capete ale criteriului, plus momentul dintre ele."""
    from core import uc_tenants as _uc
    db = schema
    mid = _activ(db)
    NOTA = 4242

    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _rr.consemneaza(cur, SCH, NOTA, mid, DATA_REEV, VALOARE, AM_LA_REEV, JUSTA)

    # (a) consemnata, NEaplicata: registrul e neatins — nota e inca o propunere
    assert _valoarea(db, mid) == VALOARE, "registrul s-a miscat din CIORNA"
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            assert _rmf.active_pentru_d406(cur, SCH, 2026)[0][-1] == [], \
                "o reevaluare neaplicata ajunge in motorul de amortizare"

    # (b) validarea o aplica
    with db.get_conn() as conn:
        assert _uc._aplica_reevaluarea(conn, SCH, NOTA) is True

    # criteriul (1): coloana din registru
    assert _valoarea(db, mid) == JUSTA

    # criteriul (2): declaratia o declara
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            randuri = _rmf.active_pentru_d406(cur, SCH, 2026)
            cols = [d[0] for d in cur.description]
    mf = dict(zip(cols, randuri[0]))
    assert len(mf["reevaluari"]) == 1, "randul aplicat nu ajunge la motor prin interogare"
    v = _valuation(_d406.xml_asset(mf, 2026))
    assert v["AcquisitionAndProductionCostsEnd"] == "3500.00", \
        "Assets declara tot costul vechi: %s" % v["AcquisitionAndProductionCostsEnd"]
    assert v["AppreciationForPeriod"] == "500.00"
    assert Decimal(v["BookValueEnd"]) == JUSTA - Decimal(v["AccumulatedDepreciation"]), \
        "valoarea ramasa nu se leaga de cost minus cumulata: %s" % v


def test_LANT_a_doua_validare_nu_urca_valoarea_inca_o_data(schema):
    """Idempotenta prin DATE. O fila deschisa de doua ori, un retry, o repornire — toate produc a
    doua validare a aceleiasi note, iar a doua aplicare n-ar lasa nicio urma ca a fost a doua."""
    from core import uc_tenants as _uc
    db = schema
    mid = _activ(db)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _rr.consemneaza(cur, SCH, 77, mid, DATA_REEV, VALOARE, AM_LA_REEV, JUSTA)
    with db.get_conn() as conn:
        assert _uc._aplica_reevaluarea(conn, SCH, 77) is True
    with db.get_conn() as conn:
        assert _uc._aplica_reevaluarea(conn, SCH, 77) is False
    assert _valoarea(db, mid) == JUSTA


def test_LANT_o_nota_oarecare_nu_declanseaza_nimic(schema):
    """Cele mai multe note n-au legatura cu mijloacele fixe: aplicarea tace, nu cade."""
    from core import uc_tenants as _uc
    db = schema
    _activ(db)
    with db.get_conn() as conn:
        assert _uc._aplica_reevaluarea(conn, SCH, 999999) is False


# ─────────────────────────── anti-vacuu pe interogari ───────────────────────────

def test_ANTI_VACUU_fiecare_citire_care_hraneste_motorul_aduce_reevaluarile():
    """O interogare viitoare care ar uita coloana ar da inapoi amortizarea de dinainte de R59, iar
    totul ar arata verde: activul exista, cifrele sunt plauzibile, nimic nu e `None`.

    Se cere pe STRUCTURA — arborele de sintaxa al modulului —, nu pe textul fisierului: numele
    `_REEV` ar putea aparea si intr-un comentariu (METODA §23).
    """
    import ast
    import inspect
    arbore = ast.parse(inspect.getsource(_rmf))
    citiri = {"de_amortizat", "active_pentru_d406", "pentru_reevaluare", "toate",
              "pentru_inventariere"}
    vazute = set()
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.FunctionDef) and nod.name in citiri:
            if any(isinstance(n, ast.Name) and n.id == "_REEV" for n in ast.walk(nod)):
                vazute.add(nod.name)
    assert vazute == citiri, "citiri fara reevaluari: %s" % sorted(citiri - vazute)


def test_ANTI_VACUU_validarea_notei_CHEAMA_aplicarea():
    """Legatura dintre validare si efect, ceruta pe ARBORE.

    Fara ea, cea mai simpla mutatie — scoaterea apelului din `jurnal_valideaza` — ar lasa toate
    probele de mai sus verzi: ele cheama `_aplica_reevaluarea` de-a dreptul. *O proba care sare
    exact peste cablu masoara piesa, nu instalatia.*

    Si se cere si ordinea: aplicarea sta SUB verificarea ca validarea a reusit. Altfel registrul
    s-ar misca si pentru o nota respinsa („nota nu e ciorna", „nota nu are linii").
    """
    import ast
    import inspect
    from core import uc_tenants as _uc
    fn = next(n for n in ast.walk(ast.parse(inspect.getsource(_uc.jurnal_valideaza)))
              if isinstance(n, ast.FunctionDef) and n.name == "jurnal_valideaza")
    apeluri = [n for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "_aplica_reevaluarea"]
    assert apeluri, "`jurnal_valideaza` nu mai cheama `_aplica_reevaluarea` — cablul e taiat"
    sub_conditie = [n for n in ast.walk(fn) if isinstance(n, ast.If)
                    for x in ast.walk(n) if x in apeluri]
    assert sub_conditie, "aplicarea nu mai sta sub verificarea reusitei — s-ar aplica si pe refuz"
