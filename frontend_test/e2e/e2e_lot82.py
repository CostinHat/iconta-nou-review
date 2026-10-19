# -*- coding: utf-8 -*-
"""Lotul 8, comanda 8.2 (Costin 18.10.2026, verbatim în DECIZII „Comanda 8.2”): deficiențele 341–381 din retestul lotului 8.1 — pașii
contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`). Fișierele sunt inventate; CNP-urile și CUI-urile
au cifra de control verificată (algoritmul din CLAUDE.md). Regula de clasă a importurilor (pct.4) are garda ei fără browser:
`core/test_regula_importurilor.py`; aici sunt pașii pe ecran pentru fiecare număr."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_import_saga import _incarca, _pas

CNP = "1800101221144"          # cifra de control verificată
CUI_DANTE = "14399840"         # DANTE INTERNATIONAL SA (ANAF, verificat 18.10.2026)
AZI = _dt.date.today()


@pytest.fixture(scope="module")
def firma_srl():
    for f in firma_noua():
        yield f


@pytest.fixture(scope="module")
def firma_pfa():
    for f in firma_noua("pfa"):
        yield f


def cnp_cu_control(baza12):
    """CNP-ul cu cifra de control calculată (algoritmul oficial, CLAUDE.md)."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


def _text(patron):
    return " ".join(patron.fereastra().split())


def _celule(pg, nr):
    """{titlul coloanei: textul celulei} pentru rândul `nr` din fișier, în tabelul comun al previzualizării."""
    antet = [" ".join(x.split()) for x in pg.locator(".mig-prev thead th").all_inner_texts()]
    return dict(zip(antet, [" ".join(x.split()) for x in
                            pg.locator('.mig-prev tbody tr[data-rand="%s"]:not(.mig-prev-motive) td' % nr).all_inner_texts()]))


def _randul(pg, nr):
    """Textul rândului `nr` din fișier, în tabelul comun al previzualizării — rândul cu datele și sub-rândul cu motivele lui (`data-rand`)."""
    return " ".join(" ".join(pg.locator('.mig-prev tbody tr[data-rand="%s"]' % nr).all_inner_texts()).split())


# ── 343 / 344 — Solduri inițiale ────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_343_contul_inexistent_din_balanta_e_respins_numit(patron, firma_srl):
    """343. Contul sintetic inexistent (999) trecea fără avertisment și se adăuga tacit în plan.
    Pașii: firma -> Import date -> Solduri inițiale -> o balanță cu 999 -> rândul 999 e „Respins — nu intră”, cu motivul „Contul 999 nu
    există în planul de conturi”; salvarea e blocată pentru el; în plan nu apare 999."""
    _pas(patron, firma_srl, "Solduri ini")
    _incarca(patron, "balanta.csv", "Cont;Denumire;Sold final debitor;Sold final creditor\n5311;Casa;100;0\n999;Inventat;0;100\n".encode(),
             "#mig-salveaza-sold")
    pg = patron.pg
    r = _randul(pg, 3)
    patron.captura()
    assert "999" in r and "respins — nu intră" in r and "contul 999 nu există în planul de conturi" in r, r
    assert sql("SELECT count(*) FROM \"%s\".plan_conturi WHERE simbol = '999'" % firma_srl["schema"])[0][0] == 0


def test_def_344_data_balantei_e_propusa_si_nota_e_informativa(patron, firma_srl):
    """344. „Data balanței” nu era propusă; caseta informativă era galbenă, ca un avertisment.
    Pașii: aceeași firmă, fără luna preluării -> Solduri inițiale -> balanța -> câmpul „Data balanței” are o dată propusă (ultima zi a
    unei luni), iar caseta „Soldurile s-au citit din coloanele …” e albastră (`caseta-info`), nu galbenă."""
    _pas(patron, firma_srl, "Solduri ini")
    _incarca(patron, "balanta.csv", "Cont;Denumire;Sold final debitor;Sold final creditor\n5311;Casa;100;0\n1012;Capital;0;100\n".encode(),
             "#mig-salveaza-sold")
    pg = patron.pg
    v = pg.input_value("#mig-data-bal")
    patron.captura()
    assert v, "data balanței nu e propusă"
    d = _dt.date.fromisoformat(v)
    assert (d + _dt.timedelta(days=1)).day == 1, "data propusă %s nu e ultima zi a unei luni" % v
    assert pg.locator(".caseta-info", has_text="Soldurile s-au citit din coloanele").count() == 1
    assert pg.locator(".caseta-atentie", has_text="Soldurile s-au citit din coloanele").count() == 0


# ── 347 / 348 / 349 — Salariați ───────────────────────────────────────────────────────────────────────────────────────────────
def _salariati(patron, firma, csv):
    _pas(patron, firma, "Salaria")
    _incarca(patron, "salariati.csv", csv.encode(), "#mig-salveaza-sal")


def test_def_347_cnp_cu_11_cifre_are_motivul_in_cuvinte(patron, firma_srl):
    """347. CNP cu 11 cifre: mesajul spunea „format (13 cifre)”. Pașii: Salariați -> fișier cu un CNP de 11 cifre -> rândul e respins cu
    „are 11 cifre; un CNP are 13”."""
    _salariati(patron, firma_srl, "Nume;Prenume;CNP;Functie baza;Norma;Salariu brut\nPop;Ion;18001012211;Da;8;5000\n")
    r = _randul(patron.pg, 2)
    patron.captura()
    assert "are 11 cifre; un CNP are 13" in r and "respins — nu intră" in r, r


def test_def_348_functia_si_data_angajarii_se_vad(patron, firma_srl):
    """348. Funcția din fișier („functie”) apărea „—”; data angajării nu se vedea.
    Pașii: Salariați -> fișier cu „Functie” = „Contabil” și „Data angajarii” = 01.03.2024 -> pe rând: „Contabil” (cu „fără cod COR”) și
    „01.03.2024”; rândul intră cu observația că lipsește codul COR (funcția din fișier e numită)."""
    _salariati(patron, firma_srl, "Nume;Prenume;CNP;Functie;Functie baza;Data angajarii;Norma;Salariu brut\n"
                                  "Pop;Ion;%s;Contabil;Da;01.03.2024;8;5000\n" % CNP)
    r = _randul(patron.pg, 2)
    patron.captura()
    assert "Contabil" in r and "fără cod COR" in r and "01.03.2024" in r, r
    assert "intră, cu observație" in r and "codul COR lipsește (funcția din fișier: «Contabil»)" in r, r


