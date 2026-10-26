# -*- coding: utf-8 -*-
"""Lotul 12, deficiența C139 — „Șterge raportul Z” pe rândul Z-ului din ecranul Raport Z.

C139 (găsită de Code la scenariul pilot, pasul 13): „Un raport Z importat (ciornă) nu se poate șterge de nicăieri: Registrul jurnal refuză
nota derivată, iar pentru Raport Z nu există drum de ștergere — un fișier AMEF importat greșit rămâne în lună.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma sintetică cantitativ-valorică a lui `e2e_bloc_c` (`firma_cv`:
„Marfa A <n>”, 20 buc intrate la 4,00 lei). Raportul Z intră prin „Import fișier AMEF” (XML-ul secțiunii II.7, OPANAF 146/2018: `rB` cu
`idR` = NUI + data și ora + numărul raportului), fiecare test cu numărul lui."""
import time

from conftest import sql
from e2e_bloc_c import AZI, _deschide, firma_cv  # noqa: F401 — fixtura modulului (firma cantitativ-valorică)

CASA = "8000000001"


def _xml_amef(nr):
    """Raportul Z al casei 8000000001 de azi: 231,00 lei (200,00 numerar + 31,00 card), cota 21%, TVA 40,09, 12 bonuri."""
    idr = "%s%s1930%s%s" % (CASA, AZI.strftime("%Y%m%d"), "%02d" % (int(time.time()) % 60), nr)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<msj idM="%s">\n  <rB idR="%s" nrAv="0" nrB="12" totB="231.00" totTva="40.09" '
            'totTaxe="0.00" totNet="0.00" monRef="RON">\n    <pl tipP="3" valPl="200.00" monPl="RON"/>\n'
            '    <pl tipP="1" valPl="31.00" monPl="RON"/>\n    <coteZ cota="21" valOp="231.00" tva="40.09"/>\n  </rB>\n</msj>\n'
            % (idr, idr)).encode("utf-8")


def _importa(patron, f, nr):
    """Raport Z -> „Import fișier AMEF” -> rândul Z-ului în listă. Întoarce id-ul notei Z (din bază, după cheia casă + număr)."""
    pg = patron.pg
    _deschide(patron, f["nume"], "raportz", "#z-salveaza")
    pg.set_input_files("#z-amef", {"name": "Z_AMEF_c139_%s.xml" % nr, "mimeType": "application/xml", "buffer": _xml_amef(nr)})
    pg.wait_for_function("() => document.querySelector('#z-amef-msg').innerText.includes('Importat')", timeout=30000)
    (zid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-%s-%s" % (CASA, nr),))]
    pg.wait_for_selector("#z-descarcare [data-z='%d'] #zd-sterge-%d" % (zid, zid), timeout=20000)
    return pg, zid


def _stoc(f):
    return sql('SELECT COALESCE(SUM(CASE WHEN m.tip = \'intrare\' THEN m.cantitate WHEN m.tip = \'iesire\' THEN -m.cantitate ELSE 0 END), 0) '
               'FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id WHERE a.denumire = %%s' % (f["schema"], f["schema"]),
               (f["marfa"],))[0][0]


def _articol(f):
    return sql('SELECT id FROM "%s".articole WHERE denumire = %%s' % f["schema"], (f["marfa"],))[0][0]


# ================================================================ ciornă importată + descărcarea ei -> se șterg toate, stocul revine
def test_def_c139_z_importat_din_amef_se_sterge_cu_descarcarea_lui(patron, firma_cv):
    """C139. Pașii: „Raport Z” -> „Import fișier AMEF” (Z nr. 1391, 231,00 lei, TVA 40,09) -> la descărcare: Marfa A, 2 buc -> „Ieșire pe
    articol” -> „Șterge raportul Z”. Întrebarea spune ce se șterge, cu cifrele (încasat 231,00 lei, TVA 40,09 lei, nota lui ciornă, 1 ieșire
    din stoc de 8,00 lei la cost — 2 × CMP 4,00, OMFP 1802/2014 pct.96); „Da, șterge raportul Z” -> confirmarea „s-a șters”, rândul dispare,
    nota Z-ului și nota ieșirii nu mai sunt, iar marfa a revenit în stoc."""
    f = firma_cv
    stoc0 = _stoc(f)
    pg, zid = _importa(patron, f, "1391")
    pg.select_option("#zd-art-%d" % zid, str(_articol(f)))
    pg.fill("#zd-cant-%d" % zid, "2")
    pg.click(".zd-iesire[data-z='%d']" % zid)
    pg.wait_for_function("() => (document.querySelector('#z-descarcare') || {innerText: ''}).innerText.includes('Ieșire înregistrată')",
                         timeout=20000)
    (nota_iesire,) = [r[0] for r in sql('SELECT inregistrare_id FROM "%s".miscari_stoc WHERE z_inregistrare_id = %%s' % f["schema"], (zid,))]
    assert _stoc(f) == stoc0 - 2
    pg.click("#zd-sterge-%d" % zid)
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    intrebare = " ".join(pg.inner_text("#caseta-atentie-activa").split())
    # data Z-ului e cea din fișierul AMEF scris de test (`_xml_amef`: idR = casa + AZI), nu ziua în care rulează
    # [lotul 13, 605, peticul firme2_4 pe `z_descarcare`] documentul Z se numește o dată: „raportul Z nr 1391 din …”, nu „raportul Z „Raport Z nr …””
    assert ("Ștergi raportul Z nr 1391 din %s (AMEF %s)" % (AZI.strftime("%d.%m.%Y"), CASA)  # AZI-dat-de-test
            in intrebare), intrebare
    assert "încasat 231,00 lei, TVA 40,09 lei" in intrebare, intrebare
    assert "1 ieșire din stoc legată de el, necontată, în valoare de 8,00 lei la cost" in intrebare, intrebare
    assert "Ștergerea nu se poate anula." in intrebare and "Da, șterge raportul Z" in intrebare
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (zid,))[0][0] == 1   # nimic șters înainte de „Da”
    patron.captura("intrebarea")
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => (document.querySelector('#z-descarcare') || {innerText: ''}).innerText.includes('s-a șters')", timeout=20000)
    assert "Marfa descărcată a revenit în stoc." in pg.inner_text("#z-descarcare")
    assert pg.locator("#z-descarcare [data-z='%d']" % zid).count() == 0
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE id IN (%%s, %%s)' % f["schema"], (zid, nota_iesire))[0][0] == 0
    assert sql('SELECT count(*) FROM "%s".rapoarte_z_amef WHERE inregistrare_id = %%s' % f["schema"], (zid,))[0][0] == 0
    assert _stoc(f) == stoc0                                            # marfa revine în stoc
    assert sql("SELECT count(*) FROM public.audit_log WHERE actiune = 'STERGERE raport Z' AND entitate_id = %s", (str(zid),))[0][0] == 1
    patron.captura("sters")


