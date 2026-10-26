# -*- coding: utf-8 -*-
"""[lotul 13, comanda Costin 13.1] Importurile de migrare — verificările pe rânduri (funcții PURE, fără bază), deficiențele:

  * 582 „Verificarea dublurilor oprește tot înainte de celelalte verificări; restul greșelilor apar abia la reîncărcare.” (Solduri parteneri)
  * 583 „Sus «4 parteneri · debit 1.700», în casetă «Fișierul nou: 0 parteneri, debit 0,00»: trebuie «0 rânduri valide din 4».”
  * 585 „3.000 lei brut la normă întreagă (sub minimul de 4.050) intră fără semnal.” (Salariați)
  * 586 „D100 cu luna 02 intră fără să spună cum a fost citit (lunar, ex. impozit pe dividende, vs trimestrial).” (Istoric declarații)
  * 587 „o valoare reziduală mare (2/3 din valoare) nu e semnalată” (Mijloace fixe)
  * 588 „Bun de 1.800 lei «sub plafonul de mijloc fix de 5.000 lei» intră totuși ca mijloc fix; trebuie propus obiect de inventar.”
  * 590 „La articol dublat, primul rând intră cu 10 buc (stocul real 13); trebuie respinse ambele până la cumulare, ca la parteneri.”
  * 666 „mesajul pentru 401 se repetă identic pe fiecare rând” (Solduri parteneri)
  * 668 „Fișele (3 articole, 4.100 lei) față de 371 din balanță (4.200) […] Aceeași regulă ca la parteneri: contul care nu se potrivește
    nu intră.” + „observația «607 dedus din 371» repetată pe fiecare rând (clasa 666)”
  * 252 (decizia Costin 13.1): „la facturile preluate, dacă fișierul are suma TVA, se ia suma din fișier; doar unde lipsește se calculează
    la cota standard, iar factura e marcată «de verificat».”
  * 609 „Soldurile creditoare și diferențele apar cu minus («401: −9.520,00»), nu ca sold C.” (Audit de preluare)

TEMEIURILE, citate pe linia aserției: Codul muncii (Legea 53/2003) art.164 alin.(6) și HG 146/2026 art.1 (585); CF art.43 alin.(2) (586);
CF art.28 alin.(2) lit.b) în forma OUG 8/2026 art.6 pct.7, aplicat din 2026 (OUG 8/2026 art.10 alin.(2)), HG 276/2013 (2.500 lei înainte) și
CF art.45 alin.(21^3) (588); OMFP 1802/2014 pct.139 alin.(2) (587). Restul: N/A — reguli de produs (comanda 13.1).
CUI-urile: cifra de control verificată (CLAUDE.md §10).
"""
import datetime as _dt
from decimal import Decimal

import pytest

from core import (articole_import_api as aa, audit_preluare as ap, istoric_declaratii_import_api as ii, migrare_api,
                  mijloace_fixe_import_api as mf, salariati_import_api as si, solduri_parteneri_api as sp)

ALFA, BETA = "401007106", "401007203"


def _cui_valid(c):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = sum(int(corp[i]) * ch[i] for i in range(9)) * 10 % 11
    return (0 if r == 10 else r) == ctrl


assert _cui_valid(ALFA) and _cui_valid(BETA)


# ── 582: dublurile nu mai opresc citirea; toate aparițiile se resping, iar celelalte verificări rulează ────────────────────────────
FISIER_582 = ("cont;cui;denumire;sold debitor;sold creditor\n"
              "4111;%s;Client Alfa;500;0\n"
              "4111;%s;Client Alfa;300;0\n"
              "4111;14837429;Client CUI greșit;200;0\n"
              "4111;%s;Client Beta;700;0\n" % (ALFA, ALFA, BETA)).encode("utf-8")


