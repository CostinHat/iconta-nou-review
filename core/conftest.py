# -*- coding: utf-8 -*-
"""conftest pytest — env de test setat INAINTE de colectare (deci inaintea ORICARUI import de modul).

De ce aici si nu in test_spv_conector.py: spv_conector citeste ANAF_CLIENT_ID/ANAF_REDIRECT_URI etc. la
IMPORT (constante la nivel de modul, spv_conector.py:39-46). Daca alt test il importa tranzitiv (via main
sau alt core) INAINTEA lui test_spv_conector.py, constanta inghetase goala -> test_url_autorizare picase
in suita completa (dar trecea izolat, cand era primul). conftest.py e incarcat de pytest inaintea colectarii
testelor -> valorile sunt garantat prezente la PRIMA incarcare a modulului, indiferent de ordine.

Placeholdere, NU secrete: ANAF_REDIRECT_URI e URL-ul PUBLIC de callback (ARHITECTURA_SPV.md), ANAF_CLIENT_ID
e fictiv, JWT_SECRET/SPV_FERNET_KEY sunt de test. Testele lovesc ANAF pe MOCK, niciodata real."""
import os
from cryptography.fernet import Fernet

os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-spv")
os.environ.setdefault("ANAF_CLIENT_ID", "TEST_CLIENT")
os.environ.setdefault("ANAF_REDIRECT_URI", "https://iconta.eu/anaf/oauth/callback")


import pytest  # noqa: E402

# R1, registrul unic de parametri fiscali (10.10.2026): constantele ancorate intră în `common.COTE` la importul modulului lor. Suita
# îl vede ÎNTREG de la început, oricare ar fi ordinea testelor — altfel un gard pe registrul întreg ar trece singur și ar pica în
# suită (sau invers), după cine a importat ce înaintea lui.
from core import common as _common  # noqa: E402

_common.registru_complet()


@pytest.fixture(autouse=True)
def _fara_anaf_la_statut_furnizor(monkeypatch, request):
    """[418a] Statutul furnizorului facturii primite se citește din ANAF: în teste, ANAF „nu răspunde” (rămâne XML-ul, apoi alegerea
    contabilului) — niciodată ANAF real. Un modul care probează funcția declară `STATUT_FURNIZOR_REAL = True` și simulează el ANAF."""
    if getattr(request.module, "STATUT_FURNIZOR_REAL", False):
        return
    import functools
    from core import anaf_api

    def _jos(*a, **k):
        raise OSError("ANAF simulat indisponibil (core/conftest.py)")
    monkeypatch.setattr(anaf_api, "statut_furnizori", functools.partial(anaf_api.statut_furnizori, interogare=_jos))


@pytest.fixture(autouse=True)
def _fara_anaf_la_emitere(monkeypatch, request):
    """[05.10.2026, comanda Costin pct.5] Emiterea consultă ANAF pentru plătitorul de TVA al beneficiarului („RO” pe factură).
    Principiul de mai sus — testele lovesc ANAF pe MOCK, niciodată real — se aplică și aici: consultarea întoarce „nu se știe”.
    Un modul care probează funcția însăși (cu `anaf_api` simulat) declară `ANAF_LA_EMITERE_REAL = True`."""
    if getattr(request.module, "ANAF_LA_EMITERE_REAL", False):
        return
    from core import uc_comun
    monkeypatch.setattr(uc_comun, "_platitor_tva_tert", lambda *a, **k: None)


@pytest.fixture(autouse=True)
def _fara_anaf_la_localitati(monkeypatch, request):
    """[lotul 10, C69] Localitatea partenerilor (D406 / D394) se aduce din ANAF înaintea generării (`anaf_api.aduce_localitati`). În
    teste ANAF „nu răspunde” și cache-ul pornește gol la fiecare test — niciodată ANAF real, nicio localitate rămasă de la alt test.
    Un modul care probează funcția declară `LOCALITATI_ANAF_REAL = True` și simulează el interogarea (`interogare=`)."""
    from core import anaf_api
    monkeypatch.setattr(anaf_api, "_CACHE_LOCALITATI", {})
    if getattr(request.module, "LOCALITATI_ANAF_REAL", False):
        return

    def _jos(*a, **k):
        raise OSError("ANAF simulat indisponibil (core/conftest.py)")
    monkeypatch.setattr(anaf_api, "aduce_localitati", lambda lista, interogare=None: _jos())


@pytest.fixture()
def contor_schema_pastrat():
    """`tenant_schema_seq` pus la loc după test. `rollback` nu întoarce o SECVENȚĂ: un test care creează o firmă în tranzacție întoarsă
    consumă totuși un număr de schemă, iar contorul e o cifră din PREDARE_LANT.md (`core/test_predare_cifre.py`) — fără readucere, suita
    o mută la fiecare rulare (suita a doua a lotului 11: 363 -> 369, de la `test_lot11_p2_surse_unice` +2 și `test_lot11_a459_cui` +4).
    Readucerea se face pe ALTĂ conexiune, după teardown-ul fixturilor care depind de ea (rollback-ul lor întâi). Garda:
    `core/test_predare_cifre.py::test_orice_test_care_creeaza_firme_readuce_contorul_de_scheme`."""
    from core import db as _db
    from core import tenant_provisioning as _tp
    _db.init_pool()
    with _db.get_conn() as c, c.cursor() as cur:
        inainte = _tp.contor_schema(cur)
    yield inainte
    with _db.get_conn() as c, c.cursor() as cur:
        _tp.contor_schema(cur, inainte)
