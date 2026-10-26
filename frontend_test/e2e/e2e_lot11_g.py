# -*- coding: utf-8 -*-
"""Lotul 11, subagentul G — 436 (afișare), clasa „paragraful repetă ce arată butoanele”, pe drumurile COZII (comanda Costin 11.1,
verbatim în DECIZII „Comanda 11.1”: „în D100, începutul casetei roșii e ascuns sub antetul fix; paragraful repetă notele pe care le arată
butoanele.”). Refuzul de la „Trimite în coadă” (`static/js/ecrane/coada_trimite.js`) pune lângă text câte un buton „Deschide nota …”
pentru fiecare notă; textul le numără, nu le mai enumeră. Trei drumuri:
  · poarta TVA cu diferență și o ciornă care nu mișcă TVA-ul (MESAJ_CIORNE_BLOCAJ, D300);
  · poarta TVA cu nota care explică diferența (284, D300: factura emisă cu nota de contare ciornă);
  · notele nevalidate ale declarației din evidență (436, bilanțul S1005 trimis din ecranul Bilanț).

Date de PORNIRE: firmele NOI ale cabinetului de test (`conftest.firma_noua`), cu Date firmă / vectorul / notele / factura pe rutele pe
care le cheamă ecranele (`firma-profil/date`, `vector`, `jurnal`, `facturi/emite`). Nicio inserare directă. CUI-urile vin din
`firma_noua` (cifra de control verificată); CNP-uri nu se folosesc. N/A temei fiscal — afișare."""
import pytest

from conftest import firma_noua, linie_nota, perioada_incheiata, sql

LUNA = perioada_incheiata("lunar")


#: [lotul 13, 515] butoanele refuzului cozii stau în rândul de imediat după zona mesajului (`coada_trimite._actiuniRefuz`)
def butoane_refuz(zona):
    return zona + " + .coada-actiuni-refuz .coada-note-refuz button"


def text_langa_butoane(pg, zona):
    """Textul refuzului FĂRĂ butoanele notelor (și fără eticheta notelor interne a partidei simple): ce citește contabilul ca paragraf;
    plus etichetele butoanelor. [lotul 13, 515] Refuzul de lângă buton îl spune caseta „NU s-a salvat.” (zona lui stă ascunsă cât stă
    caseta), iar butoanele stau în rândul de după zonă; o zonă care nu e lângă buton (Bilanț) își arată singură textul."""
    return pg.evaluate("""(sel) => { const z = [...document.querySelectorAll(sel)].pop();
        const a = z.nextElementSibling && z.nextElementSibling.classList.contains('coada-actiuni-refuz') ? z.nextElementSibling : null;
        const f = z.closest('.fereastra') || document;
        const motiv = z.hidden ? f.querySelector('.refuz-salvare .refuz-salvare-motiv') : null;
        const c = z.cloneNode(true);
        c.querySelectorAll('.coada-note-refuz, .ecran-nota').forEach((x) => x.remove());
        return {text: (motiv ? motiv.textContent : c.textContent).replace(/\\s+/g, ' ').trim(), ascunsa: z.hidden,
                butoane: a ? [...a.querySelectorAll('.coada-note-refuz button')].map((b) => b.innerText.trim()) : []}; }""", zona)


def _nota(patron, firma, data, debit, credit, suma, descriere, document_ref, valideaza=False):
    from e2e_bloc_a import _api, _ok
    r = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % firma["tenant_id"],
                 {"data": data, "descriere": descriere, "document_ref": document_ref, "linii": [linie_nota(debit, credit, suma)]}), "nota")
    if valideaza:
        _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], r["id"]), {}), "validarea notei")
    return r["id"]


@pytest.fixture()
def firma_tva_g(patron):
    """Firmă NOUĂ plătitoare de TVA, decont lunar (Date firmă + vector, `pregateste_firma`)."""
    from e2e_bloc_a import pregateste_firma
    for f in firma_noua():
        pregateste_firma(patron, f)
        try:
            yield f
        finally:
            sql("DELETE FROM public.declaratii_in_asteptare WHERE tenant_id = %s", (f["tenant_id"],))


def _d300_trimite(patron, firma):
    from e2e_bloc_c import _declaratie_pas1, _trimite_si_asteapta
    _declaratie_pas1(patron, firma["nume"], "d300", LUNA.an, luna=LUNA.luna)
    _trimite_si_asteapta(patron)
    patron.pg.wait_for_selector(butoane_refuz("#dec-coada-mesaj"), timeout=30000)
    return text_langa_butoane(patron.pg, "#dec-coada-mesaj")