def test_582_dublura_nu_opreste_citirea_si_respinge_ambele_randuri_iar_cui_ul_gresit_se_vede_deodata():
    randuri = sp.extrage(FISIER_582, "parteneri.csv")            # înainte: FisierNecitit la prima dublură, nimic altceva verificat
    assert len(randuri) == 4
    erori, bune = sp.verifica_randuri(randuri)
    pe_rand = {e["rand"]: e["regula"] for e in erori}
    assert pe_rand == {2: "partener_dublat", 3: "partener_dublat", 4: "cui_invalid"}, pe_rand
    assert [r["denumire"] for r in bune] == ["Client Beta"]
    assert "apare pe același cont 4111 și pe rândul 3" in next(e["mesaj"] for e in erori if e["rand"] == 2)


# ── 583: textul înlocuirii spune câte rânduri intră din câte s-au citit ─────────────────────────────────────────────────────────
def test_583_fisierul_nou_spune_zero_randuri_valide_din_cate_s_au_citit():
    intra = migrare_api.randuri_care_intra([{"rand_fisier": n} for n in (2, 3, 4, 5)], [{"rand": n} for n in (2, 3, 4, 5)])
    assert intra == [] and intra.citite == 4
    nou = sp.totaluri(intra)
    vechi = {"randuri": 2, "total_debit": 2500.0, "total_credit": 0.0, "data_referinta": "2026-09-30", "documente": 2, "legate": []}
    t = sp.text_inlocuire(vechi, nou)
    assert "Fișierul nou: 0 rânduri valide din 4 — nu intră nimic." in t, t
    assert migrare_api.text_fisier_nou("3 parteneri", 3, 4) == "3 parteneri (3 rânduri valide din 4)"
    assert migrare_api.text_fisier_nou("4 parteneri", 4, 4) == "4 parteneri"


# ── 666: pe rând, motivul scurt al contului nepotrivit; cifrele lui o singură dată ─────────────────────────────────────────────
def test_666_contul_potrivit_nu_e_respins_iar_mesajul_nepotrivitului_are_cifrele():
    coer = [{"cont": "401", "suma_parteneri": -1000.0, "sold_balanta": -3000.0, "diferenta": 2000.0, "coincide": False,
             "sursa": "balanța de deschidere", "data": "2026-09-30"},
            {"cont": "4111", "suma_parteneri": 2500.0, "sold_balanta": 2500.0, "diferenta": 0.0, "coincide": True,
             "sursa": "balanța de deschidere", "data": "2026-09-30"}]
    randuri = [{"cont": "401", "rand_fisier": 3}, {"cont": "401", "rand_fisier": 4}, {"cont": "4111", "rand_fisier": 5}]
    er = sp.respinse_coerenta(randuri, coer)
    assert [e["rand"] for e in er] == [3, 4]                     # 4111 se potrivește: niciun refuz
    assert {e["mesaj"] for e in er} == {"pe 401, partenerii din fișier dau creditor 1.000,00 lei, iar balanța de deschidere la 30.09.2026 "
                                        "are creditor 3.000,00 lei (diferență 2.000,00 lei) — rândurile contului nu intră până nu se potrivesc"}


# ── 252: suma TVA din fișier; lipsă -> calculată la cota standard și marcată „de verificat” ─────────────────────────────────────
FISIER_252 = ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată;TVA la încasare;TVA\n"
              "4111;RO%s;Client Alfa;FA-1;10.09.2026;;1210,00;da;210,00\n"
              "4111;RO%s;Client Beta;FB-1;12.09.2026;;1090,00;da;90,00\n"
              "4111;RO%s;Client Beta;FB-2;15.09.2026;;1210,00;da;\n" % (ALFA, BETA, BETA)).encode("utf-8")


def test_252_tva_din_fisier_se_ia_ca_atare_iar_lipsa_se_calculeaza_si_se_marcheaza():
    randuri = sp.extrage(FISIER_252, "situatie.csv")
    docs = sp.documente_din_randuri(randuri, "2026-09-30")[0]
    pe = {d["numar"]: d for d in docs}
    assert pe["FA-1"]["tva_fisier"] == Decimal("210.00") and pe["FB-1"]["tva_fisier"] == Decimal("90.00")   # cota redusă 9%: 90 din 1.090
    assert pe["FB-2"]["tva_fisier"] is None


