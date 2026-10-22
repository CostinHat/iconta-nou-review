# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) pct.16 — deficiența 440, partea serverului (W3a):
„toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp; pe toată aplicația”.

Ce se probează: refuzul SERVERULUI (nu verificarea din browser) pe două formulare zilnice — Date firmă și dispoziția de Casă — numește
toate greșelile deodată, iar ecranul pune fiecare lângă câmpul ei și pe toate în caseta „NU s-a salvat.”. Înainte, serverul se oprea la
prima, deci a doua greșeală nu apărea deloc până la a doua apăsare.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`). Date de pornire scrise direct:
niciuna — profilul și vectorul se fac pe rutele pe care le cheamă ecranele (`pregateste_firma`); ce se probează se face pe ecran."""
import datetime

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _card, pregateste_firma

AZI = datetime.date.today()
CUI_FURNIZOR = "14399840"   # cifra de control verificată (algoritmul din CLAUDE.md: 1439984 -> 0)


@pytest.fixture(scope="module")
def firma_w3a():
    for f in firma_noua():
        yield f


def _caseta(pg):
    """Caseta „NU s-a salvat.”: textele rândurilor vizibile."""
    return [t for t, viz in pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li",
                                                    "lis => lis.map(li => [li.textContent.trim(), !li.hidden])") if viz]


def _langa_camp(pg, ids):
    """[(id, aria-invalid, textele mesajelor legate prin aria-describedby)] pentru câmpurile date."""
    return pg.evaluate("""(ids) => ids.map((id) => {
        const el = document.getElementById(id);
        if (!el) return [id, null, []];
        const d = (el.getAttribute('aria-describedby') || '').split(' ').map((x) => document.getElementById(x)).filter(Boolean);
        return [id, el.getAttribute('aria-invalid'), d.map((x) => x.textContent.trim()).filter((t) => t)];
      })""", ids)


def test_def_440_date_firma_serverul_refuza_toate_valorile_deodata(patron, firma_w3a):
    """440, Date firmă (B1/A1). Pașii: fereastra firmei -> Date firmă -> seria chitanțelor „CH-440!” (litere și cifre, cel mult 10) și
    data înființării 01.01.2999 (în viitor) -> Salvează. Amândouă sunt refuzuri ale SERVERULUI (`firma_profil_api.salveaza_date`):
    lângă fiecare câmp textul lui, iar în caseta de lângă buton amândouă. Nimic nu se scrie. Înainte: numai seria (prima), data nu."""
    pg = patron.pg
    pregateste_firma(patron, firma_w3a)
    s = firma_w3a["schema"]
    # starea de dinainte de apăsare: `pregateste_firma` scrie seria chitanțelor „E2ECH” (data înființării rămâne necompletată)
    inainte = sql('SELECT serie_chitanta, data_infiintare FROM "%s".firma_profil WHERE id = 1' % s)[0]
    assert inainte[0] != "CH-440!" and inainte[1] != datetime.date(2999, 1, 1), inainte
    patron.firma(firma_w3a["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    pg.fill("#df-nume-portofoliu", firma_w3a["nume"])
    pg.fill("#df-serie_chitanta", "CH-440!")
    pg.fill("#df-data_infiintare", "2999-01-01")
    pg.click("#df-salveaza")
    # starea finală a refuzului: data marcată ȘI seria în casetă (cu mutația — numai prima eroare — data nu se marchează: ROȘU)
    pg.wait_for_function("() => document.getElementById('df-data_infiintare').getAttribute('aria-invalid') === 'true'"
                         " && [...document.querySelectorAll('.refuz-salvare-lista > li')].some(li => li.textContent.includes('Seria'))",
                         timeout=20000)
    patron.captura()
    campuri = _langa_camp(pg, ["df-serie_chitanta", "df-data_infiintare"])
    assert campuri[0][1] == "true" and any("Seria chitanțelor: litere și cifre" in t for t in campuri[0][2]), campuri
    assert campuri[1][1] == "true" and any("Data înființării nu poate fi în viitor." in t for t in campuri[1][2]), campuri   # 440
    caseta = " ".join(_caseta(pg))
    assert "Seria chitanțelor: litere și cifre" in caseta and "Data înființării nu poate fi în viitor." in caseta, caseta
    # nimic scris: amândouă câmpurile au valorile de dinainte de apăsare (nu „CH-440!”, nu 2999)
    assert sql('SELECT serie_chitanta, data_infiintare FROM "%s".firma_profil WHERE id = 1' % s)[0] == inainte


def test_def_440_casa_dispozitia_suma_si_destinatia_avansului_deodata(patron, firma_w3a):
    """440, Casă (B2/A3). Pașii: Casă -> „+ Dispoziție nouă” -> azi, „Plată către furnizor”, 500 lei, CUI-ul furnizorului (fără facturi
    deschise: plata e avans acordat) -> „Adaugă” fără să aleagă pentru ce e avansul. Casa e goală, deci plata nu încape. Serverul
    (`casa_api.adauga`) spune AMBELE: suma care nu încape în casă (lângă „Suma”) și destinația avansului (lângă „Avansul e pentru”);
    caseta le are pe amândouă. Înainte: numai „nu încape în casă”, iar destinația se afla abia după ce omul repara suma.
    [lotul 11, E2C] Marcajele rămân și după previzualizarea de după refuz (pornită de `change`-ul de la părăsirea câmpului CUI, chiar la
    clicul pe „Adaugă”): înainte, rescrierea zonei facturilor ștergea eroarea de lângă „Avansul e pentru” la 250 ms după ce apăruse. Apoi
    omul alege destinația: eroarea ei pleacă, a sumei rămâne, iar refuzul „nu încape în casă” revine sub formular (previzualizarea refăcută)."""
    pg = patron.pg
    patron.firma(firma_w3a["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "plata_furnizor")
    pg.fill("#c-suma", "500")
    pg.fill("#c-part", "FURNIZOR E2E 440 SRL")
    pg.fill("#c-cui", CUI_FURNIZOR)
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-avans-dest", timeout=20000)   # previzualizarea: plata e avans, destinația se cere
    pg.click("#c-adauga")
    pg.wait_for_function("() => document.getElementById('c-avans-dest') && "
                         "document.getElementById('c-avans-dest').getAttribute('aria-invalid') === 'true'", timeout=20000)
    # o previzualizare DUPĂ refuz (ca cea pornită de părăsirea câmpului CUI la clic): `change` pe zona câmpurilor (nu pe un câmp, deci nu
    # e o corectare — nu șterge nicio eroare); se așteaptă zona refuzului rescrisă de răspunsul ei, nu un timp
    pg.evaluate("() => { window.__e2cPreviz = document.getElementById('c-previz-refuz'); }")
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_function("() => { const x = document.getElementById('c-previz-refuz'); return !!x && x !== window.__e2cPreviz; }",
                         timeout=20000)
    patron.captura()
    campuri = _langa_camp(pg, ["c-suma", "c-avans-dest"])
    assert campuri[0][1] == "true" and any("nu încape în casă" in t for t in campuri[0][2]), campuri
    assert campuri[1][1] == "true" and any("alege pentru ce e avansul" in t for t in campuri[1][2]), campuri   # 440: amândouă
    caseta = " ".join(_caseta(pg))
    assert "nu încape în casă" in caseta and "alege pentru ce e avansul" in caseta, caseta
    assert sql('SELECT count(*) FROM "%s".casa_operatiuni' % firma_w3a["schema"])[0][0] == 0   # nimic scris
    # omul alege destinația: eroarea ei pleacă (290), a sumei rămâne, iar refuzul previzualizării revine (alegerea refăcuse previzualizarea)
    pg.evaluate("() => { window.__e2cPreviz = document.getElementById('c-previz-refuz'); }")
    pg.select_option("#c-avans-dest", "servicii")
    pg.wait_for_function("() => { const x = document.getElementById('c-previz-refuz'); return !!x && x !== window.__e2cPreviz "
                         "&& x.textContent.includes('nu încape în casă'); }", timeout=20000)
    campuri = _langa_camp(pg, ["c-suma", "c-avans-dest"])
    assert campuri[1][1] is None and not campuri[1][2], campuri
    assert campuri[0][1] == "true" and any("nu încape în casă" in t for t in campuri[0][2]), campuri
    assert pg.input_value("#c-avans-dest") == "servicii"
