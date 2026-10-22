# -*- coding: utf-8 -*-
"""Lotul 11 — subagentul N: 443 pe DATELE EXISTENTE (regula Costin 11.2 pct.3a, verbatim: „Orice reparație acoperă și datele existente.”;
443, comanda 11.1 pct.19: „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”). Pașii contabilului pe aplicația din index,
pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`; CUI-urile cu cifra de control verificată prin `pregateste_firma`).

Date de pornire scrise direct: UNA, marcată pe rândul ei — descrierea notei de contare în forma de dinainte de 443 („Contare factura F61”),
pe care aplicația de azi n-o mai scrie (o scria `contare_facturi._descriere` cu `numar_cu_serie`). Numerotarea, profilul și factura se fac
pe rutele pe care le cheamă ecranele (`PUT facturi/numerotare`, `pregateste_firma`, `emite_api`); validarea și Registrul jurnal, pe ecran."""
import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _api, _card, _ok, emite_api, pregateste_firma


@pytest.fixture(scope="module")
def firma_n():
    for f in firma_noua():
        yield f


def test_def_443_nota_veche_din_registru_jurnal_arata_seria_separat(patron, firma_n):
    """443, datele existente. Pașii: Configurare emitere cu seria „F6”, de la 1 -> factura emisă (ruta formularului): numărul ei e „F61”,
    nota de contare e ciornă -> [pornire: descrierea notei în forma de dinainte de 443, „Contare factura F61”] -> Registru jurnal ->
    „Validează” pe notă -> rândul notei VALIDATE spune „Contare factura F6 nr. 1” și „Factură F6 nr. 1 din …”, nicăieri „F61”; în bază
    descrierea rămâne cum a fost scrisă (nota validată nu se modifică — OMFP 1802/2014 pct.69, triggerul `regula_nota`)."""
    tid, s = firma_n["tenant_id"], firma_n["schema"]
    _ok(_api(patron, "PUT", "/tenants/%d/facturi/numerotare" % tid, {"serie": "F6", "numar_start": 1}), "seria F6")
    pregateste_firma(patron, firma_n)
    f = emite_api(patron, firma_n)
    assert sql('SELECT serie, numar FROM "%s".facturi WHERE id = %%s' % s, (f["factura_id"],))[0] == ("F6", "F61")
    nid, st = sql('SELECT id, status FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = \'facturi\'' % s, (f["factura_id"],))[0]
    assert st == "ciorna", st
    sql('UPDATE "%s".inregistrari SET descriere = %%s WHERE id = %%s AND status = \'ciorna\'' % s,
        ("Contare factura F61", nid))   # date-de-pornire: nota scrisă de codul de dinainte de 443
    pg = patron.pg
    patron.firma(firma_n["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    sel = ".fereastra:last-of-type [data-nota-id='%s']" % nid
    pg.wait_for_selector(sel, timeout=30000)
    pg.click("%s [data-val='%s']" % (sel, nid))
    pg.wait_for_function("(s) => { const r = document.querySelector(s); return r && !r.querySelector('[data-val]'); }", arg=sel, timeout=30000)
    assert sql('SELECT status, descriere FROM "%s".inregistrari WHERE id = %%s' % s, (nid,))[0] == ("validata", "Contare factura F61")
    rand = " ".join(pg.inner_text(sel).split())
    patron.captura()
    assert "Contare factura F6 nr. 1" in rand, rand                # 443: „F6 nr. 1”, derivat din factura notei
    assert "Factură F6 nr. 1 din" in rand, rand                    # documentul justificativ (col.3), din aceeași regulă
    assert "F61" not in rand, rand                                 # 443: „nu F61”
