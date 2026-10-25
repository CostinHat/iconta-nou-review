# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 pct.8 — Raport Z (retestul Costin pe F1, Z-8000000001-0042 din 20.10.2026), verbatim:

  a. 438: „descărcarea mărfii vândute pe Z are ca document justificativ «Bon de consum nr 1 din 20.10.2026». Bonul de consum e pentru
     consum intern; la vânzarea pe Z documentul e raportul Z (nr. 0042, casa 8000000001).”
  b. „La refuzul «numerar + card ≠ total» mesajul nu dă cifrele (total 231,00, încasat 200,00, diferență 31,00).”
  c. „După generare, titlul «Notă generată» e roșu, conturile notei nu se văd, iar «Generează notă» rămâne activ.”
  d. „La ieșirea peste stoc mesajul e «iesire 1000 peste stocul 139.000»: fără diacritice, iar «139.000» se citește 139 de mii. Corect:
     «Ieșire de 1.000 buc peste stocul de 139 buc».”
  e. „După descărcare nu se vede valoarea descărcată și nici butonul de validare a Z-ului.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma sintetică cantitativ-valorică a lui `e2e_bloc_c` (`firma_cv`:
„Marfa A <n>”, 20 buc intrate la 4,00 lei). Fiecare test își scrie Z-ul lui (casa 8000000001, alt număr), deci rulează și singur."""
import re

from conftest import sql
from e2e_bloc_c import AZI, _deschide, firma_cv  # noqa: F401 — fixtura modulului (firma cantitativ-valorică)

CASA = "8000000001"


def _z(patron, f, nr, total_21="231", numerar="231", card="0", bonuri="12"):
    """Raport Z: data de azi, casa, numărul, total 21%, numerar, card, bonuri — completat, nu trimis."""
    pg = patron.pg
    _deschide(patron, f["nume"], "raportz", "#z-salveaza")
    pg.fill("#z-data", AZI.isoformat())
    pg.fill("#z-nui", CASA)
    pg.fill("#z-nr", nr)
    pg.fill("#z-21", total_21)
    pg.fill("#z-num", numerar)
    pg.fill("#z-card", card)
    pg.fill("#z-bonuri", bonuri)
    return pg


def _genereaza(patron, f, nr, **k):
    """Z generat (ciornă, la cantitativ-valoric): întoarce id-ul notei Z, luat din bază după cheia lui (casa + numărul)."""
    pg = _z(patron, f, nr, **k)
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('Notă generată')",
                         timeout=20000)
    (zid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-%s-%s" % (CASA, nr),))]
    pg.wait_for_selector("#z-descarcare [data-z='%d']" % zid, timeout=20000)
    return pg, zid


def _articol(f):
    return sql('SELECT id FROM "%s".articole WHERE denumire = %%s' % f["schema"], (f["marfa"],))[0][0]


def _iesire(pg, zid, aid, cant):
    pg.select_option("#zd-art-%d" % zid, str(aid))
    pg.fill("#zd-cant-%d" % zid, str(cant))
    pg.click(".zd-iesire[data-z='%d']" % zid)


# ================================================================ 438 — documentul descărcării pe Z
def test_def_438_descarcarea_pe_z_are_ca_document_raportul_z(patron, firma_cv):
    """438. Pașii: Raport Z nr. 1438, casa 8000000001, 231,00 lei -> „Generează notă” -> la descărcare: Marfa A, 2 buc -> „Ieșire pe
    articol”. Nota 607 = 371 și rândul din fișa de magazie au ca document „Raport Z nr 1438 din <azi> (casa 8000000001)”, nu „Bon de
    consum”; niciun bon de consum nu s-a numerotat."""
    f = firma_cv
    pg, zid = _genereaza(patron, f, "1438")
    aid = _articol(f)
    _iesire(pg, zid, aid, 2)
    pg.wait_for_function("() => (document.querySelector('#zd-rez') || {innerText: ''}).innerText.includes('Ieșire înregistrată')",
                         timeout=20000)
    doc = "Raport Z nr 1438 din %s (casa %s)" % (AZI.strftime("%d.%m.%Y"), CASA)
    rand = sql('SELECT i.document_ref, m.document FROM "%s".miscari_stoc m JOIN "%s".inregistrari i ON i.id = m.inregistrare_id '
               "WHERE m.z_inregistrare_id = %%s" % (f["schema"], f["schema"]), (zid,))
    assert rand == [(doc, doc)], rand
    assert not [r for r in sql('SELECT document_ref FROM "%s".inregistrari' % f["schema"]) if (r[0] or "").startswith("Bon de consum")]
    patron.captura()


# ================================================================ 8b — refuzul cu cifrele
def test_def_zrefuz_numerar_plus_card_diferit_de_total_da_cifrele(patron, firma_cv):
    """8b. Pașii: Raport Z: total 21% 231,00, numerar 200,00, card 0 -> „Generează notă”. Refuzul spune totalul, încasatul și
    diferența: „total 231,00 lei, încasat 200,00 lei (…), diferență 31,00 lei”; nimic nu se scrie."""
    f = firma_cv
    pg = _z(patron, f, "2001", numerar="200")
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('diferență')", timeout=20000)
    t = " ".join(pg.inner_text("#z-rezultat").split())
    assert "total 231,00 lei, încasat 200,00 lei" in t and "diferență 31,00 lei" in t, t
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-%s-2001" % CASA,)) == [(0,)]
    patron.captura()


# ================================================================ 8c — după generare
def test_def_zgenerat_titlul_nu_e_rosu_conturile_se_vad_butonul_inactiv(patron, firma_cv):
    """8c. Pașii: Raport Z nr. 2002 cu numerar 200,00 (refuzat), apoi card 31,00 -> „Generează notă”. Titlul „Notă generată” nu e roșu
    (refuzul de dinainte nu-și lasă culoarea), conturile notei se văd (5311 = 707 200,00 lei; 5125 = 707 31,00 lei; 707 = 4427
    40,09 lei), iar „Generează notă” e inactiv; scris alt număr de Z, se reactivează."""
    f = firma_cv
    pg = _z(patron, f, "2002", numerar="200")
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('diferență')", timeout=20000)
    pg.fill("#z-card", "31")
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('Notă generată')",
                         timeout=20000)
    culoare = pg.eval_on_selector("#z-rezultat .cok-titlu", "e => getComputedStyle(e).color")
    assert culoare != "rgb(163, 35, 28)", culoare                      # roșul lui .msg-eroare (static/stil.css)
    assert "msg-eroare" not in (pg.get_attribute("#z-rezultat", "class") or "")
    linii = " ".join(pg.inner_text("#z-nota-linii").split())
    # TVA = 231,00 × 21 / 121 = 40,09 (CF art.291 alin.(1) lit.a, cota standard; rotunjire aritmetică)
    for l in ("5311 = 707 · 200,00 lei", "5125 = 707 · 31,00 lei", "707 = 4427 · 40,09 lei"):
        assert l in linii, linii
    assert pg.is_disabled("#z-salveaza")
    pg.fill("#z-nr", "2003")
    assert pg.is_enabled("#z-salveaza")
    patron.captura()


# ================================================================ 8d — ieșirea peste stoc
def test_def_zstoc_iesirea_peste_stoc_cu_cantitatea_romaneasca_si_unitatea(patron, firma_cv):
    """8d. Pașii: Raport Z nr. 2004 -> „Generează notă” -> la descărcare: Marfa A, 1000 buc -> „Ieșire pe articol”. Refuzul, la rândul
    Z-ului: „Ieșire de 1.000 buc peste stocul de <n> buc” (cu diacritice, cantitatea în formatul românesc, cu unitatea)."""
    f = firma_cv
    pg, zid = _genereaza(patron, f, "2004")
    _iesire(pg, zid, _articol(f), 1000)
    pg.wait_for_function("(id) => (document.querySelector('#zd-msg-' + id) || {innerText: ''}).innerText.includes('peste stocul')",
                         arg=zid, timeout=20000)
    t = " ".join(pg.inner_text("#zd-msg-%d" % zid).split())
    assert re.search(r"Ieșire de 1\.000 buc peste stocul de \d+ buc", t), t
    assert "iesire" not in t and ".000 buc peste" not in t.split("stocul de")[-1], t
    patron.captura()


# ================================================================ 8e — valoarea descărcată și validarea Z-ului
def test_def_zdescarcare_arata_valoarea_si_butonul_de_validare(patron, firma_cv):
    """8e. Pașii: Raport Z nr. 2005 -> „Generează notă” -> Marfa A, 2 buc -> „Ieșire pe articol”. Confirmarea spune valoarea (8,00 lei
    la cost — 2 × CMP 4,00), rândul Z-ului arată „în valoare de 8,00 lei” și butonul „Validează raportul Z”; apăsat, Z-ul se validează
    (iese din lista celor nevalidate, confirmare „e validat”)."""
    f = firma_cv
    pg, zid = _genereaza(patron, f, "2005")
    _iesire(pg, zid, _articol(f), 2)
    pg.wait_for_selector("#zd-val-%d" % zid, timeout=20000)
    # OMFP 1802/2014 pct.96: ieșirea la costul mediu ponderat — 2 buc × 4,00 = 8,00 lei
    assert "Ieșire înregistrată: 8,00 lei" in pg.inner_text("#zd-rez")
    assert "în valoare de 8,00 lei" in " ".join(pg.inner_text("#zd-valoare-%d" % zid).split())
    patron.captura("descarcat")
    pg.click("#zd-val-%d" % zid)
    # [lotul 12, 474] Z-ul n-are articole, deci înainte de validare aplicația spune ce s-a descărcat (la cost) față de vânzare și cere
    # confirmarea (`z_descarcare.avertisment_descarcare`) — aceeași valoare de 8,00 lei
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    caseta = " ".join(pg.inner_text("#caseta-atentie-activa").split())
    assert "Ai descărcat din stoc 1 ieșire la cost 8,00 lei" in caseta and pg.inner_text("#ca-ok").strip() == "Da, validează raportul Z", caseta
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => (document.querySelector('#zd-rez') || {innerText: ''}).innerText.includes('e validat')", timeout=20000)
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (zid,)) == [("validata",)]
    assert pg.locator("#z-descarcare [data-z='%d']" % zid).count() == 0
    patron.captura("validat")