class _Cur:
    """Cursorul minim al lui `cu_regimul_tva`: firma plătitoare de TVA; perioada TVA la încasare citită de `regim_tva_incasare`."""
    def __init__(self):
        self._r = None

    def execute(self, sql, params=None):
        self._r = (True,)

    def fetchone(self):
        return self._r


def test_252_cu_regimul_tva_ia_suma_din_fisier_si_marcheaza_numai_calculata(monkeypatch):
    from core import regim_tva_incasare as _rg
    monkeypatch.setattr(_rg, "aplica_la", lambda cur, zi: True)
    docs = sp.documente_din_randuri(sp.extrage(FISIER_252, "situatie.csv"), "2026-09-30")[0]
    sp.cu_regimul_tva(_Cur(), docs)
    pe = {d["numar"]: d for d in docs}
    assert (pe["FA-1"]["tva"], pe["FA-1"]["tva_de_verificat"]) == (Decimal("210.00"), False)
    assert (pe["FB-1"]["tva"], pe["FB-1"]["tva_de_verificat"]) == (Decimal("90.00"), False)   # suma din fișier, nu 21% din 1.090
    # CF art.291 alin.(1): cota standard 21% la 15.09.2026; din total: 1.210 × 21/121 = 210,00 — calculată, deci de verificat
    assert (pe["FB-2"]["tva"], pe["FB-2"]["tva_de_verificat"]) == (Decimal("210.00"), True)
    assert sp.rezumat_documente(docs)["tva_de_verificat"] == ["FB-2 (Client Beta)"]


def test_252_suma_tva_peste_restul_facturii_opreste_citirea():
    rau = FISIER_252.decode("utf-8").replace(";1210,00;da;210,00", ";1210,00;da;2100,00").encode("utf-8")
    with pytest.raises(sp._it.FisierNecitit) as e:   # refuzul de citire a fișierului (nu orice excepție)
        sp.extrage(rau, "situatie.csv")
    unde, motiv = e.value.args[0].split(": ", 1)   # „Rândul N (partener, factura): <motiv>”
    assert unde.startswith("Rândul ") and motiv.startswith(
        "suma TVA 2.100,00 lei nu poate fi mai mare decât restul facturii (1.210,00 lei)"), e.value.args


# ── 590 + 668: articolele ─────────────────────────────────────────────────────────────────────────────────────────────────────
def _art(nr, den, cant, pret, cont="371", dedus=True):
    return {"rand_fisier": nr, "denumire": den, "um": "buc", "cantitate": cant, "cantitate_brut": str(cant), "pret": pret,
            "pret_brut": str(pret), "cont_stoc": cont, "cont_cheltuiala": "607", "cont_cheltuiala_dedus": dedus}


def test_590_articolul_dublat_respinge_toate_aparitiile():
    er = aa.verifica_randuri([_art(2, "Marfa valida", 10, 5), _art(3, "marfa  VALIDA", 3, 5), _art(4, "Alta marfa", 1, 5)])
    assert sorted((e["rand"], e["regula"]) for e in er) == [(2, "articol_dublat"), (3, "articol_dublat")]


def test_668_contul_de_stoc_nepotrivit_cu_balanta_nu_intra_iar_cel_potrivit_intra():
    f7 = [_art(2, "Marfa X Test", 10, 150), _art(3, "Marfa Y Test", 20, 80), _art(4, "Marfa Z Test", 5, 200),
          _art(5, "Materie prima", 10, 30, cont="301")]
    solduri = {"371": (Decimal("4200"), Decimal("0")), "301": (Decimal("300"), Decimal("0"))}
    er = aa.verifica_randuri(f7, solduri)
    assert sorted(e["rand"] for e in er) == [2, 3, 4]
    assert {e["regula"] for e in er} == {"stoc_nu_da_soldul"}
    assert er[0]["mesaj"] == ("nu intră: articolele de pe contul 371 dau 4.100,00 lei, iar balanța de deschidere are 4.200,00 lei "
                              "(diferență 100,00 lei)")
    assert aa.verifica_randuri(f7, None) == []                  # fără balanță: nimic de confruntat


