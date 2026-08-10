# -*- coding: utf-8 -*-
"""core/test_control_reconciliere_vizibila.py — GARD pentru SUPRAFATA UNIFICATA de reconciliere
sursa<->declaratie expusa in Control fiscal (Tura 4).

control_incrucisat.reconciliaza_declaratii refoloseste ACEEASI reconciliere ca poarta de generare
(dXXX_reconciliere.reconciliaza) si o arata ca verdict cu trei stari. Acest gard probeaza:

(a) o firma a carei declaratie se reconciliaza -> constatare VERDE (calea reala, schema efemera);
(b) ANTI-MORT: o divergenta sursa<->declaratie (simulata ca aggregation-loss in generator, exact
    bug-ul pe care gardul il apara) -> constatare ROSIE care NUMESTE AMBELE valori (nu gri, nu tacut);
(c) REGRESIA "D300 mort": un apel de reconciliere RUPT (deriva de semnatura -> TypeError) NU devine
    tacit gri, ci ROSU "verificare intrerupta" (vezi core/test_control_incrucisat_wiring.py);
(d) VIZIBILITATE: reconcilierea curge prin control_fiscal_api.evalueaza_firma (reconciliere_surse) si
    o constatare ROSIE escaladeaza pastila firmei (common.pastila_firma), gri-ul NU.

DE CE divergenta se SIMULEAZA in generator, nu prin mutatie pura de DB: reconciliatoarele sunt
tautology-resistant PRIN DESIGN (recalcul INDEPENDENT al ACELEIASI surse) - o mutatie de DB schimba
SIMETRIC ambele cai, deci NU produce divergenta intr-un build corect. Singura divergenta reala e un
BUG de generator (agregare pierduta). Il injectam patchand calcul_d300 sa umfle un rand -> reconcilierul
REAL (recalcul din liniile curate) prinde divergenta si o numeste. Schema e efemera (drop + rollback).
"""
import pytest

from core import db as _db, tenant_provisioning as _tp
from core import control_incrucisat as ci
from core.common import pastila_firma

SCH = "ztest_recon_vizibil"
AN, LUNA = 2026, 6


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _schema_cu_factura(cur, cota=21):
    """Firma PFA (partida simpla) platitoare de TVA lunar, cu O factura emisa la `cota`% si o linie.
    partida simpla + fara salariati + fara IC -> planul de reconciliere = DOAR D300 + D394 (setup minim)."""
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute('SET search_path TO "%s", public' % SCH)
    cur.execute("""INSERT INTO firma_profil
        (id,nume,cui,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,tip_firma,
         declarant_nume,declarant_prenume,declarant_functie)
        VALUES (1,'ZTEST RECON PFA','14399840','Str 1','Buc','B','6202','Banca Test',
         'RO49AAAA1B31007593840000','lunar',true,'pfa','Ada','Ada','ADMINISTRATOR')""")
    cur.execute("""INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status)
        VALUES ('E-1','2026-06-10','emisa',1210,210,'RO14399840','CLIENT SRL','emisa') RETURNING id""")
    fid = cur.fetchone()[0]
    cur.execute("""INSERT INTO factura_linii (factura_id,descriere,cantitate,pret_unitar,cota_tva)
        VALUES (%s,'serviciu',1,1000,%s)""", (fid, cota))
    return fid