def test_def_349_norma_e_scurta_si_randul_nu_se_inalta(patron, firma_srl):
    """349. Coloana „Normă” înghesuia un paragraf. Pașii: același fișier -> celula „Normă” e „întreagă”; funcția de bază, scutirea și
    persoanele au coloanele lor; rândul are cel mult 3 rânduri de text (înălțime < 90 px)."""
    _salariati(patron, firma_srl, "Nume;Prenume;CNP;Functie;Functie baza;Data angajarii;Norma;Salariu brut\n"
                                  "Pop;Ion;%s;Contabil;Da;01.03.2024;8;5000\n" % CNP)
    pg = patron.pg
    antet = [" ".join(x.split()) for x in pg.locator(".mig-prev thead th").all_inner_texts()]
    i = antet.index("Normă")
    celula = pg.locator(".mig-prev tbody tr:not(.mig-prev-motive)").first.locator("td").nth(i).inner_text().strip()
    patron.captura()
    assert celula == "întreagă", celula
    assert {"Funcție de bază", "Scutit minim", "Persoane în întreținere"} <= set(antet), antet
    assert pg.locator(".mig-prev tbody tr:not(.mig-prev-motive)").first.bounding_box()["height"] < 90
    # starea rândului se vede fără derulare: celula „Starea” e în cutie (ultimele coloane de date pot derula într-o cutie lată)
    assert pg.evaluate("""() => { const c = document.querySelector('.mig-prev-cutie').getBoundingClientRect();
      const s = document.querySelector('.mig-prev tbody tr td.mig-prev-stare').getBoundingClientRect(); return s.right <= c.right; }""")


# ── 350 — modelele CSV ────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("pas", ["Istoric declara", "Mijloace fixe", "Salaria"])
def test_def_350_modelul_se_deschide_pe_coloane(patron, firma_srl, pas):
    """350. Modelele descărcate erau separate prin virgulă: în Excel românesc totul în coloana A.
    Pașii: pasul de import -> „Descarcă model (CSV)” -> fișierul are antetul pe coloane separate prin „;” (separatorul listei din Excel cu
    setări românești), nicio virgulă ca separator."""
    _pas(patron, firma_srl, pas)
    pg = patron.pg
    with pg.expect_download() as d:
        pg.click("#mig-model")
    txt = open(d.value.path(), encoding="utf-8-sig").read()
    antet = txt.splitlines()[0]
    assert ";" in antet and len(antet.split(";")) >= 3, antet


# ── 351–358 — Istoric declarații ──────────────────────────────────────────────────────────────────────────────────────────────
ISTORIC_82 = ("Tip;Luna;An;Data depunerii;Suma\n"
              "D101;;2025;20.06.2026;\n"           # 2: anuală
              "D112;01;2026;20.02.2026;\n"         # 3
              "D112;01;2026;20.02.2026;\n"         # 4: dublat
              "D112;03;2026;10.03.2026;\n"         # 5: înainte de sfârșitul lunii
              "D300;04;2026;01.12.2099;\n"         # 6: în viitor
              "D300;05;2026;;\n"                   # 7: fără dată
              "D112;06;2019;25.07.2019;\n")        # 8: an vechi


def _istoric(patron, firma):
    _pas(patron, firma, "Istoric declara")
    _incarca(patron, "istoric.csv", ISTORIC_82.encode(), ".mig-prev")


def test_def_351_declaratia_anuala_se_arata_anuala(patron, firma_srl):
    """351. D101 pe 2025 apărea cu luna „dec”. Pașii: Istoric declarații -> fișierul -> rândul D101 arată „anuală”, nu „dec”."""
    _istoric(patron, firma_srl)
    r = _randul(patron.pg, 2)
    patron.captura()
    assert "anuală" in r and "dec" not in r.lower().split("d101")[1], r


def test_def_352_titlurile_stau_deasupra_valorilor(patron, firma_srl):
    """352. Titlurile „LUNĂ” / „DATA DEPUNERII” nu stăteau deasupra valorilor. Pașii: fișierul -> tabelul are antetul în `thead`, o celulă
    pe coloană, cu „Rândul” prima și „Starea” lângă ea; fiecare rând de date are tot atâtea celule câte titluri."""
    _istoric(patron, firma_srl)
    pg = patron.pg
    antet = [" ".join(x.split()) for x in pg.locator(".mig-prev thead th").all_inner_texts()]
    patron.captura()
    assert antet[:2] == ["Rândul", "Starea"] and "Perioada" in antet, antet
    assert pg.locator('.mig-prev tbody tr[data-rand="2"]:not(.mig-prev-motive) td').count() == len(antet)


def test_def_358_motivul_are_randul_lui_nu_coloana_tip(patron, firma_srl):
    """358. Mesajul de eroare era înghesuit în coloana TIP, rândurile se înălțau și textul se tăia. Pașii: fișierul -> motivul rândului 4
    (dublat) stă pe sub-rândul lui, pe toată lățimea; celula „Tip” are numai tipul."""
    _istoric(patron, firma_srl)
    pg = patron.pg
    antet = [" ".join(x.split()) for x in pg.locator(".mig-prev thead th").all_inner_texts()]
    patron.captura()
    rand = pg.locator('.mig-prev tbody tr[data-rand="4"]:not(.mig-prev-motive)')     # rândul 4, dublat
    assert pg.locator('.mig-prev tbody tr.mig-prev-motive[data-rand="4"] .mig-prev-motiv').count() == 1
    assert rand.locator("td").nth(antet.index("Tip")).inner_text().strip() == "D112"


def test_def_353_randul_dublat_intra_o_singura_data(patron, firma_srl):
    """353. Rândul dublat (D112 2026 ian, de două ori) era acceptat de două ori. Pașii: fișierul -> rândul 4: „D112 pe 01/2026 apare și pe
    rândul 3: se importă o singură dată”."""
    _istoric(patron, firma_srl)
    r = _randul(patron.pg, 4)
    patron.captura()
    assert "D112 pe 01/2026 apare și pe rândul 3: se importă o singură dată" in r, r


