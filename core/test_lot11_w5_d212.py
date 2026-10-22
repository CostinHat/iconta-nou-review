# -*- coding: utf-8 -*-
"""[lotul 11, subagentul w5, deficiența 440 — comanda Costin 11.1 pct.16, verbatim] „toate erorile apar deodată, fiecare cu textul ei”.
D212, în INTERIORUL secțiunilor: W3b a adunat refuzurile ÎNTRE secțiuni (`genereaza`) și în `cap12_norma`; `cap11_categorie` (venitul
din I.1.1) și `cap14_sectiune` (venitul din străinătate) se opreau încă la PRIMA greșeală a secțiunii — contabilul corecta un câmp,
genera din nou, afla de următorul. Acum toate refuzurile independente ale secțiunii pleacă împreună (`d212.RefuzuriSectiune`), iar
`genereaza` le numerotează pe fiecare, cu secțiunea în față.

Temei: N/A — momentul refuzului. Regulile (OPANAF 2736/2025, CF) rămân în `cap11_categorie` / `cap14_sectiune`, neschimbate; testul
nu le reafirmă. Echivalența cu forma veche e probată diferențial (raportul w5): 80.000 de secțiuni aleatoare, aceeași secțiune calculată
pe datele bune, iar refuzul vechi se regăsește printre motivele noi pe datele greșite.
"""
import pytest

from core import d212
from core.common import Perioada

CNP_BUN = "1800101221144"   # verificat cu algoritmul oficial (CLAUDE.md „Date de test”); același ca în core/test_d212_cap12.py
AN = 2025


def test_cnp_de_proba_verificat():
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(CNP_BUN[i]) * ch[i] for i in range(12)) % 11
    assert str(1 if c == 10 else c) == CNP_BUN[12]


def _motive(fn, a):
    with pytest.raises(d212.RefuzuriSectiune) as e:
        fn(a, AN)
    return e.value.motive


#: Cedarea folosinței cu cinci greșeli independente: zile scutite (nu se aplică), data începerii (nu e o dată), data încetării (alt an),
#: pierderi reportate (nu există la cote forfetare), cheltuieli date (le stabilește cota).
CEDARE_GRESITA = {"categ_venit": 1015, "venit_brut": 12000, "chelt_deduc": 100, "pierdere_precedenta": 50, "nr_zile_scutite": 10,
                  "data_incep": "31/02/2025", "data_sf": "2026-02-01"}


def test_cap11_toate_greselile_sectiunii_deodata():
    """MUTAȚIE: un `motive.append` al secțiunii înlocuit cu `raise ValueError` pe loc (forma veche) -> numai primul motiv -> pică."""
    m = _motive(d212.cap11_categorie, dict(CEDARE_GRESITA))
    assert len(m) == 5, m                                                    # 440: toate deodată
    asteptate = ["zilele scutite nu se aplică", "data începerii '31/02/2025' nu e o dată", "data încetării (2026-02-01) nu e în anul",
                 "la cote forfetare nu se reportează pierderi", "la cote forfetare cheltuielile se calculează din venitul brut"]
    for t, x in zip(asteptate, m):
        assert t in x and x.startswith("D212 3. Cedarea folosinței"), (t, x)   # fiecare cu textul lui și secțiunea în față


def test_cap14_toate_greselile_sectiunii_deodata():
    """Pensia din străinătate cu șase greșeli independente. MUTAȚIE: `motive.append` al țării înlocuit cu `raise` -> pică."""
    m = _motive(d212.cap14_sectiune, {"categ_venit": 2020, "tara": "XX", "dubla_impunere": 3, "venit_brut": 40000,
                                      "chelt_deduc": 100, "nr_luni": 0, "pierdere_precedenta": 50, "impozit_platit": "abc"})
    asteptate = ["țara 'XX' nu e în nomenclatorul ANAF", "metoda 3 —", "impozitul plătit în străinătate 'abc' nu e o sumă în lei",
                 "suma neimpozabilă se calculează", "numărul lunilor cu pensie în an (1-12) e obligatoriu",
                 "pierderile se reportează doar la activități în sistem real"]
    assert len(m) == len(asteptate), m                                       # 440: toate deodată
    for t, x in zip(asteptate, m):
        assert t in x, (t, x)