def _constatare(rez, cheie):
    return next((c for c in rez["constatari"] if c.get("declaratie") == cheie), None)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_a_firma_care_se_reconciliaza_da_verde():
    """(a) Firma cu date coerente -> D300 se reconciliaza cu sursa -> constatare VERDE, stare generala verde."""
    _db.init_pool()
    p = _db.pool(); conn = p.getconn()
    try:
        with conn.cursor() as cur:
            _schema_cu_factura(cur)
        rez = ci.reconciliaza_declaratii(conn, SCH, AN, LUNA)
        d300 = _constatare(rez, "d300")
        assert d300 is not None, "D300 lipseste din plan (asteptat: PFA platitor -> D300+D394)"
        assert d300["stare"] == "verde", "D300 ar trebui sa se reconcilieze: %r" % d300
        assert rez["stare"] == "verde", "stare generala %r (constatari: %s)" % (
            rez["stare"], [(c["declaratie"], c["stare"]) for c in rez["constatari"]])
        # constatare STRUCTURATA (nu string colapsat): are dot + mesaj + temei
        assert d300["eticheta"] and d300["mesaj"] and d300["temei"]
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_b_divergenta_da_rosu_numind_ambele_valori(monkeypatch):
    """(b) ANTI-MORT: generator umflat cu 100 lei TVA colectat (aggregation-loss simulat) -> reconcilierul
    REAL prinde divergenta -> constatare ROSIE care numeste AMBELE valori (310 declarat vs 210 din sursa),
    NU gri, NU tacut. Old-vs-new: reconciliatorul real intoarce divergente nevide (nu le inghite)."""
    import core.d300 as d300mod
    orig = d300mod.calcul_d300

    def _umflat(prof, per, facturi, manual=None):
        res = orig(prof, per, facturi, manual)
        res.R["R9_2"] = int(res.R.get("R9_2", 0)) + 100   # +100 lei TVA colectat 21% peste ce sustine sursa
        return res
    monkeypatch.setattr("core.d300.calcul_d300", _umflat)

    _db.init_pool()
    p = _db.pool(); conn = p.getconn()
    try:
        with conn.cursor() as cur:
            _schema_cu_factura(cur)
        rez = ci.reconciliaza_declaratii(conn, SCH, AN, LUNA)
        d300 = _constatare(rez, "d300")
        assert d300 is not None
        assert d300["stare"] == "rosu", "divergenta trebuie ROSIE, nu %r" % d300["stare"]
        assert d300["stare"] != "gri", "divergenta NU e 'nu pot verifica' (gri) - regresia D300 mort"
        # NUMESTE AMBELE VALORI: 310 (declarat umflat) si 210 (recalcul din sursa)
        assert "310" in d300["mesaj"] and "210" in d300["mesaj"], (
            "mesajul trebuie sa numeasca ambele valori: %r" % d300["mesaj"])
        assert rez["stare"] == "rosu"
        # OLD-vs-NEW: acelasi reconciliator REAL, chemat direct, chiar RAPORTEAZA divergenta (nu o ascunde)
        from core import d300_reconciliere
        from core.common import Perioada
        from core import d300 as g
        per = Perioada(AN, luna=LUNA)
        prof, facturi = g.pull(conn, SCH, per)
        rap = d300_reconciliere.reconciliaza(conn, per, g.calcul_d300(prof, per, facturi, None), None)
        assert rap["divergente"], "reconciliatorul real ar trebui sa raporteze divergenta sub patch"
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c_reconciliator_rupt_nu_devine_gri_tacut(monkeypatch):
    """(c) REGRESIA "D300 mort": reconciliaza rupt prin deriva de semnatura (TypeError) NU se inghite tacit
    intr-un gri, ci iese ROSU "verificare intrerupta". Old-vs-new: apelul chiar ridica (deci vechiul
    except->gri l-ar fi facut gri), dar suprafata noua il face ROSU."""
    def _rupt(*a, **k):
        raise TypeError("semnatura reconciliaza schimbata (deriva) - simulare D300 mort")
    monkeypatch.setattr("core.d300_reconciliere.reconciliaza", _rupt)

    _db.init_pool()
    p = _db.pool(); conn = p.getconn()
    try:
        with conn.cursor() as cur:
            _schema_cu_factura(cur)
        rez = ci.reconciliaza_declaratii(conn, SCH, AN, LUNA)
        d300 = _constatare(rez, "d300")
        assert d300 is not None
        assert d300["stare"] == "rosu", "apel rupt trebuie ROSU (zgomotos), nu %r" % d300["stare"]
        assert d300["stare"] != "gri", "REGRESIE D300 mort: apelul rupt a devenit gri tacut"
        assert "INTRERUPTA" in d300["eticheta"].upper(), "eticheta trebuie sa spuna ca verificarea s-a rupt"
        assert rez["stare"] == "rosu"
        # OLD-vs-NEW: apelul chiar ridica TypeError (dovada rupturii). Vechiul `except Exception -> gri`
        # (main._incrucisat, verifica_tva) l-ar fi transformat in gri; suprafata noua il face rosu.
        with pytest.raises(TypeError):
            import core.d300_reconciliere as _r
            _r.reconciliaza(conn, None, None, None)
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d_vizibil_in_control_fiscal_si_escaladeaza_pastila(monkeypatch):
    """(d) VIZIBILITATE: reconcilierea curge prin evalueaza_firma (reconciliere_surse) si o divergenta
    ROSIE escaladeaza pastila firmei. Escaladarea prin common.pastila_firma: rosu urca o baza verde la
    rosu; gri NU escaladeaza."""
    import core.d300 as d300mod
    from core import control_fiscal_api as cf
    orig = d300mod.calcul_d300

    def _umflat(prof, per, facturi, manual=None):
        res = orig(prof, per, facturi, manual)
        res.R["R9_2"] = int(res.R.get("R9_2", 0)) + 100
        return res
    monkeypatch.setattr("core.d300.calcul_d300", _umflat)

    import datetime
    azi = datetime.date(2026, 7, 15)   # ultima luna inchisa = 2026-06 (unde traieste factura)
    _db.init_pool()
    p = _db.pool(); conn = p.getconn()
    try:
        with conn.cursor() as cur:
            _schema_cu_factura(cur)
        with _db.get_conn() as conn_public:
            rez = cf.evalueaza_firma(conn, conn_public, 999999, SCH, azi)
        recon = rez.get("reconciliere_surse")
        assert recon is not None, "evalueaza_firma trebuie sa expuna reconciliere_surse"
        assert recon["stare"] == "rosu", "reconcilierea vizibila trebuie rosie: %r" % recon["stare"]
        d300 = _constatare(recon, "d300")
        assert d300 and d300["stare"] == "rosu" and "310" in d300["mesaj"] and "210" in d300["mesaj"]
        assert rez["stare"] == "rosu", "pastila firmei trebuie sa fie rosie (escaladata din reconciliere)"

        # Contractul de escaladare (pur): o constatare ROSIE urca o baza VERDE la rosu; gri NU urca.
        assert pastila_firma("verde", recon["constatari"]) == "rosu"
        gri_only = [{"stare": "gri", "eticheta": "x", "mesaj": "y", "temei": "z"}]
        assert pastila_firma("verde", gri_only) == "verde", "gri nu trebuie sa escaladeze pastila"
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)