def test_def_354_datele_imposibile_se_resping(patron, firma_srl):
    """354. D112 pe martie depus pe 10.03.2026 și D300 pe aprilie cu data 01.12.2099 treceau „ok”. Pașii: fișierul -> rândul 5: „depusă la
    10.03.2026, înainte de sfârșitul perioadei raportate”; rândul 6: „o dată din viitor”."""
    _istoric(patron, firma_srl)
    pg = patron.pg
    r5, r6 = _randul(pg, 5), _randul(pg, 6)
    patron.captura()
    assert "înainte de sfârșitul perioadei raportate" in r5 and "respins — nu intră" in r5, r5
    assert "o dată din viitor" in r6 and "respins — nu intră" in r6, r6


def test_def_355_randul_fara_data_e_semnalat(patron, firma_srl):
    """355. Rândul fără dată de depunere trecea „ok”. Pașii: fișierul -> rândul 7 „intră, cu observație”: „fără data depunerii”."""
    _istoric(patron, firma_srl)
    r7 = _randul(patron.pg, 7)
    patron.captura()
    assert "intră, cu observație" in r7 and "fără data depunerii" in r7, r7


def test_def_356_anul_vechi_e_semnalat(patron, firma_srl):
    """356. D112 pe 2019 trecea „ok”. Pașii: fișierul -> rândul 8 „intră, cu observație”: „anul 2019 e mai vechi decât anii pe care îi
    urmărește aplicația”."""
    _istoric(patron, firma_srl)
    r8 = _randul(patron.pg, 8)
    patron.captura()
    assert "intră, cu observație" in r8 and "anul 2019 e mai vechi decât anii pe care îi urmărește aplicația" in r8, r8


def test_def_357_contorul_spune_ce_se_intampla(patron, firma_srl):
    """357. Contorul spunea „2 cu avertisment” despre rânduri respinse. Pașii: fișierul -> banda: „rânduri respinse — nu intră” și
    „rânduri intră cu observație”; „cu avertisment” nu mai apare."""
    _istoric(patron, firma_srl)
    t = _text(patron)
    patron.captura()
    assert "respinse — nu intră" in t and "intră cu observație" in t and "cu avertisment" not in t, t[:1500]


# ── 359–363 — Mijloace fixe ───────────────────────────────────────────────────────────────────────────────────────────────────
MF_82 = ("Cod;Denumire;Valoare intrare;Data PIF;Durata luni;Metoda;Cont imobilizare;Cont amortizare;Amortizare cumulata\n"
         "MF1;Laptop;6000;01.01.2025;36;liniara;2141;2814;3000\n"            # 2: ok, cu amortizarea preluată
         "MF2;Strung;9000;01.01.2027;60;liniara;2131;2813;0\n"              # 3: PIF în viitor
         "MF3;Masina;20000;01.01.2025;60;inventata;2133;2813;0\n"           # 4: metodă inexistentă
         "MF4;Mijloc pe banca;1000;01.01.2025;12;liniara;5121;2813;0\n"    # 5: cont care nu e de imobilizări
         "MF5;Licenta;1200;01.01.2025;12;liniara;205;2813;0\n"             # 6: amortizare pe alt cont
         "MF6;Teren;50000;01.01.2025;0;liniara;2111;;0\n"                  # 7: teren, durata 0 corectă
         "MF7;Imprimanta;-1500;01.01.2025;12;liniara;2141;2814;0\n")       # 8: valoare negativă


def _mf(patron, firma):
    _pas(patron, firma, "Mijloace fixe")
    _incarca(patron, "mf.csv", MF_82.encode(), "#mig-salveaza-mf")


def test_def_359_amortizarea_cumulata_preluata_se_vede_si_se_reconciliaza(patron, firma_srl):
    """359. Amortizarea cumulată la data migrării nu se prelua. Pașii: Mijloace fixe -> registrul cu „Amortizare cumulata” -> coloanele
    „Amortizare preluată” (3.000,00 lei pe MF1) și „Amortizare calculată”; caseta de reconciliere numește conturile (fără balanța de
    deschidere: spune că nu se poate confrunta încă)."""
    _mf(patron, firma_srl)
    c = _celule(patron.pg, 2)
    t = _text(patron)
    patron.captura()
    assert c["Amortizare preluată"] == "3.000,00 lei", c
    assert "Amortizare preluată" in t and "Amortizare calculată" in t, t[:1500]
    assert "conturile 2xx / 28xx" in t or "Față de balanța de deschidere" in t, t[:1500]


def test_def_360_pif_si_conturile_se_vad_metoda_liniara_nu_e_rosie(patron, firma_srl):
    """360. Previzualizarea nu arăta data PIF și conturile; „liniara” era roșu. Pașii: registrul -> rândul MF1: „01.01.2025”, „2141”,
    „2814”, „liniara”, starea nu e „Respins”."""
    _mf(patron, firma_srl)
    r = _randul(patron.pg, 2)
    patron.captura()
    assert all(x in r for x in ("01.01.2025", "2141", "2814", "liniara")) and "respins — nu intră" not in r, r


def test_def_361_pif_in_viitor_si_metoda_inexistenta_sunt_respinse(patron, firma_srl):
    """361. PIF în viitor (01.01.2027) și metoda „inventata” treceau „ok”."""
    _mf(patron, firma_srl)
    pg = patron.pg
    r3, r4 = _randul(pg, 3), _randul(pg, 4)
    patron.captura()
    assert "data PIF 01.01.2027 e în viitor" in r3, r3
    assert "metoda de amortizare «inventata» nu există" in r4, r4


def test_def_362_conturile_sunt_verificate_terenul_nu_se_amortizeaza(patron, firma_srl):
    """362. „Mijloc fix” pe 5121 nu era semnalat; licența pe 205 cu amortizare pe 2813 trecea; terenul (durata 0) nu trebuie respins."""
    _mf(patron, firma_srl)
    pg = patron.pg
    r5, r6, r7 = _randul(pg, 5), _randul(pg, 6), _randul(pg, 7)
    patron.captura()
    assert "contul 5121 nu e de imobilizări (clasa 2)" in r5, r5
    assert "amortizarea contului 205 se ține pe 2805, nu pe 2813" in r6, r6
    assert "respins — nu intră" not in r7 and "durata" not in r7.split("Teren")[1], r7


