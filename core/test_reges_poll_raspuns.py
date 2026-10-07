# -*- coding: utf-8 -*-
"""GARD — „Răspunsuri REGES” spune ce s-a întâmplat la citirea cozii REGES (comanda Costin 07.10.2026, clasa C5).

`poll_mesaj` CONSUMĂ un mesaj din coada REGES (ireversibil). Ecranul citea `mesaje`/`raspunsuri`, chei pe care ruta nu le-a
întors niciodată, deci spunea „niciun răspuns nou” și după un răspuns primit și scris la mesajul firmei. Ruta întoarce acum
`primit`, `message_id`, referințele și `salvat` (s-a găsit mesajul firmei căruia să i se scrie). Partea de ecran o păzește
`core/test_raspuns_citit.py`; aici, răspunsul rutei, pe cele patru stări.

REGES și conexiunea sunt înlocuite (apelul extern nu se poate face din test; SQL-ul `scrie_raspunsul_reges` e neschimbat):
se probează CE întoarce use-case-ul din ce a venit de la REGES și din câte rânduri a atins scrierea.
"""
import pytest

from core import reges_client, uc_tenants

MID = "0f8fad5b-d9cb-469f-a165-70867728950e"
RS = "7c9e6679-7425-40de-944b-e07fc1f90ae7"


class _Cur:
    def __init__(self, randuri):
        self.rowcount, self._randuri = 0, randuri

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Conn:
    def __init__(self, randuri):
        self.cur = _Cur(randuri)
        self.commit_uri = 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def cursor(self):
        return self.cur

    def commit(self):
        self.commit_uri += 1


@pytest.fixture
def reges(monkeypatch):
    stare = {"rasp": "", "randuri": 0, "scrieri": []}

    class _Client:
        def __init__(self, *a):
            pass

        def poll_mesaj(self):
            return 200, stare["rasp"]

    def _scrie(cur, raspuns, ref_s, ref_c, mid, tid):
        stare["scrieri"].append((ref_s, ref_c, mid, tid))
        cur.rowcount = stare["randuri"]

    monkeypatch.setattr(reges_client, "RegesClient", _Client)
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: _Conn(stare["randuri"]))
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda *a: "tenant_x")
    monkeypatch.setattr(uc_tenants.repo_salariati, "chei_reges_fara_autor", lambda cur, tid: ("u", "p", "c"))
    monkeypatch.setattr(uc_tenants.repo_salariati, "scrie_raspunsul_reges", _scrie)
    return stare


def test_coada_goala_inseamna_niciun_raspuns(reges):
    r = uc_tenants.reges_poll(7, {"uid": 1})
    assert (r["primit"], r["message_id"], r["salvat"]) == (False, None, False)
    assert reges["scrieri"] == []


def test_raspunsul_pentru_mesajul_firmei_se_spune_si_se_pastreaza(reges):
    """Instanța: înainte, aici ecranul spunea „niciun răspuns nou”. MUTAȚIE: `primit` scos din răspuns -> pică."""
    reges["rasp"] = "<Raspuns><MessageId>%s</MessageId><ReferintaSalariat><Id>%s</Id></ReferintaSalariat></Raspuns>" % (MID, RS)
    reges["randuri"] = 1
    r = uc_tenants.reges_poll(7, {"uid": 1})
    assert (r["primit"], r["message_id"], r["referinta_salariat"], r["salvat"]) == (True, MID, RS, True)
    assert reges["scrieri"] == [(RS, None, MID, 7)]


def test_raspunsul_pentru_un_mesaj_strain_nu_se_da_drept_pastrat(reges):
    """MUTAȚIE: `salvat = True` necondiționat -> pică (UPDATE-ul n-a atins niciun rând: mesajul nu e al firmei)."""
    reges["rasp"] = "<Raspuns><MessageId>%s</MessageId></Raspuns>" % MID
    reges["randuri"] = 0
    r = uc_tenants.reges_poll(7, {"uid": 1})
    assert (r["primit"], r["message_id"], r["salvat"]) == (True, MID, False)


def test_raspunsul_fara_identificator_se_arata_nu_se_ascunde(reges):
    reges["rasp"] = "<Eroare>token expirat</Eroare>"
    r = uc_tenants.reges_poll(7, {"uid": 1})
    assert (r["primit"], r["message_id"], r["salvat"]) == (True, None, False)
    assert r["raspuns"] == "<Eroare>token expirat</Eroare>"
    assert reges["scrieri"] == []
