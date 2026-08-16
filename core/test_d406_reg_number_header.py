# -*- coding: utf-8 -*-
"""GARD D406 (16.08.2026, campanie rețeta D300, pas 8/8) — RegistrationNumber firma proprie (header) cu
prefix RO pentru platitorii de TVA.

BUG: _header emitea CUI BRUT (_NEDIGIT.sub("", cui), fara prefix RO). Functia registration_number() (care
implementa regula oficiala S.CMH.1: platitor TVA -> RO+CIF, neplatitor -> CIF; d406_schema_anaf.xlsx foaia
"5. Structures") EXISTA cu docstring corect DAR era COD MORT (0 apeluri) - documenta chiar bugul: "format
invalid pentru orice platitor de TVA". FIX: cablat registration_number(prof) in header (d406.py _header).

Aserturi ASCII.
"""
import re
import pytest
from core import db as _db, tenant_provisioning as _tp, d406 as _d406


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _gen(platitor):
    _SCHEMA = "test_d406_regnum"
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                    "declarant_nume,declarant_prenume,declarant_functie,platitor_tva,tip_decont,regim_fiscal) "
                    "VALUES (1,'TEST SRL','14399840','Str 1','Buc','B','6920','BCR','RO49BCRA0000000000000000',"
                    "'POPESCU','GHEORGHE','EXPERT',%s,'L','real')", (platitor,))
            xml, _res = _d406.genereaza(conn, _SCHEMA, 2026, 6)
            return xml
        finally:
            conn.rollback()


def _company_reg(xml):
    m = re.search(r"<Company>\s*<RegistrationNumber>([^<]*)</RegistrationNumber>", xml)
    return m.group(1) if m else None


def test_registration_number_functie_nu_mai_e_cod_mort():
    """Regresie: registration_number e acum APELAT in _header (nu mai e cod mort). AST: _header contine apelul."""
    import ast, io
    src = io.open(_d406.__file__, encoding="utf-8").read()
    tree = ast.parse(src)
    header = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_header"), None)
    assert header is not None
    apeluri = {n.func.id for n in ast.walk(header)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "registration_number" in apeluri, "_header trebuie sa cheme registration_number (nu CUI brut)"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_header_platitor_tva_are_prefix_RO():
    """Firma PLATITOARE de TVA -> RegistrationNumber = RO+CIF (S.CMH.1). RED pre-fix: CUI brut '14399840'."""
    assert _company_reg(_gen(True)) == "RO14399840"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_header_neplatitor_fara_prefix_RO():
    """CONTROL: firma NEPLATITOARE -> RegistrationNumber = CIF fara RO."""
    assert _company_reg(_gen(False)) == "14399840"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_header_platitor_ramane_duk_valid():
    """Proba DUK: D406 cu RegistrationNumber RO+CIF e valid la DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d406"):
        pytest.skip("DUK d406 indisponibil")
    xml = _gen(True)
    rez = duk.valideaza(xml, "d406", an=2026, luna=6)
    assert rez["stare"] == "valid", "D406 cu RO+CIF trebuie DUK-valid; rez=%r" % rez