def test_668_previzualizarea_eticheteaza_intai_iar_confruntarea_tot_numara_randurile_contului():
    """[e2e pe arborele integrat 526f12af: „371: stoc inițial 0,00 lei · … lipsesc 4.200,00 lei”] ruta previzualizării cheamă întâi
    `eticheteaza` (rândurile contului nepotrivit primesc `stare = respins`), apoi `verifica_randuri` și `reconciliere_balanta` — cifrele
    contului rămân ale fișierului (4.100), nu 0; un rând respins pentru alt motiv (dublura) iese din sumă. MUTAȚIE: reconcilierea scoate
    iar orice rând `respins` -> 0,00 -> pică."""
    f7 = [_art(2, "Marfa X Test", 10, 150), _art(3, "Marfa Y Test", 20, 80), _art(4, "Marfa Z Test", 5, 200)]
    solduri = {"371": (Decimal("4200"), Decimal("0"))}
    aa.eticheteaza(f7, solduri)
    assert [r["stare"] for r in f7] == ["respins"] * 3
    assert aa.reconciliere_balanta(f7, solduri) == [{"cont": "371", "registru": 4100.0, "balanta": 4200.0, "diferenta": -100.0}]
    assert aa.verifica_randuri(f7, solduri)[0]["mesaj"] == (
        "nu intră: articolele de pe contul 371 dau 4.100,00 lei, iar balanța de deschidere are 4.200,00 lei (diferență 100,00 lei)")
    # un rând respins pentru alt motiv (dublura, 590: ambele apariții) nu intră în suma contului: rămâne numai Marfa Y (1.600)
    dublat = [_art(2, "Marfa X Test", 10, 150), _art(3, "Marfa X Test", 10, 150), _art(4, "Marfa Y Test", 20, 80)]
    aa.eticheteaza(dublat, solduri)
    assert aa.reconciliere_balanta(dublat, solduri)[0]["registru"] == 1600.0


def test_668_contul_de_cheltuiala_dedus_se_spune_o_singura_data():
    sem = aa.semnale_randuri([_art(2, "A", 1, 1), _art(3, "B", 1, 1), _art(4, "C", 1, 1)])
    assert len(sem) == 1 and sem[0]["rand"] == 2
    # nu pe egalitatea textului întreg (garda mesajelor afișabile): perechea de conturi la început, rândurile o singură dată, la sfârșit
    m = sem[0]["mesaj"]
    assert m.startswith("contul de cheltuială 607 e dedus din contul de stoc 371") and m.endswith("pe 3 rânduri: 2, 3, 4") \
        and m.count("2, 3, 4") == 1, m


# ── 585: salariul sub minim ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_585_brutul_sub_minim_la_norma_intreaga_se_semnaleaza():
    r = {"rand_fisier": 2, "nume": "POPESCU", "prenume": "ANA", "salariu_brut": 3000, "tip_norma": "intreaga", "cor": "251401"}
    # Codul muncii art.164 alin.(6) + HG 146/2026 art.1: „4.325 lei lunar” de la 01.07.2026
    assert si.sub_minim(r, _dt.date(2026, 10, 25)) == ("3.000,00 lei", "4.325,00 lei", " la normă întreagă")
    # HG 1506/2024 art.1: 4.050 lei de la 01.01.2025 — minimul se ia la data cerută
    assert si.sub_minim(r, _dt.date(2026, 3, 1))[1] == "4.050,00 lei"
    assert si.sub_minim(dict(r, tip_norma="partiala", ore_zi=4), _dt.date(2026, 10, 25)) is None   # 3.000 >= 4.325 × 4/8 = 2.162,50
    assert si.sub_minim(dict(r, salariu_brut=5000), _dt.date(2026, 10, 25)) is None
    sem = [s for s in si.semnale_randuri([r]) if s["regula"] == "salariu_sub_minim"]
    assert len(sem) == 1 and "sub salariul minim brut" in sem[0]["mesaj"]


