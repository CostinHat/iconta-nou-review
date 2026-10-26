# -*- coding: utf-8 -*-
"""[lotul 13, zona firme2] Raportul Z: 618 (explicația notei cu data ISO) și 605 (textele ecranului Raport Z).

Comanda Costin 13.1, verbatim:
  618: „Raport Z | Titlul notei cu data ISO («Raport Z 2026-10-20»)”
  605: „Raport Z (F1) | Textul «raportul Z Raport Z nr»; etichetele «mâncare» / «alcool, sucuri» și «Consum pe rețetă» la o firmă de comerț;
       mesajul de confirmare sus, departe de buton (clasa 45).”

CE FACE IMPOSIBIL: (a) explicația notei Z cu data ISO, pe oricare din cele două drumuri (scris de mână, import AMEF) — sursa unică e
`jurnal_api.explicatie_raport_z`, iar drumurile din `uc_tenants` o cheamă (garda textuală pe `uc_tenants.py`); (b) o ciornă Z scrisă înainte
de reparație rămasă cu data ISO după migrare; (c) migrarea care atinge o notă VALIDATĂ (evidență: regula de fond `trg_regula_nota`) sau un
text scris de om; (d) migrarea care nu e idempotentă. Schemă efemeră din șablon, tranzacție anulată, perioade sintetice (2099).
TEMEI: N/A — formatul datei pe ecran (CLAUDE.md §9: „Textele dau instrucțiuni directe, în limba contabilului”); nota validată nu se
modifică: OMFP 1802/2014 pct.69 („Înregistrarea stornării unei operațiuni contabile [...] se efectuează fie prin corectarea cu semnul minus
a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru)”), aplicat de `trg_regula_nota`.
"""
import os
import re

import pytest

from core import db as _db, jurnal_api, migrare_explicatie_raport_z as mig, migrari_registru

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot13_firme2_z"


def test_explicatia_notei_z_are_data_romaneasca_pe_ambele_drumuri():
    assert jurnal_api.explicatie_raport_z("2099-10-20", "8000000001", "0042") == "Vânzări din raportul Z nr 0042 din 20.10.2099, casa 8000000001"
    assert jurnal_api.explicatie_raport_z("2099-10-20", "8000000001", "0042", 12, amef=True) == (
        "Vânzări din raportul Z nr 0042 din 20.10.2099, casa 8000000001 (import AMEF, 12 bonuri) — de verificat cu Z-ul tipărit")
    assert not re.search(r"\d{4}-\d{2}-\d{2}", jurnal_api.explicatie_raport_z("2099-01-02", "1", "1", 1, amef=True))


def test_drumurile_z_din_uc_tenants_cheama_sursa_unica():
    """Garda textuală: niciun f-string / format „Raport Z <data ISO>” în drumurile Z-ului, ambele prin `explicatie_raport_z`."""
    s = open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read()
    assert '"Raport Z %s casa %s nr %s"' not in s, "drumul Z-ului scris de mână scrie din nou data ISO în explicație"
    assert "f\"Raport Z {rz['data']}" not in s, "drumul importului AMEF scrie din nou data ISO în explicație"
    assert s.count("_jurnal_api.explicatie_raport_z(") == 2, "ambele drumuri ale Z-ului trec prin sursa unică"


def test_migrarea_e_a_registrului():
    cale = "core/migrare_explicatie_raport_z.py"
    assert migrari_registru.e_migrare(cale, open(os.path.join(RAD, cale), encoding="utf-8").read())


@pytest.mark.parametrize("vechi, nou", [
    ("Raport Z 2099-10-20 casa 8000000001 nr 0042", "Vânzări din raportul Z nr 0042 din 20.10.2099, casa 8000000001"),
    ("Raport Z 2099-10-21 AMEF 8000000001 nr 0043 (1 bon) - de verificat cu Z tiparit",
     "Vânzări din raportul Z nr 0043 din 21.10.2099, casa 8000000001 (import AMEF, 1 bon) — de verificat cu Z-ul tipărit"),
    # `common.cate` scria „20 de bonuri” de la 20 în sus — forma veche se recunoaște și așa
    ("Raport Z 2099-10-22 AMEF 8000000001 nr 0044 (20 de bonuri) - de verificat cu Z tiparit",
     "Vânzări din raportul Z nr 0044 din 22.10.2099, casa 8000000001 (import AMEF, 20 de bonuri) — de verificat cu Z-ul tipărit"),
    ("Raport Z scris de mine", None),                 # text scris de om: nu se atinge
    ("Raport Z 2099-10-20 casa 8000000001 nr 0042 corectat", None),
])
def test_explicatia_noua_numai_pe_forma_veche_intreaga(vechi, nou):
    assert mig.explicatia_noua(vechi) == nou


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    sablon = open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(sablon, SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def _nota(cur, data, numar, descriere, sursa="horeca_z"):
    cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status, document_ref) VALUES (%s, %s, %s, %s, 'ciorna', %s) "
                "RETURNING id", (data, numar, descriere, sursa, "Raport Z nr %s din %s" % (numar[-4:], data)))
    iid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5311', '707', 100)", (iid,))
    return iid


def test_migrarea_rescrie_ciornele_si_lasa_notele_validate_si_textele_omului(conn):
    with conn.cursor() as cur:
        a = _nota(cur, "2099-10-20", "Z-8000000001-0042", "Raport Z 2099-10-20 casa 8000000001 nr 0042")
        b = _nota(cur, "2099-10-21", "Z-8000000001-0043", "Raport Z 2099-10-21 AMEF 8000000001 nr 0043 (12 bonuri) - de verificat cu Z tiparit", "amef")
        c = _nota(cur, "2099-10-22", "Z-8000000001-0044", "Raport Z 2099-10-22 casa 8000000001 nr 0044")
        d = _nota(cur, "2099-10-23", "Z-8000000001-0045", "Raport Z scris de mine")
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (c,))
    # nota validată se scrie în aceeași tranzacție (regula de fond o lasă numai tranzacției ei): migrarea se probează pe o altă tranzacție
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT dupa_scriere")
    rez = mig.aplica(conn, SCHEMA)
    assert rez["rescrise"] == [a, b] and rez["validate"] == [c] and rez["ramase"] == [], rez
    with conn.cursor() as cur:
        cur.execute("SELECT id, descriere FROM inregistrari ORDER BY id")
        d_ = dict(cur.fetchall())
    assert d_[a] == "Vânzări din raportul Z nr 0042 din 20.10.2099, casa 8000000001"
    assert d_[b] == "Vânzări din raportul Z nr 0043 din 21.10.2099, casa 8000000001 (import AMEF, 12 bonuri) — de verificat cu Z-ul tipărit"
    assert d_[c] == "Raport Z 2099-10-22 casa 8000000001 nr 0044"        # validată: evidență, neatinsă
    assert d_[d] == "Raport Z scris de mine"                             # text al omului: neatins
    assert mig.verifica(conn, SCHEMA)
    assert mig.aplica(conn, SCHEMA)["rescrise"] == []                   # idempotentă
