# -*- coding: utf-8 -*-
"""Lotul 11, subagentul D (comanda Costin 11.1, verbatim în DECIZII „Comanda 11.1”; deciziile din „Comanda 10.3” pct.4):

  C70  — „C70: refaci D101G pe validatorul v2.” D101G trece validatorul oficial (DUK), pe datele firmei din Date firmă.
  436  — afișare: „în D100, începutul casetei roșii e ascuns sub antetul fix; paragraful repetă notele pe care le arată butoanele.”
  D205 — „D205 pe anii depuși după regula veche: fără rectificative.” (refuzul cu motivul numit, pe Declarații) și
         „Semaforul D205 numără 457 preluat ca incomplet până la completarea manuală.” (Control fiscal, „Nu se poate verifica”).

Date de PORNIRE inserate direct (aplicația nu le poate produce, declarate): o D205 pe 2025 depusă prin iConta.eu pe 20.02.2026 — o
depunere din trecut, făcută după regula veche (rândul în `public.declaratii_depuse`, scos la final; depunerea trece prin SPV). Restul pe
DRUMUL APLICAȚIEI, ca la contabil (garda `core/test_e2e_fara_date_fabricate.py`): identitatea firmei din Date firmă (`POST
firma-profil/date`), balanța de deschidere a firmei preluate cu rulajul anului pe 457 din Migrare -> Solduri inițiale (`POST solduri`, cu
soldul inițial al anului și rulajele) și luna preluării din Date firmă. Restul pașilor: ecranele aplicației.
CUI-urile vin din `firma_noua` (cifra de control verificată); CNP-urile nu sunt folosite."""
import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, sql
from e2e_bloc_d import PATRON, _api as _api_cont


def _ruta(cale, corp, ce):
    """O cerere pe ruta ecranului, cu sesiunea contabilului-șef (aceleași gărzi, același autor în jurnal ca pe ecran)."""
    st, r = _api_cont(PATRON, "POST", cale, corp)
    assert st == 200 and (not isinstance(r, dict) or r.get("ok") is not False), (ce, st, r)
    return r


def _profil(f, caen="6920"):
    """Date firmă -> adresa, localitatea, județul, CAEN-ul și declarantul -> Salvează (ruta formularului, `POST firma-profil/date`)."""
    _ruta("/tenants/%d/firma-profil/date" % f["tenant_id"],
          {"adresa": "Str. Probei 11", "oras": "Cluj-Napoca", "judet": "CJ", "caen": caen, "declarant_nume": "POPESCU",
           "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR"}, "Date firmă")


@pytest.fixture()
def firma_d():
    for f in firma_noua():
        _profil(f)
        yield f


