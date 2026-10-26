# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 (Costin 21.10.2026, verbatim în DECIZII „Comanda 10.2”), punctele de la factură:

- 7d (415): „la factură, mesajul roșu «Articolul n-are cota TVA» rămâne după ce cota a fost aleasă pe linie.”
- 7e (417): „pe ecranul de detaliu al facturii de stornare nu apare trimiterea la factura inițială (pe PDF apare).”
- 7f (419, partea facturii): „după stornare butonul rămâne «Se stornează…»; factura stornată rămâne «neîncasată» până la reîmprospătare.”
- 7g: „Factură în valută: cursul BNR și TVA-ul în lei nu se văd înainte de emitere.”

Comportamentul pe ecran îl probează testele de capăt la capăt (`frontend_test/e2e/e2e_lot10b_facturi.py`); aici: serverul (previzualizarea
în lei = ce scrie emiterea, mențiunea stornării în detaliu, refuzul celei de-a doua stornări) pe o schemă efemeră din `tenant_template.sql`,
în ROLLBACK, plus forma ecranelor (sursa JS) acolo unde browserul nu intră în poartă.
CUI-ul clientului de probă (14399840, DANTE INTERNATIONAL SA) are cifra de control verificată cu algoritmul din CLAUDE.md."""
import datetime as _dt
import io
import os
import re
from decimal import ROUND_HALF_UP, Decimal as D

import pytest

from core import db as _db, tenant_provisioning as _tp
from core.arbore_js import apeluri, arbore_js, declaratii, elemente_html, functia, noduri

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_T = "ztest_lot10b_facturi"
ZI = _dt.date(2026, 9, 4)          # o zi bancară cu cursul EUR în cache-ul bazei de test (vineri)
CURS_ZI = D("5.2524")              # cursul BNR EUR din 04.09.2026 (cache-ul bazei de test); pus numai dacă lipsește, în ROLLBACK
# [lotul 11, decizia Costin 10.3: „Cursul BNR: aplici textul legal în vigoare (CF art. 290, HG 1/2016 pct. 35)”] factura din ZI ia
# cursul comunicat în ziua ANTERIOARĂ — HG 1/2016 pct.35 alin.(1): „cursul de schimb comunicat de respectiva bancă în ziua anterioară și
# care este valabil pentru operațiunile care se vor desfășura în ziua următoare”
ZI_CURS = _dt.date(2026, 9, 3)
CURS_ZI_CURS = D("5.2536")         # cursul BNR EUR comunicat pe 03.09.2026 (cache-ul bazei de test); pus numai dacă lipsește, în ROLLBACK
LINII = [{"descriere": "Consultanta IT", "cont_venit": "704", "cantitate": 2, "pret_unitar": 150, "cota_tva": 21}]


def _js(nume):
    return io.open(os.path.join(RAD, "static", "js", "ecrane", nume), encoding="utf-8").read()


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn() as c:
            c.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001 — fără bază, testele de bază se sar (cele pure rulează)
        return False


@pytest.fixture
def conn_schema():
    """Schema temporară din template + firma_profil minimă (plătitor de TVA, seria ZT). ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(),
                                                        SCHEMA_T))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA_T)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, platitor_tva, tip_decont) VALUES "
                            "(1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202',true,'L') "
                            "ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume")
                # L31/1990 art.74 alin.(3) (capitalul) + CF art.319 alin.(20) lit.a) (seria) + metoda de stoc explicită (06.10.2026)
                cur.execute("UPDATE firma_profil SET forma_juridica = 'SRL', capital_subscris = 200, serie_factura = 'ZT', "
                            "metoda_stoc = 'global_valoric' WHERE id = 1")
                # cursul zilei, numai dacă lipsește din cache (tabel partajat — se anulează la final)
                cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s, 'EUR', %s) "
                            "ON CONFLICT (data, moneda) DO NOTHING", (ZI, CURS_ZI))
                cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s, 'EUR', %s) "
                            "ON CONFLICT (data, moneda) DO NOTHING", (ZI_CURS, CURS_ZI_CURS))
            yield conn
        finally:
            conn.rollback()


