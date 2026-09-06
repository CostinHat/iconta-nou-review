# -*- coding: utf-8 -*-
"""GARD [R96, 06.09.2026]: cele trei registre obligatorii ori citesc aceeași mulțime, ori abaterea e DECLARATĂ.

**Ce s-a măsurat.** Fișa de cont (14-6-22, ține locul Cărții mari) cere `status='validata'`; balanța
și registrul-jurnal (14-1-1) nu filtrează deloc. Pe **8 firme din 20**, luna 08/2026, mulțimile
diferă — iar pe patru dintre ele *toate* notele lunii sunt ciorne: intră în două registre, lipsesc
din al treilea. **Trei registre obligatorii, aceeași lună, trei răspunsuri la «ce s-a înregistrat».**

**Ce apără gardul, și ce NU.** Nu decide care mulțime e cea corectă — aia e **R36**, o DECIZIE care
nu s-a luat. Apără ca abaterea să nu se mai poată pierde tăcut: fiecare registru care citește altceva
trebuie să fie în `ABATERI_DECLARATE`, cu motivul scris, iar declarația trebuie să fie **adevărată
despre cod**, nu doar prezentă.

**Mutația cerută de restanță** — *„o ciornă adăugată trebuie să miște exact registrele care o
declară"* — e probată pe o schemă efemeră, chemând **cititorii reali**.

**CE NU ACOPERĂ, declarat:** registrul-jurnal e o rută cu SQL **inline în `main.py`**, care cere
sesiune și tenant real; aici se compară predicatul lui declarat, nu se cheamă ruta. Populația reală
a rutei e păzită separat, de `core/test_registru_jurnal_14_1_1.py`. *Se scrie ca tăcerea să nu se
citească drept acoperire.*
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import db as _db  # noqa: E402
from core import documente_api as _doc  # noqa: E402
from core import fisa_cont as _fc  # noqa: E402
from core import scan_populatii_registre as _pr  # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402

SCH = "ztest_r96"
AN, LUNA = 2026, 8


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


def _scheme(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
        return [r[0] for r in cur.fetchall()]


# ── MIEZUL, pe portofoliu ──────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nicio_abatere_NEDECLARATA_pe_portofoliu():
    """Fie egalitate, fie o abatere scrisă. Un registru care începe să citească altceva cade aici."""
    rele, vazute = [], 0
    with _db.get_conn() as conn:
        for s in _scheme(conn):
            try:
                r = _pr.confrunta(conn, s, AN, LUNA)
            except Exception:  # noqa: BLE001  (schemă fără tabelele astea nu e o abatere)
                conn.rollback()
                continue
            vazute += 1
            if r["nedeclarate"]:
                rele.append("%s: %s" % (s, r["nedeclarate"]))
    assert vazute >= 10, "[anti-vacuu] doar %d scheme confruntate" % vazute
    assert not rele, ("registre care citesc altceva, fără declarație:\n  %s\n"
                      "Scrie abaterea în `scan_populatii_registre.ABATERI_DECLARATE`, cu motivul — sau "
                      "fă-le să citească aceeași mulțime." % "\n  ".join(rele))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ANTI_VACUU_abaterea_declarata_chiar_EXISTA():
    """Gardul de mai sus ar trece și pe egalitate perfectă — iar atunci declarația ar fi o afirmație
    netestată despre o lume care nu există. Se cere ca abaterea declarată să fie **reală azi**."""
    cu_abatere = []
    with _db.get_conn() as conn:
        for s in _scheme(conn):
            try:
                r = _pr.confrunta(conn, s, AN, LUNA)
            except Exception:  # noqa: BLE001
                conn.rollback()
                continue
            if r["abateri"]:
                cu_abatere.append(s)
    assert cu_abatere, (
        "nicio firmă n-are abatere pe %d/%02d — dacă registrele chiar citesc acum aceeași mulțime, "
        "scoate `fisa_cont` din ABATERI_DECLARATE și închide R96; dacă nu, gardul se uită în gol."
        % (AN, LUNA))
    assert all(set(_pr.confrunta(_db.get_conn().__enter__(), s, AN, LUNA)["abateri"]) <=
               set(_pr.ABATERI_DECLARATE) for s in cu_abatere[:1])


# ── MUTAȚIA CERUTĂ DE RESTANȚĂ, pe cititorii REALI ─────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_o_ciorna_adaugata_MISCA_exact_registrele_care_o_declara():
    """O notă în CIORNĂ intră în balanță și NU în fișa de cont — exact ce spune predicatul fiecăruia.

    Se cheamă **cititorii reali** (`documente_api.balanta`, `fisa_cont.fisa_cont`), nu se recitește
    SQL-ul: un gard care își scrie singur interogarea ar trece și dacă cititorul s-ar schimba."""
    sablon = open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(sablon, SCH))
        conn.commit()
        try:
            def _nota(status, suma):
                with conn.cursor() as cur:
                    cur.execute(f"""INSERT INTO {SCH}.inregistrari (data, numar, descriere, status, sursa)
                                    VALUES ('2026-08-15', 'N1', 'proba R96', %s, 'manual')
                                    RETURNING id""", (status,))
                    iid = cur.fetchone()[0]
                    cur.execute(f"""INSERT INTO {SCH}.inregistrari_linii
                                    (inregistrare_id, cont_debit, cont_credit, suma)
                                    VALUES (%s, '371', '401', %s)""", (iid, suma))
                conn.commit()
                return iid

            _nota("validata", 100)
            b0 = _doc.balanta(conn, SCH, AN, LUNA)
            f0 = _fc.fisa_cont(conn, SCH, "371", AN, LUNA)
            p0 = _pr.populatii(conn, SCH, AN, LUNA)

            _nota("ciorna", 50)                       # ← MUTAȚIA
            b1 = _doc.balanta(conn, SCH, AN, LUNA)
            f1 = _fc.fisa_cont(conn, SCH, "371", AN, LUNA)
            p1 = _pr.populatii(conn, SCH, AN, LUNA)

            assert len(p1["balanta"]) == len(p0["balanta"]) + 1, "ciorna n-a intrat în balanță"
            assert len(p1["jurnal"]) == len(p0["jurnal"]) + 1, "ciorna n-a intrat în registrul-jurnal"
            assert len(p1["fisa_cont"]) == len(p0["fisa_cont"]), "ciorna A INTRAT în fișa de cont"

            # și pe cititorii REALI, nu doar pe predicat:
            assert len(f1["randuri"]) == len(f0["randuri"]), (
                "fișa de cont s-a mișcat la o ciornă — predicatul declarat nu mai e adevărat")
            assert str(b1) != str(b0), "balanța NU s-a mișcat la o ciornă — predicatul e fals"
        finally:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            conn.commit()


def test_fiecare_abatere_declarata_are_MOTIV_scris():
    """O declarație goală ar fi o cheie care deschide orice. Motivul e obligatoriu și lung."""
    for reg, motiv in _pr.ABATERI_DECLARATE.items():
        assert reg in _pr.PREDICAT_STATUS, "abatere declarată pentru un registru necunoscut: %s" % reg
        assert motiv and len(motiv) > 120, "motiv prea scurt pentru %s: %r" % (reg, motiv)
