# -*- coding: utf-8 -*-
"""GARDĂ: fluturașul TIPĂREȘTE statul, nu îl recalculează. (21.08.2026)

CE S-A MĂSURAT. `fluturas_pdf` își refăcea singur tot calculul, cu alte intrări decât `stat_plata`.
Pe datele reale, 14 din 192 de perechi (salariat × lună) ieșeau DIFERIT — verificat pe funcția reală,
nu pe o reimplementare (prima măsurătoare a fost pe o reimplementare, adică pe exact felul de logică
paralelă pe care îl caut). Două cauze, ambele cu fluturașul în greșeală:

  1. `pontaj neconfirmat` — statul BLOCHEAZĂ tichetele de masă (HG 1045/2018 art.10(3): pe zile efectiv
     lucrate), fluturașul le acorda. tenant_003 / Popescu Ana / 2026-07: stat net 2983,39 vs fluturaș
     2808,59 — omul primea pe hârtie 920 lei de tichete pe care statul nu i-i dădea.
  2. `vacanță peste plafonul anual` (6 salarii minime) — statul mută excesul în venit salarial,
     fluturașul nu. tenant_001 / 2026-06: brut 10500 vs 4800, CAS 2625 vs 1200.

Nu e o chestiune de preferință: statul aplică regulile, fluturașul nu le aplica. Fluturașul e cel
care se repară — devine RANDARE peste rândul statului, nu un al doilea calcul.

DE CE ACUM. Statul se emite și se îngheață (`stat_plata_emis`). Un document emis pe care fluturașul
îl retipărește altfel ar face înghețarea inutilă: ai avea o amprentă pe cifre pe care nimeni nu le
vede. Deci fluturașul trebuie să tipărească exemplarul EMIS când există, și rândul statului când nu.
"""
import re
from io import BytesIO

import pytest

from core import db, perioada as _per, salarizare, stat_plata_api as _sp

BANI = ("brut", "cas", "cass", "impozit", "deducere", "net", "cam", "tichete_nominal",
        "tichete_vacanta", "cadou", "cost", "cm_brut", "tichete_zile", "cm_zile")


def _scheme():
    try:
        db.init_pool()
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            return [r[0] for r in cur.fetchall()]
    except Exception:      # MASCA MOTIVATA: fara DB testele se sar; taceri doar pe indisponibilitate
        return []


SCHEME = _scheme()
_DB = pytest.mark.skipif(not SCHEME, reason="DB/tenant indisponibil")
LUNI = [(2026, m) for m in range(1, 9)]


def _fara_calcul(fn):
    """Cheamă `fn` și întoarce funcțiile care au chemat DIRECT `salarizare.calcul_salariu`.

    Nu „de câte ori" — prima formă număra apelurile și pica pe implementarea CORECTĂ: fluturașul ia
    rândul prin `stat_plata`, iar ăla cheamă motorul o dată per salariat, cum trebuie. Un gard care
    interzice și forma bună nu păzește, ci blochează. Ce se interzice e alt lucru: ca fluturașul să
    cheme motorul EL ÎNSUȘI, adică să existe un al doilea calcul."""
    import sys as _sys
    apelanti = []
    real = salarizare.calcul_salariu

    def spion(*a, **k):
        apelanti.append(_sys._getframe(1).f_code.co_name)
        return real(*a, **k)

    salarizare.calcul_salariu = spion
    try:
        out = fn()
    finally:
        salarizare.calcul_salariu = real
    return out, apelanti


@_DB
def test_fluturasul_nu_isi_recalculeaza_cifrele():
    """MECANIC. Cât timp fluturașul cheamă motorul de salarizare, există DOUĂ calcule ale aceleiași
    lucruri și pot diverge — au și divergit, pe 14 perechi reale."""
    for schema in SCHEME:
        with db.get_conn(schema) as conn:
            rand = next((r for r in _sp.stat_plata(conn, schema, 2026, 6)), None)
            if rand is None:
                conn.rollback()
                continue
            _pdf, apelanti = _fara_calcul(
                lambda: _sp.fluturas_pdf(conn, schema, int(rand["id"]), 2026, 6, "probă"))
            conn.rollback()
            assert apelanti, "motorul n-a fost atins deloc — spionul nu vede ce crede că vede"
            assert "fluturas_pdf" not in apelanti, (
                "fluturas_pdf cheamă DIRECT calcul_salariu pe %s — al doilea calcul al aceluiași "
                "lucru. Apelanți văzuți: %s" % (schema, sorted(set(apelanti))))
            assert set(apelanti) == {"stat_plata"}, (
                "cifrele fluturașului vin și din altă parte decât statul: %s" % sorted(set(apelanti)))
            return
    pytest.skip("niciun tenant cu salariați în 2026-06")