def test_def_363_valoarea_negativa_are_motivul_real_in_format_romanesc(patron, firma_srl):
    """363. La -1.500 rândul spunea „valoarea reziduală depășește valoarea de intrare”, iar lista „-1500.0”."""
    _mf(patron, firma_srl)
    r = _randul(patron.pg, 8)
    t = _text(patron)
    patron.captura()
    assert "valoarea de intrare -1.500,00 lei e negativă" in r and "reziduală" not in r, r
    assert "-1500.0" not in t


# ── 364–367 — Asociați ────────────────────────────────────────────────────────────────────────────────────────────────────────
def _asociati(patron, firma, csv):
    _pas(patron, firma, "Asocia")
    _incarca(patron, "asociati.csv", csv.encode(), "#mig-salveaza-asoc")


def test_def_364_randul_fara_nume_se_arata(patron, firma_srl):
    """364. Rândul fără nume dispărea (7 rânduri -> „6 asociați”). Pașii: Asociați -> 2 rânduri, al doilea fără nume -> „2 rânduri citite”,
    rândul 3 „Respins”: „rândul n-are numele asociatului”; totalul cotelor îl include (100%)."""
    _asociati(patron, firma_srl, "Nume;CNP;Cota\nPop Ion;%s;60\n;%s;40\n" % (CNP, "2800101221146"))
    t = _text(patron)
    r = _randul(patron.pg, 3)
    patron.captura()
    assert "2 rânduri citite" in t and "total cote: ✓ 100%" in t, t[:800]
    assert "rândul n-are numele asociatului" in r, r


def test_def_365_cnp_dublat_fara_identificator_si_cota_negativa(patron, firma_srl):
    """365. Același CNP pe două rânduri, rândul fără CNP/CUI (clasificat „juridică”) și cota -5 nu erau semnalate."""
    _asociati(patron, firma_srl, "Nume;CNP;Cota\nPop Ion;%s;60\nIon Pop;%s;45\nFara Cod;;-5\n" % (CNP, CNP))
    pg = patron.pg
    r3, r4 = _randul(pg, 3), _randul(pg, 4)
    patron.captura()
    assert "apare și pe rândul 2" in r3, r3
    assert "lipsește CNP-ul sau CUI-ul — fără el asociatul nu poate apărea în D205" in r4 and "juridică" not in r4, r4
    assert "cota -5% nu e o cotă de participare" in r4, r4


def test_def_366_totalul_cotelor_nu_spune_rand_undefined_si_lista_are_loc(patron, firma_srl):
    """366. „rând undefined” la totalul cotelor; lista avea loc pentru 2–3 rânduri. Pașii: 8 asociați cu cote care dau 90% -> mesajul
    spune „toți asociații: cotele asociaților însumează 90%”, fără „undefined”; tabelul arată cel puțin 6 rânduri fără derulare."""
    csv = "Nume;CNP;Cota\n" + "".join("Asociat %d;%s;%s\n" % (i, cnp_cu_control("1800101221%02d" % (10 + i)), "20" if i < 4 else "2.5")
                                      for i in range(8))
    _asociati(patron, firma_srl, csv)
    t = _text(patron)
    patron.captura()
    assert "undefined" not in t and "toți asociații: cotele asociaților însumează 90" in t, t[:1500]
    cutie = patron.pg.locator(".mig-prev-cutie").bounding_box()
    rand = patron.pg.locator(".mig-prev tbody tr:not(.mig-prev-motive)").first.bounding_box()
    assert cutie["height"] >= 6 * rand["height"], (cutie, rand)


def test_def_367_cuiul_asociatului_pj_e_confruntat_cu_anaf(patron, firma_srl):
    """367. CUI-ul asociatului PJ era verificat doar ca cifră de control; 14399840 trecea ca „Firma Asociata SRL”.
    Pașii: Asociați -> „Firma Asociata SRL; 14399840; 100” -> rândul e respins: „la ANAF, CUI-ul 14399840 este al firmei «DANTE
    INTERNATIONAL SA»” (sau, dacă ANAF nu răspunde, „intră, cu observație”: serviciul ANAF nu a răspuns)."""
    _asociati(patron, firma_srl, "Nume;CUI;Cota\nFirma Asociata SRL;%s;100\n" % CUI_DANTE)
    r = _randul(patron.pg, 2)
    patron.captura()
    assert ("la ANAF, CUI-ul 14399840 este al firmei «DANTE INTERNATIONAL SA»" in r) or ("serviciul ANAF nu a răspuns" in r), r


# ── 372 — Import RIP (PFA) ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_372_data_imposibila_nu_ajunge_la_baza_si_previzualizarea_vine_inainte(patron, firma_pfa):
    """372. O dată imposibilă (2026-13-01) prăbușea importul cu eroarea brută a bazei de date; nu exista previzualizare.
    Pașii: firma PFA -> Import RIP -> registrul cu 2026-13-01 pe un rând -> previzualizarea: rândul „Respins”: „data «2026-13-01» nu e o
    dată”, nimic scris încă; „Salvează” -> numai rândul bun intră; nicio urmă de „datestyle” / „out of range”."""
    _pas(patron, firma_pfa, "Import RIP")
    _incarca(patron, "rip.csv", ("Data;Tip;Explicatie;Suma;Metoda;Categorie\n2026-13-01;incasare;vanzare;100;banca;venit\n"
                                 "15.01.2026;incasare;onorariu;200;banca;venit\n").encode(), "#mig-salveaza-rip")
    pg = patron.pg
    r = _randul(pg, 2)
    patron.captura("previzualizare")
    assert "data «2026-13-01» nu e o dată" in r and "respins — nu intră" in r, r
    assert sql('SELECT count(*) FROM "%s".rip_operatiuni' % firma_pfa["schema"])[0][0] == 0
    pg.click("#mig-salveaza-rip")
    pg.wait_for_function("() => document.body.innerText.includes('O operațiune importată.')", timeout=20000)
    t = _text(patron)
    patron.captura("salvat")
    assert "datestyle" not in t and "out of range" not in t
    assert sql('SELECT data_operatiune::text, suma::text FROM "%s".rip_operatiuni' % firma_pfa["schema"]) == [("2026-01-15", "200.00")]


