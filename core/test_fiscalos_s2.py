# -*- coding: utf-8 -*-
"""GARZI [Pachet FiscalOS §2, 01.10.2026]: temeiurile constantelor fara temei + cele 4 sarcini din common.COTE.

Sursa: ~/ghid_incoming/PACHET_FISCALOS_ICONTA.md §2 + verif_temeiuri.json (verificarea arhitectului, 18 APROB/
CORECTEAZA). Fiecare temei a fost RE-verificat verbatim in forma consolidata adusa la §1 (anaf_surse/), nu luat din
pachet. Ce pazeste fisierul:

  1. constantele aprobate poarta `Temei` ca OBIECT (common.ancoreaza), cu actul/articolul/litera aprobate si citatul
     regasit verbatim in documentul din corpus;
  2. VALOAREA constantei apare in propriul citat (forma legii: "10.000 lei", "16%") - o valoare schimbata fara
     temei nou pica, oricare ar fi constanta ancorata, inclusiv una viitoare;
  3. alerta „valori fiscale neconfirmate in prag" e goala la 01.10.2026 (cele 7 reconfirmate);
  4. clasa „articolul declarat != articolul din localizatorul citatului" (masurata: 3 aparitii, toate reparate);
  5. mesajele de casa citeaza litera plafonului APLICAT (sursa unica: temeiul constantei).
Asertiuni pe obiecte/campuri si re.search - fara `"sir" in X` pe mesaje.
"""
import re
from datetime import date
from decimal import Decimal

import pytest

from core import (bacsis, casa, common, cote_tva, d100_pozitia_116, d101, d101g, d394, expirare_cote,
                  salarizare, scan_citate, taxare_inversa)

# Constantele ancorate intră în registru (`common.COTE`, cheia „<modul>.<NUME>”; până la R1, 10.10.2026, `CONSTANTE_ANCORATE`) la IMPORT. Parametrizarea generică de mai jos îl citește la colectare, deci
# un modul neimportat aici își scotea constantele din verificare când testul rula singur (d212 — Etapa 2 și 3 — lipsea din
# lista de sus; în suita completă îl importa alt test, ascunzând golul). Modulele se derivă din cod, nu se enumeră.
_ANCORATOARE = common.module_care_ancoreaza()
common.registru_complet()

# nume -> (modul, valoare, (tip, nr, an, art, alin, lit)) - temeiul APROBAT in verif_temeiuri.json, re-verificat.
APROBATE = {
    # CF art.64 alin.(1) lit.h) + OUG 28/1999 art.2^3 alin.(10) (al doilea, ca TEMEI_BACSIS_ALTE_SURSE)
    "bacsis.COTA_IMPOZIT": (bacsis, Decimal("10"), ("CF", None, None, "64", "1", "h")),
    # Legea 70/2015 art.3 alin.(1) lit.a) / b) / c) / c) / d), art.4 alin.(1), art.4^2 alin.(1)
    "casa.PLAFON_INCASARE_PJ": (casa, Decimal("5000"), ("Legea", 70, 2015, "3", "1", "a")),
    "casa.PLAFON_INCASARE_PJ_CC": (casa, Decimal("10000"), ("Legea", 70, 2015, "3", "1", "b")),
    "casa.PLAFON_PLATA_PJ": (casa, Decimal("5000"), ("Legea", 70, 2015, "3", "1", "c")),
    "casa.PLAFON_PLATA_PJ_TOTAL": (casa, Decimal("10000"), ("Legea", 70, 2015, "3", "1", "c")),
    "casa.PLAFON_PLATA_CC_TOTAL": (casa, Decimal("10000"), ("Legea", 70, 2015, "3", "1", "d")),
    "casa.PLAFON_PF": (casa, Decimal("10000"), ("Legea", 70, 2015, "4", "1", None)),
    "casa.PLAFON_SOLD_ZI_CC": (casa, Decimal("500000"), ("Legea", 70, 2015, "4^2", "1", None)),
    # CF art.291 alin.(1)/(2) (forma Legea 141/2025 art.II pct.42)
    "cote_tva.COTA_STANDARD": (cote_tva, 21, ("CF", None, None, "291", "1", None)),
    "cote_tva.COTA_REDUSA": (cote_tva, 11, ("CF", None, None, "291", "2", None)),
    # CF art.17 ; CF art.18^1 alin.(1)
    "d101.COTA_STANDARD": (d101, Decimal("16"), ("CF", None, None, "17", None, None)),
    "d101.PRAG_IMCA_EUR": (d101, Decimal("50000000"), ("CF", None, None, "18^1", "1", None)),
    "d101g.COTA_STANDARD": (d101g, Decimal("16"), ("CF", None, None, "17", None, None)),
    # OPANAF 2194/2025 anexa 2 cartusul I pct.4.1 (lista cotelor acceptate in D394)
    "d394.COTE": (d394, (0, 5, 9, 11, 19, 20, 21, 24), ("OPANAF", 2194, 2025, None, None, None)),
    # CF art.77 alin.(3) ; CF art.331 alin.(7)
    "salarizare.PRAG_VENIT_DEDUCERE": (salarizare, Decimal("2000"), ("CF", None, None, "77", "3", None)),
    "taxare_inversa.PRAG_ELECTRONICE": (taxare_inversa, Decimal("22500"), ("CF", None, None, "331", "7", None)),
    # OUG 24/2026 art.2 alin.(2) - RESPINS in pachet doar pt corpus ilizibil; §1 a adus forma oficiala
    "d100_pozitia_116.PRAG_BRENT_USD": (d100_pozitia_116, 70, ("OUG", 24, 2026, "2", "2", None)),
}


