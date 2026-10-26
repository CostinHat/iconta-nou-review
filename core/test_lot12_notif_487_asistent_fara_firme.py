# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 487 (fost N1)] „Se poate crea un asistent fără nicio firmă alocată.”

Invitația unui coleg fără nicio firmă bifată se refuză: 422 pe lista firmelor (`camp` = `firme`, ecranul îl pune sub `#asi-firme-noi`),
ridicat în tranzacția contului (după verificarea adresei) — deci nimic scris: nici cont, nici link, nici email. Aceeași regulă ca la
scoaterea ultimei firme din ecranul colegului (`asistenti_api.aplica_regula_zero_firme`). Singurul drum care creează un cont de asistent
e `uc_asistenti.asistent_creeaza` (căutat: `grep -rn "creeaza_cont_asistent" core main.py`).

Temei: N/A — regulă de produs (asistenții lucrează pe firmele alocate), nu fiscală.
"""
import contextlib
import types

import pytest

from core import erori, nucleu
from core import uc_asistenti as ua


@pytest.fixture()
def jurnal(monkeypatch):
    j = []

    class _C:
        def cursor(self, **_k):
            return contextlib.nullcontext(types.SimpleNamespace(execute=lambda *a, **k: None, fetchone=lambda: None))   # [560] `nume_cabinet`: niciun rând

    @contextlib.contextmanager
    def _conn(schema=None):
        j.append("conn")
        try:
            yield _C()
        except Exception:
            j.append("rollback")
            raise
    monkeypatch.setattr(ua.db, "get_conn", _conn)
    monkeypatch.setattr(nucleu, "hash_parola", lambda p: "x")
    monkeypatch.setattr(ua.repo_utilizatori, "contul_dupa_email", lambda cur, e: None)
    monkeypatch.setattr(ua.repo_utilizatori, "creeaza_cont_asistent", lambda *a: j.append("cont") or {"id": 99})
    monkeypatch.setattr(ua._asist, "atribuie_firma", lambda conn, cab, uid, tid: j.append(("firma", tid)) or {"ok": True})
    monkeypatch.setattr(ua._uc_comun, "_pune_token", lambda cur, tok, uid, ttl: j.append("link"))
    monkeypatch.setattr(ua._obs, "trimite_email_html_sau_semnaleaza", lambda *a, **k: j.append("email") or True)
    return j


def _date(firme):
    return types.SimpleNamespace(email="zt.487@exemplu.ro", nume="ZT", poate_pregati=True, poate_valida=False, poate_depune=False,
                                 firme=firme)


@pytest.mark.parametrize("firme", [[], None])
def test_def_487_invitatia_fara_firme_e_refuzata_pe_lista_firmelor(jurnal, firme):
    """MUTAȚIE: `if not (date.firme or []):` -> `if False:` -> invitația trece, cu cont, link și email -> pică."""
    with pytest.raises(erori.DateInvalide) as e:
        ua.asistent_creeaza(_date(firme), {"rol": "admin_firma", "firm": 7, "uid": 1})
    d = e.value.detaliu
    assert d["cod"] == ua.COD_ASISTENT_FARA_FIRME and d["erori_campuri"] == [{"camp": "firme", "mesaj": ua.MESAJ_ASISTENT_FARA_FIRME}], d
    assert "link" not in jurnal and "email" not in jurnal, jurnal
    assert jurnal[-1] == "rollback", "refuzul trebuie ridicat în tranzacția contului (contul scris se anulează): %s" % jurnal


def test_def_487_cu_o_firma_invitatia_pleaca(jurnal):
    assert ua.asistent_creeaza(_date([3]), {"rol": "admin_firma", "firm": 7, "uid": 1}) == {"ok": True, "user_id": 99}
    assert jurnal == ["conn", "cont", ("firma", 3), "link", "email"], jurnal
