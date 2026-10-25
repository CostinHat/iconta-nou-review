# -*- coding: utf-8 -*-
"""Lotul 12, integrarea I3 (comenzile 12.2 / 12.3): testele de capăt la capăt pentru C194, C197 și C198 (deficiențele găsite de Code).

  · C194 — o D112 aflată deja în „De depus” nu devenea „depășită” când se corecta fișa salariatului (amprenta perioadei cuprindea numai
    notele și facturile). Acum D112 poartă și amprenta datelor salariaților lunii (`coada_api.amprenta_salarii`); după corectura scutirii
    (C133, „Corectează datele”) cardul D112 stă la „Depășite — de generat din nou”, cu motivul. O D112 intrată în coadă înainte de reparație
    (fără amprenta salariaților) e depășită — nu se poate ști dacă mai e cea din fișe (fail-closed, ca la 17.10.2026).
  · C197 — decizia Costin 12.3 pct.7, verbatim: „C84: livrarea intracomunitară de bunuri fără dovada transportului primește avertisment
    la emitere, nu refuz.” Factura recurentă cu o linie „livrare intracomunitară” se emitea din cron fără avertisment. Acum se emite, iar
    avertismentul ajunge în clopoțel (și pe email), cu tipul lui (`factura_recurenta_avertisment`). TEMEI: CF art.294 alin.(2) lit.a,
    CF art.294 alin.(3).
  · C198 — „Descarcă gestiunea GV <luna> (notă ciornă)”, după nota raportului Z, se oferea pe luna în curs și abia apoi primea refuzul C187.
    Acum e inactiv, cu motivul lângă el („Descărcarea gestiunii lunii se face după ce luna se încheie.”), ca „Generează amortizarea” (333).
    (Butonul din Stocuri, „Descarcă gestiunea lunii”: `e2e_lot12_fx3.py::test_def_c187_…`.)

Pașii pe aplicația din index, pe baza de TEST, pe firme NOI (`firma_noua`, `e2e_bloc_e.firma_gv`), pregătite pe drumul ecranelor. Cronul
facturilor recurente e tura lui zilnică (`facturi_recurente.emite_scadente`), chemată din test, ca la C109 (`e2e_lot12_fe3.py`)."""
import datetime as _dt

import pytest

from conftest import firma_noua, perioada_incheiata, sql
from e2e_bloc_e import firma_gv  # noqa: F401 — firma global-valorică a rulării (C198)

CNP = "1960101078916"             # cifra de control verificată (algoritmul din CLAUDE.md; test_import_saga.CNP_OK)
COD_CLIENT_IC = "DE811907980"     # clientul din DE al probelor C78 / C110 / C154 / C160 / fisc3
LUNA = perioada_incheiata("lunar")
ZI = LUNA.inceput.replace(day=10)
AZI = _dt.date.today()


@pytest.fixture()
def firma_i3():
    for f in firma_noua():
        yield f


def _api(e, metoda, cale, corp=None):
    from e2e_bloc_a import _api as a
    return a(e, metoda, cale, corp)


