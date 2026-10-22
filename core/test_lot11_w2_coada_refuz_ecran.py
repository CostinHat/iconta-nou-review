# -*- coding: utf-8 -*-
"""Lotul 11, subagentul W2 — deficiența 445 (comanda Costin 11.1 pct.21, verbatim în DECIZII „Comanda 11.1”: „orice buton «Deschide X»
dintr-un refuz întoarce în formularul de plecare, cu datele intacte.”), drumul „Trimite în coadă”.

`uc_coada.coada_adauga` prindea refuzul generatorului ca text (`except ValueError: DateInvalide(str(e))`): un `RefuzGenerare` care
numește ecranul unde se repară (`ecran`, `camp_ecran`, notele) ajungea la ecran ca frază, deci `coada_trimite.js` nu avea ce buton
„Deschide <ecran>” să pună lângă refuz. Acum, ca în `uc_declaratii` (generarea), refuzul tipat trece ca obiect (`RefuzGenerare.detaliu`),
iar celelalte `ValueError` rămân text.

Temei: N/A — contract de interfață (nicio regulă fiscală).
"""
import contextlib

import pytest

from core import erori as _erori
from core import uc_coada


class _Date:
    tenant_id = 1
    tip = "d300"

    def model_dump(self, exclude_none=True):
        return {"tenant_id": 1, "tip": "d300", "an": 2099, "luna": 1}


#: refuzul unui generator cu ecranul care-l repară (textul nu e al testului: trece neschimbat prin coadă)
_REFUZ_ADRESA = "Lipsește adresa firmei: declar-o în Date firmă."


@pytest.fixture
def coada_fara_baza(monkeypatch):
    """Drumul use-case-ului până la generator, fără bază: dreptul da, schema cunoscută, generatorul înlocuit de test."""
    monkeypatch.setattr(uc_coada._uc_comun, "_are_permisiune", lambda ctx, p: True)
    monkeypatch.setattr(uc_coada._uc_comun, "_schema_sau_404", lambda ctx, tid: "tenant_test_w2")
    import core.uc_declaratii as _ud
    monkeypatch.setattr(_ud, "aduce_localitati_parteneri", lambda schema, tip: None)
    monkeypatch.setattr(uc_coada.db, "get_conn", lambda schema=None: contextlib.nullcontext(None))

    def cu(exceptie):
        def genereaza(conn, schema, tip, body):
            raise exceptie
        monkeypatch.setattr(uc_coada.declaratii_api, "genereaza", genereaza)
    return cu


def test_refuzul_generatorului_cu_ecran_ajunge_ca_obiect(coada_fara_baza):
    coada_fara_baza(_erori.RefuzGenerare(_REFUZ_ADRESA, ecran="date_firma", camp_ecran="df-adresa"))
    with pytest.raises(_erori.DateInvalide) as ex:
        uc_coada.coada_adauga(_Date(), ctx={})
    det = ex.value.detaliu
    # înainte: detaliul era textul (`str(e)`), fără `ecran` -> fără butonul „Deschide Date firmă” lângă refuzul din coadă
    assert isinstance(det, dict), det
    assert det["ecran"] == "date_firma" and det["camp_ecran"] == "df-adresa", det
    assert det["mesaj"] == _REFUZ_ADRESA, det   # textul refuzului trece neschimbat


def test_celelalte_refuzuri_raman_text(coada_fara_baza):
    coada_fara_baza(ValueError("perioada nu e încheiată"))
    with pytest.raises(_erori.DateInvalide) as ex:
        uc_coada.coada_adauga(_Date(), ctx={})
    assert ex.value.detaliu == "perioada nu e încheiată"