def _declaratie(patron, firma, tip, an, luna=None, trim=None):
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(firma["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, tip)
    alege_perioada(pg, an, luna, trim)
    pg.click("#dec-continua")
    pg.wait_for_selector(".fereastra:last-of-type .dec-eroare, .fereastra:last-of-type details.dec-xml", timeout=90000)
    return pg


# ── C70 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c70_d101g_trece_validatorul_oficial(patron, firma_d):
    """C70. D101G n-are ecran (declarație numai prin API, `declaratii_api._DOAR_API`): cererea pleacă din pagina contabilului, cu sesiunea
    lui, pe firma lui (identitatea din Date firmă). Pasul: „validează D101G pe 2025” cu valorile consolidate ale grupului (profit 250.000,
    pierdere recuperată 10.000, impozit declarat prin D100 30.000). Înainte: „eroare structura: sectiune necunoscuta ('declaratie')”.
    Acum: validatorul ANAF D101G v2 spune „valid”, iar XML-ul are rădăcina <D101G>, CAEN, cod_obligatie 100, totalPlata_A 0."""
    import base64
    pg = patron.pg
    patron.firma(firma_d["nume"])
    cere = """async ([tid]) => { const t = sessionStorage.getItem('iconta_token');
        const r = await fetch('/declaratii/d101g/valideaza', {method: 'POST', headers: {Authorization: 'Bearer ' + t, 'Content-Type': 'application/json'},
          body: JSON.stringify({tenant_id: tid, an: 2025, manual: {P01: 250000, P02: 10000, P02a: 10000, P13: 30000}})});
        return [r.status, await r.json()]; }"""
    st, corp = pg.evaluate(cere, [firma_d["tenant_id"]])
    assert st == 200, (st, corp)
    assert corp["stare"] == "valid", corp   # validatorul oficial ANAF D101G J2.0.0
    xml = base64.b64decode(corp["xml_b64"]).decode("utf-8")
    for bucata in ("<D101G ", 'CAEN="6920"', 'cod_obligatie="100"', 'totalPlata_A="0"', 'P15="8400"'):
        assert bucata in xml, (bucata, xml[:600])
    patron.captura()


# ── D205: anii depuși după regula veche ─────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def d205_depusa_veche(firma_d):
    # fixtura-sintetica-ok: firma e2e NOUĂ (`firma_noua`, tenant_id al ei), rândul scos la final — nu atinge perioada unei firme reale
    # date-de-pornire: D205 depusă la ANAF în 02.2026 după regula veche — depunerea trece prin SPV, nu se poate produce în plasă
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, data_depunere, sursa) "
        "VALUES (%s, 2025, 12, 'd205', '<x/>', '2026-02-20 10:00:00+02', 'iconta')", (firma_d["tenant_id"],))
    try:
        yield firma_d
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd205'", (firma_d["tenant_id"],))


def test_def_d205_anul_depus_dupa_regula_veche_nu_primeste_rectificativa(patron, d205_depusa_veche):
    """Decizia Costin 10.3: „D205 pe anii depuși după regula veche: fără rectificative.” Pașii: Declarații -> D205 -> 2025 (depusă prin
    iConta.eu pe 20.02.2026, înainte de regula nouă) -> „Continuă”: refuzul spune că D205 pe 2025 e depusă la 20.02.2026 după regula de
    atunci și că pentru anii depuși după regula veche nu se face rectificativă — nu o D205 nouă care ar intra în coadă ca a doua depunere."""
    pg = _declaratie(patron, d205_depusa_veche, "d205", 2025)
    t = " ".join(pg.inner_text(".fereastra:last-of-type .dec-eroare").split())
    patron.captura()
    assert "D205 pe 2025 e depusă prin iConta.eu la 20.02.2026" in t and "nu se face rectificativă" in t, t
    assert pg.locator(".fereastra:last-of-type #dec-trimite").count() == 0


# ── D205: semaforul, 457 preluat ────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def preluata_2025_cu_457(firma_d):
    """Firma preluată în iConta.eu din 07/2025, pe drumul aplicației: Migrare -> Solduri inițiale -> balanța de deschidere la 30.06.2025,
    cu soldul la 1 ianuarie și rulajele anului (`POST solduri`, coloanele `si_*` / `rulaj_*` ale importului) — rulajul anului pe 457:
    dividende plătite înainte de preluare, 5.000 lei (debit 5.000 / credit 5.000); banca și capitalul (10.000 lei) dau balanței solduri
    (o balanță cu toate soldurile zero se refuză, `solduri_api.balanta_valida`). Apoi Date firmă -> luna preluării 07/2025."""
    tid = firma_d["tenant_id"]
    _ruta("/tenants/%d/solduri" % tid, {"data_referinta": "2025-06-30", "randuri": [
        {"cont": "457", "denumire": "Dividende de plata", "debit": 0, "credit": 0, "si_debit": 0, "si_credit": 0,
         "rulaj_debit": 5000, "rulaj_credit": 5000},
        {"cont": "5121", "denumire": "Conturi la banci in lei", "debit": 10000, "credit": 0, "si_debit": 10000, "si_credit": 0,
         "rulaj_debit": 0, "rulaj_credit": 0},
        {"cont": "1012", "denumire": "Capital subscris varsat", "debit": 0, "credit": 10000, "si_debit": 0, "si_credit": 10000,
         "rulaj_debit": 0, "rulaj_credit": 0}]}, "balanța de deschidere")
    _ruta("/tenants/%d/firma-profil/date" % tid, {"luna_preluare": "2025-07"}, "luna preluării")
    try:
        yield firma_d
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd205'", (firma_d["tenant_id"],))