def test_cap14_jocuri_felul_si_data_platii_impreuna():
    """Felul jocului și data plății sunt rubrici independente: amândouă în refuz (până acum numai felul)."""
    m = _motive(d212.cap14_sectiune, {"categ_venit": 2013, "tara": "DE", "venit_brut": 5000, "tip_joc": "x"})
    # lista motivelor, fiecare întreg pe poziția lui (core/test_garzi_pe_text.py: câmpul are valoarea asta, nu „fragmentul apare”)
    assert m == ["D212 străinătate Jocuri de noroc: alege felul jocului — cazinouri, poker, slot-machine, lozuri (art.110 alin.(2^2)) / "
                 "alte jocuri de noroc.",
                 "D212 străinătate Jocuri de noroc: data plății (în anul 2025) e obligatorie — baremul depinde de ea (CF art.110 alin.(2): "
                 "forma OG 16/2022 până la 31.07.2025, forma Legea 141/2025 de la 01.08.2025)."], m


def test_refuzul_dependent_asteapta_premisa():
    """Docstringul `cap11_categorie` / `cap14_sectiune`: la DPI ramura (forfetar / real) o alege determinarea venitului net; cât timp ea
    e invalidă, „cheltuielile la cote forfetare” nu se judecă (nu se dublează motivul). MUTAȚIE: garda `det_ok` scoasă -> două motive."""
    a = {"categ_venit": 1003, "det_ven_net": 3, "venit_brut": 1000, "chelt_deduc": 100}
    with pytest.raises(ValueError) as e:
        d212.cap11_categorie(dict(a), AN)
    m = e.value.motive   # lista motivelor (câmpul refuzului), nu reprezentarea excepției
    assert m == [str(e.value)] == ["D212 2. Drepturi de proprietate intelectuală: determinarea venitului net 3 — 1 sistem real, "
                                   "2 cote forfetare."], m   # un singur motiv
    with pytest.raises(ValueError) as e:   # aceeași regulă la DPI din străinătate (până la 22.10.2026 det=3 trecea tăcut drept sistem real)
        d212.cap14_sectiune({"categ_venit": 2003, "tara": "DE", "det_ven_net": 3, "venit_brut": 1000, "chelt_deduc": 100}, AN)
    m = e.value.args[0]   # mesajul refuzului (câmpul lui)
    assert m == ("D212 străinătate Drepturi de proprietate intelectuală: determinarea venitului net 3 — 1 sistem real, 2 cote "
                 "forfetare."), e.value.args


def test_text_nenumeric_e_refuz_nu_exceptie_bruta():
    """O sumă care nu e număr ieșea ca `decimal.InvalidOperation` (nu `ValueError`: trecea de `genereaza` ca eroare brută), un număr de
    zile ca „invalid literal for int()”. Acum: refuz numit, alături de celelalte."""
    m = _motive(d212.cap11_categorie, {"categ_venit": 1009, "venit_brut": "abc", "nr_zile_scutite": "doua", "forma_org": 9})
    assert m == ["D212 5. Activități agricole: venitul brut 'abc' nu e o sumă în lei.",
                 "D212 5. Activități agricole: zilele scutite 'doua' nu e un număr întreg.",
                 "D212 5. Activități agricole: forma de organizare 9 — 1 individual, 2 asociere."], m
    m = _motive(d212.cap12_norma, {"norma": "x", "zile_intrerupere": "y", "data_doc_autoriz": "32.13.2025"})
    # m[1] numește rubrica („data documentului”), nu cheia internă `data_doc_autoriz`: egalitatea întreagă o cere
    assert m == ["D212 normă: norma anuală de venit (rd.7) 'x' nu e o sumă în lei.",
                 "D212 normă: data documentului '32.13.2025' nu e o dată (AAAA-LL-ZZ).",
                 "D212 normă: zilele de întrerupere 'y' nu e un număr întreg."], m


def test_genereaza_numeroteaza_fiecare_motiv_din_sectiune():
    """Capăt la capăt în `genereaza`: venitul 1 (cinci motive) și venitul din străinătate 1 (două motive) -> șapte rânduri, fiecare cu
    secțiunea lui. MUTAȚIE: `refuzuri.extend(...)` din bucla veniturilor înapoi la `refuzuri.append("Venitul %d — %s" % (i, e))` ->
    un singur rând pentru venitul 1 -> pică."""
    with pytest.raises(ValueError) as e:
        d212.genereaza(None, None, Perioada(an=AN), {"cif": CNP_BUN, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1",
                                                     "venituri": [dict(CEDARE_GRESITA)],
                                                     "strainatate": [{"categ_venit": 2013, "tara": "DE", "venit_brut": 5000}]})
    m = str(e.value)
    assert m.startswith("D212 nu se poate genera — 7 motive; rezolvă-le pe toate, apoi generează din nou.\n"), m
    randuri = m.split("\n")[1:]
    assert [r.split(" — ")[0] for r in randuri] == ["%d. Venitul 1" % i for i in range(1, 6)] + \
        ["6. Venitul din străinătate 1", "7. Venitul din străinătate 1"], m


