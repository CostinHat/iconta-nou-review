# -*- coding: utf-8 -*-
"""282 — Panou Admin → Înregistrare: cererile neconfirmate și „Retrimite confirmarea” (comanda Costin 16.10.2026, „Lotul 6, comanda 1”
pct.11, verbatim în DECIZII): „Cardul «Înregistrare» le listează: data, denumirea cabinetului, emailul, dacă emailul de confirmare a
plecat și când expiră linkul, cu acțiunea «Retrimite confirmarea».” Temei: N/A — produs (urmărirea cererilor de cont).
Rând sintetic (email pe domeniul de test, rezervat), șters la ieșire."""
import datetime

import pytest

from core import db as _db

EMAIL = "e2e-282@prisma-cont.test"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def cerere():
    from core import inregistrare_libera as il
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.inregistrari_in_asteptare WHERE email = %s", (EMAIL,))
            tok = il.creeaza(cur, {"email": EMAIL, "nume_cabinet": "Cabinet 282 SRL"}, "x", "v1", None,
                             acum=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=30))
            il.marcheaza_trimis(cur, tok)
            cur.execute("SELECT id FROM public.inregistrari_in_asteptare WHERE email = %s", (EMAIL,))
            cid = cur.fetchone()[0]
        c.commit()
    yield cid, tok
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.inregistrari_in_asteptare WHERE email = %s", (EMAIL,))
        c.commit()


def test_282_lista_spune_trimiterea_si_expirarea(cerere):
    from core import uc_auth
    x = [c for c in uc_auth.inregistrari_neconfirmate({})["cereri"] if c["id"] == cerere[0]][0]
    assert (x["nume_cabinet"], x["email"], x["expirata"], x["retrimiteri"]) == ("Cabinet 282 SRL", EMAIL, True, 0), x
    assert x["email_trimis_la"], "momentul trimiterii, scris la trimitere"


def test_282_retrimiterea_da_link_nou_numai_daca_emailul_pleaca(cerere, monkeypatch):
    """MUTAȚIE: `if not _trimite_confirmarea(...)` -> `if False` -> eșecul trimiterii lasă totuși linkul nou -> pică."""
    from core import uc_auth, erori, inregistrare_libera as il
    trimise = []
    monkeypatch.setattr(uc_auth, "_trimite_confirmarea", lambda email, cab, tok: trimise.append((email, cab, tok)) and False)
    with pytest.raises(erori.ServiciuIndisponibil):
        uc_auth.retrimite_confirmarea(cerere[0], {})
    with _db.get_conn() as c:
        with c.cursor() as cur:
            assert il.ia_pentru_confirmare(cur, cerere[1])["cerere"]["id"] == cerere[0], "linkul vechi a rămas (trimiterea a eșuat)"
        c.rollback()
    monkeypatch.setattr(uc_auth, "_trimite_confirmarea", lambda email, cab, tok: trimise.append((email, cab, tok)) or True)
    assert uc_auth.retrimite_confirmarea(cerere[0], {})["email"] == EMAIL
    nou = trimise[-1][2]
    with _db.get_conn() as c:
        with c.cursor() as cur:
            assert il.ia_pentru_confirmare(cur, cerere[1])["cerere"] is None, "linkul vechi nu mai merge"
            s = il.ia_pentru_confirmare(cur, nou)
        c.rollback()
    assert s["valida"], "linkul nou e valabil din nou (cererea expirase)"
    x = [c for c in uc_auth.inregistrari_neconfirmate({})["cereri"] if c["id"] == cerere[0]][0]
    assert (x["expirata"], x["retrimiteri"]) == (False, 1), x


def test_282_inregistrarea_consemneaza_trimiterea():
    """`_register_liber` scrie momentul trimiterii după ce emailul a plecat (o cerere fără el n-ar spune nimic în Panou Admin)."""
    import ast
    import io
    src = io.open("core/uc_auth.py", encoding="utf-8").read()
    fn = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "_register_liber"][0]
    corp = ast.get_source_segment(src, fn)
    assert corp.index("_trimite_confirmarea(") < corp.index("_il.marcheaza_trimis(cur, tok)")