def _campuri(t):
    return (t.tip, t.nr, t.an, t.art, t.alin, t.lit)


@pytest.mark.parametrize("nume", sorted(APROBATE))
def test_s2_constanta_ancorata_pe_temeiul_aprobat(nume):
    # MUTATIE: lit="b" -> "a" la casa.PLAFON_INCASARE_PJ_CC -> pica pe campuri; citat stricat -> pica pe verbatim.
    modul, valoare, campuri = APROBATE[nume]
    assert nume in common.ancorate(), "%s nu e ancorata (common.ancoreaza)" % nume
    v, t = common.ancorata(nume)
    assert getattr(modul, nume.split(".", 1)[1]) == v == valoare
    assert _campuri(t) == campuri, "%s: temei %s, aprobat %r" % (nume, t, campuri)
    assert t.nivel_sursa == "MO" and t.verificat_la == date(2026, 10, 1)
    assert scan_citate._verbatim(t) is True, "%s: citatul nu e verbatim in %s" % (nume, t.url)


def _forme_legale(v):
    """Cum scrie legea valoarea: 10.000 / 16% / 0,5% / 365 de zile. Lista de forme, nu o singura - legea scrie "10.000 lei"
    la plafoane si "16%" la cote; ambele sunt valoarea, niciuna nu e alta."""
    d = Decimal(str(v))
    intreg = "{:,}".format(int(d)).replace(",", ".") if d == d.to_integral() else None
    forme = [str(d).replace(".", ",") + "%"]
    if intreg:
        forme += [intreg + "%", intreg + " lei", intreg + " euro", intreg + " USD", intreg + " de lei",
                  intreg + " de zile", intreg + " zile"]   # un numar de zile (d212.ZILE_AN_NORMA: „la 365 de zile”)
    return forme


@pytest.mark.parametrize("nume", sorted(common.ancorate()))
def test_s2_valoarea_e_in_propriul_citat(nume):
    # GENERIC: orice constanta ancorata (si una adaugata maine) isi poarta valoarea in citatul temeiului.
    # MUTATIE: casa.PLAFON_PF Decimal("10000") -> Decimal("15000") -> "15.000 lei" nu e in citat -> pica.
    v, t = common.ancorata(nume)
    valori = [x for x in (v if isinstance(v, tuple) else (v,)) if x != 0]   # 0 = structura (TIP_COTA_ZERO)
    for x in valori:
        assert any(re.search(re.escape(f) + r"(?![0-9])", t.text_citat) for f in _forme_legale(x)), (
            "%s = %s: valoarea nu apare in citatul temeiului (%s)" % (nume, x, t.text_citat[:120]))


def test_s2_alerta_de_reconfirmare_e_goala_la_predare():
    # Cele 7 valori din alerta (tva_standard, tva_redusa, tva_redusa_9, tva_redusa_5, impozit_dividend,
    # impozit_micro, impozit_venit) reconfirmate la sursa pe 01.10.2026, pe pragul per articol.
    # MUTATIE: impozit_venit verificat_la -> "2026-08-07" -> reapare in alerta -> pica.
    care = expirare_cote.cote_neconfirmate(6, la_data=date(2026, 10, 1), prag_pentru=expirare_cote._prag_pentru)
    assert [x["nume"] for x in care] == []


