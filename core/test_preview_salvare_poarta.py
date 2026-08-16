# -*- coding: utf-8 -*-
"""GARD Q5 — preview = salvare, O SINGURA POARTA (tura import CUBUS, 16.08.2026).

DEFECT reparat structural: endpointul de PREVIEW (/incarca) al fiecarui strat de migrare isi
lua verdictul din flagurile ad-hoc ale lui extrage (`cnp_valid`, `ok`) - o A DOUA validare care
DRIFTA de la `verifica_randuri`, poarta pe care SALVAREA (importa) o aplica la scriere. Preview
arata "toate valide", userul trimitea, salvarea intorcea 422 pe randuri pe care preview nu le
semnalase. Fix: fiecare endpoint de preview intoarce `erori = verifica_randuri(...)` (prin
migrare_api.erori_verifica), ACELASI verdict ca salvarea (DS cap.24).

Gardul trece ACELASI fisier prin AMBELE capete si cere verdict IDENTIC pe fiecare rand:
  - capatul PREVIEW = raspunsul endpointului /incarca (`res["erori"]`);
  - capatul SALVARE = verifica_randuri (poarta pe care importa o ridica - vezi *_import_api.importa).
Randul-drift din fiecare caz TRECE flagul lui extrage (cnp_valid=True / ok=True) dar PICA la
verifica_randuri -> pe codul vechi preview il rata (nu exista cheia `erori`) -> gardul e RED.
"""
import io
import asyncio
import contextlib
import pytest
from starlette.datastructures import UploadFile

import main
from core import migrare_api
from core import solduri_parteneri_api as _part
from core import salariati_import_api as _sal
from core import asociati_import_api as _aso
from core import mijloace_fixe_import_api as _mf
from core import istoric_declaratii_import_api as _ist


@contextlib.contextmanager
def _fake_conn(*a, **k):
    yield None


def _uf():
    return UploadFile(io.BytesIO(b"x"), filename="x.csv")


# (nume, endpoint, modul, randuri-cu-un-rand-drift, motiv asteptat, are_nevoie_de_conn)
CAZURI = [
    ("parteneri", main.parteneri_incarca, _part,
     [{"cont": "4111", "cui": "", "denumire": "POP", "debit": 100.0, "credit": 0.0}],
     "cui_invalid", True),
    ("salariati", main.salariati_import_incarca, _sal,
     [{"nume": "POP", "prenume": "ION", "cnp_valid": True, "tip_norma": "", "ore_zi": 0}],
     "norma_lipsa", False),
    ("asociati", main.asociati_import_incarca, _aso,
     [{"nume": "POP ION", "cnp": "1234567890123", "cota": 100}],
     "cnp_invalid", False),
    ("mijloace", main.mijloace_import_incarca, _mf,
     [{"cod": "MF1", "denumire": "X", "valoare": 5000.0, "rezidual": 0.0, "dnf_luni": 0, "ok": True}],
     "durata", False),
    ("istoric", main.istoric_import_incarca, _ist,
     [{"tip": "D999", "an": 2025, "luna": 1, "data_depunere": "", "ok": True}],
     "tip", False),
]


@pytest.mark.parametrize("nume,endpoint,modul,randuri,motiv,cu_conn",
                         CAZURI, ids=[c[0] for c in CAZURI])
def test_preview_intoarce_verdictul_salvarii(monkeypatch, nume, endpoint, modul, randuri, motiv, cu_conn):
    monkeypatch.setattr(main, "_schema_sau_404", lambda ctx, tid: "public")
    monkeypatch.setattr(modul, "extrage", lambda *a, **k: randuri)
    if cu_conn:
        monkeypatch.setattr(main.db, "get_conn", _fake_conn)
        monkeypatch.setattr(_part, "coerenta", lambda conn, r: [])

    res = asyncio.run(endpoint(1, fisier=_uf(), ctx={"uid": 1}))

    assert "erori" in res, "preview NU intoarce cheia `erori` (poarta lipseste) - %s" % nume
    asteptat = migrare_api.erori_verifica(modul.verifica_randuri(randuri))
    assert res["erori"] == asteptat, "preview != verifica_randuri (drift) - %s" % nume
    assert any(e.get("motiv") == motiv for e in res["erori"]), \
        "randul-drift (extrage OK, verifica_randuri respinge) nu apare la preview - %s: %r" % (nume, res["erori"])


def test_preview_curat_nu_blocheaza():
    """Un rand VALID -> erori == [] (Salvarea nu se blocheaza; fara fals-pozitiv)."""
    randuri = [{"cod": "MF1", "denumire": "Strung", "cont_imobilizare": "2131",
                "valoare": 5000.0, "rezidual": 0.0, "dnf_luni": 60, "ok": True}]
    import types
    mp = pytest.MonkeyPatch()
    try:
        mp.setattr(main, "_schema_sau_404", lambda ctx, tid: "public")
        mp.setattr(_mf, "extrage", lambda *a, **k: randuri)
        res = asyncio.run(main.mijloace_import_incarca(1, fisier=_uf(), ctx={"uid": 1}))
    finally:
        mp.undo()
    assert res["erori"] == [], res["erori"]