# ── 373–375 — Articole, stoc, rețete ───────────────────────────────────────────────────────────────────────────────────────────
ARTICOLE_82 = ("Denumire;UM;Cantitate;Pret;Cont stoc\n"
               "Marfa A;buc;10;5;371\n"        # 2: ok
               ";buc;1;1;371\n"                # 3: fără denumire
               "Marfa B;;2;3;371\n"            # 4: fără UM
               "Marfa C;kg;zece;3;371\n"       # 5: cantitate text
               "Marfa D;buc;1;2;5121\n")       # 6: cont care nu e de stoc


def test_def_373_articolele_fara_valori_din_oficiu(patron, firma_srl):
    """373. 6 rânduri greșite -> „3 articole valide”: rândul fără denumire dispărea, „zece” devenea 0, UM lipsă „buc”, marfă pe 5121.
    Pașii: Articole și stoc inițial -> fișierul -> „5 rânduri citite”; rândurile 3–6 respinse, fiecare cu motivul lui."""
    _pas(patron, firma_srl, "Articole")
    _incarca(patron, "articole.csv", ARTICOLE_82.encode(), "#mig-importa")
    pg = patron.pg
    t = _text(patron)
    patron.captura()
    assert "5 rânduri citite" in t, t[:800]
    assert "rândul n-are denumirea articolului" in _randul(pg, 3)
    assert "unitatea de măsură lipsește — nu se presupune „buc”" in _randul(pg, 4)
    assert "cantitatea «zece» nu e un număr" in _randul(pg, 5)
    assert "contul 5121 nu e un cont de stoc (clasa 3)" in _randul(pg, 6)


def test_def_374_stocul_se_reconciliaza_pe_contul_de_stoc(patron, firma_srl):
    """374. Valoarea stocului nu era comparată cu balanța; contul nu se vedea. Pașii: aceeași firmă (balanța de deschidere fără 371) ->
    previzualizarea arată coloana „Cont stoc” (371 pe rândul 2) și caseta „Față de balanța de deschidere”: 371 stoc inițial 50,00 lei."""
    _pas(patron, firma_srl, "Articole")
    _incarca(patron, "articole.csv", ARTICOLE_82.encode(), "#mig-importa")
    t = _text(patron)
    patron.captura()
    assert "371" in _randul(patron.pg, 2)
    assert ("371: stoc inițial 50,00 lei" in t) or ("conturile de stoc nu se pot confrunta" in t), t[:1500]


RETETE_82 = ("Reteta;Pret;Ingredient;Cantitate\n"
             "Pizza;25;Faina;0.2\nPizza;28;Branza;0.1\n"     # 2–3: două prețuri
             ";30;Sare;1\n"                                   # 4: fără rețetă
             "Supa;;Faina;0\n")                               # 5: fără preț, cantitate 0


def test_def_375_retetele_nu_se_aleg_in_tacere(patron, firma_srl):
    """375. Rândul fără rețetă dispărea; două prețuri -> 28 tacit; rețeta fără preț -> 0,00 lei; cantitatea 0 fără mesaj; „Importă 0
    rețete” activ; ordinea (articolele întâi) nespusă. Pașii: Rețete -> fișierul -> fiecare rând cu motivul lui; butonul inactiv:
    „Nicio rețetă nu poate intra”; textul spune că articolele se importă înaintea rețetelor."""
    _pas(patron, firma_srl, "Rețete")
    t0 = _text(patron)
    assert "articolele se importă înaintea rețetelor" in t0, t0[:800]
    _incarca(patron, "retete.csv", RETETE_82.encode(), "#mig-importa")
    pg = patron.pg
    patron.captura()
    assert "are prețuri diferite în fișier: 25 (rândul 2), 28 (rândul 3)" in _randul(pg, 2)
    assert "rândul n-are numele rețetei" in _randul(pg, 4)
    r5 = _randul(pg, 5)
    assert "cantitatea pe porție e 0" in r5 and "prețul de vânzare lipsește — nu intră cu 0 lei" in r5, r5
    assert pg.is_disabled("#mig-importa") and pg.inner_text("#mig-importa") == "Nicio rețetă nu poate intra"


# ── 341 / 342 — Firme (Migrare cabinet) ───────────────────────────────────────────────────────────────────────────────────────
def _firme_validate(patron, firma_srl):
    """Migrare cabinet -> Firme -> CUI-ul firmei din portofoliu și 14399841 (cifra de control greșită) -> „Validează la ANAF”:
    textul fiecărui rând din listă."""
    from e2e_lot5_migrare import _migrare
    pg = patron.pg
    _migrare(patron)
    pg.locator("#mig-meniu .mig-op", has_text="Firme").first.click()
    pg.wait_for_selector("#mig-text", timeout=20000)
    cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (firma_srl["tenant_id"],))[0][0]
    pg.fill("#mig-text", "%s\n14399841" % cui)
    pg.click("#mig-valideaza")
    pg.wait_for_selector("#mig-lista .mig-rand", timeout=60000)
    patron.captura()
    return [" ".join(x.split()) for x in pg.locator("#mig-lista .mig-rand").all_inner_texts()]


def test_def_341_firma_din_portofoliu_nu_se_ofera(patron, firma_srl):
    """341. Firma deja în portofoliu apărea „găsită”, bifată și oferită; după import, bifă verde cu „0 firme adăugate”.
    Pașii: Migrare cabinet -> Firme -> CUI-ul firmei din portofoliu -> „Validează la ANAF”: rândul ei „deja în portofoliu”, „nu se importă a
    doua oară”, nebifat; butonul de import inactiv (niciun rând de importat)."""
    t = _firme_validate(patron, firma_srl)
    port = next(x for x in t if "deja în portofoliu" in x)
    assert "nu se importă a doua oară" in port, port
    assert patron.pg.locator("#mig-lista input[type=checkbox]:checked").count() == 0
    assert patron.pg.is_disabled("#mig-importa")