def test_def_436_coada_refuzul_nu_repeta_notele_ciorna_din_perioada(patron, firma_tva_g):
    """Pașii: luna încheiată are nota VALIDATĂ 4426 = 401 de 241,50 (TVA pe care documentele nu-l au) și o plată către furnizor în
    ciornă (401 = 5311, „DP-G436”) -> Declarații -> D300 pe luna aceea -> „Trimite în coadă →”: refuzul spune diferența pe 4426 și că
    perioada are 1 notă nevalidată (ce e de făcut și că declarația intră singură în coadă după validare), fără s-o enumere; nota e
    butonul „Deschide nota … DP-G436 …”. Înainte: paragraful repeta „nota din … — DP-G436, 100,00 lei” deasupra butonului care o numea."""
    _nota(patron, firma_tva_g, LUNA.inceput.replace(day=7).isoformat(), "4426", "401", 241.50, "NIR fara factura G436", "NIR-G436",
          valideaza=True)
    _nota(patron, firma_tva_g, LUNA.inceput.replace(day=9).isoformat(), "401", "5311", 100, "Plata furnizor ciorna G436", "DP-G436")
    m = _d300_trimite(patron, firma_tva_g)
    patron.captura()
    assert "Declarația nu intră în coadă: TVA-ul ei nu se potrivește cu balanța lunii" in m["text"] and "contul 4426 are 241,50" in m["text"], m
    assert "Perioada are 1 notă nevalidată — dacă ele corectează diferența, validează-le și generează din nou" in m["text"], m
    assert "se generează din nou și intră singură în coadă" in m["text"], m
    assert "DP-G436" not in m["text"] and "100,00 lei" not in m["text"], m          # nota nu se mai enumeră în paragraf
    assert len(m["butoane"]) == 1 and "DP-G436" in m["butoane"][0], m               # o numește butonul


def test_def_436_coada_refuzul_nu_repeta_notele_nota_care_explica_diferenta(patron, firma_tva_g):
    """Pașii (284): o factură emisă în luna încheiată (nota ei de contare e ciornă) -> Declarații -> D300 pe luna ei -> „Trimite în
    coadă →”: refuzul spune diferența pe 4427 și că „Diferența pe contul 4427 o explică 1 notă nevalidată”, fără numărul, documentul și
    suma notei — pe care le arată butonul „Deschide nota … Factură …”. Înainte: „Diferența o explică pe contul 4427: nota din … — Factură
    …, 363,00 lei” deasupra aceluiași buton."""
    from e2e_bloc_a import emite_api
    emite_api(patron, firma_tva_g, data_emitere=LUNA.inceput.replace(day=15))
    m = _d300_trimite(patron, firma_tva_g)
    patron.captura()
    assert "Declarația nu intră în coadă: TVA-ul ei nu se potrivește cu balanța lunii" in m["text"], m
    assert "Diferența pe contul 4427 o explică 1 notă nevalidată." in m["text"], m
    assert "se generează din nou și intră singură în coadă" in m["text"], m
    assert "Diferența o explică pe contul 4427:" not in m["text"] and "Factură" not in m["text"], m
    assert len(m["butoane"]) == 1 and "Factură" in m["butoane"][0], m


@pytest.fixture()
def firma_bilant_g(patron):
    """Firmă NOUĂ cu datele bilanțului în Date firmă (`e2e_bloc_d._date_firma`: forma de proprietate, mare contribuabil) și luna preluării
    01/2024 (evidența cuprinde 2025 întreg și anul precedent — ca la testul 72), plus o notă în ciornă pe 10.06.2025 („DP-G438”)."""
    from e2e_bloc_a import _api, _ok
    from e2e_bloc_d import _date_firma
    for f in firma_noua():
        _date_firma(f)
        _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"luna_preluare": "2024-01"}), "luna preluării")
        f["ciorna"] = _nota(patron, f, "2025-06-10", "6022", "5311", 11, "Combustibil ciorna G438", "DP-G438")
        try:
            yield f
        finally:
            sql("DELETE FROM public.declaratii_in_asteptare WHERE tenant_id = %s", (f["tenant_id"],))


def test_def_436_coada_refuzul_nu_repeta_notele_bilantul_din_evidenta(patron, firma_bilant_g):
    """Pașii (436): firma -> Bilanț anual -> 2025, S1005 -> „Trimite în coadă →” (din ecranul Bilanț, pe drumul comun al cozii): refuzul
    spune „Declarația nu se depune până la validarea notelor: cifra ei nu cuprinde 1 notă nevalidată din perioada ei. Validează-le …”,
    plus că după validare declarația se generează din nou și intră singură în coadă — fără „nota din 10.06.2025 — DP-G438, 11,00 lei”,
    pe care o arată butonul de sub text. Nu intră în coadă."""
    from e2e_bloc_c import _deschide
    pg = patron.pg
    _deschide(patron, firma_bilant_g["nume"], "bilant", "#bl-coada")
    pg.fill("#bl-an", "2025")
    pg.dispatch_event("#bl-an", "change")
    pg.select_option("#bl-tip", "s1005")
    pg.click("#bl-coada")
    pg.wait_for_selector(butoane_refuz("#bl-coada-mesaj"), timeout=90000)
    m = text_langa_butoane(pg, "#bl-coada-mesaj")
    patron.captura()
    assert m["text"].startswith("Declarația nu se depune până la validarea notelor: cifra ei nu cuprinde 1 notă nevalidată din perioada "
                                "ei. Validează-le în Registrul jurnal, apoi generează din nou."), m
    assert "se generează din nou și intră singură în coadă" in m["text"], m
    assert "DP-G438" not in m["text"] and "11,00 lei" not in m["text"], m
    assert len(m["butoane"]) == 1 and "DP-G438" in m["butoane"][0], m
    assert not sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 's1005'", (firma_bilant_g["tenant_id"],))