# ── C194 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c194_d112_din_coada_devine_depasita_dupa_corectarea_fisei_salariatului(patron, firma_i3):
    """C194. Pașii: firmă cu un salariat nescutit (angajat 2024, pe ruta „+ Salariat nou”) -> D112 pe luna încheiată în coadă (ruta „Trimite
    în coadă”) -> „De depus”: cardul D112 NU e la „Depășite” -> Salariați -> „Corectează datele”: „Scutit de contribuția minimă” = Da,
    motivul 5 -> Salvează -> „De depus”: cardul D112 stă la „Depășite — de generat din nou”, cu „Declarația e depășită: după generare s-au
    schimbat datele salariaților lunii …”. Apoi documentul de dinainte de reparație: aceeași D112 fără amprenta salariaților -> depășită
    („a intrat în coadă înainte ca aplicația să-i păstreze datele-sursă”).
    MUTAȚIA (`mut_lot12_int3.json`): în `coada_api.depasire`, confruntarea amprentei salariaților -> `True` -> cardul rămâne nedepășit ->
    ROȘU."""
    from e2e_bloc_a import pregateste_firma, _ok
    from e2e_lot72_declaratii import _curata, _deschide_coada, _in_coada, _peste
    f = firma_i3
    pregateste_firma(patron, f, platitor=True, regim_fiscal="profit")
    sid = _ok(_api(patron, "POST", "/tenants/%d/salariati" % f["tenant_id"], {
        "nume": "DEPASIT", "prenume": "ANA", "cnp": CNP, "data_angajare": "2024-01-01", "tip_norma": "intreaga", "ore_zi": 8,
        "salariu_brut": 5000, "persoane_intretinere": 0, "scutit_contrib_minim": False, "functie_baza": True, "cor": "241107",
        "judet_casa": "B"}), "salariatul")
    sid = sid.get("id") or sid.get("salariat_id")
    peste = _peste()
    pg = patron.pg
    try:
        cid = _ok(_in_coada(patron, f, tip="d112"), "D112 în coadă")["coada_id"]
        rand = _deschide_coada(patron, cid)
        patron.captura("d112_in_coada")
        assert pg.locator("#val-depasite " + rand).count() == 0, "D112 depășită înainte de orice corectură"
        # Salariați -> „Corectează datele” -> scutit, motivul 5 (pașii lui C133, `e2e_lot12_sal3.py`)
        patron.firma(f["nume"])
        pg.click("#fa-salariati")
        pg.wait_for_selector("[data-date='%s']" % sid, timeout=30000)
        pg.click("[data-date='%s']" % sid)
        pg.wait_for_selector("#ed-scutit", timeout=20000)
        pg.wait_for_function("() => (document.querySelector('#ed-scutit') || {}).value !== ''", timeout=20000)
        pg.select_option("#ed-scutit", "true")
        pg.select_option("#ed-motiv", "5")
        pg.click("#ed-save")
        pg.wait_for_function("() => document.body.innerText.includes('Corectura scutirii intră')", timeout=30000)
        assert sql('SELECT scutit_contrib_minim, motiv_exceptare FROM "%s".salariati WHERE id = %%s' % f["schema"], (sid,)) == [(True, 5)]
        rand = _deschide_coada(patron, cid)
        txt = " ".join(pg.inner_text(rand).split())
        patron.captura("d112_depasita")
        assert pg.locator("#val-depasite " + rand).count() == 1, "D112 nu e la „Depășite” după corectarea fișei"
        assert ("Declarația e depășită: după generare s-au schimbat datele salariaților lunii (fișa unui salariat, salariul, un concediu "
                "medical, o suspendare, pontajul, elementele variabile sau tichetele).") in txt, txt
        # documentul de dinainte de reparație: D112 intrată în coadă fără amprenta salariaților
        # date-de-pornire: D112 intrată în coadă înainte de C194 (payload fără `amprenta_salarii`), cum stă pe producție
        sql("UPDATE public.declaratii_coada SET payload = payload #- '{_surse,amprenta_salarii}' WHERE id = %s", (cid,))
        rand = _deschide_coada(patron, cid)
        txt = " ".join(pg.inner_text(rand).split())
        patron.captura("vechi_d112_fara_amprenta_salariatilor")
        assert pg.locator("#val-depasite " + rand).count() == 1 and "a intrat în coadă înainte ca aplicația să-i păstreze datele-sursă" in txt, txt
    finally:
        _curata(f, peste)