def test_def_342_cuiul_cu_cifra_de_control_gresita_spune_ce_e_gresit(patron, firma_srl):
    """342. CUI cu cifra de control greșită apărea „nu a fost găsit la ANAF”. Pașii: Migrare cabinet -> Firme -> 14399841 -> „Validează la
    ANAF”: rândul „CUI greșit”, cu „cifra de control greșită”, nu „nu a fost găsit la ANAF”; nebifat."""
    t = _firme_validate(patron, firma_srl)
    gresit = next(x for x in t if "CUI greșit" in x)
    assert "cifra de control greșită" in gresit and "nu a fost găsit la ANAF" not in gresit, gresit
    assert patron.pg.locator("#mig-lista input[type=checkbox]:checked").count() == 0


# ── 345 / 346 — Solduri parteneri ─────────────────────────────────────────────────────────────────────────────────────────────
def test_def_345_terminat_nu_e_activ_cat_balanta_are_terti_fara_parteneri(patron, firma_srl):
    """345. „Finalizează stratul” (jargon) era activ cu firme cu balanță fără parteneri. Pașii: firma are în balanța de deschidere 401
    (credit 500), fără parteneri -> Migrare cabinet -> Solduri parteneri: butonul „Am terminat soldurile pe parteneri” e inactiv și
    textul numește firma și „401 în balanță”."""
    from e2e_lot5_migrare import _migrare
    sch = firma_srl["schema"]
    sql('DELETE FROM "%s".solduri_initiale' % sch)
    sql('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (\'401\', 0, 500, \'2026-09-30\'), '
        '(\'5311\', 500, 0, \'2026-09-30\')' % sch)
    pg = patron.pg
    try:
        _migrare(patron)
        pg.locator("#mig-meniu .mig-op", has_text="Solduri parteneri").first.click()
        pg.wait_for_selector("#mig-finalizeaza", timeout=20000)
        motiv = pg.inner_text("#mig-fin-motiv")
        patron.captura()
        assert pg.is_disabled("#mig-finalizeaza") and pg.inner_text("#mig-finalizeaza") == "Am terminat soldurile pe parteneri"
        assert firma_srl["nume"] in motiv and "401 în balanță" in motiv, motiv
    finally:
        sql('DELETE FROM "%s".solduri_initiale' % sch)


def test_def_346_partenerii_care_nu_dau_soldul_contului_nu_intra(patron, firma_srl):
    """346 (grav). Pe F2 se lăsa salvarea unei sume (net creditor 100) diferite de 401 din contabilitate (debitor 500).
    Pașii: balanța de deschidere 401 credit 500 -> Solduri parteneri -> fișier cu un furnizor pe 401 credit 100 -> rândul e respins:
    „pe 401, partenerii din fișier dau … iar balanța de deschidere … are …”; caseta de confruntare numește cifrele; nimic scris."""
    sch = firma_srl["schema"]
    sql('DELETE FROM "%s".solduri_initiale' % sch)
    sql('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (\'401\', 0, 500, \'2026-09-30\'), '
        '(\'5311\', 500, 0, \'2026-09-30\')' % sch)
    try:
        _pas(patron, firma_srl, "Solduri parteneri")
        _incarca(patron, "parteneri.csv", ("Cont;CUI;Denumire;Debit;Credit\n401;%s;DANTE INTERNATIONAL SA;0;100\n" % CUI_DANTE).encode(),
                 ".mig-prev")
        r = _randul(patron.pg, 2)
        t = _text(patron)
        patron.captura()
        assert "respins — nu intră" in r and "pe 401, partenerii din fișier dau" in r, r
        assert "Soldurile pe parteneri, față de soldul fiecărui cont" in t, t[:1500]
        assert sql('SELECT count(*) FROM "%s".solduri_parteneri' % sch)[0][0] == 0
    finally:
        sql('DELETE FROM "%s".solduri_initiale' % sch)


