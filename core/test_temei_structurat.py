# -*- coding: utf-8 -*-
"""Temei fiscal STRUCTURAT (act/nr/an/art/alin/lit/data_in/data_out/url) + garda de EXPIRARE.

DE CE (31.07.2026): temeiul era string liber. Structurat = grep-abil la o schimbare de lege
(gasesti TOATE locurile afectate) + poarta data_out, deci cota() RIDICA la expirare in loc sa
intoarca tacit valoarea veche. Nu exista API legislativ RO fiabil (dovedit): garda de EXPIRARE
(data_out) e mecanismul PRINCIPAL de deriva, nu un proxy. Se comporta ca string peste tot unde
codul vechi asteapta un string (afisare, JSON, operatorul `in`)."""
from datetime import date

import pytest

from core.common import Temei, cota, COTE


def test_temei_se_comporta_ca_string_citare_canonica():
    t = Temei("HG", 146, 2026, data_in="2026-07-01", data_out="2027-07-01",
              url="https://legislatie.just.ro/x", verificat_la="2026-07-31", de_cine="Code")
    assert str(t) == "HG 146/2026"
    assert "HG 146/2026" in ("temei: " + t)     # concatenare (compat calleri vechi)
    assert t in "citat: HG 146/2026 aici"        # operatorul `in` pe string
    assert t.data_in == date(2026, 7, 1)
    assert t.data_out == date(2027, 7, 1)
    assert t.url.endswith("/x") and t.verificat_la == date(2026, 7, 31)


def test_temei_coduri_fara_nr_an():
    assert str(Temei("CF", art="146", alin="5^6")) == "CF art.146 alin.(5^6)"
    assert str(Temei("Legea", 141, 2025)) == "Legea 141/2025"
    assert str(Temei("OUG", 89, 2025, art="III", alin="4", lit="b")) == "OUG 89/2025 art.III alin.(4) lit.b"


def test_cota_cu_data_out_expirat_ridica(monkeypatch):
    """O cota al carei Temei poarta data_out in trecut -> cota() RIDICA dupa data_out, nu
    intoarce tacit valoarea veche. (azi: fara data_out, cota() ar intoarce 5 oricand)."""
    t = Temei("HG", 1, 2020, data_in="2020-01-01", data_out="2020-12-31")
    monkeypatch.setitem(COTE, "_proba_expira", [(date(2020, 1, 1), 5, t)])
    assert cota("_proba_expira", date(2020, 6, 1))[0] == 5      # inainte de data_out: ok
    with pytest.raises(ValueError) as e:
        cota("_proba_expira", date(2021, 6, 1))                 # dupa data_out: RIDICA
    assert "2020-12-31" in str(e.value), "mesajul nu spune data_out expirata"


def test_cota_data_out_None_nu_expira(monkeypatch):
    """data_out=None (inca in vigoare) + fara EXPIRA_DUPA_LUNI -> nu expira."""
    t = Temei("Legea", 227, 2015, data_in="2017-01-01", data_out=None)
    monkeypatch.setitem(COTE, "_proba_fara_out", [(date(2017, 1, 1), 9, t)])
    assert cota("_proba_fara_out", date(2099, 1, 1))[0] == 9


# ── ETAPA 2: temeiuri STRUCTURATE populate pe clusterele verificate ──
def test_clustere_verificate_au_temei_structurat():
    """salariu minim, tichete, TVA, facilitati - temei = Temei (nu string liber), cu actul
    structurat, grep-abil la o schimbare de lege."""
    from datetime import date as _d
    cazuri = [("salariu_minim", _d(2026, 7, 1), "HG", 146),
              ("tichet_masa_plafon", _d(2026, 6, 1), "Legea", 201),
              ("tva_standard", _d(2026, 1, 1), "Legea", 141),
              ("facilitate_salariu_minim", _d(2026, 7, 1), "OUG", 89)]
    for nume, ld, tip, nr in cazuri:
        _, t = cota(nume, ld)
        assert isinstance(t, Temei), "%s: temei nestructurat: %r" % (nume, t)
        assert t.tip == tip and t.nr == nr, "%s: act gresit %s/%s" % (nume, t.tip, t.nr)