# ── 7g: cursul BNR și TVA-ul în lei, înainte de emitere ─────────────────────────────────────────────────────────────────────
def test_7g_sumele_in_lei_se_rotunjesc_aritmetic():
    """CF art.319 alin.(20) lit.j) cere „suma taxei colectate, exprimate în lei”; rotunjirea fiscală e aritmetică (CLAUDE.md „Rotunjire
    fiscală”, deficiența 280): 1,00 EUR × 5,0250 = 5,025 -> 5,03 (la par ar fi 5,02)."""
    from core import facturi_api
    tva_lei, total_lei = facturi_api.sume_lei({"tva": D("1.00"), "total": D("1.21")}, D("5.0250"))
    assert tva_lei == D("5.03")      # ROUND_HALF_UP pe ,xx5 (CLAUDE.md „Rotunjire fiscală”)
    assert total_lei == D("6.08")    # 1,21 × 5,025 = 6,08025 -> 6,08


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_7g_previzualizarea_in_lei_e_ce_scrie_emiterea(conn_schema):
    """Formularul arată, înainte de emitere, cursul și sumele în lei; emiterea scrie EXACT aceleași cifre (curs, data cursului, TVA și total
    în lei) — o singură definiție (`curs_automat` + `sume_lei`). 2 × 150 EUR la 21% = 63,00 EUR TVA; la cursul din cache."""
    from core import facturi_api
    with conn_schema.cursor() as cur:
        cur.execute("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = %s", (ZI_CURS,))
        curs = D(str(cur.fetchone()[0]))
    p = facturi_api.previzualizare_lei(conn_schema, "EUR", ZI, [{k: l[k] for k in ("cantitate", "pret_unitar", "cota_tva")} for l in LINII])
    # CF art.290 alin.(2): „ultimul curs de schimb comunicat de Banca Națională a României [...] valabil la data la care intervine
    # exigibilitatea” — cursul ales de `curs_bnr.curs_pentru`, cel cu care emite serverul
    # + HG 1/2016 pct.35 alin.(1): cel comunicat „în ziua anterioară” (03.09.2026, joi), deci vechimea e 1 zi
    assert p["ok"] is True and D(p["curs"]) == curs and p["data_curs"] == ZI_CURS.isoformat() and p["vechime_zile"] == 1, p
    assert (D(p["tva"]), D(p["total"])) == (D("63.00"), D("363.00")), p
    assert D(p["tva_lei"]) == (D("63.00") * curs).quantize(D("0.01"), rounding=ROUND_HALF_UP), p      # CF art.319 alin.(20) lit.j) — TVA în lei
    r = facturi_api.emite_factura(conn_schema, [dict(l) for l in LINII], data_emitere=ZI.isoformat(), moneda="EUR", platitor_tva=True,
                                  tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840")
    assert r.get("factura_id"), r
    with conn_schema.cursor() as cur:
        cur.execute("SELECT curs_bnr, data_curs, tva_lei, total_lei FROM facturi WHERE id = %s", (r["factura_id"],))
        curs_f, data_f, tva_lei_f, total_lei_f = cur.fetchone()
    assert (D(str(curs_f)), data_f.isoformat(), D(str(tva_lei_f)), D(str(total_lei_f))) == \
        (D(p["curs"]), p["data_curs"], D(p["tva_lei"]), D(p["total_lei"])), (r, p)   # ce s-a arătat = ce s-a scris pe factură
    assert (D(str(r["tva_lei"])), D(str(r["total_lei"]))) == (D(p["tva_lei"]), D(p["total_lei"])), (r, p)   # și ce a spus emiterea


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_7g_fara_linii_numai_cursul_iar_refuzul_e_al_emiterii(conn_schema):
    """Cota încă nestabilită (linii=None): numai cursul, fără sume în lei; o monedă pe care BNR n-o cotează: același refuz ca la emitere."""
    from core import facturi_api
    p = facturi_api.previzualizare_lei(conn_schema, "EUR", ZI, None)
    assert p["ok"] is True and "tva_lei" not in p and p["data_curs"] == ZI_CURS.isoformat(), p   # HG 1/2016 pct.35 alin.(1)
    p0 = facturi_api.previzualizare_lei(conn_schema, "EUR", ZI, [])
    assert (D(p0["tva_lei"]), D(p0["total_lei"])) == (D("0.00"), D("0.00")), p0   # liniile fără valoare: zero, nu „—”
    refuz = facturi_api.previzualizare_lei(conn_schema, "XYZ", ZI, None)
    emis = facturi_api.emite_factura(conn_schema, [dict(l) for l in LINII], data_emitere=ZI.isoformat(), moneda="XYZ",
                                     platitor_tva=True, tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840")
    assert refuz["ok"] is False and refuz["cod"] == emis["cod"] == "MONEDA_NECOTATA" and refuz["mesaj"] == emis["mesaj"], (refuz, emis)


def test_7g_formularul_cere_cursul_serverului_nu_il_calculeaza():
    """Ecranul cere previzualizarea serverului (aceeași conversie ca emiterea) și n-are aritmetica lei proprie (interdicția 4); blocul stă
    sub monedă, iar moneda declară ruta (garda drepturilor din UI)."""
    js = _js("emitere_ecran.js")
    arb, cod = arbore_js("emitere_ecran.js")
    lei = functia(arb, "actualizeazaLei")
    # previzualizarea o cere serverului (aceeași conversie ca emiterea, `facturi_api.previzualizare_lei`) — exact un apel, cu cererea
    assert apeluri(lei, cod, "api.post") == [("`/tenants/${tenantId}/facturi/previzualizare-lei`", "cerere")]
    # moneda declară ruta pe care o cheamă la schimbare (garda drepturilor din UI)
    assert [at.get("id") for _t, at in elemente_html(arb)
            if at.get("data-actiune-camp") == "POST /tenants/{tenant_id}/facturi/previzualizare-lei"] == ["em-moneda"]
    assert re.search(r'id="em-moneda-nota"></span>\s*</div>\s*<div class="fd-valuta" id="em-valuta"', js), "blocul în lei, sub monedă"
    # interdicția 4: sumele în lei vin din răspunsul serverului, fără înmulțire cu cursul pe ecran
    membri = {cod(m) for m in noduri(lei, "MemberExpression")}
    assert membri >= {"r.tva_lei", "r.total_lei"}, sorted(membri)
    assert [cod(b) for b in noduri(lei, "BinaryExpression") if b["operator"] == "*"
            and {cod(b["left"]), cod(b["right"])} & {"r.curs"}] == []
    assert apeluri(functia(arb, "recalc"), cod, "actualizeazaLei") == [("nestiut",)]


# ── 7d (415): mesajul „Articolul n-are cota TVA” dispare când cota e aleasă ─────────────────────────────────────────────────
def test_415_alegerea_cotei_pe_linie_scoate_mesajul_articolului():
    """DS cap.6 v2.92 (clasa 290): „Eroarea dispare când câmpul e corectat”. Mesajul spune „alege cota pe linie”; aleasă, zona lui
    (`em-l{i}-cota-mesaj`) se golește în handlerul alegerii."""
    js = _js("emitere_ecran.js")
    i = js.index('if (selCota) selCota.addEventListener("change"')
    handler = js[i:js.index("});", i)]
    assert re.search(r'if \(l\.cota_tva != null\) \{[^}]*-cota-mesaj"\);\s*if \(z\) z\.innerHTML = "";', handler), handler


# ── 7e (417): trimiterea la factura inițială, pe detaliul stornării ────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_417_detaliul_stornarii_numeste_factura_initiala(conn_schema):
    """CF art.330 alin.(1) lit.b): factura de stornare e cea „în care se înscriu numărul și data facturii corectate”. Detaliul stornării
    poartă aceeași mențiune ca PDF-ul (`facturi.mentiune_storno`); factura inițială n-o are."""
    from core import facturi_api
    r = facturi_api.emite_factura(conn_schema, [dict(l) for l in LINII], data_emitere=ZI.isoformat(), moneda="RON", platitor_tva=True,
                                  tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840")
    s = facturi_api.storneaza(conn_schema, r["factura_id"])
    d = facturi_api.detalii_factura(conn_schema, s["factura_id"])
    assert d["mentiune_storno"] == "Stornare factura ZT nr. %s din %s" % (r["numar"][2:], ZI.strftime("%d.%m.%Y")), d["mentiune_storno"]
    assert d["storno_din_id"] == r["factura_id"]
    assert facturi_api.detalii_factura(conn_schema, r["factura_id"])["mentiune_storno"] is None


def test_417_ecranul_arata_mentiunea_si_duce_la_factura_stornata():
    arb, cod = arbore_js("facturi_ecran.js")
    # CF art.330 alin.(1) lit.b): pe detaliul stornării, mențiunea facturii corectate — numai când factura o are
    c = [x for x in noduri(arb, "ConditionalExpression") if cod(x["test"]) == "f.mentiune_storno"]
    assert len(c) == 1, [cod(x) for x in c]
    assert elemente_html(c[0]["consequent"]) == [("div", {"class": "fd-antet-linie", "id": "fd-storno-din"}),
                                                 ("button", {"class": "btn-link", "id": "fd-vezi-stornata"})]
    assert [cod(e) for e in c[0]["consequent"]["expressions"]] == ["esc(f.mentiune_storno)"] and cod(c[0]["alternate"]) == '""'
    # clicul duce la factura stornată (`storno_din_id`)
    assert apeluri(arb, cod, "btnVeziStornata.addEventListener") == [
        ('"click"', "() => detaliiFactura(corp, nav, tenantId, f.storno_din_id, opt)")]


# ── 7f (419): după stornare, detaliul refăcut; a doua stornare refuzată ────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_419_factura_stornata_nu_se_mai_storneaza(conn_schema):
    """CF art.330 alin.(1) lit.b): stornarea anulează valorile facturii corectate — a doua stornare ar scădea din nou o operațiune care
    nu mai există. Nici o stornare nu se stornează. Nimic scris la refuz."""
    from core import facturi_api
    r = facturi_api.emite_factura(conn_schema, [dict(l) for l in LINII], data_emitere=ZI.isoformat(), moneda="RON", platitor_tva=True,
                                  tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840")
    s = facturi_api.storneaza(conn_schema, r["factura_id"])
    assert facturi_api.detalii_factura(conn_schema, r["factura_id"])["stare_incasare"]["stare"] == "stornata"   # 416: aceeași definiție
    with conn_schema.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi")
        n0 = cur.fetchone()[0]
    with pytest.raises(ValueError) as e:
        facturi_api.storneaza(conn_schema, r["factura_id"])
    # CF art.330 alin.(1) lit.b): stornarea anulează valorile facturii corectate — temeiul e scris în refuz
    # [lotul 12, 443.1] factura și stornarea ei numite ca în Istoric („ZT nr. 1”, nu „ZT1”: `pdf_util.serie_nr`)
    from core.pdf_util import serie_nr
    assert str(e.value) == ("Factura %s e deja stornată integral (prin %s): nu mai rămâne nimic de stornat (CF art.330 alin.(1) lit.b))."
                            % (serie_nr(r["serie"], r["numar"]), serie_nr(s["serie"], s["numar"])))
    with pytest.raises(ValueError) as e2:
        facturi_api.storneaza(conn_schema, s["factura_id"])
    # refuzul numește stornarea și factura pe care o stornează (mențiunea ei din detaliu), cu temeiul — din datele facturilor
    mentiune = facturi_api.detalii_factura(conn_schema, s["factura_id"])["mentiune_storno"]
    assert str(e2.value) == ("Factura %s e ea însăși o stornare (%s): o stornare nu se stornează la rândul ei (%s)."
                             % (serie_nr(s["serie"], s["numar"]), mentiune, facturi_api.TEMEI_STORNARE)), e2.value
    with conn_schema.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi")
        assert cur.fetchone()[0] == n0   # refuzul nu rezervă număr și nu scrie factură


def test_419_dupa_stornare_detaliul_se_reface_si_nu_mai_ofera_stornarea():
    """DS cap.27 v2.93–v2.94: „o listă care trebuie reîmprospătată se reface ACUM, iar confirmarea se pune peste ea”, „în zona de mesaj a
    ecranului redesenat”. Butonul „Se stornează…” dispare odată cu fereastra confirmării; starea „stornată” vine de la server; „Stornează”
    și „Emite chitanță” nu se mai aplică facturii stornate. [lotul 13, 673 / 675 — DS cap.2a / cap.1 v2.104] Confirmarea stornării e o
    fereastră mică; după „Confirm stornarea” confirmarea e lăsată detaliului (`laRevenire`), apoi „←”, iar detaliul REFĂCUT (de ecran sau de
    navigator) o pune în zona lui de stornare; „Stornează” / „Emite chitanță” stau la locul lor, inactive, cu motivul."""
    js = _js("facturi_ecran.js")
    i = js.index('c2.querySelector("#fd-storno-ok").addEventListener("click"')
    h = js[i:js.index("} catch (e) {", i)]
    assert h.index("laRevenire(tenantId, facturaId,") < h.index('id="fd-storno-rez">') < h.index("nav.inapoi();") < h.index(
        "await detaliiFactura(corp, nav, tenantId, facturaId, opt);"), h
    arb, cod = arbore_js("facturi_ecran.js")
    ok = [c for c in noduri(arb, "CallExpression") if cod(c["callee"]) == 'c2.querySelector("#fd-storno-ok").addEventListener']
    assert len(ok) == 1, len(ok)
    handler = ok[0]["arguments"][1]
    # zona de stornare se ia din detaliul REFĂCUT (`c`, corpul primit la revenire), iar confirmarea se pune în ea
    assert declaratii(handler, cod).get("zs") == ['c.querySelector("#fd-storno-zona")'], declaratii(handler, cod)
    assert apeluri(handler, cod, 'zs.querySelector("#fd-storno-rez").appendChild') == [("bi",)]
    # 416: „stornată” = starea de încasare a serverului; „Stornează” și „Emite chitanță” nu se aplică pe ea (inactive, cu motivul)
    assert declaratii(arb, cod).get("stornata") == ['!!(f.stare_incasare && f.stare_incasare.stare === "stornata")']
    m = js[js.index("  const motiv = {"):]
    m = m[:m.index("\n  };")]
    storno = m[m.index("    storno:"):m.index("    transforma:")]
    chitanta = m[m.index("    chitanta:"):m.index("    saga:")]
    assert "f.storno_din_id" in storno and "stornata" in storno, storno
    assert "f.platita_la" in chitanta and "stornata" in chitanta, chitanta
    assert 'id="fd-storno"${inactivDaca(motiv.storno)}' in js and 'data-actiune="POST /tenants/{tenant_id}/chitante"${inactivDaca(motiv.chitanta)}' in js
    butoane = {at.get("id"): at.get("data-actiune") for _t, at in elemente_html(arb)}
    assert (butoane["fd-storno"], butoane["fd-chitanta"]) == ("POST /tenants/{tenant_id}/facturi/{factura_id}/storno",
                                                              "POST /tenants/{tenant_id}/chitante")


def test_419_clasa_chitanta_si_spv_refac_detaliul_dupa_act():
    """Clasa lui 419 („starea veche rămâne pe detaliu după act”), căutată pe tot detaliul facturii: „Emite chitanță” (starea de încasare)
    și „Trimite în SPV” (eticheta SPV din antet) refac detaliul de la server și pun confirmarea în zona de mesaj a detaliului refăcut
    (`#fd-act-rez`), ca „Transformă în factură” (C64). „Trimite pe email” și „Export SAGA” nu schimbă starea facturii."""
    js = _js("facturi_ecran.js")
    # [lotul 13, 673] chitanța se emite în fereastra ei: confirmarea e lăsată detaliului (`mesajDupaRevenire`), apoi „←”, iar detaliul se
    # reface de la server — de ecran (fereastra păstrată) sau de navigator (redesenată) — și o pune în `#fd-act-rez`, după desenare
    i = js.index('form.querySelector("#fd-chit-ok").addEventListener("click"')
    h = js[i:js.index("} catch (e) {", i)]
    assert h.index("mesajDupaRevenire(tenantId, facturaId,") < h.index("nav.inapoi();") < h.index(
        "await detaliiFactura(corp, nav, tenantId, facturaId, opt);"), h
    m = js[js.index("function mesajDupaRevenire("):]
    assert 'arataMesaj(c.querySelector("#fd-act-rez") || c, text, fel)' in m[:m.index("\n}")], m[:300]
    d = js[js.index("async function detaliiFactura("):]
    d = d[:d.index("\nasync function ") if "\nasync function " in d else len(d)]
    assert d.index("corp.innerHTML = `") < d.index("dupaRevenire(corp);"), "confirmarea se pune după desenarea detaliului"
    i = js.index("/facturi/${facturaId}/trimite-spv`")
    h = js[i:js.index("} catch (e) {", i)]
    assert h.index("await detaliiFactura(corp, nav, tenantId, facturaId, opt);") < h.index('arataMesaj(corp.querySelector("#fd-act-rez")'), h
    assert "pictaStareSpv();" not in h   # zona SPV o pictează detaliul refăcut; răspunsul nu mai e rescris de ea


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_417_clasa_detaliul_arata_mentiunile_de_pe_pdf(conn_schema):
    """Clasa lui 417 („pe PDF apare”, pe detaliu nu): mențiunea „conform bon fiscal nr./data” (HG 1/2016 pct.97 alin.(1): „fiind
    suficientă mențiunea «conform bon fiscal nr./data»”) vine pe detaliu din aceeași funcție ca pe PDF (`facturi.mentiune_bon`); factura
    obișnuită n-are mențiuni."""
    from core import facturi_api
    r = facturi_api.emite_factura(conn_schema, [dict(l) for l in LINII], data_emitere=ZI.isoformat(), moneda="RON", platitor_tva=True,
                                  tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840", bon_fiscal_nr="0042",
                                  bon_fiscal_data=ZI.isoformat())
    assert facturi_api.detalii_factura(conn_schema, r["factura_id"])["mentiuni"] == ["conform bon fiscal nr. 0042/04.09.2026"]
    r2 = facturi_api.emite_factura(conn_schema, [dict(l) for l in LINII], data_emitere=ZI.isoformat(), moneda="RON", platitor_tva=True,
                                   tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840")
    assert facturi_api.detalii_factura(conn_schema, r2["factura_id"])["mentiuni"] == []
    arb, cod = arbore_js("facturi_ecran.js")
    # mențiunile vin din lista serverului (`facturi.mentiune_bon`, aceeași ca pe PDF), una pe linie, scăpate
    harta = [c for c in noduri(arb, "CallExpression") if c["callee"].get("type") == "MemberExpression"
             and c["callee"]["property"].get("name") == "map" and cod(c["callee"]["object"]) == "f.mentiuni || []"]
    assert len(harta) == 1, len(harta)
    sablon = harta[0]["arguments"][0]["body"]
    assert elemente_html(sablon) == [("div", {"class": "fd-antet-linie"})] and [cod(e) for e in sablon["expressions"]] == ["esc(m)"]
    assert [(c["callee"]["property"].get("name"), tuple(cod(a) for a in c["arguments"])) for c in noduri(arb, "CallExpression")
            if c["callee"].get("type") == "MemberExpression" and c["callee"]["object"] is harta[0]] == [("join", ('""',))]