# ================================================================ Z validat: fără buton; luna blocată: refuz numit, nimic șters
def test_def_c139_z_validat_n_are_buton_iar_luna_blocata_refuza(patron, firma_cv):
    """C139. Pașii: două importuri AMEF (Z nr. 1392 și 1393). Z-ul 1392: „Fără marfă din stoc” -> „Validează raportul Z” -> rândul lui arată
    „validat”, fără „Șterge raportul Z”, cu motivul (stornare, OMFP 1802/2014 pct.69). Luna se blochează -> la Z-ul 1393 „Șterge raportul Z”
    -> refuzul „luna … e blocată”, fără întrebare, iar Z-ul rămâne."""
    f = firma_cv
    pg, z1 = _importa(patron, f, "1392")
    pg.click(".zd-fara[data-z='%d']" % z1)
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_selector("#zd-val-%d" % z1, timeout=20000)
    pg.click("#zd-val-%d" % z1)
    pg.wait_for_function("() => (document.querySelector('#z-descarcare') || {innerText: ''}).innerText.includes('e validat')", timeout=20000)
    rand = pg.locator("#z-descarcare [data-z-validat='%d']" % z1)
    assert rand.count() == 1 and "validat" in rand.inner_text(), pg.inner_text("#z-descarcare")
    assert "stornare (OMFP 1802/2014 pct.69)" in " ".join(rand.inner_text().split())
    # [lotul 13, 675] „Șterge raportul Z” stă la locul lui, inactiv, cu motivul (nu dispare); clicul nu face nimic
    b = rand.locator("button", has_text="Șterge raportul Z")
    assert b.count() == 1 and b.get_attribute("aria-disabled") == "true" and "stornare" in (b.get_attribute("title") or "")
    assert rand.locator(".zd-sterge").count() == 0 and pg.locator("#zd-sterge-%d" % z1).count() == 0
    patron.captura("validat_fara_buton")
    pg2, z2 = _importa(patron, f, "1393")
    # date-de-pornire: luna Z-ului blocată cu Z-ul 1393 încă ciornă înăuntru — poarta închiderii (R58: ciornele perioadei) o refuză pe ecran
    sql('INSERT INTO "%s".perioade_blocate (an, luna) VALUES (%%s, %%s)' % f["schema"], (AZI.year, AZI.month))
    try:
        _deschide(patron, f["nume"], "raportz", "#z-salveaza")
        pg2.wait_for_selector("#zd-sterge-%d" % z2, timeout=20000)
        pg2.click("#zd-sterge-%d" % z2)
        pg2.wait_for_function("(id) => (document.querySelector('#zd-msg-' + id) || {innerText: ''}).innerText.includes('e blocată')",
                              arg=z2, timeout=20000)
        assert "luna %s e blocată" % AZI.strftime("%m.%Y") in pg2.inner_text("#zd-msg-%d" % z2)   # AZI-dat-de-test: luna blocată de test
        assert pg2.locator("#caseta-atentie-activa").count() == 0               # refuzul se spune fără întrebare
        assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (z2,)) == [("ciorna",)]
        patron.captura("luna_blocata")
    finally:
        sql('DELETE FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % f["schema"], (AZI.year, AZI.month))
