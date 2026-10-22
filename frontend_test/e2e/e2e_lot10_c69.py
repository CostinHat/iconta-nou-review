# -*- coding: utf-8 -*-
"""Lotul 10, deficiența C69 — „valoare inventată pe documentul ANAF în loc de blocaj”, ce rămăsese după antetul D406 (subagentul N2).

Deciziile lui Costin, 20.10.2026 (verbatim în DECIZII „Lotul 10, C69 … deciziile lui Costin”): (1) localitatea partenerului în D406 —
„Completez din ANAF”, se blochează numai ce rămâne; (2) bilanțul — „Câmpuri noi + blocaj” (Mare contribuabil, Forma de proprietate);
(3) firma fără cont bancar — „Varianta 1”, cu contradicția pe 512 numită; fără întrebare: e-Factura nu mai scrie „-” (BR-RO-080 / 082 /
090 / 092, BR-06 / 07); prin analogie: D394 judP al partenerului; D101G — declarantul cerut (validatorul D101G v2).
Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`). Partenerii probelor sunt persoane fizice
fără cod (ANAF nu se consultă pentru ele — aplicația din proba e2e nu atinge ANAF real). IBAN sintetic RO59BTRLRONCRT0C69TEST01 (mod-97
verificat cu `salariati_api.iban_valid`)."""
import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, sql

IBAN = "RO59BTRLRONCRT0C69TEST01"


@pytest.fixture(scope="module")
def firma_c69():
    for f in firma_noua():
        s = f["schema"]
        sql('UPDATE "%s".firma_profil SET adresa = %%s, oras = %%s, judet = %%s, caen = %%s, banca = %%s, iban = %%s, telefon = %%s, '
            'declarant_nume = %%s, declarant_prenume = %%s, declarant_functie = %%s, reg_com = %%s, regim_fiscal = %%s, '
            'platitor_tva = true, tip_decont = %%s, operatiuni_ic = false, mare_contribuabil = NULL, forma_proprietate = NULL, '
            # [lotul 11, decizia 10.3] interesul public declarat (și întocmitorul, mai jos): testul e despre bifaMC / codPP, nu despre ele
            'interes_public = false WHERE id = 1' % s,
            ("Str. Probei 9", "Cluj-Napoca", "CJ", "6920", "BT", IBAN, "0264111222", "POPESCU", "ION", "ADMINISTRATOR", "J12/69/2020",
             "micro", "lunar"))
        from e2e_bloc_e import INTOCMITOR_PROBA
        from core import db, uc_cabinet
        with db.get_conn() as c:   # întocmitorul cabinetului, pe drumul ecranului Date cabinet (`uc_cabinet.salveaza_intocmitor_conn`)
            r = uc_cabinet.salveaza_intocmitor_conn(c, f["cabinet_id"], INTOCMITOR_PROBA)
            assert r.get("ok"), r
            c.commit()
        yield f


def _date_firma(patron, firma):
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    return patron.pg


def _salveaza(pg):
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('alvat')", timeout=30000)


