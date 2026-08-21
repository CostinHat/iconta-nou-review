# -*- coding: utf-8 -*-
"""GARDĂ: statul de plată e un DOCUMENT EMIS, nu o vedere recalculată. (21.08.2026)

DATORIA (29.07.2026, restatuată 20.08.2026, `test_datorie_state_plata_se_persista`): statul se
recalcula la fiecare afișare. Un fluturaș dat unui salariat în ianuarie și redeschis în iulie putea
ieși ALTFEL — nu fiindcă s-a greșit ceva, ci fiindcă între timp s-a schimbat cota, salariul minim sau
codul. Pentru un act semnat și predat unui om, asta nu e o problemă de performanță; e una de
integritate: documentul din mâna salariatului și cel din aplicație nu mai sunt același document.

DECIS DE COSTIN (21.08.2026):
  - se persistă LA EMITERE, cu amprentă (ca declarațiile depuse — `amprenta_declaratie.py`);
  - un exemplar persistat care nu mai corespunde recalculului SEMNALEAZĂ, nu tace;
  - corecția e AL DOILEA EXEMPLAR, cu referință la primul — primul nu se rescrie, fiindcă el e cel
    care a ajuns la om;
  - corecția o emite CONTABILUL, nu aplicația; dar contradicția nesoluționată rămâne vizibilă, nu se
    stinge prin ignorare.

DE CE E SCRISĂ ÎNAINTE. Datoria avea deja o gardă (xfail strict), dar ea caută `INSERT INTO
state_plata` în sursă — trece în clipa în care APARE un INSERT, oriunde, orice ar scrie el. Asta
verifică existența unei linii de cod, nu comportamentul actului. Gărzile de aici sunt pe
comportament, și sunt roșii pe HEAD înainte de orice reparație.
"""
import io
import os

import pytest

from core import db

try:
    from core import stat_plata_emis as spe
except Exception:  # pragma: no cover - pe HEAD modulul nu există; gărzile trebuie să fie ROȘII
    spe = None

_LIPSA = pytest.mark.skipif(spe is None, reason="core/stat_plata_emis nu există")


def test_modulul_exista():
    """Roșu pe HEAD. Datoria cere un act de emitere, nu doar un tabel cu coloane."""
    assert spe is not None, (
        "core/stat_plata_emis.py lipsește — statul de plată nu are act de emitere, deci fiecare "
        "afișare produce un document nou")


# ---------------------------------------------------------------- motorul (pur)

RAND = {"id": 7, "nume": "Ionescu Maria", "brut": 5000.0, "cas": 1250.0, "cass": 500.0,
        "impozit": 218.0, "deducere": 620.0, "net": 3032.0, "cam": 112.5,
        "tichete_nominal": 660.0, "total_disponibil": 3692.0, "cm_zile": 0}


@_LIPSA
def test_amprenta_e_deterministica():
    """Aceleași cifre → aceeași amprentă. Fără asta, orice reafișare ar părea o contradicție."""
    assert spe.amprenta_rand(RAND) == spe.amprenta_rand(dict(RAND))


@_LIPSA
def test_amprenta_nu_depinde_de_ordinea_cheilor():
    """Canonizare, nu `str(dict)`: ordinea în care se construiește rândul nu e o schimbare de fond."""
    invers = {k: RAND[k] for k in reversed(list(RAND))}
    assert spe.amprenta_rand(invers) == spe.amprenta_rand(RAND)


@_LIPSA
def test_amprenta_se_schimba_la_un_ban():
    """ANTI-VACUU pe mecanism. Dacă amprenta ar ignora sumele, TOATE testele de mai jos ar trece
    fiindcă nimic nu diferă niciodată — verde despre o lume pe care n-o vede."""
    alt = dict(RAND, net=3032.01)
    assert spe.amprenta_rand(alt) != spe.amprenta_rand(RAND), (
        "un ban diferență nu schimbă amprenta — amprenta nu acoperă sumele documentului")


@_LIPSA
def test_amprenta_ignora_campurile_care_nu_sunt_documentul():
    """Fluturașul e sumele, nu starea interfeței. `pontaj_neconfirmat` sau un nume de coloană de
    editare se schimbă fără ca documentul dat omului să se schimbe — altfel gardul ar striga la
    fiecare refactorizare și s-ar dezactiva (GĂRZI regula 3: un gard cu fals-pozitive moare)."""
    assert spe.amprenta_rand(dict(RAND, pontaj_neconfirmat=True, nume_ed="X")) \
        == spe.amprenta_rand(RAND)


