# -*- coding: utf-8 -*-
"""[17.5-F5, AC202] Un singur semn «?» pe titlu sau pe zona fără titlu propriu: inventarul celor 18 locuri (plus cheile cu mai multe ID-uri
din Declarații), ordinea secțiunilor, eticheta contextuală și regula din verificator (probă pozitivă, negativă, două zone distincte)."""
import ast
import csv
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js")

#: fișierul, ID-urile în ordinea secțiunilor, zona (textul din „Ajutor: <zona>”) — inventarul pe sursa C9, după titlu, funcție și ID-uri
INVENTAR = (
    ("ecrane/emitere_ecran.js", ("F048", "F180"), '"Configurare emitere"'),
    ("ecrane/emitere_ecran.js", ("F025", "F172", "F252", "F254"), '"Emite factură"'),
    ("ecrane/etransport_ecran.js", ("F044", "F121"), '"e-Transport"'),
    ("ecrane/facturi_ecran.js", ("F171", "F187"), '"Istoric facturi"'),
    ("ecrane/facturi_ecran.js", ("F045", "F046"), '"Factură"'),
    ("ecrane/firme.js", ("F089", "F088"), '"Stocuri"'),
    ("ecrane/firme.js", ("F140", "F141"), '"Mișcări, fișe de magazie, coduri, nivel minim"'),
    ("ecrane/firme.js", ("F012", "F011", "F073"), '"Bancă"'),
    ("ecrane/login.js", ("F004", "F188"), '"CUI"'),
    ("ecrane/migrare.js", ("F084", "F267"), '(nav.titluCurent ? nav.titluCurent() : "Migrare")'),
    ("ecrane/produse_ecran.js", ("F023", "F070"), '"Produse și servicii"'),
    ("ecrane/setari.js", ("F005", "F114"), '"Chei API"'),
    ("ecrane/setari.js", ("F199", "F204"), '"Export date cabinet"'),
    ("ecrane/setari.js", ("F257", "F261"), '"Notificări"'),
    ("ecrane/termene.js", ("F081", "F093"), '(nav.titluCurent ? nav.titluCurent() : "Termene")'),
    ("navigator.js", ("F062", "F115", "F164"), '"Notificări"'),
    ("ecrane/control_verdict.js", ("F169", "F163", "F162"), '"Declarație vs contabilitate"'),
    ("ecrane/control_verdict.js", ("F051", "F101"), '"Verificări contabile"'),
)
#: grupurile cu un singur semn, păstrate neschimbate (regresii): fișierul și ID-ul
SEMNE_SIMPLE = (("ecrane/control_verdict.js", "F184"), ("ecrane/control_verdict.js", "F183"))


def _cod(f):
    return open(os.path.join(JS, f), encoding="utf-8").read()


def _toate():
    out = {}
    for r, _d, fs in os.walk(JS):
        for f in fs:
            if f.endswith(".js") and ".bak" not in f:
                p = os.path.join(r, f)
                out[os.path.relpath(p, JS)] = open(p, encoding="utf-8").read()
    return out


def test_cele_18_locuri_au_un_singur_semn_de_grup_cu_ordinea_si_zona():
    assert len(INVENTAR) == 18
    for f, ids, zona in INVENTAR:
        apel = 'semnAjutorGrup([%s], %s)' % (", ".join('"%s"' % i for i in ids), zona)
        assert _cod(f).count(apel) == 1, (f, apel)


def test_banca_in_ordinea_operatiilor_contabilului():
    assert 'semnAjutorGrup(["F012", "F011", "F073"], "Bancă")' in _cod("ecrane/firme.js")
    assert 'semnAjutor("F011")' not in _cod("ecrane/firme.js") and 'semnAjutor("F073")' not in _cod("ecrane/firme.js")


def test_grupurile_fiscale_cu_un_semn_raman_simple():
    for f, i in SEMNE_SIMPLE:
        assert 'semnAjutor("%s")' % i in _cod(f)


def test_declaratiile_cu_mai_multe_id_uri_au_un_semn():
    cod = _cod("ecrane/declaratii.js")
    assert "semnAjutorGrup(_DECL_AJUTOR[S.tip], S.tip.toUpperCase())" in cod
    assert ".map((id) => semnAjutor(id))" not in cod


def test_fiecare_id_de_grup_are_nume_si_text_de_ajutor_in_registru():
    reg = {r["ID"]: r for r in csv.DictReader(open(os.path.join(RAD, "FUNCTIONALITATI.csv"), encoding="utf-8-sig"))}
    for _f, ids, _z in INVENTAR:
        for i in ids:
            assert reg[i]["Functionalitate"].strip() and reg[i]["ajutor"].strip(), i


def test_semnul_de_grup_si_fereastra_cu_sectiuni():
    api = _cod("api.js")
    f = api[api.index("export function semnAjutorGrup("):api.index("function _liniiAjutor(")]
    assert 'const et = "Ajutor: " + zona;' in f and 'title="${esc(et)}" aria-label="${esc(et)}"' in f
    assert 'data-ajutor="${esc(lista.join(","))}"' in f and "if (lista.length < 2) return semnAjutor(lista[0]" in f
    g = api[api.index("function _randeazaAjutorGrup("):]
    assert "data-ajutor-sectiune=" in g and "data-ajutor-sectiune-titlu" in g and "_liniiAjutor(a.ajutor)" in g and "data-ajutor-incomplet" in g
    h = api[api.index('if (fid.includes(",")) {'):]
    assert "window._navGlobal.deschide(titluG" in h[:900] and "_ajutorOverlayLiber(titluG" in h[:900], "aceeași fereastră, cu și fără shell"
    assert 'title="Ce face și cum se folosește" aria-label="Ajutor"' in api, "semnul simplu își păstrează comportamentul"


def _reguli_f5():
    src = open(os.path.join(RAD, "verificator_conformitate.py"), encoding="utf-8").read()
    arb = ast.parse(src)
    parti = [ast.get_source_segment(src, n) for n in arb.body
             if (isinstance(n, ast.FunctionDef) and n.name == "reguli_f5")
             or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("_RX_F5_SEMNE", "CHEI_CONSULTANTA") for t in n.targets))]
    ns = {"re": re, "os": os}
    exec("\n".join(parti), ns)
    return ns["reguli_f5"]


def test_verificatorul_accepta_un_semn_si_refuza_doua_in_aceeasi_zona():
    r = _reguli_f5()
    assert r({"x.js": '<h2 class="pf-titlu">Bancă ${semnAjutorGrup(["F012", "F011"], "Bancă")}</h2>'}) == []
    assert r({"x.js": '<h2 class="pf-titlu">Casă ${semnAjutor("F010")}</h2>'}) == []
    # două zone distincte ale aceleiași ferestre: fiecare cu semnul ei, pe titlul ei
    assert r({"x.js": '<h3>Grup 1 ${semnAjutor("F184")}</h3>\n<h3>Grup 2 ${semnAjutor("F183")}</h3>'}) == []
    for rau in ('<h2>Bancă <span class="semne-ajutor">${semnAjutor("F011")}${semnAjutor("F012")}</span></h2>',
                '{ ajutor: semnAjutor("F051") + semnAjutor("F101") }',
                '[].concat(ids).map((id) => semnAjutor(id)).join("")'):
        assert [x[2] for x in r({"x.js": rau})] == ["F5-AC202"], rau


def test_depozitul_nu_mai_are_semne_alaturate():
    assert [x for x in _reguli_f5()(_toate()) if x[2] == "F5-AC202"] == []
