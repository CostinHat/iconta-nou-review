# -*- coding: utf-8 -*-
"""Lotul 07.10, partea 2 — gărzile pe ecrane (JS), pe NUMĂRĂTOARE de structuri, nu pe apartenența unui șir.

Regulile DS noi (v2.74: ascuns = invizibil, mesajul în vedere, refuzul cu buton spre ecran) au gărzile lor în verificator
(`HIDDEN_CU_DISPLAY`, `MESAJ_FARA_ADUCERE_IN_VEDERE`, `REFUZ_ECRAN_FARA_BUTON`). Aici: comportamentele de ecran ale lotului
care nu sunt reguli generale — ciorna facturii, răspunsul la „Pleacă marfa acum?”, legăturile din notificări, cifrele
cardului „De validat”, fraza despre semnal."""
import io
import re

_JS = "static/js/"


def _js(rel):
    return io.open(_JS + rel, encoding="utf-8").read()


def _corp(src, antet):
    """Corpul funcției care începe cu `antet` (până la prima linie `}` de la începutul rândului, la aceeași indentare)."""
    i = src.index(antet)
    ind = len(src[src.rfind("\n", 0, i) + 1:i])
    j = src.index("\n" + " " * ind + "}", i)
    return src[i:j]


def test_ciorna_facturii_se_sterge_numai_la_emitere_sau_la_renuntare():
    """pct.2: „o factură începută rămâne păstrată … până o emite sau o abandonează explicit”. Ciorna e pe utilizator ȘI firmă,
    se citește înainte de prima desenare a liniilor, se șterge pe exact două drumuri (emiterea reușită, „Renunță la factură”) —
    plus golirea formularului de către om. MUTAȚIE: `stergeCiorna` scos de pe drumul emiterii -> 1 drum -> pică."""
    s = _js("ecrane/emitere_ecran.js")
    cheie = _corp(s, "function cheieCiorna(tenantId)")
    assert len(re.findall(r"u\.id|tenantId", cheie)) >= 2                         # utilizatorul și firma, în cheie
    f = _corp(s, "function formularEmitere(")
    assert len(re.findall(r"stergeCiorna\(tenantId\)", f)) == 3                  # golit de om · emisă · renunțare
    assert f.index("const ciorna = citesteCiorna(tenantId)") < f.index("  deseneazaLinii();\n  ciornaPornita = true;")


def test_raspunsul_la_pleaca_marfa_ramane_pentru_aceleasi_articole():
    """pct.17: după „Stabilește seria și emite” întrebarea nu se repune. MUTAȚIE: verificarea `semnMarfa === semnArticole()`
    scoasă din `porniEmitere` -> pică."""
    p = _corp(_js("ecrane/emitere_ecran.js"), "function porniEmitere()")
    assert len(re.findall(r"pleacaMarfaCurent !== null && semnMarfa === semnArticole\(\)", p)) == 1


def test_scadenta_propusa_urmeaza_data_pana_la_editare():
    """pct.18: scadența propusă = data + zilele serverului, până când omul o schimbă. MUTAȚIE: `scadentaScrisa = true` scos
    de pe evenimentul câmpului -> propunerea ar suprascrie ce a scris omul -> pică."""
    f = _corp(_js("ecrane/emitere_ecran.js"), "function formularEmitere(")
    assert len(re.findall(r"num\.scadenta_zile", f)) >= 2
    assert len(re.findall(r'inScad\.addEventListener\("(?:input|change)", \(\) => \{ scadentaScrisa = true; \}\)', f)) == 2


def test_notificarile_duc_la_element():
    """pct.8: legăturile `validat:<id>` și `jurnal:<firmă>:<notă>[:<an>:<lună>]` deschid ținta. MUTAȚIE: ramura `jurnal:`
    scoasă din clopot -> pică."""
    s = _js("navigator.js")
    assert len(re.findall(r'n\.link\.startsWith\("validat:"\)', s)) == 1
    assert len(re.findall(r'n\.link\.startsWith\("jurnal:"\)', s)) == 1
    assert len(re.findall(r"evidentiaza", _js("ecrane/validat.js"))) >= 2
    assert len(re.findall(r"opt\.evidentiaza", _js("ecrane/firme.js"))) >= 2


def test_cardul_si_fereastra_numara_notele_la_fel():
    """pct.10: „Cardul arată «3 nevalidate», fereastra «Note de validat (2)». Numerele se potrivesc.” Aceeași expresie de
    selecție în ambele. MUTAȚIE: cardul numără și `aprobata` -> expresia diferă -> pică."""
    expr = r'c\.fel === "nota" && c\.stare === "la_senior"'
    assert len(re.findall(expr, _js("ecrane/validat.js"))) == 1
    assert len(re.findall(expr, _js("ecrane/cabinet.js"))) == 1


def test_fraza_despre_semnal_numai_cand_cifrele_difera():
    """pct.21: fraza „Diferențele de mai sus …” stă sub condiția `p.divergente.length`. MUTAȚIE: condiția scoasă -> pică."""
    f = _js("ecrane/firme.js")
    assert len(re.findall(r'\$\{p\.divergente\.length \? " Diferențele de mai sus', f)) == 1
    assert len(re.findall(r"Semnalul de mai sus se recalculează", f)) == 0
