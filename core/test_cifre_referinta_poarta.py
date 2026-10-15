# -*- coding: utf-8 -*-
"""GARD — cifrele de referință ale firmelor F1–F5 opresc publicarea la orice diferență (comanda Costin 10.10.2026 pct.1, verbatim în
DECIZII: „Leagă gardul «orice diferență față de referință oprește publicarea». O schimbare voită se face doar cu aprobarea mea,
consemnată în DECIZII.”). Calculul pe producție îl face poarta (`scripts/githooks/poarta-suita`); aici se păzesc legătura, comparația și
regula schimbării. Fără acces la producție."""
import io
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import cifre_referinta as cr  # noqa: E402


def _citeste(rel):
    return io.open(os.path.join(RAD, rel), encoding="utf-8").read()


def test_poarta_ruleaza_verificarea_si_respinge_la_orice_iesire_nenula():
    """MUTAȚIE: treapta scoasă din poartă -> pică."""
    t = _citeste("scripts/githooks/poarta-suita")
    m = re.search(r'^"\$PY" scripts/cifre_referinta\.py --productie --verifica > \$J/precommit_cifre\.log 2>&1\nRC=\$\?', t, re.M)
    assert m, "poarta nu mai confruntă cifrele cu referința aprobată"
    dupa = t[m.end():m.end() + 900]
    linii_dupa = [x.strip() for x in dupa.splitlines()]   # liniile scriptului, nu un sub-șir oarecare din el
    assert 'if [ "$RC" -ne 0 ]; then' in linii_dupa and "exit 1" in linii_dupa[linii_dupa.index('if [ "$RC" -ne 0 ]; then'):], (
        "o diferență (sau o măsurătoare eșuată) nu oprește poarta")
    assert m.start() < t.find('scripts/e2e_poarta.py'), "cifrele se confruntă înaintea plasei"


def test_referinta_e_cea_aprobata_si_nu_e_goala():
    """Anti-vacuu: cinci firme, patru cu balanța pe cel puțin o lună (F4 n-are date încă); amprenta fișierului e cea consemnată în
    DECIZII."""
    ref = json.load(open(cr.REFERINTA, encoding="utf-8"))
    assert len(ref) == 5 and sum(1 for f in ref.values() if f.get("balanta")) >= 4, sorted(ref)
    assert cr.amprenta_fisier() in _citeste("DECIZII.md"), "referința nu are aprobarea consemnată în DECIZII (cu amprenta ei)"


def test_comparatia_vede_orice_schimbare_si_nimic_in_plus():
    """MUTAȚIE: `diferente` care întoarce mereu [] -> pică."""
    ref = json.load(open(cr.REFERINTA, encoding="utf-8"))
    assert cr.diferente(ref, json.loads(json.dumps(ref))) == []
    alt = json.loads(json.dumps(ref))
    f = sorted(alt)[0]
    luna = sorted(alt[f]["balanta"])[0]
    rand = alt[f]["balanta"][luna][0]
    rand["sf_d"] = float(rand.get("sf_d") or 0) + 0.01                    # un ban pe un sold
    alt[f]["D112"] = {}                                                   # o declarație care dispare
    d = [c for c, _a, _b in cr.diferente(ref, alt)]
    assert any("/balanta/" in c for c in d) and any("/D112/" in c or c.endswith("/D112") for c in d), d


def test_amprenta_ignora_numai_data_generarii():
    """Amprenta XML-ului nu depinde de ziua generării (`AuditFileDateCreated`, `DateCreated`), dar depinde de orice cifră.
    MUTAȚIE: `AuditFileDateCreated` scos din `_VOLATIL` -> pică."""
    x = "<H><AuditFileDateCreated>%s</AuditFileDateCreated></H><T><TotalDebit>%s</TotalDebit></T>"
    assert cr._amprenta(x % ("2026-10-09", "100.00")) == cr._amprenta(x % ("2026-10-10", "100.00"))
    assert cr._amprenta(x % ("2026-10-09", "100.00")) != cr._amprenta(x % ("2026-10-09", "100.01"))


def test_schimbarea_referintei_cere_amprenta_in_decizii():
    """MUTAȚIE: regula scoasă din `verifica-mesaj` -> pică."""
    linii = {x.strip() for x in _citeste("scripts/githooks/verifica-mesaj").splitlines()}   # liniile scriptului, ca mulțime
    assert 'REF_CIFRE="scripts/cifre_referinta_aprobate.json"' in linii
    regula = r'git diff --cached -U0 -- DECIZII.md | grep -E ' + r"'^\+'" + r' | grep -q "$AMPR"'
    assert any(regula in x and x.startswith("if ") for x in linii), "regula aprobării lipsește (condiția unui `if` din script)"


def test_lunile_cu_date_vin_numai_din_notele_validate():
    """[14.10.2026, decizia Costin, varianta (c), verbatim în DECIZII] „Unealta de cifre alege lunile numai din notele validate (R36).”
    Pe o schemă din `tenant_template.sql` (baza de TEST, anulată): o notă validată în 01/2099 și o ciornă în 12/2099 -> numai 01/2099
    (cazul din 13.10: ciornele de închidere la 31.12.2026 pe F2 adăugau o lună goală). MUTAȚIE: filtrul `status = 'validata'` scos din
    `_luni_cu_date` -> pică."""
    from core import db as _db
    from core import tenant_provisioning as _tp
    schema = "ztest_cifre_r36"
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
                cur.execute(_tp.parametrizeaza_template(_citeste("tenant_template.sql"), schema))
                for data, stare in (("2099-01-15", "validata"), ("2099-12-31", "ciorna")):
                    cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status) VALUES (%%s, 'proba R36', 'manual', %%s)"
                                % schema, (data, stare))
                assert cr._luni_cu_date(cur, schema) == [(2099, 1)]
        finally:
            conn.rollback()