@_LIPSA
def test_contradictia_e_derivata_din_comparatie_nu_dintr_un_camp():
    """Miezul deciziei lui Costin. Contradicția se CALCULEAZĂ din amprenta emisă vs recalcul; nu
    există niciun câmp pe care cineva să-l pună pe zero. Un flag se poate stinge prin apăsare; o
    comparație nu."""
    emis = [{"id": 1, "salariat_id": 7, "exemplar": 1, "amprenta": spe.amprenta_rand(RAND),
             "corectie_la": None, "motiv": None}]
    assert spe.contradictii(emis, [RAND]) == []
    c = spe.contradictii(emis, [dict(RAND, net=2000.0)])
    assert len(c) == 1 and c[0]["salariat_id"] == 7
    assert c[0]["amprenta_emisa"] != c[0]["amprenta_curenta"]


@_LIPSA
def test_motivul_nu_sterge_contradictia_ci_o_asuma():
    """«Rămâne vizibilă, nu se stinge prin ignorare.» Un motiv înregistrat o marchează ASUMATĂ —
    tot în listă, cu decizia și data alături, ca `regula_produs` din harta casetelor."""
    emis = [{"id": 1, "salariat_id": 7, "exemplar": 1, "amprenta": spe.amprenta_rand(RAND),
             "corectie_la": None, "motiv": "recalculul e cel greșit, cota s-a schimbat retroactiv",
             "motiv_de": "costin", "motiv_la": "2026-08-21"}]
    c = spe.contradictii(emis, [dict(RAND, net=2000.0)])
    assert len(c) == 1, "motivul a STINS contradicția — exact ce a interzis Costin"
    assert c[0]["asumata"] is True
    assert c[0]["motiv"] and c[0]["motiv_de"] and c[0]["motiv_la"], (
        "motiv fără cine+când: o asumare anonimă nu e o decizie")


@_LIPSA
def test_corectia_supracrie_vederea_dar_nu_exemplarul():
    """Al doilea exemplar devine documentul curent (față de el se compară de-acum), dar primul rămâne
    în listă — el e cel care a ajuns la om."""
    a1 = spe.amprenta_rand(RAND)
    nou = dict(RAND, net=2000.0)
    emis = [{"id": 1, "salariat_id": 7, "exemplar": 1, "amprenta": a1, "corectie_la": None,
             "motiv": None},
            {"id": 2, "salariat_id": 7, "exemplar": 2, "amprenta": spe.amprenta_rand(nou),
             "corectie_la": 1, "motiv": None}]
    assert spe.contradictii(emis, [nou]) == [], "corecția emisă nu a stins contradicția"
    assert spe.ultimul(emis, 7)["exemplar"] == 2
    assert spe.ultimul(emis, 7)["corectie_la"] == 1, "corecția nu referă exemplarul pe care îl repară"


@_LIPSA
def test_un_salariat_fara_exemplar_nu_e_contradictie():
    """Regula bazei nule, în direcția corectă: cine n-a primit fluturaș nu are ce contrazice.
    Absența unui document emis NU e o divergență — e o absență, și se numește altfel."""
    assert spe.contradictii([], [RAND]) == []


# ---------------------------------------------------------------- actul (pe DB)

def _tenant():
    try:
        db.init_pool()
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name LIMIT 1")
            r = cur.fetchone()
        return r[0] if r else None
    except Exception:
        return None


_SCH = _tenant()
_DB = pytest.mark.skipif(_SCH is None, reason="DB/tenant indisponibil")


def _amprenta_curenta(conn, sid, an, luna):
    from core import stat_plata_api as _sp
    r = next((x for x in _sp.stat_plata(conn, _SCH, an, luna) if int(x.get("id") or 0) == sid), None)
    return spe.amprenta_rand(r) if r else None