def test_un_singur_motiv_ramane_fraza_lui():
    """Contractul de până acum: o singură greșeală -> fraza ei, fără numerotare (`core/test_d212_categorii.py`)."""
    with pytest.raises(ValueError) as e:
        d212.cap11_categorie({"categ_venit": 1015, "venit_brut": 1000, "chelt_deduc": 5}, AN)
    assert str(e.value) == ("D212 3. Cedarea folosinței bunurilor (altele decât cele de la pct.4): la cote forfetare cheltuielile se "
                            "calculează din venitul brut; câmpul se lasă gol.")


def test_sectiunile_bune_se_calculeaza_ca_inainte():
    """Pe date bune secțiunea iese neschimbată (cifrele le apără testele `core/test_d212_categorii.py` / `test_d212_cap14.py`, pe DUK);
    aici, numai că strângerea refuzurilor n-a oprit calculul: cedare 12.000 -> 20% cheltuieli forfetare (OPANAF 2736/2025 pct.5.6.6)."""
    c = d212.cap11_categorie({"categ_venit": 1015, "venit_brut": 12000}, AN)
    assert c["chelt_deduc"] == 2400 and c["venit_net_anual"] == 9600, c      # CF art.84 alin.(3): cota forfetară 20%
    s = d212.cap14_sectiune({"categ_venit": 2013, "tara": "DE", "venit_brut": 5000, "tip_joc": "altele", "data_plata": "2025-09-01"}, AN)
    assert s["str_impozit_datorat_Ro"] == 200, s                             # CF art.110 alin.(2), forma Legea 141/2025: 4% până la 10.000


# ── generalizarea: aceeași clasă în celelalte secțiuni D212 ────────────────────────────────────────────────────────────────────
def test_venitul_din_registru_ambele_refuzuri_deodata():
    """`cap11_sistem_real` (venitul din registrul RIP): pierderea reportată negativă și zilele scutite 400 — două motive (până acum
    numai primul). MUTAȚIE: `motive.append` al zilelor -> `raise ValueError` pe loc -> pică."""
    with pytest.raises(d212.RefuzuriSectiune) as e:
        d212.cap11_sistem_real(10000, 2000, -5, None, 400)
    assert e.value.motive == ["Venitul brut, cheltuielile și pierderea reportată nu pot fi negative.",
                              "Zilele scutite trebuie să fie între 0 și numărul de zile ale anului."], e.value.motive


def test_genereaza_venitul_din_registru_si_cass_cu_celelalte(monkeypatch):
    """Venitul din registru (refuzat), veniturile pentru CASS 2.2 negative și un venit I.1.1 greșit: toate în același refuz. Până la
    22.10.2026 refuzul registrului oprea generarea înaintea celorlalte secțiuni, iar cel al CASS 2.2 apărea abia după ce toate secțiunile
    treceau. Registrul e înlocuit (`cap11_din_rip`, fără bază): testul privește colectarea, nu fișa. MUTAȚIE: `try/except` din jurul
    `cap11_din_rip` scos -> numai motivele registrului -> pică."""
    monkeypatch.setattr(d212, "cap11_din_rip", lambda conn, schema, an, pp, caen, scut: (d212.cap11_sistem_real(1000, 0, pp, caen, scut),
                                                                                          None))
    with pytest.raises(ValueError) as e:
        d212.genereaza(object(), "s", Perioada(an=AN), {
            "cif": CNP_BUN, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti", "din_rip": True, "pierdere_precedenta": -1,
            "nr_zile_scutite_rip": 400, "alte_cass": {"asociere_pj": -10},
            "venituri": [{"categ_venit": 1015, "venit_brut": 1000, "chelt_deduc": 5}]})
    randuri = str(e.value).split("\n")
    assert randuri[0].startswith("D212 nu se poate genera — 4 motive"), str(e.value)
    assert [r.split(" — ")[0] for r in randuri[1:]] == ["1. Venitul din registrul RIP", "2. Venitul din registrul RIP",
                                                        "3. D212: veniturile pentru CASS și CASS reținută nu pot fi negative.",
                                                        "4. Venitul 1"], str(e.value)


def test_cass_22_refuzul_e_un_singur_loc():
    """Refuzul sumelor negative pentru CASS 2.2 trăiește într-un singur loc (`_alte_cass_refuz`): `oblig_realizat` îl ridică la fel."""
    with pytest.raises(ValueError, match="nu pot fi negative"):
        d212.oblig_realizat([], [], AN, alte_cass={"cass_retinuta": -1})
    assert d212._alte_cass_refuz({"dividende_dobanzi": "abc"}).endswith("se scriu în lei, ca numere.")
    assert d212._alte_cass_refuz({"asociere_pj": 5}) is None
