# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1, zona `infra` — C201: blocaj fără ieșire între o cerere a aplicației și o operație de structură (DDL) pe
aceeași firmă.

CE ERA (25.10.2026, `DEFICIENTE.md` C201). Control fiscal ținea în aceeași cerere două conexiuni; una rămânea „idle in transaction” cu
blocări pe tabelele firmei, `DROP SCHEMA` (curățenia e2e; la fel o migrare rulată cu aplicația pornită) o aștepta, iar a doua conexiune
a cererii aștepta după DDL — 38 de minute, fără niciun termen nicăieri. Pe ecran: fereastra Control fiscal rămânea pe „Se încarcă…”.

CE E ACUM. (1) Control fiscal lucrează pe O SINGURĂ conexiune (garda `core/test_lot13_infra_o_conexiune.py`, peste tot codul);
(2) conexiunile aplicației poartă termene (`db.optiuni_sesiune`: `lock_timeout` 30 s, `idle_in_transaction_session_timeout` 10 min),
iar o cerere oprită de termen răspunde 503 cu textul pentru contabil (`db.text_blocaj`), pe care fereastra îl arată.

PAȘII CONTABILULUI: Control fiscal -> firma -> detaliul se încarcă; apoi, cât o operație de structură ține tabelele firmei (aici
`LOCK TABLE … IN ACCESS EXCLUSIVE MODE`, blocarea pe care o ia orice ALTER / DROP), același drum: fereastra nu mai rămâne agățată — în
cel mult termenul aplicației spune „Datele firmei sunt ocupate chiar acum … Nimic nu s-a salvat; încearcă din nou peste un minut.”;
după ce operația s-a încheiat, același drum arată din nou controlul firmei.

Temei: N/A — reparație tehnică (nu aplică o regulă fiscală)."""
import time

import pytest

from conftest import _db, firma_noua
from e2e_bloc_a import pregateste_firma
from e2e_bloc_d import _control, _control_firma

#: cât poate dura răspunsul cu firma blocată: termenul aplicației (30 s, `db.LOCK_TIMEOUT_IMPLICIT`) + încărcarea paginii
TERMEN_ECRAN_SEC = 55


@pytest.fixture()
def firma_c201():
    for f in firma_noua():
        yield f


def _deschide_detaliul(patron, firma, cu_firma_blocata=False):
    """Control fiscal -> rândul firmei. Navigatorul are O SINGURĂ `.fereastra` (stiva se redesenează în ea, traseul e în antet), deci
    deschiderea se vede pe conținut, nu pe numărul ferestrelor. Cu firma ținută de o operație de structură, fereastra detaliului trebuie
    să apară IMEDIAT, cu „Se încarcă…” (contabilul vede că s-a întâmplat ceva), iar mesajul vine în ea când răspunde cererea."""
    _control(patron)
    patron.pg.locator(".fereastra:last-of-type #cf-lista .mig-frand", has_text=firma["nume"]).first.click()
    if cu_firma_blocata:
        patron.pg.wait_for_function(
            "() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return !!f && !f.querySelector('#cf-lista') && "
            "f.innerText.includes('Se încarcă'); }", timeout=5000)
        patron.captura("fereastra_deschisa_imediat_se_incarca")
    # fereastra detaliului iese din „Se încarcă…”: fie controlul, fie mesajul de eroare
    patron.pg.wait_for_function(
        "() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return !!f && !f.querySelector('#cf-lista') && "
        "!!f.querySelector('.cf-decl, .cf-grup-titlu, .msg-eroare') && !f.innerText.includes('Se încarcă'); }",
        timeout=TERMEN_ECRAN_SEC * 1000)


def test_def_c201_control_fiscal_raspunde_cu_mesaj_cand_firma_e_tinuta_de_o_operatie_de_structura(patron, firma_c201):
    tid, s = firma_c201["tenant_id"], firma_c201["schema"]
    pregateste_firma(patron, firma_c201, platitor=True, regim_fiscal="micro")
    pg = patron.pg

    # 1. firma liberă: controlul se încarcă
    _control_firma(patron, firma_c201)
    inainte = patron.fereastra()
    patron.captura("firma_libera")
    assert firma_c201["nume"] in inainte and "Nu s-a putut" not in inainte, inainte[:400]
    titluri_inainte = pg.locator(".fereastra:last-of-type .cf-grup-titlu").all_inner_texts()
    assert titluri_inainte, "detaliul firmei nu are grupurile de declarații"

    # 2. o operație de structură ține tabelele firmei
    db = _db()
    with db.get_conn() as h, h.cursor() as cur:
        cur.execute("SET LOCAL lock_timeout = '5s'")
        # date-de-pornire: blocarea (nu o scriere) pe care o ia orice operație de structură (ALTER / DROP) pe tabelele firmei
        cur.execute('LOCK TABLE "%s".firma_profil IN ACCESS EXCLUSIVE MODE' % s)
        t0 = time.monotonic()
        _deschide_detaliul(patron, firma_c201, cu_firma_blocata=True)
        durata = time.monotonic() - t0
        blocata = patron.fereastra()
        patron.captura("firma_tinuta_de_o_operatie_de_structura")
        h.rollback()                                   # operația s-a încheiat: blocarea se ridică
    assert "Datele firmei sunt ocupate chiar acum" in blocata and "Nimic nu s-a salvat" in blocata, blocata[:400]
    assert durata < TERMEN_ECRAN_SEC, "fereastra a stat %.0f s — termenul aplicației nu a oprit cererea" % durata
    assert any(st == 503 and "/control-fiscal/%d" % tid in u for st, u in patron.cereri_rele), patron.cereri_rele
    assert not [x for x in patron.cereri_rele if x[0] != 503], patron.cereri_rele   # nicio altă cădere (500) pe drum
    patron.cereri_rele.clear()

    # 3. după operație: același drum arată din nou controlul, cu aceleași grupuri
    _control_firma(patron, firma_c201)
    dupa = patron.fereastra()
    patron.captura("dupa_operatie")
    assert "Datele firmei sunt ocupate" not in dupa and "Nu s-a putut" not in dupa, dupa[:400]
    assert pg.locator(".fereastra:last-of-type .cf-grup-titlu").all_inner_texts() == titluri_inainte
    assert not patron.cereri_rele and not patron.erori, (patron.cereri_rele, patron.erori)