def _muta_baza(conn, sid, an, luna):
    """Mută baza de calcul pe SURSA UNICĂ (`salariu_istoric.seteaza`) și DOVEDEȘTE că recalculul s-a
    mișcat.

    Prima formă a acestui ajutor făcea `UPDATE salariu_istoric SET salariu_brut = salariu_brut + 1000`
    și trecea. Tenantul are istoricul GOL — salariul vine din bridge-ul `salariati.salariu_brut` —
    deci UPDATE-ul prindea ZERO rânduri, recalculul nu se clintea, iar două teste verificau o lume
    nemișcată: unul „a rezistat" fiindcă nimic nu se schimbase. Aserțiunea de mai jos e ce le-a scos."""
    from datetime import date as _date

    from core import salariu_istoric as _si
    inainte = _amprenta_curenta(conn, sid, an, luna)
    with conn.cursor() as cur:
        cur.execute("SELECT salariu_brut FROM salariati WHERE id=%s", (sid,))
        baza = float(cur.fetchone()[0] or 0)
        _si.seteaza(cur, sid, baza + 1000, _date(an, luna, 1))
    dupa = _amprenta_curenta(conn, sid, an, luna)
    assert dupa != inainte, (
        "mutația nu a schimbat recalculul — testul ar verifica o lume nemișcată, iar «documentul a "
        "rezistat» ar însemna doar că nimeni n-a atins nimic")
    return dupa


@pytest.fixture
def pe_tenant():
    """Scrie pe un tenant REAL, apoi ANULEAZĂ. Nimic nu rămâne: statul de plată e keyed pe (salariat,
    lună) — o fixtură care ar comite ar lăsa exemplare fantomă într-o lună reală a unei firme reale."""
    with db.get_conn(_SCH) as conn:
        spe.aplica(conn, _SCH)
        try:
            yield conn
        finally:
            conn.rollback()


@_LIPSA
@_DB
def test_emiterea_persista_documentul(pe_tenant):
    """Actul: după emitere, exemplarele EXISTĂ în bază, cu amprentă și cu cifrele înghețate."""
    em = spe.emite(pe_tenant, _SCH, 2026, 6, de_cine="garda")
    if not em:
        pytest.skip("tenantul nu are salariați activi în 2026-06")
    citit = spe.citeste(pe_tenant, _SCH, 2026, 6)
    assert len(citit) == len(em)
    assert all(x["amprenta"] and x["date"] for x in citit), "exemplar fără amprentă sau fără cifre"
    assert all(x["exemplar"] == 1 and x["corectie_la"] is None for x in citit)
    # A doua apasare nu produce al doilea document. RED-proof-ul (M6) a aratat ca nimic nu asertea
    # asta: mutatia care scotea idempotenta trecea, fiindca testul chema `emite` o singura data.
    assert spe.emite(pe_tenant, _SCH, 2026, 6, de_cine="garda") == [], (
        "a doua emitere a produs exemplare noi - un al doilea exemplar e o CORECTIE, se apasa explicit")
    assert len(spe.citeste(pe_tenant, _SCH, 2026, 6)) == len(citit)


@_LIPSA
@_DB
def test_documentul_emis_nu_se_schimba_cand_se_schimba_datele(pe_tenant):
    """DATORIA ÎNSĂȘI. Se mută salariul de bază sub un stat deja emis; documentul emis trebuie să
    întoarcă aceleași cifre. Dacă se schimbă, «emis» înseamnă tot «recalculat»."""
    em = spe.emite(pe_tenant, _SCH, 2026, 6, de_cine="garda")
    if not em:
        pytest.skip("tenantul nu are salariați activi în 2026-06")
    sid = em[0]["salariat_id"]
    inainte = spe.citeste(pe_tenant, _SCH, 2026, 6, salariat_id=sid)[0]
    _muta_baza(pe_tenant, sid, 2026, 6)
    dupa = spe.citeste(pe_tenant, _SCH, 2026, 6, salariat_id=sid)[0]
    assert dupa["amprenta"] == inainte["amprenta"]
    assert dupa["date"] == inainte["date"], "documentul emis s-a schimbat sub mâna salariatului"


@_LIPSA
@_DB
def test_divergenta_se_semnaleaza_si_nu_emite_singura_corectia(pe_tenant):
    """«Se semnalează, nu tace» + «contabilul decide»: după ce datele se mișcă, verificarea
    raportează contradicția ȘI nu creează niciun exemplar nou."""
    em = spe.emite(pe_tenant, _SCH, 2026, 6, de_cine="garda")
    if not em:
        pytest.skip("tenantul nu are salariați activi în 2026-06")
    sid = em[0]["salariat_id"]
    _muta_baza(pe_tenant, sid, 2026, 6)
    c = spe.verifica(pe_tenant, _SCH, 2026, 6)
    assert any(x["salariat_id"] == sid for x in c), "divergența a trecut în tăcere"
    assert len(spe.citeste(pe_tenant, _SCH, 2026, 6)) == len(em), (
        "verificarea a emis singură o corecție — decizia e a contabilului, nu a aplicației")


