# -*- coding: utf-8 -*-
"""GARDA (15.09.2026): atribuirea scrierilor la o ruta nu poate nici degenera, nici tacea.

DE CE EXISTA. Perimetrul etapei 2 se DERIVA (`scan_lanturi_declaratie`), iar derivarea sta pe o
singura intrebare: *„in ce tabele scrie ruta asta?"*. Raspunsul a fost, pana azi, reuniunea
scrierilor TUTUROR modulelor rutei. Valul use-case al lui P7 (13.09) a mutat corpurile rutelor in
`core/uc_*.py`; `uc_comun` e importat de aproape fiecare invelis si mosteneste, prin pasul
modul->depozit din `scan_trasee`, scrierile a 18 tabele. Efect MASURAT pe 15.09.2026, inainte de
reparatie: `GET /declaratii/tipuri` — ruta de pura citire — „scria" 18 tabele, 255 din 424 de
unitati „scriau" 10 sau mai multe, iar nucleul etapei 2 iesea **266** in loc de 72. *Un perimetru in
care aproape totul alimenteaza aproape tot nu delimiteaza nimic.*

CELE PATRU FELURI DE ESEC pe care le pazeste, fiindca instrumentul poate gresi in AMBELE directii
(METODA §22), iar unul care greseste in amandoua n-are niciun plafon:
  1. DEGENERARE — o ruta crediteaza zeci de tabele care nu sunt ale ei;
  2. TACERE — o ruta care chiar scrie iese goala (asa arata un punct orb: nu minte, tace);
  3. VACUU — instrumentul intoarce gol peste tot, iar gardul de mai sus trece triumfator;
  4. ALIASUL REFOLOSIT — modul propriu de esec al reparatiei, gasit CHIAR DE EA: stratul use-case
     importa in corpul functiei si refoloseste acelasi alias (`_s` e `stocuri_api` intr-o functie si
     `stocuri_cv_api` in urmatoarea). Rezolvat pe fisier, apelul ateriza in modulul gresit, unde
     numele nu exista — deci tacere. Masurat atunci: `stocuri_adauga` si `cv_intrare`, doua rute
     care chiar scriu, ieseau goale.
"""
import ast
import os
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from scripts import scan_functionalitati as F  # noqa: E402

#: Rute care SCRIU, cu tabelul pe care nicio atribuire corecta nu-l poate rata. Perechile sunt
#: citite la sursa, nu din memorie, si se cer prin INCLUZIUNE — instrumentul poate vedea si mai
#: mult (lantul lung), dar niciodata mai putin.
SCRIU = {
    "factura_creeaza": {"facturi", "factura_linii"},
    "salariat_creeaza": {"salariati"},
    "jurnal_creeaza": {"inregistrari", "inregistrari_linii"},
    "casa_adauga": {"casa_operatiuni"},
    "d300_manual_adauga": {"d300_manual"},
    "d390_manual_adauga": {"d390_manual"},
    "d301_operatiuni_adauga": {"d301_operatiuni"},
    "facturi_emite": {"facturi"},
    # cele doua care au dat de gol aliasul refolosit — raman aici ca proba, nu ca amintire
    "stocuri_adauga": {"nir"},
    "cv_intrare": {"miscari_stoc"},
}

#: Rute de PURA CITIRE. Oricare din ele cu un tabel scris inseamna ca atribuirea a inceput iar sa
#: imprumute de la vecini.
CITESC = ("declaratii_tipuri", "facturi_lista", "salariati_lista", "tenant_jurnal",
          "d300_manual_lista", "d301_operatiuni_lista", "d390_clasificare_stare",
          "factura_detalii", "salariat_detalii")

#: Plafonul de degenerare. Masurat pe populatia reala de azi: maximul e 9 tabele pe unitate, iar
#: distributia nu se mai misca de la adancimea 4. Pragul lasa loc lantului lung si prinde intoarcerea
#: la reuniunea pe modul, care punea 18-24.
PLAFON_TABELE = 14

#: Podeaua de anti-vacuu: atatea unitati trebuie sa aiba CEL PUTIN o scriere. Masurat azi: 128.
PODEA_SCRIITORI = 100


@pytest.fixture(scope="module")
def masurat():
    r, _g, mod, _d, _t, _o, _du = F.construieste()
    return r, mod, {x.get("fn"): x for x in r if x.get("fn")}