# ── C197 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c197_recurenta_cu_livrare_ic_se_emite_cu_avertismentul_in_clopotel(patron, firma_i3):
    """C197. Pașii: firmă plătitoare, stoc global-valoric -> Facturi recurente -> „+ Șablon nou” (DE811907980, „Piese schimb marfa E2E
    C197”, cota 0%, categoria „livrare intracomunitară”, ziua 5) -> salvat (avertisment, nu refuz) -> tura cronului: factura lunii se emite
    -> clopoțelul contabilului-șef: „<firma>: factura recurentă pentru KUNDE … s-a emis (<nr>, <zi>), cu 1 avertisment: Factura s-a emis
    automat cu scutirea livrării intracomunitare …, fără ca aplicația să te poată întreba dacă ai dovada transportului …”.
    TEMEI: CF art.294 alin.(2) lit.a (scutirea), CF art.294 alin.(3) (documentele care justifică scutirea).
    MUTAȚIA (`mut_lot12_int3.json`): ramura `if _avert:` din cron -> `if False:` -> nimic în clopoțel -> ROȘU."""
    from conftest import _db
    from core import facturi_recurente
    from e2e_lot12_fe3 import _sablon
    from e2e_lot12_fx3 import _platitor_gv
    f = firma_i3
    s = f["schema"]
    _platitor_gv(patron, f)
    _sablon(patron, f, COD_CLIENT_IC, "KUNDE E2E C197 GMBH", "Piese schimb marfa E2E C197", 0, categorie="livrare_ic", tara="DE")
    _db()
    emise = facturi_recurente.emite_scadente(s, ZI)                   # tura cronului zilnic, în ziua emiterii
    em = [e for e in emise if "sablon" in e]
    assert len(em) == 1 and em[0].get("factura") and em[0].get("avertismente"), emise
    pg = patron.pg
    patron.acasa()
    pg.click("#nav-clopot")
    pg.wait_for_selector(".clopot-item, .clopot-gol", timeout=20000)
    it = pg.locator(".clopot-item", has_text=f["nume"]).filter(has_text="factura recurentă").first
    it.wait_for(timeout=20000)
    txt = " ".join(it.inner_text().split())
    patron.captura("clopot_avertisment")
    assert ("factura recurentă pentru KUNDE E2E C197 GMBH s-a emis (%s, %s), cu 1 avertisment: Factura s-a emis automat cu scutirea "
            "livrării intracomunitare" % (em[0]["factura"], ZI.strftime("%d.%m.%Y"))) in txt, txt
    assert "fără ca aplicația să te poată întreba dacă ai dovada transportului" in txt and "art.294 alin.(3)" in txt, txt
    assert sql("SELECT count(*) FROM public.notificari n JOIN public.users u ON u.id = n.user_id WHERE u.email = 'patron@prisma-cont.test' "
               "AND n.tip = %s AND n.text LIKE %s", (facturi_recurente.TIP_AVERTISMENT, f["nume"] + ":%"))[0][0] == 1


# ── C198 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c198_descarcarea_gv_dupa_z_e_inactiva_pe_luna_in_curs(patron, firma_gv):  # noqa: F811
    """C198. Pașii: firmă global-valorică -> Raport Z de azi (casa 8000000001, 121,00 lei la 21%, numerar) -> „Generează notă” -> sub
    nota Z, „Descarcă gestiunea GV <luna curentă> (notă ciornă)” e inactiv, cu motivul lângă el: „Descărcarea gestiunii lunii se face după
    ce luna se încheie.” (înainte: activ, iar clicul primea refuzul C187). Nicio notă DESC-GV a lunii.
    MUTAȚIA (`mut_lot12_int3.json`): `zInCurs` -> `false` -> butonul activ, fără motiv -> ROȘU."""
    from e2e_bloc_c import _deschide
    f = firma_gv
    pg = patron.pg
    _deschide(patron, f["nume"], "raportz", "#z-salveaza")
    pg.fill("#z-data", AZI.isoformat())
    pg.fill("#z-nui", "8000000001")
    pg.fill("#z-nr", "198%d" % (int(_dt.datetime.now().timestamp()) % 100000))
    pg.fill("#z-21", "121")
    pg.fill("#z-num", "121")
    pg.fill("#z-card", "0")
    pg.fill("#z-bonuri", "3")
    pg.click("#z-salveaza")
    pg.wait_for_selector("#z-desc-gv", timeout=30000)
    patron.captura("z_descarcare_inactiva")
    assert pg.is_disabled("#z-desc-gv") and pg.get_attribute("#z-desc-gv", "aria-describedby") == "z-desc-gv-motiv"
    assert " ".join(pg.inner_text("#z-desc-gv-motiv").split()) == "Descărcarea gestiunii lunii se face după ce luna se încheie."
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("DESC-GV-%d-%02d" % (AZI.year, AZI.month),)) == [(0,)]   # AZI-dat-de-test: luna pe care testul a cerut-o / a datat Z-ul
