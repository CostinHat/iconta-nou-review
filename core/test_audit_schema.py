# -*- coding: utf-8 -*-
"""Teste F165 — auditor conformitate schema tenant vs tenant_template.sql.

Doua straturi:
  1. PURE (compara/sugereaza_alter/are_drift_hard pe dict-uri sintetice) - fara DB, rapid.
  2. POARTA reala: construieste referinta din template in ROLLBACK, compara TOTI tenantii,
     PICA la drift HARD (template->tenant). E gardul care converteste driftul tacut in rosu
     la dev, INAINTE de commit (cazul link_plata n-avea nimic care sa-l prinda mecanic).

De ce test si nu doar verificator: suita e verde-obligatoriu; un tenant driftat rupe suita.
"""
import pathlib
import pytest
from core import audit_schema as a
from core import db


# ============================================================
#  1. PURE — diff pe dict-uri de introspectie sintetice
# ============================================================
def _meta(dt="integer", nul="YES", cmax=None, dflt=None):
    return (dt, nul, cmax, dflt)


def test_compara_conform_zero_drift():
    ref = {"t": {"id": _meta(), "nume": _meta("character varying", "NO", 255)}}
    ten = {"t": {"id": _meta(), "nume": _meta("character varying", "NO", 255)}}
    d = a.compara(ref, ten)
    assert not a.are_drift_hard(d)


def test_compara_coloana_lipsa_e_hard():
    ref = {"t": {"id": _meta(), "link_plata": _meta("text")}}
    ten = {"t": {"id": _meta()}}                      # tenantul n-a primit link_plata
    d = a.compara(ref, ten)
    assert a.are_drift_hard(d)
    assert d["coloane_lipsa"] == {"t": ["link_plata"]}


def test_compara_tabela_lipsa_e_hard():
    ref = {"t": {"id": _meta()}, "noua": {"id": _meta()}}
    ten = {"t": {"id": _meta()}}
    d = a.compara(ref, ten)
    assert a.are_drift_hard(d)
    assert d["tabele_lipsa"] == ["noua"]


def test_compara_tip_diferit_e_hard():
    ref = {"t": {"suma": _meta("numeric")}}
    ten = {"t": {"suma": _meta("integer")}}
    d = a.compara(ref, ten)
    assert a.are_drift_hard(d)
    assert d["tip_dif"] and d["tip_dif"][0][:2] == ("t", "suma")


def test_compara_nullable_diferit_e_hard():
    ref = {"t": {"cui": _meta("text", "NO")}}
    ten = {"t": {"cui": _meta("text", "YES")}}
    d = a.compara(ref, ten)
    assert a.are_drift_hard(d)
    assert d["nullable_dif"] and d["nullable_dif"][0][:2] == ("t", "cui")


def test_compara_extra_in_tenant_NU_e_hard():
    # tabela/coloana extra in tenant (lazy/legacy) -> informativ, NU pica (fara whitelist)
    ref = {"t": {"id": _meta()}}
    ten = {"t": {"id": _meta(), "vechi": _meta("text")}, "d301_operatiuni": {"id": _meta()}}
    d = a.compara(ref, ten)
    assert not a.are_drift_hard(d)                    # extra nu e drift hard
    assert d["tabele_extra"] == ["d301_operatiuni"]
    assert d["coloane_extra"] == {"t": ["vechi"]}


def test_norm_default_scoate_numele_schemei():
    # nextval cu nume de schema diferit NU trebuie sa para tip-diferit
    ref_dflt = a._norm_default("nextval('zaudit_schema_ref.t_id_seq'::regclass)", "zaudit_schema_ref")
    ten_dflt = a._norm_default("nextval('tenant_002.t_id_seq'::regclass)", "tenant_002")
    assert ref_dflt == ten_dflt                       # egale dupa normalizare


def test_sugereaza_alter_pt_coloana_lipsa():
    ref = {"facturi": {"link_plata": _meta("text", "YES")}}
    d = a.compara(ref, {"facturi": {}})
    sug = a.sugereaza_alter("tenant_003", d, ref)
    assert any("ADD COLUMN IF NOT EXISTS link_plata text" in s for s in sug)
    assert any('"tenant_003".facturi' in s for s in sug)


def test_sugereaza_alter_not_null_fara_default_avertizeaza():
    ref = {"t": {"x": _meta("integer", "NO")}}        # NOT NULL, fara default
    d = a.compara(ref, {"t": {}})
    sug = a.sugereaza_alter("tenant_003", d, ref)
    assert any(s.startswith("-- ATENTIE") and "NOT NULL fara default" in s for s in sug)


# ============================================================
#  2. POARTA reala — toti tenantii conform cu template-ul
# ============================================================
def test_toti_tenantii_conform_cu_template():
    template_sql = (pathlib.Path(__file__).resolve().parent.parent / "tenant_template.sql").read_text(encoding="utf-8")
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            schemas = a._schemele_tenant(cur)
        rapoarte, ref = a.auditeaza(conn, schemas, template_sql)
        conn.rollback()                               # ref temporara, zero mutatie
    driftate = {s: rapoarte[s] for s in schemas if a.are_drift_hard(rapoarte[s])}
    if driftate:
        msg = ["DRIFT de schema tenant vs tenant_template.sql (template->tenant):"]
        for s, d in driftate.items():
            msg.append(a._raporteaza(s, d, ref))
        msg.append("-> tenantul e in urma template-ului: codul care foloseste ce lipseste va crapa "
                   "pe ACEST tenant. Scrie un core/migrare_*.py (idempotent, ADD COLUMN IF NOT EXISTS) "
                   "+ mirror in tenant_template.sql, ruleaza-l pe schemele existente. SQL sugerat mai sus.")
        pytest.fail("\n".join(msg))


def test_mutatie_negativa_poarta_prinde_coloana_lipsa():
    # dovada ca poarta chiar prinde: pornim de la introspectia REALA a template-ului si
    # simulam un tenant caruia ii lipseste o coloana din template -> trebuie drift HARD.
    template_sql = (pathlib.Path(__file__).resolve().parent.parent / "tenant_template.sql").read_text(encoding="utf-8")
    db.init_pool()
    with db.get_conn() as conn:
        _, ref = a.auditeaza(conn, [], template_sql)   # doar introspectia template-ului (ref real)
        conn.rollback()
    tabela = next(t for t in ref if ref[t])
    col = sorted(ref[tabela])[0]
    ten_stricat = {t: dict(c) for t, c in ref.items()}
    del ten_stricat[tabela][col]                       # tenantul n-a primit `col`
    d = a.compara(ref, ten_stricat)
    assert a.are_drift_hard(d)
    assert col in d["coloane_lipsa"].get(tabela, [])
