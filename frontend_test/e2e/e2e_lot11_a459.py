# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.3 pct.5 (Costin 22.10.2026, verbatim în DECIZII „Comanda 11.3”) — 459: „un CUI cu cifra de control greșită e
acceptat la adăugarea firmei; la schimbarea CUI-ului rămân datele celui vechi.”

Pașii contabilului pe aplicația din index, pe baza de TEST. Nimic nu se scrie direct în bază (garda `core/test_e2e_fara_date_fabricate.py`):
firma de pornire e `firma_e2e` (provizionarea aplicației), datele ei vechi intră pe ruta formularului Date firmă (`POST firma-profil/date`),
corectura trece prin ecran. Răspunsul ANAF e servit de plasă pe server (`anaf_api.CHEIE_SIMULAT`, `<dir>/anaf.json` — cheile celorlalte
teste se păstrează, a noastră se scoate la final). CUI-urile au cifra de control calculată cu algoritmul din CLAUDE.md (`cui_cu_control`);
cel greșit e unul valid cu ultima cifră schimbată. Mutațiile: frontend_test/e2e/mut_lot11_a459.json."""
import json
import os
import time

from conftest import PREFIX_FIRMA, cui_cu_control, sql
from e2e_bloc_d import PATRON, _api as _api_cont

#: textul refuzului, același pe toate drumurile (`tenant_provisioning.MESAJ_CUI_CONTROL`)
CIFRA = "cifra de control nu corespunde — verifică CUI-ul"


def _gresit(cui):
    return cui[:-1] + str((int(cui[-1]) + 1) % 10)


def _anaf_pune(raspunsuri):
    """Adaugă răspunsuri în plasa ANAF (`anaf_api._raspuns_simulat`), fără să le șteargă pe ale altor teste. -> cheile puse."""
    d = os.environ["ICONTA_ANAF_SIMULAT"]
    os.makedirs(d, exist_ok=True)
    cale = os.path.join(d, "anaf.json")
    vechi = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
    vechi.update(raspunsuri)
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(vechi, f, ensure_ascii=False)
    return list(raspunsuri)


def _anaf_scoate(chei):
    cale = os.path.join(os.environ["ICONTA_ANAF_SIMULAT"], "anaf.json")
    if os.path.exists(cale):
        d = json.load(open(cale, encoding="utf-8"))
        for k in chei:
            d.pop(k, None)
        with open(cale, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)


def _ruta(cale, corp, ce):
    st, r = _api_cont(PATRON, "POST", cale, corp)
    assert st == 200 and (not isinstance(r, dict) or r.get("ok") is not False), (ce, st, r)
    return r


def _deschide_adauga_firma(patron):
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.wait_for_timeout(400)
    if pg.query_selector("#opt-existente"):
        pg.click("#opt-existente")
    pg.wait_for_selector("#firme-adauga", timeout=20000)
    pg.click("#firme-adauga")
    pg.wait_for_selector("#fn-cui", timeout=10000)
    return pg


def _eroare_cui(pg):
    pg.wait_for_selector(".msg-eroare[data-camp='fn-cui']", timeout=30000)
    return pg.inner_text(".msg-eroare[data-camp='fn-cui']")


def test_def_459_cui_gresit_e_refuzat_langa_camp_la_adaugarea_firmei(patron):
    """459 (1). Pașii: Firme -> „+ Adaugă firmă” -> CUI-ul cu cifra de control greșită: lângă câmp „CUI-ul … nu e valid: cifra de control
    nu corespunde — verifică CUI-ul”, câmpul marcat, „Adaugă firma” inactiv (și după denumire), nicio întrebare la ANAF („negăsit” ar fi
    fals) -> „RO-” + un CUI bun: „un CUI are numai cifre” -> CUI-ul corect: eroarea dispare, butonul se activează. Nicio firmă creată."""
    baza = cui_cu_control(45900000 + int(time.time()) % 99999)
    gresit = _gresit(baza)
    try:
        pg = _deschide_adauga_firma(patron)
        pg.fill("#fn-cui", gresit)
        txt = _eroare_cui(pg)
        assert ("CUI-ul %s nu e valid: " % gresit) in txt and CIFRA in txt, txt
        assert pg.get_attribute("#fn-cui", "aria-invalid") == "true"
        assert pg.is_disabled("#fn-salveaza"), "„Adaugă firma” activ pe un CUI greșit"
        assert "ANAF" not in pg.inner_text("#fn-cui-info"), pg.inner_text("#fn-cui-info")
        pg.fill("#fn-nume", "%s CUI Gresit %s SRL" % (PREFIX_FIRMA, gresit))
        assert pg.is_disabled("#fn-salveaza"), "denumirea a activat butonul peste un CUI greșit"
        patron.captura("cifra_de_control")
        pg.fill("#fn-cui", "RO-" + baza)
        pg.wait_for_function("() => ((document.querySelector(\".msg-eroare[data-camp='fn-cui']\") || {}).textContent || '')"
                             ".includes('numai cifre')", timeout=30000)
        assert pg.is_disabled("#fn-salveaza")
        pg.fill("#fn-cui", baza)
        pg.wait_for_function("() => !document.querySelector('#fn-salveaza').disabled", timeout=30000)
        assert not pg.query_selector(".msg-eroare[data-camp='fn-cui']"), "eroarea a rămas după CUI-ul corect"
        patron.captura("cui_corect")
        assert sql("SELECT count(*) FROM public.tenants WHERE cui IN (%s, %s, %s)", (gresit, baza, "RO-" + baza)) == [(0,)]
    finally:
        for (tid,) in sql("SELECT id FROM public.tenants WHERE cui IN (%s, %s) AND nume LIKE %s", (gresit, baza, PREFIX_FIRMA + "%")):
            from conftest import _scoate_firmele_e2e
            _scoate_firmele_e2e(tid)


def _corectura(patron, firma, cui_nou):
    """Date firmă -> „Corectează CUI-ul” -> CUI-ul corect -> „Continuă”: avertismentul serverului, cu propunerea ANAF. -> (pg, aviz)."""
    from e2e_bloc_a import _card
    # firma se caută în listă după denumirea ei DE ACUM: corectura cu date ANAF (testul de mai sus) o redenumește — corect, 459 —, iar
    # testele modulului împart aceeași `firma_e2e`
    patron.firma(sql("SELECT nume FROM public.tenants WHERE id = %s", (firma["tenant_id"],))[0][0])
    _card(patron, "datefirma", "#df-cui-corecteaza")
    pg = patron.pg
    pg.click("#df-cui-corecteaza")
    pg.fill("#df-cui-nou", cui_nou)
    pg.click("#df-cui-continua")
    pg.wait_for_selector("#df-cui-confirma", timeout=30000)
    return pg, pg.inner_text("#df-cui-aviz")


def _confirma(pg):
    pg.click("#df-cui-confirma")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('CUI-ul a fost corectat')",
                         timeout=30000)
    return pg.inner_text("#df-msg")


def test_def_459_corectura_cui_inlocuieste_datele_celui_vechi_cu_cele_de_la_anaf(patron, firma_e2e):
    """459 (2). Pornire: firma are datele scrise pentru CUI-ul vechi (adresa, localitatea, județul, CAEN, nr. registrului, pe ruta Date
    firmă). Pașii administratorului: Date firmă -> „Corectează CUI-ul” -> CUI-ul corect -> „Continuă”: avertismentul spune ce dă ANAF pentru
    CUI-ul nou, câmp cu câmp („Adresa: Str. Veche 1 → Str. Noua 2” …) -> „Corectez CUI-ul”: „Din ANAF s-au preluat: …”, iar câmpurile
    din Date firmă arată datele CUI-ului nou; în bază, denumirea (în ambele locuri), denumirea ANAF și jurnalul."""
    tid, schema = firma_e2e["tenant_id"], firma_e2e["schema"]
    _ruta("/tenants/%d/firma-profil/date" % tid,
          {"adresa": "Str. Veche 1", "oras": "Bucuresti", "judet": "B", "caen": "4711", "reg_com": "J40/1/2020"}, "datele vechi")
    nou = cui_cu_control(45910000 + int(time.time()) % 99999)
    den = "%s A459 Noua %s SRL" % (PREFIX_FIRMA, nou)
    chei = _anaf_pune({nou: {"denumire": den, "adresa": "Str. Noua 2", "nr_reg_com": "J12/2/2021", "cod_caen": "6920",
                             "localitate": "Cluj-Napoca", "judet": "CJ", "platitor_tva": False, "tva_la_incasare": False,
                             "data_inregistrare": "2021-03-04", "forma_juridica": "", "tva_incasare_rtvai": None, "inactiv": False}})
    try:
        pg, aviz = _corectura(patron, firma_e2e, nou)
        assert ("La ANAF, CUI-ul %s e al firmei „%s”" % (nou, den)) in aviz, aviz
        for linie in ("Adresa: Str. Veche 1 → Str. Noua 2", "Localitatea: Bucuresti → Cluj-Napoca", "Județul: B → CJ",
                      "Cod CAEN: 4711 → 6920", "Nr. registrul comerțului: J40/1/2020 → J12/2/2021"):
            assert linie in aviz, (linie, aviz)
        patron.captura("propunerea_anaf")
        msg = _confirma(pg)
        assert "Din ANAF s-au preluat:" in msg and "Adresa" in msg, msg
        pg.wait_for_selector("#df-adresa", timeout=20000)
        ecran = {k: pg.input_value("#df-" + k) for k in ("cui", "adresa", "oras", "judet", "caen", "reg_com")}
        assert ecran == {"cui": nou, "adresa": "Str. Noua 2", "oras": "Cluj-Napoca", "judet": "CJ", "caen": "6920",
                         "reg_com": "J12/2/2021"}, ecran
        patron.captura("datele_noi")
        assert sql("SELECT nume, cui, nume_anaf FROM public.tenants WHERE id = %s", (tid,)) == [(den, nou, den)]
        assert sql('SELECT nume, adresa FROM "%s".firma_profil' % schema) == [(den, "Str. Noua 2")]
        jurnal = {r[0] for r in sql('SELECT camp FROM "%s".firma_profil_jurnal' % schema)}
        assert jurnal >= {"cui", "nume", "adresa", "oras", "judet", "caen", "reg_com"}, jurnal
    finally:
        _anaf_scoate(chei)


def test_def_459_corectura_fara_date_anaf_spune_ce_ramane_de_verificat(patron, firma_e2e):
    """459 (2, fără ANAF). Pașii: „Corectează CUI-ul” -> un CUI corect pe care ANAF nu-l are -> „Continuă”: avertismentul spune că ANAF
    n-are date și ce rămâne de verificat -> „Corectez CUI-ul”: mesajul (avertisment, nu „ok”) repetă ce e de verificat; denumirea ANAF
    a CUI-ului vechi nu mai rămâne pe firmă."""
    tid = firma_e2e["tenant_id"]
    nou = cui_cu_control(45920000 + int(time.time()) % 99999)
    pg, aviz = _corectura(patron, firma_e2e, nou)
    assert ("ANAF nu are date pentru CUI-ul %s" % nou) in aviz and "de verificat în Date firmă după corectură" in aviz, aviz
    patron.captura("fara_anaf")
    msg = _confirma(pg)
    assert "de verificat" in msg, msg
    assert pg.query_selector("#df-msg.msg-avert, #df-msg > .msg-avert"), "fără ANAF mesajul e un avertisment, nu o confirmare simplă"
    assert sql("SELECT cui, nume_anaf FROM public.tenants WHERE id = %s", (tid,)) == [(nou, None)]
    patron.captura("dupa")

