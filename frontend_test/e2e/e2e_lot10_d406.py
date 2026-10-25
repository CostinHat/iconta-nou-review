# -*- coding: utf-8 -*-
"""Lotul 10, deficiența C69 (găsită de Code la 427): clasa „valoare inventată pe documentul ANAF în loc de blocaj” — antetul D406.

Până la C69, D406 scria în antet „-” la telefon, prenumele persoanei de contact și localitate, „000000” la codul poștal, IBAN-ul fix
„RO00BANK0000000000000000” și DENUMIREA firmei ca nume al persoanei de contact; validatorul ANAF le accepta pe toate. Acum un câmp cerut
de schema ANAF (S.AD.5 City, S.CTH.2 Telephone, S.PN.2/S.PN.5 persoana de contact, S.BA.1 IBANNumber — anaf_surse/d406_schema_anaf.xlsx)
care lipsește din Date firmă OPREȘTE D406, numit, iar antetul poartă datele firmei. Pașii contabilului pe aplicația din index, pe baza
de TEST, pe o firmă NOUĂ (`firma_noua`). IBAN sintetic cu cifra de control mod-97 verificată (`salariati_api.iban_valid`)."""
import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, sql

IBAN = "RO59BTRLRONCRT0C69TEST01"


@pytest.fixture(scope="module")
def firma_d406():
    for f in firma_noua():
        yield f


def _date_firma(patron, firma):
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    return patron.pg


def _d406(patron, firma, an, luna):
    """Declarații -> D406 -> perioada -> Continuă; întoarce după ce ecranul a răspuns (XML-ul generat sau refuzul)."""
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(firma["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, "d406")
    alege_perioada(pg, an, luna)
    pg.click("#dec-continua")
    pg.wait_for_selector(".dec-eroare, details.dec-xml summary:text('Vezi XML-ul generat')", timeout=90000)
    return pg


def test_def_c69_d406_cere_telefonul_si_nu_inventeaza_antetul(patron, firma_d406):
    """C69. Pașii: firma are în Date firmă localitatea, IBAN-ul și declarantul, dar NU telefonul -> Date firmă: panoul „Profil incomplet”
    spune „Telefon — blochează D394, D406” -> Declarații, D406 pe 09.2026 -> Continuă: refuz „Lipsă telefonul firmei … Completează
    „Telefon” în Date firmă”, cu butonul spre Date firmă; niciun XML -> butonul duce în Date firmă, la Telefon: 0264 111 222 -> Salvează ->
    Declarații, D406 pe 09.2026: XML-ul generat are telefonul firmei, IBAN-ul ei și declarantul ca persoană de contact — nu „-”, nu
    „RO00BANK0000000000000000”."""
    s = firma_d406["schema"]
    sql('UPDATE "%s".firma_profil SET adresa = %%s, oras = %%s, judet = %%s, caen = %%s, banca = %%s, iban = %%s, telefon = NULL, '
        'declarant_nume = %%s, declarant_prenume = %%s, declarant_functie = %%s, reg_com = %%s, regim_fiscal = %%s, '
        'platitor_tva = true, tip_decont = %%s, operatiuni_ic = false WHERE id = 1' % s,
        ("Str. Probei 9", "Cluj-Napoca", "CJ", "6920", "BT", IBAN, "POPESCU", "ION", "ADMINISTRATOR", "J12/69/2020", "micro", "lunar"))
    pg = _date_firma(patron, firma_d406)
    panou = pg.inner_text(".dec-avert")
    assert "Profil incomplet" in panou and "Telefon" in panou and "D406" in panou, panou
    patron.captura("profil_incomplet")

    pg = _d406(patron, firma_d406, 2026, 9)
    err = pg.inner_text(".dec-eroare")
    assert "Lipsă telefonul firmei" in err and "„Telefon” în Date firmă" in err, err
    # [lotul 12, 596] pagina principală de dedesubt are acum și ea `details.dec-xml` („Cum se face” pe cardurile „Primii pași”): XML-ul se
    # caută în fereastra declarației, cea din față
    assert not pg.evaluate("() => !![...document.querySelectorAll('.fereastra')].pop().querySelector('details.dec-xml')"), \
        "D406 refuzat nu arată niciun XML"
    patron.captura("refuz")
    buton = pg.locator(".dec-eroare button[data-ecran-destinatie='date_firma']")
    assert buton.count() == 1, "refuzul trimite la Date firmă"
    buton.click()
    pg.wait_for_selector("#df-telefon", timeout=30000)
    pg.fill("#df-telefon", "0264 111 222")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('alvat')", timeout=30000)
    assert sql('SELECT telefon FROM "%s".firma_profil' % s) == [("0264 111 222",)]

    pg = _d406(patron, firma_d406, 2026, 9)
    assert not pg.query_selector(".dec-eroare"), pg.inner_text(".dec-eroare")
    xml = pg.locator("details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").text_content()
    patron.captura("generat")
    assert "<Telephone>0264 111 222</Telephone>" in xml                       # S.CTH.2 — telefonul firmei (era „-”)
    assert "<IBANNumber>%s</IBANNumber>" % IBAN in xml                         # S.BA.1 — IBAN-ul firmei (era RO00BANK…)
    assert "<FirstName>ION</FirstName>" in xml and "<LastName>POPESCU</LastName>" in xml   # S.PN.2 / S.PN.5 — declarantul
    assert "<City>Cluj-Napoca</City>" in xml                                   # S.AD.5
    for inventat in ("RO00BANK0000000000000000", "<Telephone>-</Telephone>", "<FirstName>-</FirstName>", "<PostalCode>000000"):
        assert inventat not in xml, inventat
