# -*- coding: utf-8 -*-
"""Lotul 3 (comanda Costin 14.10.2026, verbatim în DECIZII „Lotul 3”): 246 — asistentul (fără „Poate valida”) vede ciorna ALTUI utilizator,
dar nu o editează, nu o șterge, nu o trimite la validare; C26 — consolidarea și coada de validare îi arată asistentului numai firmele
alocate lui. Pe aplicația din index, pe baza de TEST, pe o firmă sintetică alocată asistentului."""
import os
import sys

import pytest

from conftest import _scoate_firmele_e2e, firma_noua, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_d import ASISTENT, PATRON, _api, _firma_noua, _jurnal, _uid   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core import drepturi as _dr   # noqa: E402


@pytest.fixture(scope="module")
def firma_246():
    f = _firma_noua("D246")          # alocată asistentului (`_atribuie_asistentului`)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _nume(email):
    return sql("SELECT COALESCE(NULLIF(btrim(concat_ws(' ', prenume, nume)), ''), email) FROM public.users WHERE email = %s", (email,))[0][0]


def _nota(email, tid, descriere):
    import datetime
    st, r = _api(email, "POST", "/tenants/%d/jurnal" % tid, {"data": datetime.date.today().isoformat(), "descriere": descriere,
                                                            "document_ref": "D246", "linii": [{"debit": "6022", "credit": "5311", "suma": 12}]})
    assert st == 200 and r.get("id"), (st, r)
    return r["id"]


def test_def_246_ciorna_altui_utilizator_se_vede_dar_nu_se_schimba(asistent, firma_246):
    """246. Registru jurnal (F2), ca Ana Asistent: nota-ciornă scrisă de contabilul-șef se vede, fără „Editează”, „Șterge”, „Trimite la
    validare”, cu motivul scris pe rând; nota ei proprie nu poartă motivul. Cererile directe (editare, ștergere, trimitere la validare)
    sunt refuzate de server cu același text, iar nota rămâne neatinsă."""
    tid = firma_246["tenant_id"]
    a_patronului = _nota(PATRON, tid, "Ciorna contabilului-șef D246")
    a_ei = _nota(ASISTENT, tid, "Ciorna Anei D246")
    _jurnal(asistent, firma_246)
    pg = asistent.pg
    stare = pg.evaluate("""(ids) => ids.map(i => { const r = document.querySelector(`.fereastra:last-of-type [data-nota-id='${i}']`);
        const m = r && r.querySelector('.jn-a-altuia');
        return r ? {edit: !!r.querySelector('[data-edit]'), del: !!r.querySelector('[data-del]'), trimite: !!r.querySelector('[data-retrimite]'),
                    motiv: m ? m.innerText.trim() : null} : null; })""", [a_patronului, a_ei])
    asistent.captura()
    nume = _nume(PATRON)
    motiv = _dr.MESAJ_CIORNA_ALTUI % (a_patronului, nume, nume)
    assert stare[0] == {"edit": False, "del": False, "trimite": False, "motiv": motiv}, stare[0]
    assert stare[1] is not None and stare[1]["motiv"] is None, stare[1]
    for metoda, cale, corp in (("PUT", "/tenants/%d/jurnal/%d" % (tid, a_patronului), {"descriere": "schimbată de Ana"}),
                               ("DELETE", "/tenants/%d/jurnal/%d" % (tid, a_patronului), None),
                               ("POST", "/tenants/%d/jurnal/%d/retrimite" % (tid, a_patronului), {})):
        st, r = _api(ASISTENT, metoda, cale, corp)
        assert (st, (r or {}).get("detail")) == (403, motiv), (metoda, st, r)
    assert sql("SELECT descriere, status FROM %s.inregistrari WHERE id = %%s" % firma_246["schema"], (a_patronului,)) == \
        [("Ciorna contabilului-șef D246", "ciorna")]
    assert sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND creat_de_id = %s "
               "AND payload->>'inregistrare_id' = %s", (tid, _uid(ASISTENT), str(a_patronului))) == [(0,)]


def test_def_c26_consolidarea_si_coada_asistentului_numai_firmele_lui(asistent, firma_246):
    """C26. Cabinet -> Consolidare (`GET /cabinet/consolidare`) și coada de validare (`GET /coada`), ca asistent: numai firmele alocate
    lui; contabilul-șef le vede pe toate ale cabinetului (inclusiv o firmă nealocată asistentului)."""
    for nealocata in firma_noua():   # firmă NOUĂ a cabinetului, NEALOCATĂ asistentului
        alocate = {r[0] for r in sql("SELECT tenant_id FROM public.user_tenants WHERE user_id = %s", (_uid(ASISTENT),))}
        assert firma_246["tenant_id"] in alocate and nealocata["tenant_id"] not in alocate
        st, a = _api(ASISTENT, "GET", "/cabinet/consolidare")
        st_p, p = _api(PATRON, "GET", "/cabinet/consolidare")
        assert (st, st_p) == (200, 200), (st, a, st_p)
        ale_ei = {f["tenant_id"] for f in a["firme"]}
        assert firma_246["tenant_id"] in ale_ei and ale_ei <= alocate, (ale_ei, alocate)
        assert nealocata["tenant_id"] in {f["tenant_id"] for f in p["firme"]}
        st, c = _api(ASISTENT, "GET", "/coada")
        assert st == 200 and {x["tenant_id"] for x in c["coada"]} <= alocate, c
        asistent.acasa()
        asistent.captura()