@_LIPSA
@_DB
def test_verificarea_nu_scrie_nimic(pe_tenant):
    """Clasa arsă deja o dată (`test_get_fara_scriere`): o sondă «de citire» a lăsat 24 de rânduri în
    exact acest tabel. Numărătoare înainte/după, nu încredere în numele funcției."""
    em = spe.emite(pe_tenant, _SCH, 2026, 6, de_cine="garda")
    if not em:
        pytest.skip("tenantul nu are salariati activi in 2026-06")
    # PROVOACA divergenta INTAI. Prima forma numara pe o lume fara nicio contradictie: o verificare
    # care emite singura corectii ar fi trecut, fiindca n-avea ce corecta. RED-proof-ul (M4) a
    # aratat-o - un gard care nu poate vedea cazul periculos nu-l pazeste.
    _muta_baza(pe_tenant, em[0]["salariat_id"], 2026, 6)
    with pe_tenant.cursor() as cur:
        cur.execute('SELECT count(*) FROM "%s".state_plata' % _SCH)
        inainte = cur.fetchone()[0]
    assert spe.verifica(pe_tenant, _SCH, 2026, 6), "fara divergenta, testul n-ar proba nimic"
    spe.verifica(pe_tenant, _SCH, 2026, 6)
    with pe_tenant.cursor() as cur:
        cur.execute('SELECT count(*) FROM "%s".state_plata' % _SCH)
        assert cur.fetchone()[0] == inainte, "verificarea a scris în state_plata"


@_LIPSA
@_DB
def test_corectia_e_al_doilea_exemplar_cu_referinta_la_primul(pe_tenant):
    """«Fluturașul e un document dat unui om»: primul exemplar rămâne în bază, cu cifrele lui, iar al
    doilea îl referă. Nu UPDATE peste primul — ăla ar șterge ce s-a dat."""
    em = spe.emite(pe_tenant, _SCH, 2026, 6, de_cine="garda")
    if not em:
        pytest.skip("tenantul nu are salariați activi în 2026-06")
    sid = em[0]["salariat_id"]
    primul = spe.citeste(pe_tenant, _SCH, 2026, 6, salariat_id=sid)[0]
    _muta_baza(pe_tenant, sid, 2026, 6)
    al_doilea = spe.corectie(pe_tenant, _SCH, sid, 2026, 6, de_cine="costin")
    toate = spe.citeste(pe_tenant, _SCH, 2026, 6, salariat_id=sid)
    assert len(toate) == 2, "corecția a înlocuit exemplarul, nu l-a urmat"
    vechi = [x for x in toate if x["id"] == primul["id"]][0]
    assert vechi["amprenta"] == primul["amprenta"] and vechi["date"] == primul["date"]
    assert al_doilea["exemplar"] == 2 and al_doilea["corectie_la"] == primul["id"]
    assert spe.verifica(pe_tenant, _SCH, 2026, 6) == [] or all(
        x["salariat_id"] != sid for x in spe.verifica(pe_tenant, _SCH, 2026, 6)), (
        "corecția emisă nu a rezolvat contradicția")


@_LIPSA
@_DB
def test_motivarea_cere_cine_si_cand(pe_tenant):
    """O asumare anonimă nu e o decizie. Fără autor, motivarea trebuie să fie refuzată."""
    em = spe.emite(pe_tenant, _SCH, 2026, 6, de_cine="garda")
    if not em:
        pytest.skip("tenantul nu are salariați activi în 2026-06")
    with pytest.raises(ValueError):
        spe.motiveaza(pe_tenant, _SCH, em[0]["id"], "", de_cine="costin")
    with pytest.raises(ValueError):
        spe.motiveaza(pe_tenant, _SCH, em[0]["id"], "recalculul e cel greșit", de_cine="")


# ---------------------------------------------------------------- doc ↔ cod

@_LIPSA
def test_datoria_nu_mai_e_declarata_ca_deschisa():
    """DOC↔COD (METODA §7): dacă actul există, datoria din `test_datorie.py` nu mai are voie să
    descrie o lume în care el lipsește. xfail-ul strict cade singur — dar formularea rămâne, și ea
    minte. Gardul ăsta o ține sincronizată."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_datorie.py")
    t = io.open(p, encoding="utf-8").read()
    assert "state_plata nu se persista LA EMITERE" not in t, (
        "datoria state_plata încă e scrisă ca deschisă, deși actul de emitere există — scoate xfail-ul "
        "și consemnează închiderea")