def test_def_d205_semaforul_numara_457_preluat_ca_incomplet(patron, preluata_2025_cu_457):
    """Decizia Costin 10.3: „Semaforul D205 numără 457 preluat ca incomplet până la completarea manuală.” Pașii: Control fiscal pe firma
    preluată: D205 pe 2025 stă la „Nu se poate verifica”, cu „incompletă până la completarea manuală: dividende plătite înainte de preluare
    (5.000,00 lei)”, nu la „Restanțe”."""
    from e2e_bloc_e import _card
    pg = patron.pg
    _card(patron, preluata_2025_cu_457, "control", ".cf-stare-mare")
    grup = lambda titlu: pg.evaluate("(titlu) => { const t = [...[...document.querySelectorAll('.fereastra')].pop()"
                                     ".querySelectorAll('.cf-grup-titlu')].find((x) => x.textContent.trim().startsWith(titlu));"
                                     " return t ? t.nextElementSibling.innerText : ''; }", titlu)
    neclar, restante = " ".join(grup("Nu se poate verifica").split()), " ".join(grup("Restanțe").split())
    patron.captura()
    assert ("D205 pe 2025 — incompletă până la completarea manuală: dividende plătite înainte de preluare (5.000,00 lei)" in neclar), neclar
    assert "D205" not in restante, restante


# ── 436, afișare ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_436_caseta_de_refuz_incepe_sub_antet_si_nu_repeta_notele(patron, firma_amortizare):
    """436 (afișare): „în D100, începutul casetei roșii e ascuns sub antetul fix; paragraful repetă notele pe care le arată butoanele.”
    Cazul F2 refăcut ca la lotul 10 (`e2e_lot10b_declaratii.firma_amortizare`: amortizarea 01–07/2026 nevalidată). Pașii, într-o
    fereastră de browser joasă (1280 × 520 — acolo bara de jos, cu cele 7 note enumerate și 7 butoane, trecea peste antet): Declarații -> D100 T3/2026 -> pasul 2: caseta roșie de lângă „Trimite în coadă” începe sub antetul lipit sus
    („Pasul 2 din 3 …”), nu sub el; paragraful spune câte note opresc depunerea, fără să le enumere, iar cele 7 note sunt butoanele
    „Deschide nota …”."""
    from e2e_lot82 import _d100_t3
    f = firma_amortizare
    pg = patron.pg
    pg.set_viewport_size({"width": 1280, "height": 520})
    try:
        _d100_t3(patron, f)
        m = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop();
            const cas = f.querySelector('#dec-blocaj'), rez = f.querySelector('.rezumat-fix'), msg = cas.querySelector('.ca-mesaj');
            return {cas: cas.getBoundingClientRect().top, rez: rez.getBoundingClientRect().bottom,
                    text: [...msg.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(' '),
                    butoane: msg.querySelectorAll('.coada-note-refuz button').length}; }""")
        patron.captura()
        assert m["cas"] >= m["rez"] - 1, "începutul casetei e sub antetul lipit sus: %s" % m
        assert m["butoane"] == 7, m
        assert "7 note nevalidate" in m["text"] and "Amortizare 01/2026" not in m["text"], m["text"]
    finally:
        pg.set_viewport_size({"width": 1700, "height": 1000})


from e2e_lot10b_declaratii import firma_amortizare  # noqa: E402,F401 — fixtura cazului F2 (lotul 10), aceeași firmă refăcută
