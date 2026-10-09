# -*- coding: utf-8 -*-
"""GARD — codul nu repornește pe producție înaintea migrării lui (comanda Costin 09.10.2026, pct.2: „Dacă un commit conține o migrare
nerulată pe producție, aplicația nu repornește. Nu procedură scrisă.”).

Drumurile (căutarea e în docstringul `core/migrari_registru.py`): (a) o migrare din HEAD fără rândul ei în `public.migrari_rulate`
(amprenta conținutului din HEAD) — și cea comisă într-un lot ANTERIOR, nerulată; (b) o tabelă / coloană din `tenant_template.sql`
lipsă într-o schemă de firmă. Plus: fail-closed când nu se poate ști, și drumul NOU — un fișier de migrare nerecunoscut ca migrare
(fără bloc `__main__`) ar scăpa registrului, deci orice `core/migrare_*.py` fără bloc trebuie numit aici.
Testele cu baza rulează într-o tranzacție anulată, pe nume sintetice (`core/migrare_zz_proba_*.py`): `public.migrari_rulate` e tabelă
partajată (CLAUDE.md: fixture pe tabel partajat = rollback).
"""
import glob
import os

import pytest

from core import db as _db
from core import migrari_registru as mr

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: `core/migrare_*.py` care NU sunt migrări (n-au bloc `__main__`), fiecare cu motivul. Un fișier nou fără bloc pică testul de drum nou.
NU_SUNT_MIGRARI = {
    "core/migrare_api.py": "API-ul migrărilor la cerere (`asigura_tabel`), DDL `IF NOT EXISTS` la rulare",
    "core/migrare_supervizor_confirmari.py": "funcții chemate din alte module, fără rulare proprie",
}


def test_ce_e_o_migrare():
    assert mr.e_migrare("core/migrare_x.py", "def _main():\n    pass\n\nif __name__ == \"__main__\":\n    _main()\n")
    assert not mr.e_migrare("core/migrare_x.py", "def f():\n    pass\n")                 # fără bloc: nu se rulează ca program
    assert not mr.e_migrare("core/test_migrare_x.py", "if __name__ == '__main__':\n    pass\n")
    assert not mr.e_migrare("scripts/migrare_x.py", "if __name__ == '__main__':\n    pass\n")


def test_drum_nou_orice_fisier_de_migrare_e_recunoscut_sau_numit():
    """MUTAȚIE: `_RE_FISIER` restrâns -> migrări reale ies din registru -> pică."""
    head = mr.migrari_la_commit("HEAD")
    toate = {os.path.relpath(f, _RAD) for f in glob.glob(os.path.join(_RAD, "core", "migrare_*.py"))}
    necunoscute = sorted(f for f in toate if f not in NU_SUNT_MIGRARI
                         and not mr.e_migrare(f, open(os.path.join(_RAD, f), encoding="utf-8").read()))
    assert not necunoscute, "core/migrare_*.py fără bloc __main__, deci invizibile registrului: %s" % necunoscute
    assert len(head) >= 84, "anti-vacuu: doar %d migrări găsite în HEAD" % len(head)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    c = p.getconn()
    with c.cursor() as cur:            # registrul e PARTAJAT și are rânduri reale (baza, rulările): fiecare test pornește de la gol,
        mr._tabel(cur)                 # în tranzacția lui, anulată la final (CLAUDE.md: testele nu presupun gol un tabel partajat)
        cur.execute("DELETE FROM public.migrari_rulate")
    try:
        yield c
    finally:
        c.rollback()
        p.putconn(c)


def test_registrul_numara_amprenta_nu_numele(conn):
    """O migrare SCHIMBATĂ după rulare e din nou nerulată (amprenta conținutului). MUTAȚIE: comparația pe nume -> pică."""
    with conn.cursor() as cur:
        m = {"core/migrare_zz_proba_a.py": "a" * 64, "core/migrare_zz_proba_b.py": "b" * 64}
        mr.inregistreaza(cur, "core/migrare_zz_proba_a.py", "a" * 64, "rulata", "proba")
        assert mr.nerulate(cur, m) == [("core/migrare_zz_proba_b.py", "b" * 64)]
        mr.inregistreaza(cur, "core/migrare_zz_proba_b.py", "0" * 64, "rulata", "proba")   # versiunea veche a lui b
        assert mr.nerulate(cur, m) == [("core/migrare_zz_proba_b.py", "b" * 64)]
        with pytest.raises(Exception):                                                  # felul e o mulțime închisă
            mr.inregistreaza(cur, "core/migrare_zz_proba_c.py", "c" * 64, "presupusa", "proba")


