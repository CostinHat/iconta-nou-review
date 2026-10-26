# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 448 (registrul DEFICIENTE.md: „F5: ciorna salariilor 10/2026 are alte sume decât statul curent (cazul lui 451).”) —
reparația e a lui 451 (`core/ciorne_depasite.py`: ciorna derivată se regenerează pe uscat din sursa ei la validare și la afișarea
Registrului jurnal; altfel e DEPĂȘITĂ, „Validează” inactiv, refacerea din sursă oferită). Testele 451 (`e2e_lot11_s.py`) fac drumul pe
stoc; acesta îl face pe SALARII. Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test.

Date de pornire scrise direct: niciuna. Firma și salariatul (5.000 lei brut, normă întreagă, funcția de bază) vin din fixtura `firma_sal`
(ruta salariaților, `POST /tenants/{id}/salariati`); statul, nota, schimbarea salariului, refacerea și validarea sunt pe ecrane. Luna e
ultima lună ÎNCHEIATĂ (`perioada_incheiata`): nota salariilor se scrie după ce luna s-a încheiat (deficiența 216)."""
from conftest import perioada_incheiata, sql
from e2e_bloc_b import _deschide_rand, _linii_detaliu, _mergi_la_luna, _nota_jn
from e2e_bloc_d import firma_sal  # noqa: F401 — fixtura modulului (firma cu salariatul de 5.000 lei)
from e2e_bloc_d import _stat
from e2e_lot11_s import _jurnal

_F = ".fereastra:last-of-type "
P = perioada_incheiata()


def _ciorne_salarii(s):
    """[(id, suma pe 641 = 421)] ciornele salariilor firmei."""
    return sql('SELECT i.id, (SELECT sum(l.suma) FROM "%s".inregistrari_linii l WHERE l.inregistrare_id = i.id AND l.cont_debit = \'641\' '
               "AND l.cont_credit = '421') FROM \"%s\".inregistrari i WHERE i.status = 'ciorna' AND i.sursa = 'salarii' ORDER BY i.id" % (s, s))


def test_def_448_ciorna_salariilor_depasita_se_reface_din_stat_si_se_valideaza(patron, firma_sal):
    """448. „F5: ciorna salariilor 10/2026 are alte sume decât statul curent (cazul lui 451).” Înainte: statul se schimba după ce nota
    salariilor fusese scrisă, iar ciorna cu sumele vechi rămânea validabilă — intra în evidență cu alte sume decât statul de plată.
    Pașii: Salariați -> statul ultimei luni încheiate -> „Contabilizează statul” -> „Scrie nota ciornă” (641 = 421 · 5.000,00) ->
    „Salariu” pe salariat: 6.000 lei de la 01 al lunii -> statul arată brut 6.000,00 -> Registru jurnal, luna statului: pe rândul ciornei
    caseta spune că acum statul de plată ar scrie 641 = 421 6.000,00 (pe ciornă: 641 = 421 5.000,00), „Validează” inactiv ->
    „Refă nota din statul de plată”: confirmarea „Nota a fost refăcută din statul de plată LL/AAAA”, ciorna veche nu mai există, nota nouă
    are 641 = 421 · 6.000,00 și nicio casetă de depășire -> „Validează”: Validată.
    Temei: OMFP 2634/2015 pct.58 lit.c (`ciorne_depasite.TEMEI`) — „fiecare dată înregistrată în contabilitate trebuie să se regăsească în
    conținutul unui document”; o ciornă cu alte sume decât statul de plată de acum nu se regăsește în documentul ei."""
    s = firma_sal["schema"]
    pg = patron.pg
    # 1. statul lunii încheiate, contat: nota salariilor e ciornă, cu salariul de 5.000
    _stat(patron, firma_sal, luni_inapoi=1)
    pg.click(_F + "#sp-contare")
    pg.wait_for_selector(_F + "#sp-contare-scrie", timeout=30000)
    pg.click(_F + "#sp-contare-scrie")
    pg.wait_for_function("() => { const z = [...document.querySelectorAll('.fereastra')].pop().querySelector('#sp-contare-zona');"
                         " return z && !z.querySelector('#sp-contare-scrie'); }", timeout=30000)
    vechi = _ciorne_salarii(s)
    assert len(vechi) == 1 and float(vechi[0][1]) == 5000.0, vechi
    nid = vechi[0][0]
    # 2. sursa se schimbă: salariul de bază 6.000 de la prima zi a lunii statului („de la” vine cu ea)
    # [lotul 13, 673 / 677] fereastra contabilizării -> statul -> fereastra salariatului -> „Salariu” (fereastra ei)
    from e2e_lot13_sal_ajutor import buton, deschide_salariat, inchide
    inchide(patron)
    deschide_salariat(patron)
    buton(patron, "salariu")
    pg.wait_for_selector(_F + "#salariu-input", timeout=20000)
    assert pg.input_value(_F + "#salariu-data") == P.inceput.isoformat()
    pg.fill(_F + "#salariu-input", "6000")
    pg.click(_F + "#salariu-save")
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop();"
                         " return f && !f.querySelector('#salariu-input') && f.textContent.replace(/\\s+/g, ' ').includes('e 6.000,00 lei de la'); }",
                         timeout=30000)
    patron.captura("statul_schimbat")
    # 3. Registrul jurnal al lunii: ciorna e depășită, cu sumele statului de acum și cele de pe ciornă; „Validează” inactiv
    pg = _jurnal(patron, firma_sal)
    _mergi_la_luna(patron, P.an, P.luna)
    # [lotul 12, 617] caseta depășirii stă în detaliul notei: rândul se deschide întâi (clic pe rând), ca la contabil
    _deschide_rand(patron, _nota_jn(patron, nid))
    pg.wait_for_selector("#jn-depasita-%d" % nid, timeout=30000)
    t = " ".join(pg.inner_text("#jn-depasita-%d" % nid).split())
    patron.captura("depasita")
    assert "nu se validează" in t and ("statul de plată %02d/%d" % (P.luna, P.an)) in t, t
    assert "pe ciornă:" in t and t.index("641 = 421 6.000,00") < t.index("pe ciornă:") < t.index("641 = 421 5.000,00"), t
    assert pg.is_disabled("[data-val='%d']" % nid)
    assert pg.inner_text("[data-reface='%d']" % nid).strip() == "Refă nota din statul de plată"
    # 4. refacerea din stat: ciorna veche înlocuită de nota cu sumele de acum, fără casetă de depășire
    pg.click("[data-reface='%d']" % nid)
    pg.wait_for_function("(t) => (document.querySelector('#j-mesaj') || {innerText: ''}).innerText.includes(t)",
                         arg="Nota a fost refăcută din statul de plată %02d/%d" % (P.luna, P.an), timeout=30000)
    noi = _ciorne_salarii(s)
    assert len(noi) == 1 and noi[0][0] != nid and float(noi[0][1]) == 6000.0, noi
    nou = noi[0][0]
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE id = %%s' % s, (nid,)) == [(0,)]
    pg.wait_for_selector("[data-nota-id='%d']" % nou, timeout=20000)
    assert pg.locator("#jn-depasita-%d" % nou).count() == 0
    # [lotul 12, 617] liniile notei stau în detaliul ei (tabelul Debit / Credit / Sumă), nu pe rând ca „641 = 421 · 6.000,00”
    linii = _linii_detaliu(_deschide_rand(patron, _nota_jn(patron, nou)))
    assert ["641", "421", "6.000,00"] in [l[:3] for l in linii], linii
    assert pg.is_enabled("[data-val='%d']" % nou)
    patron.captura("refacuta")
    # 5. validarea: nota din statul de acum intră în evidență
    pg.click("[data-val='%d']" % nou)
    pg.wait_for_function("(id) => { const r = document.querySelector(`[data-nota-id='${id}']`); return r && r.innerText.includes('Validată'); }",
                         arg=nou, timeout=30000)
    patron.captura("validata")
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % s, (nou,)) == [("validata",)]