# ── 368 / 371 — regimul PFA, straturile din sursa unică ───────────────────────────────────────────────────────────────────────
def test_def_368_la_pfa_se_ascund_straturile_partidei_duble_mijloacele_fixe_raman(patron, firma_pfa):
    """368. PFA-ul apărea ca un SRL; meniul per firmă ascundea Mijloace fixe. Pașii: firma PFA -> Import date: „Mijloace fixe” și „Import
    RIP” sunt în listă; „Solduri inițiale”, „Solduri parteneri”, „Asociați”, „Plan de conturi” nu."""
    pg = patron.pg
    patron.firma(firma_pfa["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    titluri = [" ".join(x.split()) for x in pg.locator(".mig-frand .mig-frand-nume").all_inner_texts()]
    patron.captura()
    assert "Mijloace fixe" in titluri and "Import RIP" in titluri, titluri
    for t in ("Solduri inițiale", "Solduri parteneri", "Asociați", "Plan de conturi"):
        assert t not in titluri, titluri


def test_def_371_migrare_cabinet_are_toate_straturile_filtrate_pe_regim(patron, firma_pfa, firma_srl):
    """371. Migrare cabinet nu conținea Import RIP, Articole, Rețete. Pașii: Migrare cabinet -> „Import RIP (PFA)” -> lista firmelor are
    firma PFA, nu și SRL-ul; „Solduri parteneri” -> lista are SRL-ul, nu și PFA-ul."""
    from e2e_lot5_migrare import _migrare
    pg = patron.pg
    _migrare(patron)
    titluri = pg.eval_on_selector_all("#mig-meniu .mig-op .mig-op-titlu", "els => els.map(e => e.textContent.trim())")
    assert {"Import RIP (PFA)", "Articole și stoc inițial", "Rețete (HoReCa)"} <= set(titluri), titluri
    pg.locator("#mig-meniu .mig-op", has_text="Import RIP (PFA)").first.click()
    pg.wait_for_selector(".mig-frand", timeout=20000)
    nume = " ".join(pg.locator(".mig-frand").all_inner_texts())
    patron.captura("rip")
    assert firma_pfa["nume"] in nume and firma_srl["nume"] not in nume, nume


# ── 369 — Plan de conturi: funcțiunea din OMFP ─────────────────────────────────────────────────────────────────────────────────
def test_def_369_functiunea_contului_e_cea_din_omfp(patron, firma_srl):
    """369. Toate conturile apăreau „Bifunctional”. Pașii: firma -> Import date -> Plan de conturi -> caută 1012: „Pasiv”; 4111: „Activ”;
    117: „Bifuncțional” (cu diacritice)."""
    _pas_plan = lambda: (patron.firma(firma_srl["nume"]), patron.pg.click("#fa-import"),
                         patron.pg.wait_for_selector(".mig-frand", timeout=20000),
                         patron.pg.locator(".mig-frand", has_text="Plan de conturi").first.click(),
                         patron.pg.wait_for_selector("#pc-cauta", timeout=10000))
    _pas_plan()
    pg = patron.pg
    for cont, asteptat in (("1012", "Pasiv"), ("4111", "Activ"), ("117", "Bifuncțional")):
        pg.fill("#pc-cauta", cont)
        pg.wait_for_function("(c) => [...document.querySelectorAll('#pc-rezultate .mig-frand-nume')].some((x) => x.textContent.startsWith(c + ' '))",
                             arg=cont, timeout=10000)
        rand = pg.locator("#pc-rezultate .mig-frand", has=pg.locator(".mig-frand-nume", has_text=cont + " ·")).first
        sub = rand.locator(".mig-frand-sub").inner_text().strip()
        assert sub.startswith(asteptat), (cont, sub)
    patron.captura()


# ── 370 — Auditul de preluare păstrat ─────────────────────────────────────────────────────────────────────────────────────────
def test_def_370_primul_audit_ramane_langa_ultimul(patron, firma_srl):
    """370. La reluarea auditului raportul anterior era înlocuit. Pașii: Control fiscal -> firma -> „Rulează auditul de preluare” de două
    ori -> sus „Ultimul audit … (2 rulări)”, dedesubt, închis, „Primul audit după preluare … păstrat: ce s-a primit de la contabilul
    anterior”."""
    from e2e_bloc_d import _control_firma
    pg = patron.pg
    _control_firma(patron, firma_srl)
    for _ in range(2):
        pg.click(".fereastra:last-of-type #cf-audit-run")
        pg.wait_for_function("() => { const b = document.querySelector('.fereastra:last-of-type #cf-audit-run'); return b && !b.disabled "
                             "&& b.textContent === 'Rerulează auditul'; }", timeout=60000)
    pg.wait_for_selector(".fereastra:last-of-type details.cf-audit-primul", timeout=20000)
    t = " ".join(pg.inner_text(".fereastra:last-of-type #cf-audit-istoric").split())
    patron.captura()
    assert "Ultimul audit" in t and "rulări)" in t, t[:600]
    assert "Primul audit după preluare" in t and "păstrat: ce s-a primit de la contabilul anterior" in t, t[:600]


# ── 376–378 — D100 pe impozitul pe profit ─────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_profit(patron):
    """O firmă NOUĂ pe impozit pe profit, plătitoare de TVA trimestrial: vânzări de 10.000 lei în ianuarie și 5.000 lei în august 2026
    (note validate, 5311 = 704)."""
    from e2e_bloc_a import _api, _ok, pregateste_firma
    from e2e_bloc_e import _nota
    for f in firma_noua():
        pregateste_firma(patron, f)
        _ok(_api(patron, "POST", "/tenants/%d/vector" % f["tenant_id"],
                 {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "trimestrial", "operatiuni_ic": False,
                  "inreg_art317": False, "tva_data_inceput": "2026-01-01"}), "vector profit")
        _nota(f, "2026-01-15", [{"debit": "5311", "credit": "704", "suma": 10000}], "Vânzări ianuarie E2E", valideaza=True)
        _nota(f, "2026-08-14", [{"debit": "5311", "credit": "704", "suma": 5000}], "Vânzări august E2E", valideaza=True)
        yield f


def test_def_376_d100_e_datorat_la_firma_pe_profit(patron, firma_profit):
    """376 (PRIORITAR). F2 (impozit pe profit) nu avea D100 nici în „Datorate”, nici în restanțe. Pașii: Control fiscal -> firma pe profit ->
    D100 apare pe trimestrele I–III ale lui 2026; D101 rămâne declarația anuală."""
    from e2e_bloc_d import _control_firma, _grupuri_control
    _control_firma(patron, firma_profit)
    g = _grupuri_control(patron)
    patron.captura()
    toate = [r for v in g.values() for r in v]
    d100 = [r for r in toate if r.startswith("D100")]
    assert d100, g
    assert any("2026" in r for r in d100), d100


def _d100_t3(patron, firma):
    from conftest import alege_perioada, alege_tipul
    from e2e_bloc_e import _card
    pg = patron.pg
    _card(patron, firma, "declaratii", "#dec-tip")
    alege_tipul(pg, "d100")
    alege_perioada(pg, 2026, trim=3)
    pg.click("#dec-continua")
    pg.wait_for_selector("#dec-trimite, #dec-gol-da, .dec-eroare", timeout=90000)
    return " ".join(patron.fereastra().split())


def test_def_377_d100_scade_impozitul_declarat_inainte_de_preluare(patron, firma_profit):
    """377 (PRIORITAR). D100 T3 considera „deja impozitat în trimestrele anterioare: 0,00 lei” la firma preluată.
    Pașii: Istoric declarații -> D100 pe 03/2026, depus 25.04.2026, cu suma de plată 1.600 -> salvat -> Declarații -> D100 T3/2026: sinteza
    spune „deja declarat pe T1/2026: 1.600,00 lei (preluat din istoric la migrare (depus pe 25.04.2026))” și „de plată pe T3/2026: 2.400,00 lei −
    1.600,00 lei = 800,00 lei”."""
    _pas(patron, firma_profit, "Istoric declara")
    _incarca(patron, "istoric.csv", "Tip;Luna;An;Data depunerii;Suma de plata\nD100;03;2026;25.04.2026;1600\n".encode(), ".mig-prev")
    pg = patron.pg
    pg.click("#mig-salveaza-ist")
    pg.wait_for_function("() => document.body.innerText.includes('declarați')", timeout=20000)
    t = _d100_t3(patron, firma_profit)
    patron.captura()
    assert "deja declarat pe T1/2026: 1.600,00 lei (preluat din istoric la migrare (depus pe 25.04.2026))" in t, t
    assert "de plată pe T3/2026: 2.400,00 lei − 1.600,00 lei = 800,00 lei" in t, t


def test_def_378_d100_porneste_de_la_rezultatul_fiscal_cumulat(patron, firma_profit):
    """378. D100 calcula pe profitul contabil. Pașii: Registrul de evidență fiscală -> o cheltuială nedeductibilă de 1.000 lei pe T3
    (rd.33) -> D100 T3: „cheltuieli nedeductibile: 1.000,00 lei”, impozitul cumulat 2.560,00 lei (16% din 16.000), de plată 960,00 lei."""
    from e2e_bloc_a import _api, _ok
    _ok(_api(patron, "POST", "/tenants/%d/ajustari-fiscale" % firma_profit["tenant_id"],
             {"an": 2026, "trim": 3, "rand": "P33", "suma": 1000, "descriere": "Amenda E2E"}), "ajustarea fiscală")
    t = _d100_t3(patron, firma_profit)
    patron.captura()
    assert "cheltuieli nedeductibile: 1.000,00 lei" in t, t
    assert "impozitul cumulat: 2.560,00 lei" in t and "= 960,00 lei" in t, t


# ── 379–381 — declarațiile: rândurile, D406 ───────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_tva(patron):
    """O firmă NOUĂ plătitoare de TVA (lunar), cu o factură de 5.000 lei la 21% pe 704, emisă azi, și nota ei validată."""
    from core import db, facturi_api
    from e2e_bloc_a import pregateste_firma
    from e2e_lot81 import _valideaza_luna
    for f in firma_noua():
        pregateste_firma(patron, f)
        with db.get_conn(f["schema"]) as c:
            r = facturi_api.emite_factura(c, [{"descriere": "Servicii consultanță", "cantitate": 1, "pret_unitar": 5000, "cota_tva": 21,
                                              "cont_venit": "704"}], tert_nume="DANTE INTERNATIONAL SA", tert_cui=CUI_DANTE,
                                          data_emitere=AZI.replace(day=2).isoformat(), status="emisa")
            assert r.get("ok"), r
            c.commit()
        _valideaza_luna(patron, f)
        yield f


def test_def_379_randurile_d300_au_denumirea_oficiala(patron, firma_tva):
    """379. La D300 rândurile apăreau doar ca număr („rândul 9, coloana Valoare”). Pașii: Declarații -> D300 pe luna curentă -> „Din ce e
    făcută declarația” -> „Rânduri completate” are coloana „denumire în formular”: rândul 9 = „Livrări de bunuri şi prestări de servicii,
    taxabile cu cota 21%”, rândul 19 = „TOTAL TAXĂ COLECTATĂ …”."""
    from e2e_bloc_e import _declaratie, _deschide_componente, _sectiune
    _declaratie(patron, firma_tva, "d300", AZI.year, AZI.month)
    _deschide_componente(patron)
    sec = _sectiune(patron, "Rânduri completate")
    patron.captura()
    assert sec and "denumire în formular" in sec[0], sec
    randuri = [" | ".join(r) for r in sec[1]]
    assert any("rândul 9, coloana Valoare" in r and "taxabile cu cota 21%" in r for r in randuri), randuri
    assert any("rândul 19" in r and "TOTAL TAXĂ COLECTATĂ" in r for r in randuri), randuri


def test_def_380_contul_de_venit_al_facturii_e_cel_din_nota(patron, firma_tva):
    """380 (PRIORITAR). Factura contată pe 704 apărea pe 707 în „Facturi de vânzare”. Pașii: Declarații -> D406 pe luna curentă -> „Din ce e
    făcută declarația” -> „Facturi de vânzare”: „704 · credit 5.000,00”, niciun 707; fără avertismentul de nepotrivire jurnal–facturi."""
    from e2e_bloc_e import _declaratie, _deschide_componente, _sectiune
    _declaratie(patron, firma_tva, "d406", AZI.year, AZI.month)
    t = _text(patron)
    _deschide_componente(patron)
    sec = _sectiune(patron, "Facturi de vânzare")
    patron.captura()
    linii = " | ".join(" ".join(r) for r in sec[1])
    assert "704 · credit 5.000,00" in linii and "707" not in linii, linii
    assert "nu se potrivesc cu nota lor din jurnal" not in t, t[:1500]


def test_def_381_nota_pe_401_cere_partenerul_si_d406_il_poarta(patron, firma_tva):
    """381. Nota „plata furnizor” (401 = 5311) n-avea furnizor: D406 spunea „0 furnizori, 0 plăți”.
    Pașii: Registrul jurnal -> Notă nouă 401 = 5311, 500 lei, fără partener -> „Salvează”: refuzul „scrie partenerul” lângă câmp, nimic
    scris -> partenerul DANTE INTERNATIONAL SA, CUI 14399840 -> salvată și validată -> D406 pe luna curentă: fără avertismentul „fără
    partener”, iar XML-ul are plata cu SupplierID-ul partenerului."""
    from e2e_bloc_b import _jurnal
    from e2e_bloc_e import _declaratie
    from e2e_lot81 import _valideaza_luna
    pg = patron.pg
    _jurnal(patron, firma_tva, None)
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-desc", timeout=10000)
    pg.fill("#je-data", AZI.replace(day=3).isoformat())
    pg.fill("#je-desc", "Plata furnizor E2E 381")
    pg.fill("#je-doc", "OP 381")
    pg.fill("#je-linii .je-deb", "401")
    pg.fill("#je-linii .je-cre", "5311")
    pg.fill("#je-linii .je-sum", "500")
    pg.click("#je-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('scrie partenerul')", timeout=20000)
    patron.captura("refuz")
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE descriere = %%s' % firma_tva["schema"], ("Plata furnizor E2E 381",))[0][0] == 0
    pg.fill("#je-linii .je-pcui", CUI_DANTE)
    pg.fill("#je-linii .je-pnume", "DANTE INTERNATIONAL SA")
    with pg.expect_response(lambda r: r.url.split("?")[0].endswith("/jurnal") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#je-salveaza")
    assert rr.value.status < 400, rr.value.text()
    _valideaza_luna(patron, firma_tva)
    _declaratie(patron, firma_tva, "d406", AZI.year, AZI.month)
    t = _text(patron)
    xml = pg.locator("details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").text_content()
    patron.captura("d406")
    assert "fără partener" not in t, t[:1500]
    assert "<Payments>" in xml and ("<SupplierID>" in xml.split("<Payments>")[1]), xml[-3000:]