def _declaratie(patron, firma, tip, an, luna):
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(firma["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, tip)
    alege_perioada(pg, an, luna)
    pg.click("#dec-continua")
    pg.wait_for_selector(".dec-eroare, details.dec-xml summary:text('Vezi XML-ul generat')", timeout=90000)
    return pg


def _xml(pg):
    return pg.locator("details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").text_content()


def _factura_pf(firma, numar, directie, nume, oras=None, judet=None, data="2026-09-10"):
    """Factură către / de la o persoană fizică fără cod (tert_cui gol), cu o linie de 100 lei + 21%."""
    s = firma["schema"]
    fid = sql('INSERT INTO "%s".facturi (numar, data_emitere, directie, total, tva, tert_cui, tert_nume, tert_oras, tert_judet, status) '
              "VALUES (%%s, %%s, %%s, 121, 21, '', %%s, %%s, %%s, %%s) RETURNING id" % s, (numar, data, directie, nume, oras, judet, directie))[0][0]
    sql('INSERT INTO "%s".factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) VALUES (%%s, %%s, %%s, 1, 100, 21)' % s,
        (fid, "Marfa", "buc"))
    return fid


def test_def_c69_bilant_cere_mare_contribuabil_si_forma_de_proprietate(patron, firma_c69):
    """C69 (decizia 2). Pașii: Date firmă — panoul „Profil incomplet” spune „Mare contribuabil — blochează Bilanț” și „Forma de proprietate —
    blochează Bilanț” -> Bilanț 2025, S1005, „Descarcă XML”: refuz „Nu e declarat dacă firma e mare contribuabil … Forma de proprietate …”,
    cu butonul „Deschide Date firmă” -> butonul duce în Date firmă -> Mare contribuabil: Nu, Forma de proprietate: Societăți cu răspundere
    limitată -> Salvează -> Bilanț, „Descarcă XML”: bifaMC="0", codJJ="12" (= județul sediului, Cluj), codPP="35", nume_admin="POPESCU ION"
    — nu bifaMC=1 / codJJ=10 / „ADMINISTRATOR”."""
    import re
    from e2e_bloc_e import _bilant
    s = firma_c69["schema"]
    pg = _date_firma(patron, firma_c69)
    panou = pg.inner_text(".dec-avert")
    assert "Mare contribuabil" in panou and "Forma de proprietate" in panou and "Bilanț" in panou, panou
    patron.captura("profil_incomplet")
    _bilant(patron, firma_c69, 2025, "s1005")
    pg.click("#bl-xml")
    pg.wait_for_selector("#bl-rez [data-ecran-destinatie='date_firma']", timeout=60000)
    rez = pg.inner_text("#bl-rez")
    assert "mare contribuabil" in rez and "Forma de proprietate" in rez, rez
    patron.captura("refuz")
    pg.click("#bl-rez [data-ecran-destinatie='date_firma']")
    pg.wait_for_selector("#df-mare_contribuabil", timeout=30000)
    pg.select_option("#df-mare_contribuabil", "0")
    pg.select_option("#df-forma_proprietate", "35")
    _salveaza(pg)
    assert sql('SELECT mare_contribuabil, forma_proprietate FROM "%s".firma_profil' % s) == [(False, "35")]
    _bilant(patron, firma_c69, 2025, "s1005")
    with pg.expect_response(lambda r: "/s1005-xml" in r.url, timeout=90000) as rsp:
        with pg.expect_download(timeout=90000):
            pg.click("#bl-xml")
    xml = rsp.value.json()["xml"]
    at = dict(re.findall(r'\b(bifaMC|codTT|codJJ|codPP|nume_admin)="([^"]*)"', xml))
    assert at == {"bifaMC": "0", "codTT": "12", "codJJ": "12", "codPP": "35", "nume_admin": "POPESCU ION"}, at
    patron.captura("generat")


def test_def_c69_d406_localitatea_partenerului_nu_e_liniuta(patron, firma_c69):
    """C69 (decizia 1). Pașii: o vânzare din 09.2026 către IONESCU MARIA (persoană fizică, fără localitate pe factură) -> Declarații,
    D406 pe 09.2026 -> Continuă: refuz „lipsește localitatea pentru 1 partener … IONESCU MARIA (facturile C69-L1)”, niciun XML ->
    localitatea clientului completată pe factură (Sibiu) -> D406 pe 09.2026: Customers și factura au <City>Sibiu</City>, nicăieri
    <City>-</City>."""
    s = firma_c69["schema"]
    sql('UPDATE "%s".firma_profil SET mare_contribuabil = false, forma_proprietate = %%s WHERE id = 1' % s, ("35",))
    fid = _factura_pf(firma_c69, "C69-L1", "emisa", "IONESCU MARIA")
    pg = _declaratie(patron, firma_c69, "d406", 2026, 9)
    err = pg.inner_text(".dec-eroare")
    assert "lipsește localitatea" in err and "IONESCU MARIA (facturile C69-L1)" in err, err
    assert not pg.query_selector("details.dec-xml"), "D406 refuzat nu arată niciun XML"
    patron.captura("refuz")
    sql('UPDATE "%s".facturi SET tert_oras = %%s WHERE id = %%s' % s, ("Sibiu", fid))
    pg = _declaratie(patron, firma_c69, "d406", 2026, 9)
    assert not pg.query_selector(".dec-eroare"), pg.inner_text(".dec-eroare")
    xml = _xml(pg)
    patron.captura("generat")
    cust = xml[xml.index("<Customers>"):xml.index("</Customers>")]
    assert "<City>Sibiu</City>" in cust                             # S.C.3 / S.AD.5 City — a partenerului (era „-”)
    assert "<City>Sibiu</City>" in xml[xml.index("<SalesInvoices>"):]   # S.I.25 BillingAddress (era „-” pe orice factură)
    assert "<City>-</City>" not in xml


def test_def_c69_d406_firma_fara_cont_bancar(patron, firma_c69):
    """C69 (decizia 3). Pașii: Date firmă — IBAN șters, „Nu are cont bancar”: Da -> Salvează -> D406 pe 09.2026: antetul are
    <BankAccountNumber>Fara cont bancar</BankAccountNumber>, fără IBAN -> o încasare în bancă validată (5121 = 4111, 121 lei, 15.09.2026)
    -> D406 pe 09.2026: refuz „firma e declarată fără cont bancar …, dar balanța arată … contul 5121 … rulaj debitor 121,00 lei …”,
    cu butonul spre Date firmă."""
    s = firma_c69["schema"]
    sql('UPDATE "%s".firma_profil SET mare_contribuabil = false, forma_proprietate = %%s WHERE id = 1' % s, ("35",))
    sql('UPDATE "%s".facturi SET tert_oras = COALESCE(tert_oras, %%s)' % s, ("Sibiu",))
    pg = _date_firma(patron, firma_c69)
    pg.fill("#df-iban", "")
    pg.select_option("#df-fara_cont_bancar", "1")
    _salveaza(pg)
    assert sql('SELECT iban, fara_cont_bancar FROM "%s".firma_profil' % s) in ([(None, True)], [("", True)])
    pg = _declaratie(patron, firma_c69, "d406", 2026, 9)
    assert not pg.query_selector(".dec-eroare"), pg.inner_text(".dec-eroare")
    xml = _xml(pg)
    assert "<BankAccountNumber>Fara cont bancar</BankAccountNumber>" in xml and "<IBANNumber>" not in xml   # S.BA.2
    patron.captura("fara_cont")
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, status, sursa, document_ref) VALUES (%%s, %%s, %%s, %%s, %%s) RETURNING id'
              % s, ("2026-09-15", "incasare client", "ciorna", "manual", "Extras BT C69"))[0][0]
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, 121)' % s,
        (nid, "5121", "4111"))
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))   # [lotul 10] ciornă -> linii -> validată
    pg = _declaratie(patron, firma_c69, "d406", 2026, 9)
    err = pg.inner_text(".dec-eroare")
    assert "declarată fără cont bancar" in err and "contul 5121" in err and "rulaj debitor 121,00 lei" in err, err
    assert pg.locator(".dec-eroare [data-ecran-destinatie='date_firma']").count() == 1
    patron.captura("contradictie_512")


