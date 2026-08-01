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
              url="https://legislatie.just.ro/x", estimat=True)
    assert str(t) == "HG 146/2026"
    assert "HG 146/2026" in ("temei: " + t)     # concatenare (compat calleri vechi)
    assert t in "citat: HG 146/2026 aici"        # operatorul `in` pe string
    assert t.data_in == date(2026, 7, 1)
    assert t.data_out == date(2027, 7, 1)
    assert t.estimat is True and t.url.endswith("/x")


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


def test_salariu_minim_data_out_estimat():
    """HG 146/2026 nu spune explicit pana cand -> data_out = sfarsit perioada rezonabila (anual),
    marcat ESTIMAT (regula data_out)."""
    from datetime import date as _d
    _, t = cota("salariu_minim", _d(2026, 7, 1))
    assert t.data_out == _d(2026, 12, 31) and t.estimat is True


def test_tva_standard_are_data_out_estimat_si_expira():
    """Regula 01.08 (ciclul>ratchet): nicio cota nu ramane fara termen. TVA n-are termen LEGAL, deci
    primeste data_out ESTIMAT (re-verificare anuala); cota() RIDICA dupa el - garda nu tace la infinit."""
    import pytest
    from datetime import date as _d
    _, t = cota("tva_standard", _d(2026, 1, 1))
    assert t.data_out is not None and t.estimat
    with pytest.raises(ValueError):
        cota("tva_standard", _d(2035, 1, 1))


def test_salariu_minim_expira_la_1_ianuarie_2027():
    """Salariul minim are cadenta ISTORICA semestriala/anuala (4050 de la 1 ian 2025, 4325 de la
    1 iul 2026). Daca majorarea vine la 1 ian 2027, un proxy de 12 luni (data_out 2027-07-01) ar
    tacea 6 luni si ar calcula cu o valoare moarta - exact ce s-a intamplat cu 3700. data_out
    scurt deliberat (2026-12-31): mai bine eroare devreme decat cifra gresita tacut."""
    from datetime import date as _d
    assert cota("salariu_minim", _d(2026, 12, 1))[0] == 4325     # inca in S2 2026: ok
    with pytest.raises(ValueError) as e:
        cota("salariu_minim", _d(2027, 1, 15))                   # 2027: RIDICA, nu intoarce 4325
    assert "2026-12-31" in str(e.value)


def test_url_completat_doar_din_sursa_deschisa():
    """URL just.ro completat DOAR unde sursa a fost efectiv deschisa in sesiune (HG 146/2026,
    HG 1506/2024). Restul raman None - nu se inventeaza (REGULA DE AUR)."""
    from datetime import date as _d
    _, t46 = cota("salariu_minim", _d(2026, 7, 1))
    assert t46.url and "308231" in t46.url and "just.ro" in t46.url
    _, t1506 = cota("salariu_minim", _d(2025, 3, 1))
    assert t1506.url and "291450" in t1506.url
    _, ttva = cota("tva_standard", _d(2026, 1, 1))
    assert ttva.url is None   # neverificat -> None, nu inventat