@_DB
def test_toate_perechile_coincid_cu_statul():
    """FUNCȚIONAL, pe toată populația: rândul din care se tipărește fluturașul e rândul statului."""
    perechi = dif = 0
    rele = []
    for schema in SCHEME:
        with db.get_conn(schema) as conn:
            for an, luna in LUNI:
                try:
                    stat = _sp.stat_plata(conn, schema, an, luna)
                except Exception:  # MASCA MOTIVATA: luna necalculabilă (date lipsă) nu e o divergență
                    continue
                for r in stat:
                    f = _sp.rand_fluturas(conn, schema, int(r["id"]), an, luna)
                    perechi += 1
                    d = [k for k in BANI
                         if round(float(r.get(k) or 0), 2) != round(float(f.get(k) or 0), 2)]
                    if d:
                        dif += 1
                        if len(rele) < 6:
                            rele.append("%s %d-%02d %s: %s" % (schema, an, luna, r["nume"], d))
            conn.rollback()
    assert perechi >= 100, (
        "doar %d perechi comparate — gardul nu-și mai vede lumea (firme fără salariați?)" % perechi)
    assert not dif, "fluturașul diferă de stat pe %d din %d perechi:\n  %s" % (
        dif, perechi, "\n  ".join(rele))


@_DB
def test_pdf_ul_tiparit_arata_cifra_statului():
    """PROBĂ DE RANDARE, nu de structură: se citește NETUL din PDF-ul generat.

    Cazul se CONSTRUIEȘTE (se deconfirmă pontajul lunii, în tranzacție anulată), ca gardul să nu
    depindă de ce se întâmplă să conțină datele unei firme — «punctul orb e FIRMA, nu ecranul»."""
    from pypdf import PdfReader

    from core.pdf_util import bani as _b
    for schema in SCHEME:
        with db.get_conn(schema) as conn:
            _per.deconfirma(conn, schema, 2026, 6, "pontaj")
            r = next((x for x in _sp.stat_plata(conn, schema, 2026, 6)
                      if float(x.get("tichet_masa_valoare") or 0) > 0), None)
            if r is None:
                conn.rollback()
                continue
            assert r["pontaj_neconfirmat"] and float(r["tichete_nominal"]) == 0, (
                "cazul nu s-a construit: statul nu blochează tichetele deși pontajul e neconfirmat")
            pdf = _sp.fluturas_pdf(conn, schema, int(r["id"]), 2026, 6, "probă")
            conn.rollback()
        text = re.sub(r"[\s ]+", " ", PdfReader(BytesIO(pdf)).pages[0].extract_text() or "")
        assert _b(r["net"], "lei") in text, (
            "PDF-ul nu tipărește netul statului (%s). Text: %.400s" % (_b(r["net"], "lei"), text))
        assert "Tichete masa" not in text, (
            "fluturașul tipărește tichete de masă deși statul le blochează (pontaj neconfirmat, "
            "HG 1045/2018 art.10(3)) — omul primește pe hârtie ce nu i s-a acordat")
        return
    pytest.skip("niciun tenant cu salariați cu tichete în 2026-06")


@_DB
def test_exemplarul_emis_bate_recalculul():
    """Când luna e EMISĂ, fluturașul tipărește exemplarul înghețat, nu recalculul de azi. Altfel
    amprenta ar păzi cifre pe care nimeni nu le vede."""
    from core import stat_plata_emis as spe
    for schema in SCHEME:
        with db.get_conn(schema) as conn:
            spe.aplica(conn, schema)
            em = spe.emite(conn, schema, 2026, 6, de_cine="garda")
            if not em:
                conn.rollback()
                continue
            sid = em[0]["salariat_id"]
            inainte = _sp.rand_fluturas(conn, schema, sid, 2026, 6)
            with conn.cursor() as cur:
                cur.execute("SELECT salariu_brut FROM salariati WHERE id=%s", (sid,))
                baza = float(cur.fetchone()[0] or 0)
                from datetime import date as _d

                from core import salariu_istoric as _si
                _si.seteaza(cur, sid, baza + 1000, _d(2026, 6, 1))
            recalc = next(x for x in _sp.stat_plata(conn, schema, 2026, 6)
                          if int(x["id"]) == sid)
            dupa = _sp.rand_fluturas(conn, schema, sid, 2026, 6)
            conn.rollback()
            assert round(float(recalc["brut"]), 2) != round(float(inainte["brut"]), 2), (
                "mutația nu a mișcat recalculul — testul ar verifica o lume nemișcată")
            assert round(float(dupa["brut"]), 2) == round(float(inainte["brut"]), 2), (
                "fluturașul a urmat recalculul, nu exemplarul emis")
            return
    pytest.skip("niciun tenant cu salariați în 2026-06")