def test_def_c69_d394_judetul_partenerului_nu_al_firmei(patron, firma_c69):
    """C69 (pct.5, prin analogie cu decizia 1). Pașii: o vânzare din 08.2026 către POPESCU ION (persoană fizică, fără cod, fără județ pe
    factură) -> Declarații, D394 pe 08.2026 -> Continuă: refuz „… POPESCU ION (operațiunea L) … Completează județul clientului …” (până
    la C69: judP = județul FIRMEI, sau „40”) -> județul clientului pe factură: Prahova -> D394 pe 08.2026: op1 are judP="29" (Prahova),
    nu "12" (Cluj, sediul firmei). Cere ca selecția facturilor D394 să aducă `tert_judet` (repo_d394, subagentul K)."""
    s = firma_c69["schema"]
    fid = _factura_pf(firma_c69, "C69-J1", "emisa", "POPESCU ION", oras="Ploiesti", data="2026-08-10")
    pg = _declaratie(patron, firma_c69, "d394", 2026, 8)
    err = pg.inner_text(".dec-eroare")
    assert "POPESCU ION (operațiunea L)" in err and "județul" in err, err
    patron.captura("refuz")
    sql('UPDATE "%s".facturi SET tert_judet = %%s WHERE id = %%s' % s, ("PH", fid))
    pg = _declaratie(patron, firma_c69, "d394", 2026, 8)
    assert not pg.query_selector(".dec-eroare"), pg.inner_text(".dec-eroare")
    xml = _xml(pg)
    op1 = [l for l in xml.split("\n") if "<op1 " in l and "POPESCU ION" in l]
    assert op1 and 'judP="29"' in op1[0] and 'judP="12"' not in op1[0], op1
    patron.captura("generat")