def test_s2_sarcinile_cote():
    # (a) dividende: consumatorii (D205, decontari_asociati) sunt beneficiari PF -> CF art.97 alin.(7), verbatim.
    _d, v, t = sorted(common.COTE["impozit_dividend"], key=lambda r: r[0])[-1]
    assert v == Decimal("0.16") and (t.tip, t.art, t.alin) == ("CF", "97", "7") and scan_citate._verbatim(t)
    # (b) micro 1% ancorat pe forma art.51 alin.(1) din 2026 (OUG 89/2025 art.I pct.4), citat verbatim.
    _d, v, t = sorted(common.COTE["impozit_micro"], key=lambda r: r[0])[-1]
    assert v == Decimal("0.01") and (t.art, t.alin) == ("51", "1") and scan_citate._verbatim(t)
    assert re.search(r"OUG 89/2025", t.lant_acte)
    # (c) 9%/5% sunt ISTORIC: valoarea curenta a cheilor comasate = tva_redusa, pe ACELASI alineat (291 alin.2).
    #     MUTATIE: tva_redusa_5 alin "2" -> "3" (alineatul ABROGAT de Legea 141/2025 pct.43) -> pica.
    for k in ("tva_redusa_9", "tva_redusa_5"):
        v, t = common.cota(k, date(2026, 10, 1))
        assert v == common.cota("tva_redusa", date(2026, 10, 1))[0] and (t.art, t.alin) == ("291", "2"), k
        assert re.search(r"doar istoric, nu se reconfirmă", expirare_cote.ETICHETE[k]), k


def _localizator_art(t):
    tc = t.text_citat or ""
    if ":" not in tc:
        return None
    loc = tc.split(":", 1)[0]
    if len(loc) > 90:
        return None
    return re.findall(r"\bart\.\s*([0-9]+(?:\^[0-9]+)?)", loc, re.I) or None


def test_s2_articolul_declarat_e_cel_din_localizatorul_citatului():
    # CLASA (masurata 01.10.2026 pe toate Temei-urile din core): Temei(art=97) cu citat "art.43 ...:" (dividende
    # 2026 si 2023), Temei(art=78) cu citat "art.64 alin.(1): ..." (impozit_venit). Reparate toate 3 - la
    # impozit_venit pe articolul SPECIFIC consumatorului (salarii: art.78 alin.(2) lit.a), nu pe cel general.
    # MUTATIE: localizatorul lui impozit_venit "art.78 alin.(2) lit.a):" -> "art.64 alin.(1):" -> pica.
    rele = []
    for cale, t in scan_citate._temeiuri():
        arts = _localizator_art(t)
        if arts and t.art and str(t.art) not in arts:
            rele.append("%s: declarat %s, localizatorul citeaza art.%s" % (cale, t, "/".join(arts)))
    assert not rele, "\n".join(rele)


@pytest.mark.parametrize("ops,cc,cod,constanta", [
    ([{"tip": "incasare", "suma": 6000, "partener": "A"}], False, "PLAFON_INCASARE_PJ", "casa.PLAFON_INCASARE_PJ"),
    ([{"tip": "incasare", "suma": 12000, "partener": "A"}], True, "PLAFON_INCASARE_PJ_CC", "casa.PLAFON_INCASARE_PJ_CC"),
    ([{"tip": "plata", "suma": 6000, "partener": "A"}], False, "PLAFON_PLATA_PJ", "casa.PLAFON_PLATA_PJ"),
    ([{"tip": "plata", "suma": 4000, "partener": x} for x in "ABC"], False, "PLAFON_PLATA_PJ_TOTAL",
     "casa.PLAFON_PLATA_PJ_TOTAL"),
    ([{"tip": "plata", "suma": 12000, "partener": "M", "cash_and_carry": True}], False, "PLAFON_PLATA_CC_TOTAL",
     "casa.PLAFON_PLATA_CC_TOTAL"),
    ([{"tip": "incasare", "suma": 12000, "partener": "P", "partener_tip": "pf"}], False, "PLAFON_PF", "casa.PLAFON_PF"),
])
def test_s2_mesajul_de_casa_citeaza_litera_plafonului_aplicat(ops, cc, cod, constanta):
    # La firma cash&carry se aplica lit.b) (10.000), dar mesajul citea lit.a) (nota colaterala din verificare).
    # MUTATIE: cod_inc_pj fortat la "PLAFON_INCASARE_PJ" -> randul cash&carry pica (cod + litera).
    ops = [dict(o, data="2026-06-10") for o in ops]
    pr = [p for p in casa.verifica_plafon(ops, cash_and_carry=cc, la_data=date(2026, 6, 1)) if p["cod"] == cod]
    assert pr, "plafonul %s nu s-a declansat" % cod
    t = common.temei_ancorat(constanta)
    assert Decimal(str(pr[0]["asteptat"])) == common.ancorata(constanta)[0]
    assert re.search(r"art\. %s alin\. \(%s\)" % (re.escape(t.art), t.alin), pr[0]["temei"]), (cod, pr[0]["temei"])
    if t.lit:
        assert re.search(r"lit\. %s\)" % t.lit, pr[0]["temei"]), (cod, pr[0]["temei"], t)