def test_salariu_minim_curent_None_istoric_derivat():
    """Modelul de temei 01.08: valoarea CURENTA (4325) are data_out=None (in vigoare); istoricul (4050)
    are data_out DERIVAT = ziua dinaintea succesorului (2026-06-30). Nimic estimat, nimic scris de mana."""
    from datetime import date as _d
    _, t_cur = cota("salariu_minim", _d(2026, 7, 1))
    assert t_cur.data_out is None
    _, t_ist = cota("salariu_minim", _d(2025, 3, 1))
    assert t_ist.data_out == _d(2026, 6, 30)


def test_tva_standard_curent_nu_expira():
    """Corectie 01.08: valoarea CURENTA (data_out=None) NU expira. cota(2035) intoarce valoarea curenta,
    nu ridica - o lege spune de CAND intra, nu pana cand. (Era: data_out estimat + RIDICA.)"""
    from datetime import date as _d
    v, t = cota("tva_standard", _d(2035, 1, 1))
    assert int(v * 100) == 21 and t.data_out is None


def test_salariu_minim_curent_nu_expira_intoarce_valoarea():
    """Corectie 01.08: valoarea curenta a salariului minim (4325, data_out=None) nu expira; cota(2027)
    intoarce 4325 (nu ridica). Riscul rezidual (valoare stale pentru 2027) se acopera prin raportul de
    VECHIME A CONFIRMARII, nu prin blocaj la calcul pe un termen inventat."""
    from datetime import date as _d
    assert int(cota("salariu_minim", _d(2026, 12, 1))[0]) == 4325
    assert int(cota("salariu_minim", _d(2027, 1, 15))[0]) == 4325


def test_url_completat_doar_din_sursa_deschisa():
    """Corpus (1) 07.08: URL pointeaza la SURSA LOCALA din anaf_surse/ (nu link extern just.ro, blocat de pe
    server). Completat DOAR unde fisierul local a fost deschis si verificat verbatim -> nivel_sursa MO;
    restul raman REDARE cu url None (nu se inventeaza - REGULA DE AUR)."""
    from datetime import date as _d
    _, t46 = cota("salariu_minim", _d(2026, 7, 1))
    assert t46.url == "anaf_surse/hg_146_2026_salariu_minim.html" and t46.nivel_sursa == "MO"
    _, t1506 = cota("salariu_minim", _d(2025, 3, 1))
    assert t1506.url == "anaf_surse/hg_1506_2024_salariu_minim.html" and t1506.nivel_sursa == "MO"
    _, ttva = cota("tva_standard", _d(2026, 1, 1))   # =21% @2025-08, legat la Legea 141/2025 (local)
    assert ttva.url == "anaf_surse/legea_141_2025_consolidat.html" and ttva.nivel_sursa == "MO"
    _, ttva19 = cota("tva_standard", _d(2018, 1, 1))  # =19% @2017: adus CF forma initiala 2015 (09.08 tura 7) -> MO
    assert ttva19.url == "anaf_surse/cf_2015_forma_initiala.html" and ttva19.nivel_sursa == "MO"


def test_temei_are_nivel_sursa_text_citat_lant_acte():
    """ETAPA 2 Model de temei: campuri noi pe Temei. nivel_sursa valid; text_citat obligatoriu doar la MO."""
    t = Temei("Legea", 141, 2025, art="291", nivel_sursa="REDARE", lant_acte="X abroga Y")
    assert t.nivel_sursa == "REDARE" and t.text_citat is None and t.lant_acte == "X abroga Y"
    assert "MO" in Temei.NIVELE_SURSA and "REDARE" in Temei.NIVELE_SURSA


def test_cote_au_toate_nivel_sursa():
    """Fiecare Temei din COTE poarta nivel_sursa (gri-ul in structura, nu in comentariu)."""
    for nume, intrari in COTE.items():
        for din, val, t in intrari:
            assert getattr(t, "nivel_sursa", None) in Temei.NIVELE_SURSA, "%s@%s fara nivel_sursa" % (nume, din)
            if t.nivel_sursa == "MO":
                assert t.text_citat, "%s@%s: MO fara text_citat verbatim" % (nume, din)
