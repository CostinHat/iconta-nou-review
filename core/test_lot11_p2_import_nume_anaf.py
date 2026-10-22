# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 444, comanda Costin 11.1 pct.20, verbatim: „când numele de la ANAF diferă de fișa partenerului, se spune și se
propune actualizarea.”] Drumul importului e-Factura (`uc_tenants.facturi_primite_lista`): fiecare factură primită al cărei furnizor e găsit
la ANAF poartă `fisa_vs_anaf` — fișele firmei cu CIF-ul emitentului, fiecare cu `diferit` (`clienti_api.compara_cu_anaf`, aceeași
comparație ca ecranul fișelor, NIR-ul și casa) —, deci ecranul validării o poate spune și propune actualizarea.
N/A temei fiscal: comparația numelui e o regulă de produs (decizia Costin), nu o normă. ANAF e SIMULAT (niciodată real în teste).
Schemă efemeră din template, în tranzacție anulată (tiparul din core/test_418_import_efactura.py)."""
import contextlib
import hashlib
import io

import pytest
from psycopg2.extras import RealDictCursor

from core import anaf_api, db as _db, tenant_provisioning as _tprov
from core.test_418_import_efactura import _XML, _ConnProxy, _db_ok

STATUT_FURNIZOR_REAL = True   # ANAF îl simulează testul însuși (core/conftest.py)

# CUI 14399840 (DANTE INTERNATIONAL SA, furnizorul din _XML) — cifra de control verificată cu algoritmul din CLAUDE.md
_CUI = "14399840"


def _anaf(denumire):
    def interogare(cuii, data_interogare=None):
        return [{"cui": "".join(ch for ch in c if ch.isdigit()), "gasit": True, "platitor_tva": True, "tva_la_incasare": False,
                 "denumire": denumire} for c in cuii]
    return interogare


@contextlib.contextmanager
def _firma(monkeypatch, nume_fisa):
    """Firmă efemeră cu o factură primită de la 14399840 și (dacă `nume_fisa`) fișa furnizorului cu acel nume."""
    _db.init_pool()
    SCH = "efemer_p2_444_import"
    c = _db.pool().getconn()
    try:
        with c.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('EF P2 444') RETURNING id"); fid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ef_p2_444@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (fid,)); uid = cur.fetchone()["id"]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'F1 SRL','9010105',%s,true) RETURNING id", (SCH, fid)); tid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (uid, tid))
            cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
            cur.execute('INSERT INTO "%s".firma_profil (id,nume,cui,platitor_tva) VALUES (1,%%s,%%s,true)' % SCH, ("F1 SRL", "9010105"))
            cur.execute('INSERT INTO "%s".efactura_primite (id_mesaj_anaf,cif_emitent,cif_beneficiar,tip,xml_brut,xml_sha256,status,importat_la) '
                        "VALUES ('EF-P2-444','RO14399840','RO9010105','factura',%%s,%%s,'descarcata',now())" % SCH,
                        (_XML, hashlib.sha256(_XML.encode()).hexdigest()))
            if nume_fisa:
                cur.execute('INSERT INTO "%s".furnizori (nume, cui) VALUES (%%s, %%s) RETURNING id' % SCH, (nume_fisa, "RO" + _CUI))
                fz = cur.fetchone()["id"]
            else:
                fz = None

        @contextlib.contextmanager
        def _fake(schema=None):
            with c.cursor() as cc:
                cc.execute('SET LOCAL search_path TO "%s", public' % schema if schema else "SET LOCAL search_path TO public")
            yield _ConnProxy(c)
        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"tid": tid, "fz": fz, "ctx": {"uid": uid, "rol": "admin_firma", "accounting_firm_id": fid, "firm": fid}}
    finally:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.rollback()
        _db.pool().putconn(c)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_importul_spune_cand_numele_anaf_difera_de_fisa_furnizorului(monkeypatch):
    from core import uc_tenants
    with _firma(monkeypatch, "DANTE SRL") as f:
        monkeypatch.setattr(anaf_api, "valideaza_cui", _anaf("DANTE INTERNATIONAL SA"))
        p, = uc_tenants.facturi_primite_lista(f["tid"], f["ctx"])["primite"]
        v = p["fisa_vs_anaf"]
        # comanda Costin 11.1 pct.20: „se spune și se propune actualizarea” — fișa cu alt nume e numită, cu id-ul pe care îl actualizează butonul
        assert v["nume_diferit"] is True and v["denumire"] == "DANTE INTERNATIONAL SA", v
        assert v["fise"] == [{"fel": "furnizori", "id": f["fz"], "nume": "DANTE SRL", "diferit": True}], v
        assert v["mesaj_nume"] == ("Numele de la ANAF (DANTE INTERNATIONAL SA) diferă de fișa furnizorului: DANTE SRL. Actualizează fișa "
                                   "cu numele de la ANAF, dacă e cel corect."), v   # câmpul întreg (core/test_garzi_pe_text.py)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_importul_tace_cand_fisa_are_numele_anaf_sau_nu_exista(monkeypatch):
    from core import uc_tenants
    with _firma(monkeypatch, "Dante International S.A.") as f:   # aceeași denumire: fără majuscule / puncte (`clienti_api.nume_diferit`)
        monkeypatch.setattr(anaf_api, "valideaza_cui", _anaf("DANTE INTERNATIONAL SA"))
        p, = uc_tenants.facturi_primite_lista(f["tid"], f["ctx"])["primite"]
        assert p["fisa_vs_anaf"]["nume_diferit"] is False and p["fisa_vs_anaf"]["mesaj_nume"] is None, p["fisa_vs_anaf"]
    with _firma(monkeypatch, None) as f:
        monkeypatch.setattr(anaf_api, "valideaza_cui", _anaf("DANTE INTERNATIONAL SA"))
        p, = uc_tenants.facturi_primite_lista(f["tid"], f["ctx"])["primite"]
        assert p["fisa_vs_anaf"] == {"fise": [], "nume_diferit": False, "mesaj_nume": None, "denumire": "DANTE INTERNATIONAL SA"}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_raspuns_anaf_nu_se_compara(monkeypatch):
    from core import uc_tenants

    def _jos(*a, **k):
        raise OSError("ANAF simulat indisponibil")
    with _firma(monkeypatch, "DANTE SRL") as f:
        monkeypatch.setattr(anaf_api, "valideaza_cui", _jos)
        p, = uc_tenants.facturi_primite_lista(f["tid"], f["ctx"])["primite"]
        assert "fisa_vs_anaf" not in p, p   # nimic de comparat: denumirea ANAF lipsește