def test_s2_ancoreaza_refuza_doua_surse_si_temei_neobiect():
    # MUTATIE: scoate verificarea `vechi[0] != valoare` -> a doua ancorare cu alta valoare trece -> pica.
    # R1 (10.10.2026): și temeiul fără `data_in` — o intrare de registru care nu spune de când e valabilă nu se selectează după dată.
    # MUTAȚIE: verificarea `data_in is None` scoasă -> ancorarea fără dată trece -> pică.
    nume = "test_s2.__SINTETIC__"
    try:
        assert common.ancoreaza(nume, 1, common.Temei("CF", art="1", data_in="2020-01-01")) == 1
        assert common.COTE[nume] == [(date(2020, 1, 1), 1, common.COTE[nume][0][2])], "ancorarea nu scrie în registru"
        assert common.ancoreaza(nume, 1, common.Temei("CF", art="1", data_in="2020-01-01")) == 1   # aceeași valoare: idempotent
        with pytest.raises(ValueError):
            common.ancoreaza(nume, 2, common.Temei("CF", art="1", data_in="2020-01-01"))
        with pytest.raises(TypeError):
            common.ancoreaza(nume + "2", 1, "CF art.1")
        with pytest.raises(ValueError):
            common.ancoreaza(nume + "3", 1, common.Temei("CF", art="1"))
        assert nume + "3" not in common.COTE
    finally:
        for k in (nume, nume + "2", nume + "3"):
            common.COTE.pop(k, None)


@pytest.mark.parametrize("nume,cheie", [
    ("d101.COTA_STANDARD", "impozit_profit"),
    ("d101g.COTA_STANDARD", "impozit_profit"),
    ("cote_tva.COTA_STANDARD", "tva_standard"),
    ("cote_tva.COTA_REDUSA", "tva_redusa"),
])
def test_s2_geamana_din_registru_nu_diverge(nume, cheie):
    # LIMITA ancorarii (CONFORMITATE interdictia 1): aceste patru constante DUBLEAZA o cheie din COTE - temeiul le-a
    # venit, scrierea in doua locuri a ramas (mutarea in registru = campania interdictiei 1 / R26). Pana atunci,
    # divergenta e imposibila: procentul de modul == valoarea CURENTA a cheii, si ambele pe acelasi articol.
    # MUTATIE: cote_tva.COTA_REDUSA 11 -> 9 -> 9/100 != 0.11 -> pica (citatul ar pica si el: „11%").
    v, t = common.ancorata(nume)
    vc, tc = common.cota(cheie, date(2026, 10, 1))
    assert Decimal(str(v)) / 100 == vc, "%s=%s, dar COTE[%s]=%s" % (nume, v, cheie, vc)
    assert (t.art, t.alin) == (tc.art, tc.alin), "%s pe %s, COTE[%s] pe %s" % (nume, t, cheie, tc)


def test_s2_fiecare_modul_care_ancoreaza_e_in_registru():
    # gardul de mai sus nu are voie să depindă de ordinea în care alte teste importă modulele
    prefixe = {k.split(".", 1)[0] for k in common.ancorate()}
    assert _ANCORATOARE.count("d212") == 1 and set(_ANCORATOARE) <= prefixe, set(_ANCORATOARE) - prefixe