def test_o_ruta_care_scrie_isi_arata_tabelul(masurat):
    """Directia pozitiva: ce scrie se vede. O lipsa aici e un PUNCT ORB, nu o cifra mai mica."""
    _r, mod, idx = masurat
    lipsa = {}
    for fn, cerute in SCRIU.items():
        x = idx.get(fn)
        assert x is not None, "ruta %s nu mai exista — proba si-a pierdut subiectul" % fn
        vazute = F.scrie_unitatea(x, mod)
        if not cerute <= vazute:
            lipsa[fn] = sorted(cerute - vazute)
    assert not lipsa, "rute care scriu, dar ies fara tabelul lor: %s" % lipsa


def test_o_ruta_de_citire_nu_imprumuta_scrieri(masurat):
    """Directia negativa: tacerea unei citiri. Aici a cazut instrumentul dupa P7."""
    _r, mod, idx = masurat
    vinovate = {}
    for fn in CITESC:
        x = idx.get(fn)
        assert x is not None, "ruta %s nu mai exista — proba si-a pierdut subiectul" % fn
        scrise = F.scrie_unitatea(x, mod)
        if scrise:
            vinovate[fn] = sorted(scrise)
    assert not vinovate, ("rute de citire carora li se atribuie scrieri — atribuirea imprumuta iar "
                          "de la modul: %s" % vinovate)


def test_atribuirea_nu_degenereaza(masurat):
    """Nicio unitate nu poate scrie in zeci de tabele. Inainte de reparatie: 255 peste 10."""
    r, mod, _idx = masurat
    grase = {(x.get("metoda"), x.get("norm")): len(F.scrie_unitatea(x, mod)) for x in r
             if len(F.scrie_unitatea(x, mod)) > PLAFON_TABELE}
    assert not grase, ("unitati cu peste %d tabele scrise — atribuirea a redevenit pe modul: %s"
                       % (PLAFON_TABELE, grase))


def test_atribuirea_nu_e_goala(masurat):
    """ANTI-VACUU: un instrument tacut ar trece toate gardurile de mai sus."""
    r, mod, _idx = masurat
    scriitori = sum(1 for x in r if F.scrie_unitatea(x, mod))
    assert scriitori >= PODEA_SCRIITORI, (
        "numai %d unitati mai au vreo scriere (podea %d): atribuirea a amutit, nu s-a ingustat"
        % (scriitori, PODEA_SCRIITORI))


def test_aliasul_refolosit_nu_se_amesteca_intre_functii(tmp_path):
    """MUTATIE pe propriul mod de esec: doua functii, acelasi alias, module diferite.

    Calibrare sintetica — daca rezolvarea ar fi iar pe fisier, al doilea import l-ar suprascrie pe
    primul si una din cele doua functii s-ar rezolva in modulul gresit. Se cere ca fiecare functie
    sa-si vada PROPRIUL modul.
    """
    src = ("def a():\n"
           "    from core import stocuri_api as _s\n"
           "    return _s.adauga_nir()\n"
           "def b():\n"
           "    from core import stocuri_cv_api as _s\n"
           "    return _s.intrare()\n")
    arb = ast.parse(src)
    fn = {n.name: n for n in arb.body}
    assert F._alias_local(fn["a"]) == {"_s": "stocuri_api"}, "prima functie nu-si vede modulul"
    assert F._alias_local(fn["b"]) == {"_s": "stocuri_cv_api"}, "a doua functie a luat modulul primei"


def test_ce_nu_se_rezolva_se_DECLARA_nu_se_taie(masurat):
    """Rutele din afara stratului de aplicatie cad pe atribuirea VECHE (plafon superior), nu pe gol.

    `core/spv_rute.py` e montat din afara, deci `scan_sql_efectiv.functia` nu-l gaseste. Raspunsul
    corect acolo e plafonul pe modul — o tacere s-ar citi ca „ruta n-are efect".
    """
    r, mod, _idx = masurat
    dinafara = [x for x in r if x.get("sursa") and x["sursa"] != "main.py"]
    assert dinafara, "ANTI-VACUU: nicio ruta montata din afara — proba n-are subiect"
    nerezolvate = [x for x in dinafara if F.scrie_functia(x) is None]
    assert nerezolvate, ("niciuna nu mai cade pe plafonul pe modul: daca stratul s-a schimbat, "
                         "motivul se rescrie aici, nu se sterge proba")
    for x in nerezolvate:
        pe_modul = set()
        for m in x.get("module") or []:
            pe_modul |= set((mod.get(m) or {}).get("scrie") or {})
        assert F.scrie_unitatea(x, mod) >= pe_modul, (
            "%s nu mai primeste plafonul pe modul" % x.get("fn"))