def test_def_c69_efactura_nu_pleaca_cu_liniuta(patron, firma_c69):
    """C69 (e-Factura, fără întrebare: sursa tranșează). Pașii: factură emisă către POPESCU ION fără adresă și fără localitate -> detaliul
    facturii -> „Trimite în SPV”: în proba e2e cabinetul nu e conectat la SPV, iar trimiterea se oprește la poarta tokenului ÎNAINTE de
    XML (ca la C62, `e2e_lot92`); de aceea XML-ul se generează cu funcția pe care o cheamă „Trimite în SPV” după poarta tokenului
    (`efactura_trimitere.genereaza_din_factura`): refuzul numește adresa și localitatea clientului (BR-RO-082, BR-RO-092), fără „-"."""
    from core import db, efactura_send as ef, efactura_trimitere as et
    s = firma_c69["schema"]
    fid = _factura_pf(firma_c69, "C69-E1", "emisa", "POPESCU ION")
    with db.get_conn(s) as c:
        with pytest.raises(ef.EDateIncomplete) as ei:
            et.genereaza_din_factura(c, s, fid)
    m = str(ei.value)
    assert "adresa clientului" in m and "localitatea clientului" in m and "BR-RO-082" in m and "BR-RO-092" in m, m
    patron.captura()


def test_def_c69_d101g_cere_declarantul(patron, firma_c69):
    """C69 (pct.6). D101G n-are ecran (declarație numai prin API, `declaratii_api._DOAR_API`): cererea pleacă din pagina contabilului,
    cu sesiunea lui. Pașii: prenumele declarantului șters în Date firmă -> POST /declaratii/d101g pe 2025: refuz „Lipsă prenumele
    declarantului …” (era prenume_declar="-") -> prenumele completat -> XML-ul are prenume_declar="ION"."""
    s = firma_c69["schema"]
    pg = _date_firma(patron, firma_c69)
    pg.fill("#df-declarant_prenume", "")
    _salveaza(pg)
    cere = """async ([tid]) => { const t = sessionStorage.getItem('iconta_token');
        const r = await fetch('/declaratii/d101g', {method: 'POST', headers: {Authorization: 'Bearer ' + t, 'Content-Type': 'application/json'},
          body: JSON.stringify({tenant_id: tid, an: 2025, manual: {P01: 1000, cota: 16}})});
        return [r.status, await r.text()]; }"""
    st, corp = pg.evaluate(cere, [firma_c69["tenant_id"]])
    assert st == 422 and "prenumele declarantului" in corp, (st, corp[:400])
    sql('UPDATE "%s".firma_profil SET declarant_prenume = %%s WHERE id = 1' % s, ("ION",))
    st, corp = pg.evaluate(cere, [firma_c69["tenant_id"]])
    assert st == 200 and 'prenume_declar=\\"ION\\"' in corp, (st, corp[:400])   # JSON: ghilimelele XML-ului vin escapate
    patron.captura()