# ── 586: D100 lunară ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_586_d100_pe_luna_02_e_citita_ca_lunara_si_se_spune():
    sem = ii.semnale_randuri([{"rand_fisier": 2, "tip": "D100", "an": 2026, "luna": 2, "data_depunere": "2026-03-20", "suma": 160}],
                             _dt.date(2026, 10, 25))
    d = [s for s in sem if s["regula"] == "d100_lunara"]
    # CF art.43 alin.(2): impozitul pe dividende se declară „până la data de 25 inclusiv a lunii următoare celei în care se plătește”
    assert len(d) == 1 and "luna 02 nu încheie un trimestru — rândul e citit ca D100 lunară" in d[0]["mesaj"]
    assert "scrie luna de sfârșit a trimestrului (03 = T1)" in d[0]["mesaj"]
    sem3 = ii.semnale_randuri([{"rand_fisier": 2, "tip": "D100", "an": 2026, "luna": 3, "data_depunere": "2026-04-20", "suma": 1}],
                              _dt.date(2026, 10, 25))
    assert not [s for s in sem3 if s["regula"] == "d100_lunara"]


# ── 587 + 588: mijloacele fixe ───────────────────────────────────────────────────────────────────────────────────────────────
def _mf(nr, val, pif, rez=0.0, cont="2131"):
    return {"rand_fisier": nr, "cod": "MF%d" % nr, "denumire": "Bun %d" % nr, "valoare": val, "rezidual": rez, "dnf_luni": 36,
            "data_pif": pif, "metoda": "liniara", "cont_imobilizare": cont, "cont_amortizare": "2813", "amortizat_preluat": None}


def test_588_sub_plafonul_la_data_intrarii_nu_intra_ca_mijloc_fix():
    er = mf.verifica_randuri([_mf(2, 1800, "2026-03-10"), _mf(3, 3000, "2025-06-01"), _mf(4, 1800, "2025-06-01"), _mf(5, 6000, "2026-03-10")],
                             _dt.date(2026, 10, 25))
    sub = {e["rand"]: e["mesaj"] for e in er if e["regula"] == "sub_plafon_mf"}
    # CF art.28 alin.(2) lit.b) (OUG 8/2026 art.6 pct.7, din 2026): 5.000 lei; HG 276/2013: 2.500 lei înainte; CF art.45 alin.(21^3): cele
    # între 2.500 și 5.000 intrate până la 31.12.2025 rămân mijloace fixe
    assert set(sub) == {2, 4}, sub
    assert sub[2] == ("Bun 2: valoarea de intrare 1.800,00 lei e sub plafonul de mijloc fix de 5.000,00 lei la data intrării 10.03.2026 "
                      "(CF art.28 alin.(2) lit.b)) — e obiect de inventar, nu mijloc fix amortizabil: nu intră în registrul mijloacelor fixe")
    assert "2.500,00 lei la data intrării 01.06.2025" in sub[4]


def test_587_valoarea_reziduala_se_semnaleaza_cu_partea_din_valoare():
    csv = ("cod;denumire;valoare intrare;data PIF;durata luni;metoda;cont imobilizare;cont amortizare;amortizare cumulata;"
           "valoare reziduala la sfarsitul duratei (de obicei 0)\n"
           "MF1;Utilaj;9000;2025-01-10;60;liniara;2131;2813;1500;6000\n").encode("utf-8")
    r = mf.extrage(csv, "mf.csv", _dt.date(2026, 9, 30))[0]
    assert r["rezidual"] == 6000.0
    # OMFP 1802/2014 pct.139 alin.(2): valoarea amortizabilă = costul minus valoarea reziduală -> 6.000 nu se amortizează (67% din 9.000)
    assert any("valoarea reziduală 6.000,00 lei (67% din valoarea de intrare) nu se amortizează" in m for m in r["motive"]), r["motive"]


# ── 609: auditul fără minus ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_609_soldul_si_diferenta_fara_minus():
    assert ap.sold_pe_natura(Decimal("6000"), "creditor") == "creditor 6.000,00 lei"
    assert ap.sold_pe_natura(Decimal("-500"), "debitor") == "creditor 500,00 lei"
    assert ap.text_diferenta("în registru", Decimal("-24000")) == "în registru lipsesc 24.000,00 lei față de balanță"
    assert ap.text_diferenta("în stocul inițial", Decimal("100")) == "în stocul inițial sunt cu 100,00 lei mai mult decât în balanță"