def _registru(conn, head, fara=None):
    """Registrul exact = migrările din `head`, mai puțin `fara`. Din nou înaintea fiecărui `verifica` (acela anulează tranzacția)."""
    with conn.cursor() as cur:
        mr._tabel(cur)
        cur.execute("DELETE FROM public.migrari_rulate")
        for f, a in head.items():
            if f != fara:
                mr.inregistreaza(cur, f, a, "baza", "proba")


def test_verifica_opreste_pe_migrare_nerulata_si_trece_cand_toate_sunt_rulate(conn):
    """(a): HEAD cu toate migrările în registru -> 0; una lipsă (inclusiv dintr-un commit anterior) -> 1, numită, cu comanda.
    MUTAȚIE: `nerulate` întoarce [] -> restartul ar porni peste migrarea lipsă -> pică."""
    head = mr.migrari_la_commit("HEAD")
    _registru(conn, head)
    cod, linii = mr.verifica("HEAD", conn=conn)
    assert (cod, linii) == (0, []), linii
    lipsa = sorted(head)[0]
    _registru(conn, head, fara=lipsa)
    cod, linii = mr.verifica("HEAD", conn=conn)
    assert cod == 1 and len(linii) == 1 and lipsa in linii[0] and "ruleaza --productie %s" % lipsa in linii[0], linii


def test_verifica_opreste_pe_schema_in_urma_sablonului(conn):
    """(b): o coloană din șablon lipsă într-o firmă (șablon schimbat fără migrare) -> 1, cu schema și coloana.
    MUTAȚIE: `drift_schema` întoarce {} -> pică."""
    head = mr.migrari_la_commit("HEAD")
    _registru(conn, head)
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY 1 LIMIT 1")
        s = cur.fetchone()[0]
        cur.execute('ALTER TABLE "%s".casa_operatiuni DROP COLUMN storno_de CASCADE' % s)   # exact cazul d0abd48f
    cod, linii = mr.verifica("HEAD", conn=conn)
    ale_ei = [ln for ln in linii if ln.startswith("schema %s " % s)]
    assert cod == 1 and ale_ei == ["schema %s e în urma șablonului: tabele lipsă -, coloane lipsă {'casa_operatiuni': ['storno_de']}, "
                                   "triggere lipsă -" % s], linii


def test_fail_closed_cand_nu_se_poate_sti(monkeypatch):
    """Baza de neatins / acreditare spre altă bază -> 2 (nu 0): restartul nu se face pe ghicite.
    MUTAȚIE: întoarcerea 0 la conexiune lipsă -> pică."""
    monkeypatch.setattr(mr, "_conexiune_productie", lambda: (None, "proba: baza nu răspunde"))
    cod, linii = mr.verifica("HEAD")
    assert cod == 2 and linii == ["NU SE POATE ȘTI dacă producția are migrările lui HEAD: proba: baza nu răspunde"], linii


def test_verifica_opreste_pe_trigger_lipsa(conn):
    """(b'): un trigger din șablon lipsă într-o firmă (o regulă de fond pusă în șablon fără migrare) -> 1, numit.
    MUTAȚIE: triggerele scoase din `audit_schema.are_drift_hard` -> pică."""
    head = mr.migrari_la_commit("HEAD")
    _registru(conn, head)
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY 1 LIMIT 1")
        s = cur.fetchone()[0]
        cur.execute('DROP TRIGGER IF EXISTS trg_verifica_perioada_blocata ON "%s".inregistrari' % s)
    cod, linii = mr.verifica("HEAD", conn=conn)
    ale_ei = [ln for ln in linii if ln.startswith("schema %s " % s)]
    assert cod == 1 and ale_ei == ["schema %s e în urma șablonului: tabele lipsă -, coloane lipsă -, triggere lipsă "
                                   "['inregistrari.trg_verifica_perioada_blocata']" % s], linii
