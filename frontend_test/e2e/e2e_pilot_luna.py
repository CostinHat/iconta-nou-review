# -*- coding: utf-8 -*-
"""PILOTUL — scenariul lunii complete a firmei-pilot, parcurs pe ecran ca un contabil (CLAUDE.md §2, verbatim: „Pilotul are un scenariu
automat al lunii complete a firmei-pilot, parcurs pe ecran ca un contabil, cu cifrele exacte așteptate la fiecare pas, până la declarații.
Scenariul crește cu fiecare poziție pilot rezolvată și rulează permanent în poartă. Pilotul e atins când scenariul e verde de la cap la
coadă.”). Comanda 12.1: firma de comerț cu salariați (F1, F5), cele 43 de poziții „pilot” din `FUNCTIONALITATI.csv` + „Primii pași”.
Legătura poziție -> pas -> stare: `PILOT_CRITERII.md`, păzită de `core/test_lot12_pilot_criterii.py`.

FIRMA-PILOT: un SRL de comerț NOU, creat de la zero în baza de TEST (`conftest.firma_noua`: CUI sintetic cu cifra de control verificată,
`conftest.cui_cu_control`), plătitor de TVA lunar, MICROÎNTREPRINDERE (1%) — ca F1 („Comert Stoc SRL”, SRL micro plătitor de TVA lunar,
cu salariați, pe 09/2026: DECIZII „F1 e micro 1% -> depune D100”, `scripts/cifre_referinta_aprobate.json`), cu stocul cantitativ-valoric
(F1). Firma e înființată în 2025 (capital vărsat; în decembrie 2025 a cumpărat 7 scaune de birou și a vândut 2 pe credit clientului Delta,
neîncasate) și n-a avut venituri în 2026 până la preluare (o cheltuială de consultanță neplătită). E PRELUATĂ de cabinet din 09/2026:
balanța de deschidere la 31.08.2026, soldurile pe parteneri (furnizorul și clientul Delta), articolele cu stocul inițial (5 scaune de
birou). De aceea D100 pe T3/2026 cuprinde numai septembrie — legal, firma n-a avut venituri în iulie–august (CF art.53 alin.(1): baza =
veniturile; art.56 alin.(1): trimestrial).
[lotul 13, comanda Costin 13.1 pct.7, verbatim: „Extinde scenariul automat al lunii pilot cu preluarea: balanța de deschidere, soldurile pe
parteneri, articolele cu stoc inițial și încasarea unei creanțe preluate, cu cifre așteptate exacte. Rămâne permanent în poartă.”] Pașii
01–04: balanța (8 conturi, cu 371 și 4111), pașii următori spuși la salvare (664), articolele cu stocul inițial potrivit cu 371 (668),
partenerii pe 401 și 4111, auditul, iar soldul preluat al clientului Delta încasat din Casă pe documentul lui preluat (669).

LUNA: 09/2026, FIXĂ — încheiată (deficiența 383: declarațiile nu se generează pe luna în curs), închide trimestrul (D100 T3/2026), iar
cifrele se calculează o dată, după legea în vigoare atunci (salariul minim 4.325 lei de la 01.07.2026, HG 146/2026 art.1; cota TVA 21%, CF
art.291 alin.(1) în forma Legii 141/2025; certificatele CM din 01.02.2026–31.12.2027 cu diminuarea cu o zi, OUG 91/2025 art.II alin.(1)).
Septembrie 2026 are 22 de zile lucrătoare (8 zile de weekend, nicio sărbătoare legală). Singura parte dependentă de ziua rulării e
„Declarație vs contabilitate” (Control fiscal confruntă ULTIMA LUNĂ ÎNCHEIATĂ, `control_fiscal_api.luna_confruntata`): pe ecran în
octombrie 2026; după, pasul citește aceeași sursă (`control_incrucisat.verifica_tva` / `verifica_d112`) pe 09/2026 și o spune.

PAȘII: fiecare e un test `test_pilot_<nn>_<pas>`, în ordine (pytest le rulează în ordinea din fișier), pe aceeași firmă (fixtura de modul
`firma_pilot`), marcați cu pozițiile pe care le acoperă (`@pozitii(...)`). Un pas pe care azi nu-l poate face o deficiență deschisă din
DEFICIENTE.md e scris totuși, `xfail(strict=True, reason="deficiența <nr>: …")`: pică (XPASS) când se repară și intră atunci în scenariu.
Pașii xfail nu schimbă cifrele pașilor verzi: verifică întâi ce lipsește (citire), iar cei care ar scrie stau la coadă, pe luna următoare
(10/2026), sau își scot urma.

DATELE DE PORNIRE puse altfel decât din ecran (pe rutele aplicației, aceeași sesiune — `e2e_bloc_a._api`): Date firmă și vectorul fiscal
(`pregateste_firma`, o dată, ca la orice test al plasei), răspunsurile ANAF ale partenerilor sintetici (`ICONTA_ANAF_SIMULAT`, serviciu
extern) și răspunsul AI al cotei (`ICONTA_AI_SIMULAT`). Restul — preluarea, nomenclatorul, NIR-ul, facturile, casa, banca, salariații,
statul, validarea, închiderea, declarațiile — pe ecran.

CIFRELE LUNII (calculate din lege, nu citite din aplicație; temeiul pe linia fiecărui assert):
  balanța de deschidere 31.08.2026: 1012 C 10.000 · 1171 C 1.580 · 121 D 1.000 · 371 D 1.000 (5 × 200, Marfă birou pilot) · 401 C 1.000
    (Consultanță Înființare) · 4111 D 2.420 (Delta) · 5121 D 7.660 · 5311 D 500 — debit = credit = 12.580
  casa 03.09: încasarea creanței preluate de la Delta, 2.420,00 (5311 = 4111, pe documentul „Sold la 31.08.2026”)
  NIR 1 / 02.09: 20 × 150,00 = 3.000,00 + transport 200,00 (repartizat integral pe singura linie) = 3.200,00 -> CMP 160,00 / buc;
    TVA 21%: 630,00 + 42,00 = 672,00 (nesosită: 4428.01 = 408) -> factura MF-901 / 03.09 (3.200 + 672) se leagă: 408 = 401 3.872,00,
    4426 = 4428.01 672,00
  chirie IMB-0925 / 05.09: 1.000 + 210 (612 = 401, 4426 = 401)
  E2EA1 / 10.09 Alfa: 10 × 300 (707) + montaj 300 (704) = 3.300 + TVA 693 = 3.993,00; descărcare 10 × 160 = 1.600 (607 = 371)
  casa 12.09: încasare E2EA1 3.993,00 cu chitanță (5311 = 4111)
  Z 0042 / 15.09: 2 bonuri, 726,00 numerar (baza 600, TVA 126); descărcare 2 × 160 = 320
  Z 0041 / 14.09, importat din fișierul AMEF: 1 bon, 363,00 numerar (baza 300, TVA 63); descărcare 1 × 160 = 160
  E2EA2 / 15.09 Gamma, pe baza bonului 0002: 1 × 300 + 63 = 363,00 — fără notă, fără descărcare (vânzarea e în Z)
  casa 18.09: depunere 3.000 la bancă (581 = 5311)
  E2EA3 / 20.09 Beta: 5 × 300 = 1.500 + 315 = 1.815,00; descărcare 5 × 160 = 800
  E2EA4 / 29.09 Alfa: montaj 300 + 63 = 363,00 — neîncasată la 30.09
  banca: −1.000 (Consultanță) · +3.000 (depunere) · +1.815 (Beta) · −3.872 (Mobila) · −1.210 (chirie) · −15 (comision 627)
  casa la 30.09: 500 + 2.420 (Delta) + 3.993 (E2EA1) + 363 (Z 0041) + 726 (Z 0042) − 3.000 (depunerea) = 5.002
  salarii: POPA ANDREI 8.000 brut; MARIN ELENA 8.800 contractual, CM cod 01 14–18.09 (5 zile lucrătoare) -> 6.800 lucrat + CM 550
  TVA: colectată 693 + 63 + 315 + 126 + 63 = 1.260 · deductibilă 672 + 210 = 882 · de plată 378
  D100 T3: 1% × (707: 3.000 + 600 + 300 + 1.500 = 5.400; 704: 300 + 300 = 600) = 1% × 6.000 = 60

Fiecare test lasă capturi (`patron.captura`). Mutațiile: `frontend_test/e2e/mut_lot12_pilot.json`.
"""
import datetime as _dt
import json
import os
import re
from decimal import ROUND_HALF_UP, Decimal

import pytest

from conftest import ai_pregateste, alege_perioada, alege_tipul, cui_cu_control, firma_noua, sql
from e2e_bloc_a import _api, _card, _deschide_emiterea, _ok, _pdf_ok, _pdf_text, pregateste_firma
from e2e_bloc_b import _cnp, _jurnal, _linie
from e2e_bloc_d import _control_firma, _grupuri_control
from e2e_bloc_e import _asteapta_text, _inchidere, _la_luna
from e2e_import_saga import _incarca, _pas
from e2e_lot10_balanta import _celule
from e2e_lot11_s9 import _propunerea_zilelor
from e2e_lot72_cont import cabinet_nou  # noqa: F401 — fixtura: cabinetul nou al pasului „Primii pași”
from e2e_lot81 import _cont
from e2e_pozitii_validate import _iban_ro

AN, LUNA = 2026, 9
_F = ".fereastra:last-of-type "


def zi(n):
    """Ziua `n` din luna-pilot (09/2026)."""
    return _dt.date(AN, LUNA, n)


def pozitii(*ids):
    """Pozițiile pilot (ID-urile din FUNCTIONALITATI.csv, „PRIMII_PASI” pentru fereastra de bun venit) pe care le acoperă pasul. Citite
    de garda `core/test_lot12_pilot_criterii.py` din sursă (decoratorul), confruntate cu `PILOT_CRITERII.md`."""
    def marcheaza(fn):
        fn.pozitii_pilot = ids
        return fn
    return marcheaza


# ── partenerii (CUI sintetice, cifra de control verificată de `cui_cu_control`) ─────────────────────────────────────────────────────
def _partener(baza, nume, oras, judet, platitor=True):
    return {"cui": cui_cu_control(baza), "nume": nume, "oras": oras, "judet": judet, "platitor": platitor,
            "adresa": "Str. Pilotului nr. %d" % (baza % 100)}


ALFA = _partener(41200001, "ALFA MOBILIER PILOT SRL", "București", "B")
BETA = _partener(41200002, "BETA BIROTICA PILOT SRL", "Cluj-Napoca", "CJ")
GAMMA = _partener(41200003, "GAMMA DESIGN PILOT SRL", "București", "B")
MOBILA = _partener(41200004, "MOBILA FURNIZOR PILOT SRL", "Brașov", "BV")
IMOB = _partener(41200005, "IMOBILIARE PILOT SRL", "București", "B")
INFIINTARE = _partener(41200006, "CONSULTANTA INFIINTARE PILOT SRL", "București", "B", platitor=False)
DELTA = _partener(41200007, "DELTA CLIENT PILOT SRL", "Ploiești", "PH")   # [lotul 13, pct.7] clientul cu creanța preluată
PARTENERI = (ALFA, BETA, GAMMA, MOBILA, IMOB, INFIINTARE, DELTA)

MARFA = "Marfă scaun ergonomic pilot"           # „marf” -> 707 (`facturi.tip_din_denumire`), fără AI
MARFA_STOC = "Marfă birou pilot"               # [lotul 13, pct.7] articolul cu stocul inițial: 5 buc × 200,00 = 1.000,00 (371 la 31.08)
SERVICIU = "Servicii de montaj mobilier pilot"  # „servici” -> 704
CASA_Z = "8000000001"
D = Decimal
STOC_INITIAL_CANT, STOC_INITIAL_PRET = 5, D("200")   # [pct.7] 5 × 200,00 = 1.000,00 — soldul lui 371 din balanța de deschidere
STOC_INITIAL = STOC_INITIAL_CANT * STOC_INITIAL_PRET
CREANTA_DELTA = D("2420")                            # [pct.7] 4111 Delta la 31.08.2026: 2.000 + TVA 21% 420 (factura din 12/2025)


def _bani(x):
    """Decimal -> „1.234,56” (cum scrie ecranul)."""
    s = "{:,.2f}".format(D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP))
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _q(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def _leu(x):
    """Rotunjirea aritmetică la leu (CLAUDE.md §10: Decimal + ROUND_HALF_UP, niciodată round())."""
    return D(x).quantize(D("1"), rounding=ROUND_HALF_UP)


# ── cifrele așteptate, din lege ──────────────────────────────────────────────────────────────────────────────────────────────────
COTA = D("0.21")      # CF art.291 alin.(1): „nivelul acesteia este 21%” (la 01-08-2025, Legea 141/2025 art.II pct.42)
PRET_ACHIZITIE, CANT_NIR, TRANSPORT = D("150"), 20, D("200")
COST_NIR = _q(PRET_ACHIZITIE * CANT_NIR + TRANSPORT)           # OMFP 1802/2014 pct.62 alin.(1): costul de achiziție cuprinde transportul
CMP = _q(COST_NIR / CANT_NIR)                                  # OMFP 1802/2014 pct.96: costul mediu ponderat = 160,00
TVA_NIR = _q(PRET_ACHIZITIE * CANT_NIR * COTA) + _q(TRANSPORT * COTA)    # 630,00 + 42,00
PRET_VANZARE = D("300")
CHIRIE = D("1000")
# facturile emise: (baza 707, baza 704)
E1 = (PRET_VANZARE * 10, D("300"))
E3 = (PRET_VANZARE * 5, D("0"))
E4 = (D("0"), D("300"))
Z_TOTAL, Z_BONURI = D("726.00"), 2
Z_BAZA = _q(Z_TOTAL / (1 + COTA))                              # 600,00 (prețul cu TVA inclusă; CF art.286 alin.(1) + art.291)
Z_TVA = Z_TOTAL - Z_BAZA                                       # 126,00
# Z 0041, importat din AMEF: un bon cu un scaun (300 + TVA 21% = 363), plătit numerar
Z2_TOTAL, Z2_BONURI = _q(PRET_VANZARE * (1 + COTA)), 1         # 363,00
Z2_BAZA = _q(Z2_TOTAL / (1 + COTA))                            # 300,00 (CF art.286 alin.(1) + art.291 alin.(1))
Z2_TVA = Z2_TOTAL - Z2_BAZA                                    # 63,00
BON = (PRET_VANZARE, _q(PRET_VANZARE * COTA))                  # E2EA2: 300 + 63
TVA_COL = _q(sum(E1) * COTA) + _q(sum(E3) * COTA) + _q(sum(E4) * COTA) + Z_TVA + Z2_TVA   # 693 + 315 + 63 + 126 + 63 = 1.260
TVA_DED = TVA_NIR + _q(CHIRIE * COTA)                          # 672 + 210 = 882
TVA_PLATA = TVA_COL - TVA_DED                                  # 378
DESCARCAT = 10 + 2 + 1 + 5                                     # bucăți ieșite din stoc în 09/2026: E2EA1, Z 0042, Z 0041, E2EA3
# salarii (CF art.138 lit.a CAS 25%, art.156 CASS 10%, art.78 alin.(2) lit.a impozit 10%, art.220^3 alin.(1) CAM 2,25%)
SAL1 = {"nume": "POPA", "prenume": "ANDREI", "cnp": "185031240001", "brut": D("8000"), "cor": "241107"}
SAL2 = {"nume": "MARIN", "prenume": "ELENA", "cnp": "288070540012", "brut": D("8800"), "cor": "331302"}
ZILE_LUCRATOARE, ZILE_CM = 22, 5
CM_VEN6, CM_ZILE6 = D("31250"), 125                            # adeverința angajatorului anterior: media zilnică 250,00
CM_MEDIE = _q(CM_VEN6 / CM_ZILE6)                              # OUG 158/2005 art.10 alin.(1)
CM_PROC = D("0.55")                                            # OUG 158/2005 art.17 alin.(1) lit.a: până la 7 zile — 55%
CM_ZILE_PLATITE = ZILE_CM - 1                                  # OUG 91/2025 art.II alin.(1): „prin diminuarea cu o zi”
CM_BRUT = _leu(CM_MEDIE * CM_PROC * CM_ZILE_PLATITE)           # 550; angajatorul plătește zilele 2–6 (art.II alin.(1) lit.a)
CM_CAS = _leu(CM_BRUT * D("0.25"))                             # CF art.144: baza CAS = indemnizația -> 137,5 -> 138
CM_CASS = _leu(CM_BRUT * D("0.10"))                            # CF art.155 alin.(1) lit.i (cod 01) + art.157 alin.(1) lit.v -> 55
CM_IMPOZIT = _leu((CM_BRUT - CM_CAS - CM_CASS) * D("0.10"))    # CF art.76 alin.(2) + art.78 alin.(2) lit.a -> 35,7 -> 36
CM_NET = CM_BRUT - CM_CAS - CM_CASS - CM_IMPOZIT               # 321


def _salariu(brut):
    """(CAS, CASS, impozit, net) pe salariu, deducerea personală 0: brutul e peste salariul minim + 2.000 = 6.325 lei (CF art.77 alin.(3),
    salariul minim 4.325 lei, HG 146/2026 art.1)."""
    cas, cass = _leu(brut * D("0.25")), _leu(brut * D("0.10"))
    imp = _leu((brut - cas - cass) * D("0.10"))
    return cas, cass, imp, brut - cas - cass - imp


S1 = _salariu(SAL1["brut"])                                    # 2.000 · 800 · 520 · 4.680
SAL2_LUCRAT = _q(SAL2["brut"] * (ZILE_LUCRATOARE - ZILE_CM) / ZILE_LUCRATOARE)   # Codul muncii art.159 alin.(1): 6.800,00
S2 = _salariu(SAL2_LUCRAT)                                     # 1.700 · 680 · 442 · 3.978
NET_FLUTURASI = S1[3] + S2[3]                                  # 8.658 — contul 421
NET_DE_PLATA = NET_FLUTURASI + CM_NET                          # 8.979 — fișierul de plată
D112_IMPOZIT = S1[2] + S2[2] + CM_IMPOZIT                      # 998
D112_CAS = S1[0] + S2[0] + CM_CAS                              # 3.838
D112_CASS = S1[1] + S2[1] + CM_CASS                            # 1.535
# CAM: CF art.220^4 alin.(1) (baza = câștigurile brute din salarii și asimilate) + art.76 alin.(1) („inclusiv indemnizațiile pentru
# incapacitate temporară de muncă”) + art.220^5 (exceptată numai partea FNUASS); OPANAF 605/2026 anexa 2 secțiunea B rd.4: „sumele
# suportate de angajator, primele 5 zile de incapacitate temporară de muncă […] pentru care angajatorul datorează contribuţia
# asiguratorie pentru muncă” -> 2,25% × (8.000 + 6.800 + 550) = 345,375 -> 345
D112_CAM = _leu((SAL1["brut"] + SAL2_LUCRAT + CM_BRUT) * D("0.0225"))
# D100 micro T3/2026: CF art.51 alin.(1) „Cota de impozit pe veniturile microîntreprinderilor este de 1%” (la 01-01-2026, OUG 89/2025);
# art.53 alin.(1): baza = veniturile; art.56 alin.(1): trimestrial
V707 = E1[0] + E3[0] + Z_BAZA + Z2_BAZA                        # 5.400
V704 = E1[1] + E4[1]                                           # 600
D100_IMPOZIT = _leu((V707 + V704) * D("0.01"))                 # 60


# ── fixtura de modul: firma-pilot ────────────────────────────────────────────────────────────────────────────────────────────────
def _anaf_pune(p):
    """Răspunsul ANAF al plasei pentru partenerul sintetic (`anaf_api._raspuns_simulat`, serviciu extern)."""
    d = os.environ["ICONTA_ANAF_SIMULAT"]
    os.makedirs(d, exist_ok=True)
    cale = os.path.join(d, "anaf.json")
    toate = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
    toate[str(p["cui"])] = {"denumire": p["nume"], "platitor_tva": p["platitor"], "tva_data_inceput": "2020-01-01" if p["platitor"] else None,
                            # localitatea și județul domiciliului fiscal, ca în răspunsul real (v9 `adresa_domiciliuFiscal`): un partener
                            # numai din preluare (fără fișă în nomenclator) își ia localitatea D406 de aici (`anaf_api.aduce_localitati`)
                            "adresa": "%s, %s" % (p["adresa"], p["oras"]), "localitate": p["oras"], "judet": p["judet"],
                            "cod_caen": "4759", "nr_reg_com": "J40/1/2020",
                            "data_inregistrare": "2020-01-01", "inactiv": False, "tva_la_incasare": False}
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(toate, f, ensure_ascii=False)


@pytest.fixture(scope="module")
def firma_pilot(_anaf_simulat_numai_baza):
    """Firma-pilot: NOUĂ (`conftest.firma_noua`), scoasă la final; răspunsurile ANAF ale partenerilor puse după golirea simulatorului
    (de aceea cere fixtura care golește). Dicționarul ține și ce află pașii (id-urile facturilor, ale notelor)."""
    for p in PARTENERI:
        _anaf_pune(p)
    for f in firma_noua():
        yield f


# ── ajutoare ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _note(f, unde, param=()):
    """[(debit, credit, suma)] ale notelor care îndeplinesc `unde` (pe `i` = inregistrari) — observarea efectului din bază."""
    return sorted(sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
                      "ON l.inregistrare_id = i.id WHERE %s" % (f["schema"], f["schema"], unde), param))


def _sintetic(c):
    return str(c).split(".")[0] if str(c).split(".")[0] in ("401", "4111") else str(c)


def _factura(f, numar_sufix):
    """(id, numar) al facturii emise E2EA<n>."""
    r = sql('SELECT id, numar FROM "%s".facturi WHERE directie = \'emisa\' AND numar LIKE %%s ORDER BY id' % f["schema"],
            ("%%%s" % numar_sufix,))
    assert r, "factura emisă …%s nu e în bază" % numar_sufix
    return r[-1]


def _articol_id(f):
    return sql('SELECT id FROM "%s".articole WHERE denumire = %%s' % f["schema"], (MARFA,))[0][0]


def _deschide_factura_luna(patron, f, factura_id):
    """Facturi -> „Istoric facturi” (pornește pe luna de azi) -> „← luna” până la 09/2026 -> factura -> detaliul ei. (Istoricul arată
    luna curentă; factura din luna-pilot se caută în luna ei, ca de contabil.)"""
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    _la_luna(patron, "#fac-prev", AN, LUNA)
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % factura_id, timeout=25000)
    pg.click(".fac-frand-btn[data-id='%s']" % factura_id)
    pg.wait_for_selector("#fd-pdf", timeout=25000)


def _asteapta_nemiscat(pg, loc, pas_ms=150, incercari=40):
    """Așteaptă ca elementul să stea pe loc (aceeași poziție la două citiri la `pas_ms`): o derulare „smooth” în curs l-ar muta sub clic."""
    ultim = None
    for _ in range(incercari):
        bb = loc.bounding_box()
        if bb and ultim and all(abs(bb[k] - ultim[k]) < 0.5 for k in ("x", "y")):
            return
        ultim = bb
        pg.wait_for_timeout(pas_ms)


def _ce_e_sub(pg, loc):
    """Diagnostic pentru un clic fără efect: poziția butonului, elementul aflat de fapt în centrul lui (`elementFromPoint`), dacă e activ."""
    return loc.evaluate("""(b) => { const r = b.getBoundingClientRect(); const x = r.left + r.width / 2, y = r.top + r.height / 2;
        const e = document.elementFromPoint(x, y);
        return {buton: b.outerHTML.slice(0, 200), rect: [r.left, r.top, r.width, r.height], conectat: b.isConnected, activ: !b.disabled,
                sub_clic: e ? e.outerHTML.slice(0, 200) : null, acelasi: e === b || (e && b.contains(e)), vh: window.innerHeight}; }""")


def _scadentar(patron, f):
    """Facturi -> „Scadențar” -> vederea „Facturi neîncasate”: {id factură: textul rândului} (rândul deschide factura, `sc-fact-btn`)."""
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-scadentar")
    pg.click("#fac-scadentar")
    pg.wait_for_selector("#sc-lista", timeout=30000)
    randuri = dict(pg.eval_on_selector_all("#sc-lista .sc-fact-btn", "bs => bs.map((b) => [Number(b.dataset.id), b.innerText])"))
    patron.captura()
    return {k: " ".join(v.split()) for k, v in randuri.items()}


def _valideaza_z(patron, f, zid, cost, vanzari):
    """Raport Z -> „Validează raportul Z” -> confirmarea cu cifrele descărcării (deficiența 474: Z-ul n-are articole, deci aplicația spune
    costul descărcat față de vânzarea fără TVA și adaosul, și cere confirmarea) -> „Da, validează raportul Z”: butonul dispare, nota e
    validată."""
    pg = patron.pg
    pg.click("#zd-val-%d" % zid)
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=20000)
    avert = " ".join(pg.inner_text("#caseta-atentie-activa").split())
    patron.captura("avertisment_z_%d" % zid)
    adaos = _leu((vanzari - cost) * 100 / cost)        # (vânzarea fără TVA − costul) / cost, la procent întreg (ROUND_HALF_UP)
    assert ("Ai descărcat din stoc 1 ieșire la cost %s lei, pentru vânzări de %s lei fără TVA pe acest Z (adaos %s%%)"
            % (_bani(cost), _bani(vanzari), adaos)) in avert, avert
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("(z) => !document.querySelector('#zd-val-' + z)", arg=zid, timeout=30000)
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (zid,)) == [("validata",)]


def _emite_pe_ecran(patron, f, data, client, linii, pleaca=None, bon=None):
    """Facturi -> „Emite factură”: data, clientul (CUI, denumire, adresă, localitate, județ), liniile (articolul din stoc sau denumirea din
    nomenclator, cantitatea, prețul, cota) -> „Emite” -> la poarta „Pleacă marfa acum?” răspunsul `pleaca`. Întoarce textul rezultatului."""
    pg = patron.pg
    _deschide_emiterea(patron, f["nume"])
    pg.fill("#em-data", data.isoformat())
    pg.dispatch_event("#em-data", "change")
    pg.wait_for_function("(d) => (document.querySelector('#em-scadenta') || {value: ''}).value !== ''", arg=data.isoformat(), timeout=10000)
    pg.fill("#em-cui", client["cui"])
    pg.dispatch_event("#em-cui", "change")
    pg.fill("#em-nume", client["nume"])
    pg.fill("#em-adresa", client["adresa"])
    pg.fill("#em-oras", client["oras"])
    pg.select_option("#em-judet", client["judet"])
    for i, (den, cant, pret, cu_articol) in enumerate(linii):
        if i:
            pg.click("#em-add-linie")
            pg.wait_for_selector("#em-l%d-descriere" % i, timeout=10000)
        _linie(pg, i, den, cant, pret, articol_id=_articol_id(f) if cu_articol else None)
    if bon:
        pg.fill("#em-bon-nr", bon[0])
        pg.fill("#em-bon-data", bon[1].isoformat())
    # [F252] clasificarea TVA a facturii: țara partenerului și tipul operațiunii (D300 rd.9 pentru o livrare internă)
    assert pg.input_value("#em-tara") == "RO" and pg.input_value("#em-tipop") == "normal", (pg.input_value("#em-tara"),
                                                                                             pg.input_value("#em-tipop"))
    pg.click("#em-emite")
    if pleaca is not None:
        pg.wait_for_selector("#em-poarta-da", timeout=20000)
        pg.click("#em-poarta-da" if pleaca else "#em-poarta-nu")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=60000)
    return " ".join(pg.inner_text("#em-rezultat").split())


def _ubl(numar, data, furnizor, client, cui_client, linii):
    """XML-ul e-Factura (UBL 2.1 / CIUS-RO) al furnizorului: liniile (denumire, cantitate, preț) la 21%, cu defalcarea BG-23."""
    baza = sum(_q(c * p) for _d, c, p in linii)
    tva = _q(baza * COTA)
    rand = "".join(
        '<cac:InvoiceLine><cbc:InvoicedQuantity unitCode="H87">%s</cbc:InvoicedQuantity><cbc:LineExtensionAmount currencyID="RON">%s'
        '</cbc:LineExtensionAmount><cac:Item><cbc:Name>%s</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21'
        '</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item><cac:Price><cbc:PriceAmount currencyID="RON">%s</cbc:PriceAmount>'
        '</cac:Price></cac:InvoiceLine>' % (c, _q(c * p), den, _q(p)) for den, c, p in linii)
    return ("""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cbc:ID>%s</cbc:ID><cbc:IssueDate>%s</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
 <cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>%s</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
 <cac:AccountingCustomerParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
  </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>%s</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingCustomerParty>
 <cac:TaxTotal><cbc:TaxAmount currencyID="RON">%s</cbc:TaxAmount>
  <cac:TaxSubtotal><cbc:TaxableAmount currencyID="RON">%s</cbc:TaxableAmount><cbc:TaxAmount currencyID="RON">%s</cbc:TaxAmount>
   <cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory>
  </cac:TaxSubtotal></cac:TaxTotal>
 <cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount currencyID="RON">%s</cbc:TaxExclusiveAmount>
  <cbc:TaxInclusiveAmount currencyID="RON">%s</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
 %s
</Invoice>""" % (numar, data.isoformat(), furnizor["cui"], furnizor["nume"], cui_client, client, tva, baza, tva, baza, baza + tva, rand))


def _importa_si_valideaza(patron, f, xml, numar, cont, nir=False):
    """Facturi -> „Facturi primite” -> „Importă XML UBL” -> factura -> contul -> „Validează” -> confirmarea; la marfa cu NIR „fără factură”
    la același furnizor, aplicația propune NIR-ul: „Leagă de NIR-ul ales”. Întoarce propunerea NIR-ului (textul opțiunii alese)."""
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-xml", state="attached", timeout=20000)
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % numar, "mimeType": "text/xml", "buffer": xml.encode("utf-8")})
    pg.wait_for_function("() => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes('importat')", timeout=40000)
    assert "1 factură importată în lista de validat." in pg.inner_text("#fp-mesaj"), pg.inner_text("#fp-mesaj")
    pg.locator(".fac-primita-btn", has_text=numar).first.click()
    pg.wait_for_selector("#pr-cont", timeout=20000)
    pg.fill("#pr-cont", cont)
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    propus = None
    if nir:
        pg.wait_for_selector(_F + "#nir-legat", timeout=30000)
        propus = pg.eval_on_selector(_F + "#nir-legat", "s => s.options[s.selectedIndex].text")
        patron.captura("nir_propus_%s" % numar)
        pg.click(_F + "#nir-leaga")
    pg.wait_for_function("() => { const o = document.querySelector('#caseta-atentie-activa #ca-ok'); if (o) { o.click(); return false; }"
                         " return (document.querySelector('#pr-zona') || {innerText: ''}).innerText.includes('Validată'); }", timeout=60000)
    return propus


def _xml_pas2(pg):
    """XML-ul declarației de la pasul 2 („Vezi XML-ul generat”)."""
    return pg.locator(_F + "details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").first.text_content()


def _atr(xml, nume):
    m = re.search(r'\b%s="([^"]*)"' % nume, xml)
    return m.group(1) if m else None


def _genereaza_declaratia(patron, f, tip, luna=None, trim=None):
    """Firma -> Declarații -> tipul -> anul și perioada -> „Continuă →” -> pasul 2 (sau refuzul)."""
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-declaratii")
    _asteapta_text(patron, "Pasul 1 din 3")
    alege_tipul(pg, tip, zona=_F)
    alege_perioada(pg, AN, luna, trim, zona=_F)
    pg.click(_F + "#dec-continua")
    pg.wait_for_function("() => { const t = [...document.querySelectorAll('.fereastra')].pop().innerText; "
                         "return t.includes('Pasul 2 din 3 — verifică') || !!document.querySelector('.fereastra:last-of-type .dec-eroare'); }",
                         timeout=120000)
    patron.captura("%s_pas2" % tip)
    assert not pg.locator(_F + ".dec-eroare").count(), patron.fereastra()[:3000]
    return pg


def _duk_valid(patron, xml, tip, luna):
    """Validatorul oficial: rezultatul de pe ecran („Validat cu DUKIntegrator …, fără erori”) și, pe același XML, `core.duk.valideaza`
    (judecătorul final, CLAUDE.md §10)."""
    from core import duk
    ok = patron.pg.locator(_F + ".dec-ok")
    assert ok.count() == 1 and "fără erori" in ok.inner_text(), patron.fereastra()[:3000]
    assert duk.poate_valida(tip), "validatorul DUK pentru %s nu e instalat" % tip
    rez = duk.valideaza(xml, tip, an=AN, luna=luna)
    assert rez["stare"] == "valid", rez


def _trimite_in_coada(patron):
    pg = patron.pg
    pg.wait_for_selector(_F + "#dec-trimite", timeout=60000)
    pg.click(_F + "#dec-trimite")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Trimisă în coad')", timeout=90000)


def _depune(patron, f, eticheta, index):
    """De validat -> declarația firmei („D300”, …) -> „Confirmă depunerea” -> indexul SPV -> „— depusă.” (validarea în doi e oprită pe
    cabinetul de test: declarația trimisă de contabilul-șef e aprobată)."""
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector(_F + ".cf-grup-titlu", timeout=60000)
    rand = pg.locator(_F + ".val-info", has_text=f["nume"]).filter(has_text=eticheta).first.locator("xpath=..")
    rand.locator(".val-depune").wait_for(timeout=30000)
    rand.locator(".val-depune").click()
    pg.wait_for_selector(_F + "#dlg-input", timeout=20000)
    pg.fill(_F + "#dlg-input", index)
    pg.click(_F + "#dlg-ok")
    pg.wait_for_function("() => { const t = [...document.querySelectorAll('.fereastra')].pop().innerText; "
                         "return t.includes('— depusă.') || !!document.querySelector('#val-conf-ok'); }", timeout=60000)
    if pg.locator("#val-conf-ok").count():   # constatări certe de confirmat: un motiv pe fiecare, ca orice contabil
        for i in range(pg.locator(".val-conf-motiv").count()):
            pg.locator(".val-conf-motiv").nth(i).fill("scenariul pilot: declarația lunii 09/2026")
        pg.click("#val-conf-ok")
        pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('— depusă.')", timeout=60000)


def _stat_09(patron, f, an=AN, luna=LUNA):
    """Salariați -> statul de plată, înapoi de la luna de azi până la „Luna LL/AAAA” (implicit 09/2026)."""
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-contare", timeout=30000)
    azi = _dt.date.today()
    for _ in range((azi.year - an) * 12 + azi.month - luna):
        prev = pg.inner_text(_F + ".pf-intro")
        pg.click(_F + "#sp-prev")
        pg.wait_for_function("(p) => { const i = [...document.querySelectorAll('.fereastra')].pop().querySelector('.pf-intro'); "
                             "return i && i.innerText !== p; }", arg=prev, timeout=30000)
    _asteapta_text(patron, "Luna %02d/%d" % (luna, an))
    pg.wait_for_selector(_F + "#sp-tabel tbody tr.sp-rand", timeout=30000)   # [lotul 13, 677] statul = tabel, un rând pe salariat
    return pg


def _salariat(pg, nume):
    """[lotul 13, 677] Rândul statului -> fereastra salariatului (cu butoanele lui și compoziția netului pe trei coloane)."""
    pg.locator(_F + "#sp-tabel tbody tr.sp-rand", has_text=nume).first.locator(".sp-deschide").click()
    pg.wait_for_selector(_F + "#ss-butoane", timeout=30000)


def _coloane(pg):
    """Compoziția netului din fereastra salariatului: {etichetă: (valoare, net)} (rândurile celor trei coloane, `data-*`)."""
    return pg.eval_on_selector_all(
        _F + "#ss-compozitie tr[data-eticheta]",
        "rs => Object.fromEntries(rs.map(r => [r.dataset.eticheta, [r.dataset.valoare === '' ? null : Number(r.dataset.valoare),"
        " r.dataset.net === undefined ? null : Number(r.dataset.net)]]))")


def _rand_stat(pg, nume):
    """Sumele salariatului, citite din fereastra lui, ca „brut … · CAS … · CASS … · impozit … · net …” (în luna cu concediu medical
    „net <de plată> (salariu <net> + indemnizație CM <net CM>)”); fereastra se închide, înapoi la stat."""
    _salariat(pg, nume)
    c = _coloane(pg)
    pg.click(_F + ".nav-inapoi")
    pg.wait_for_selector(_F + "#sp-tabel tbody tr.sp-rand", timeout=30000)
    v = lambda e: D(str(c[e][0]))   # noqa: E731
    net = "net %s" % _bani(v("Net de plată"))
    if "Indemnizație concediu medical" in c:
        cm = D(str(c["Indemnizație concediu medical"][1]))
        net += " (salariu %s + indemnizație CM %s)" % (_bani(v("Net de plată") - cm), _bani(cm))
    return "brut %s · CAS %s · CASS %s · impozit %s · %s" % (_bani(v("Salariu pe zile lucrate")), _bani(v("CAS (25%)")),
                                                              _bani(v("CASS (10%)")), _bani(v("Impozit pe venit")), net)


def _sume(text):
    """{brut, CAS, CASS, impozit, net: textul sumei} — prima apariție pe rândul statului."""
    out = {}
    for k, v in re.findall(r"\b(brut|CAS|CASS|impozit|net)\s+([\d.]+,\d{2})", text):
        out.setdefault(k, v)
    return out


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 00 — Primii pași
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("PRIMII_PASI")
def test_pilot_00_primii_pasi(browser, request, cabinet_nou):
    """Primii pași. Pașii: administratorul unui cabinet NOU intră: pe pagina principală „Primii pași”, cu cele trei carduri („Pasul 1 · Adu
    firmele din aplicația veche”, „Pasul 2 · Leagă contul de ANAF …”, „Pasul 3 · Adaugă echipa”), niciunul făcut -> „Pasul 1”: butonul
    spre Migrare deschide drumul preluării firmelor. (Rotița peste carduri — 321 — și „Lucrez singur” — 322 — au testele lor, în
    `e2e_lot81.py`.)"""
    with _cont(browser, request, cabinet_nou["email"]) as e:
        pg = e.pg
        e.acasa()
        pg.wait_for_selector("#inceput-carduri .inceput-card", timeout=30000)
        t = " ".join(pg.inner_text("#inceput-carduri").split())
        e.captura("carduri")
        assert "Primii pași" in t and "Pasul 1 · Adu firmele din aplicația veche" in t and "Pasul 3 · Adaugă echipa" in t, t
        assert pg.locator("#inceput-carduri .inceput-card.inceput-facut").count() == 0, "un cabinet nou nu are niciun pas făcut"
        pg.click("#inceput-carduri .inceput-card[data-card='preluare'] [data-inceput='migrare']")
        pg.wait_for_selector(".fereastra:last-of-type #mig-meniu, .fereastra:last-of-type .mig-op, .fereastra:last-of-type .mig-frand",
                             timeout=30000)
        e.captura("migrare")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 01–04 — preluarea firmei
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# [lotul 13, pct.7] cu stocul (371) și creanța (4111) preluate; 1171 = profitul nerepartizat al anului 2025 (1.600 − impozitul micro 20)
BALANTA_DESCHIDERE = ("cont;denumire;sold debitor;sold creditor\n1012;Capital subscris vărsat;0;10000\n"
                      "1171;Rezultatul reportat reprezentând profitul nerepartizat;0;1580\n121;Profit sau pierdere;1000;0\n"
                      "371;Mărfuri;1000;0\n401;Furnizori;0;1000\n4111;Clienți;2420;0\n5121;Conturi la bănci în lei;7660;0\n"
                      "5311;Casa în lei;500;0\n")
BANCA_INITIAL = D("7660")


@pozitii("F084")
def test_pilot_01_preluarea_luna_si_balanta_de_deschidere(patron, firma_pilot):
    """F084. Pașii: Date firmă (vectorul fiscal: micro, TVA lunar) -> „Luna preluării” 09/2026 -> „Salvează”: „Datele firmei au fost
    salvate” -> Import date -> „Solduri inițiale” -> fișierul balanței la 31.08.2026 (8 conturi, debit = credit = 12.580) -> data propusă
    31.08.2026 -> „Salvează”: „8 conturi salvate, cu soldurile la 31.08.2026.” și pașii următori necesari (664): „Solduri parteneri —
    … 401 (creditor 1.000,00 lei în balanță) … 4111 (debitor 2.420,00 lei în balanță) …” și „Articole și stoc inițial — … 371 …” ->
    [lotul 13, pct.7] Import date -> „Articole și stoc inițial” -> „Marfă birou pilot”, 5 buc × 200,00 -> confruntarea cu balanța: „371:
    stoc inițial 1.000,00 lei · balanță 1.000,00 lei · se potrivesc” -> „Importă articolele”: „1 articol importat.”; în fișa de magazie
    intrarea „sold initial (import)” din 31.08.2026: 5 buc, 1.000,00."""
    f = firma_pilot
    pregateste_firma(patron, f)                      # date de pornire: profilul + vectorul (micro, TVA lunar), seria facturilor
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#df-luna_preluare", timeout=30000)
    pg.fill("#df-luna_preluare", "%d-%02d" % (AN, LUNA))
    pg.click("#df-salveaza")
    _asteapta_text(patron, "Datele firmei au fost salvate")
    patron.captura("luna_preluarii")
    _pas(patron, f, "Solduri ini")
    _incarca(patron, "balanta_31082026.csv", BALANTA_DESCHIDERE.encode("utf-8"), "#mig-salveaza-sold")
    assert pg.input_value("#mig-data-bal") == "2026-08-31", pg.input_value("#mig-data-bal")   # ultima zi dinaintea lunii preluării
    t = " ".join(patron.fereastra().split())
    assert "8 conturi" in t and "echilibrat" in t, t[:2000]
    pg.click("#mig-salveaza-sold")
    pg.wait_for_function("() => document.body.innerText.includes('8 conturi salvate, cu soldurile la 31.08.2026.')", timeout=30000)
    patron.captura("balanta")
    # [lotul 13, 664] salvarea numește pașii următori necesari: partenerii pe 401 și 4111, articolele pe 371 (cantitativ-valoric)
    pg.wait_for_function("() => document.body.innerText.includes('Pașii următori necesari pentru')", timeout=30000)
    t = " ".join(patron.fereastra().split())
    assert ("Solduri parteneri — De defalcat pe parteneri: 401 (creditor 1.000,00 lei în balanță) — partenerii dau 0,00 lei; 4111 "
            "(debitor 2.420,00 lei în balanță) — partenerii dau 0,00 lei.") in t, t[:3000]
    assert "Articole și stoc inițial — Articolele cu stocul inițial trebuie să dea soldul conturilor de stoc din balanță — 371" in t, t[:3000]
    # [lotul 13, pct.7] articolele cu stocul inițial, potrivit cu 371 (OMFP 1802/2014 pct.130: soldurile de deschidere)
    _pas(patron, f, "Articole")
    _incarca(patron, "articole_31082026.csv", ("denumire;um;cantitate;pret;cont stoc\n%s;buc;%d;%s;371\n"
                                               % (MARFA_STOC, STOC_INITIAL_CANT, STOC_INITIAL_PRET)).encode("utf-8"), "#mig-importa")
    rec = " ".join(pg.inner_text("#mig-reconciliere").split())
    patron.captura("articole")
    assert "371: stoc inițial %s lei · balanță %s lei · se potrivesc" % (_bani(STOC_INITIAL), _bani(STOC_INITIAL)) in rec, rec
    pg.click("#mig-importa")
    pg.wait_for_function("() => document.body.innerText.includes('1 articol importat.')", timeout=30000)
    patron.captura("articole_importate")
    st = sql('SELECT m.data::text, m.cantitate::text, m.valoare::text FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id '
             "WHERE a.denumire = %%s" % (f["schema"], f["schema"]), (MARFA_STOC,))
    assert [(d_, D(c), D(v)) for d_, c, v in st] == [("2026-08-31", D(STOC_INITIAL_CANT), STOC_INITIAL)], st


@pozitii("F085")
def test_pilot_02_soldurile_pe_parteneri(patron, firma_pilot):
    """F085. Pașii: Import date -> „Solduri parteneri” -> fișierul (401, Consultanță Înființare, creditor 1.000; [lotul 13, pct.7] 4111, Delta,
    debitor 2.420) -> previzualizarea: soldurile pe parteneri se potrivesc cu 401 și 4111 din balanță -> „Salvează”: „2 parteneri salvați.”,
    cu „2 facturi deschise preluate (de încasat 2.420,00 lei, de plătit 1.000,00 lei)”; în Import date, „Solduri parteneri” și
    „Articole și stoc inițial” sunt „gata”."""
    f = firma_pilot
    pg = patron.pg
    _pas(patron, f, "Solduri parteneri")
    csv = ("cont;cui;denumire;sold debitor;sold creditor\n401;RO%s;%s;0;1000\n4111;RO%s;%s;%s;0\n"
           % (INFIINTARE["cui"], INFIINTARE["nume"], DELTA["cui"], DELTA["nume"], CREANTA_DELTA))
    _incarca(patron, "parteneri_31082026.csv", csv.encode("utf-8"), "#mig-salveaza-part")
    coer = " ".join(patron.fereastra().split())
    assert "se potrivesc (401, 4111)" in coer, coer[:2000]
    pg.click("#mig-salveaza-part")
    pg.wait_for_function("() => document.body.innerText.includes('2 parteneri salvați.')", timeout=30000)
    t = " ".join(patron.fereastra().split())
    patron.captura()
    assert "2 facturi deschise preluate (de încasat %s lei, de plătit 1.000,00 lei)" % _bani(CREANTA_DELTA) in t, t[:2000]
    # [lotul 13, 663 / 665] pașii pe care balanța i-a făcut necesari sunt acum „gata”
    for strat in ("solduri_parteneri", "articole"):
        assert pg.get_attribute(".mig-frand[data-strat='%s'] [data-stare-pas]" % strat, "data-stare-pas") == "gata", strat


@pozitii("F183")
def test_pilot_03_auditul_de_preluare(patron, firma_pilot):
    """F183. Pașii: Control fiscal -> firma -> „Audit de preluare” -> „Rulează auditul de preluare”: „Primul audit după preluare”; contul 401:
    defalcarea pe parteneri (creditor 1.000,00 lei) coincide cu balanța; nimic „Divergent” pentru 401."""
    pg = patron.pg
    _control_firma(patron, firma_pilot)
    pg.wait_for_selector(_F + "#cf-audit-run", timeout=30000)
    pg.click(_F + "#cf-audit-run")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #cf-audit-istoric') || {innerText: ''}).innerText"
                         ".includes('Primul audit după preluare')", timeout=60000)
    text = " ".join(pg.inner_text(_F + "#cf-audit-istoric").split())
    patron.captura()
    assert "Contul 401: defalcarea pe parteneri (creditor 1.000,00 lei) coincide cu balanța." in text, text
    assert "Contul 401: parteneri" not in text, text
    # [lotul 13, pct.7] creanța preluată pe partener și stocul inițial pe articole dau balanța
    assert "Contul 4111: defalcarea pe parteneri (debitor %s lei) coincide cu balanța." % _bani(CREANTA_DELTA) in text, text
    assert "Stocul inițial dă soldurile din balanța de deschidere pe 1 cont." in text, text


@pozitii("F085")
def test_pilot_04_soldul_preluat_e_document_deschis(patron, firma_pilot):
    """252 (partea reparată: factura deschisă preluată). Pașii: după preluare, plata furnizorului preluat (Consultanță Înființare, 1.000 lei)
    găsește în Bancă un document deschis al partenerului, ca o factură. Citire: facturile deschise pe care le oferă potrivirea băncii (ruta
    ecranului Bancă, „Alege facturile”: `{facturi: [{tert_cui, directie, sold, …}]}`).
    [lotul 13, pct.7 + 669: „Soldurile preluate pe parteneri trebuie să apară ca sume de încasat/plătit, ca să poată fi stinse în prima
    lună.”] Încasarea creanței preluate: Casa -> „+ Dispoziție nouă” -> 03.09.2026, încasare de la client, 2.420,00, CUI-ul lui Delta ->
    „Factura încasată” oferă „Sold la 31.08.2026 · Delta · rămas 2.420,00 lei” (nu „Nicio factură emisă neîncasată”) -> bifată -> „Adaugă”:
    „Dispoziția a fost salvată”, nota 5311 = 4111 2.420,00 pe documentul preluat (nu avans: nici 419, nici 4427) -> documentul nu mai e
    deschis."""
    f = firma_pilot
    r = _ok(_api(patron, "GET", "/tenants/%d/banca/reconciliere/facturi-deschise" % f["tenant_id"]), "documentele deschise")
    gasite = [x for x in r.get("facturi", []) if str(x.get("tert_cui") or "").endswith(INFIINTARE["cui"])]
    # soldul creditor al lui 401 pe partener la 31.08.2026 (balanța de deschidere, pasul 02) = datoria de plătit
    assert len(gasite) == 1 and gasite[0]["directie"] == "primita" and _q(gasite[0]["sold"]) == D("1000.00"), r
    delta = [x for x in r.get("facturi", []) if str(x.get("tert_cui") or "").endswith(DELTA["cui"])]
    # soldul debitor al lui 4111 pe Delta la 31.08.2026 = creanța de încasat
    assert len(delta) == 1 and delta[0]["directie"] == "emisa" and _q(delta[0]["sold"]) == CREANTA_DELTA, r
    doc = delta[0]["id"]
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", zi(3).isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", str(CREANTA_DELTA))
    pg.fill("#c-cui", DELTA["cui"])
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-facturi [data-cf='%d']" % doc, timeout=30000)
    oferta = " ".join(pg.inner_text("#c-facturi").split())
    patron.captura("creanta_preluata")
    assert "Sold la 31.08.2026" in oferta and DELTA["nume"] in oferta and "rămas %s lei" % _bani(CREANTA_DELTA) in oferta, oferta
    pg.check("#c-facturi [data-cf='%d']" % doc)
    pg.click("#c-adauga")
    pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=30000)
    patron.captura("incasata")
    # OMFP 1802/2014: încasarea în numerar a creanței (5311 = 4111), pe documentul preluat — soldul lui e deja în balanța de deschidere
    assert [(d_, _sintetic(c), s) for d_, c, s in _note(f, "i.factura_id = %s", (doc,))] == [("5311", "4111", "%s.00" % CREANTA_DELTA)]
    r = _ok(_api(patron, "GET", "/tenants/%d/banca/reconciliere/facturi-deschise" % f["tenant_id"]), "documentele deschise")
    assert not [x for x in r.get("facturi", []) if x["id"] == doc], r


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 05–09 — nomenclatorul, NIR-ul cu transport, facturile primite, partenerii
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
_AI_COTA = json.dumps({"cota": 21, "categorie": "standard", "tip": "serviciu",
                       "justificare": "CF art.291 alin.(1): cota standard 21% pentru prestările de servicii", "incredere": "mare"},
                      ensure_ascii=False)


@pozitii("F070", "F023")
def test_pilot_05_nomenclatorul_cu_cota_propusa(patron, firma_pilot):
    """F070, F023. Pașii: Produse -> „+ Adaugă produs” -> denumirea serviciului, prețul 300 -> sub denumire, propunerea cotei: „TVA 21% ·
    AI”, cu justificarea (cota din regula oficială pe 09/2026: 21% — CF art.291 alin.(1)) -> „Salvează”: rândul are „TVA 21%” și
    „300,00 lei”. Răspunsul modelului e al plasei (`ICONTA_AI_SIMULAT`)."""
    ai_pregateste(*[_AI_COTA] * 4)
    pg = patron.pg
    patron.firma(firma_pilot["nume"])
    _card(patron, "produse", "#pr-add")
    pg.click("#pr-add")
    pg.wait_for_selector("#pr-den", timeout=20000)
    pg.fill("#pr-den", SERVICIU)
    pg.fill("#pr-pret", "300")
    pg.wait_for_selector("#pr-cota-preview .pr-cota-rezultat", timeout=30000)
    prev = " ".join(pg.inner_text("#pr-cota-preview").split())
    patron.captura("propunerea")
    assert "TVA 21% · AI" in prev and "CF art.291" in prev, prev            # CF art.291 alin.(1): cota standard 21%
    pg.click("#pr-salveaza")
    rand = pg.locator(".pr-rand", has_text=SERVICIU).first
    rand.wait_for(timeout=30000)
    t = " ".join(rand.inner_text().split())
    patron.captura("salvat")
    assert "TVA 21%" in t and "300,00 lei" in t, t


@pozitii("F139", "F089")
def test_pilot_06_nir_cu_transport(patron, firma_pilot):
    """F139, F089. Pașii: Stocuri -> „+ NIR nou” -> nr. 1 din 02.09.2026, furnizorul Mobila (CUI), factura n-a sosit -> articol nou
    „Marfă scaun ergonomic pilot”, 20 × 150,00, cota 21% -> transport 200,00, TVA transport 21% -> „Salvează NIR”: „NIR salvat · 4 note
    ciorne, la cost 3.200,00 lei (din care accesoriu 200,00 …” -> detaliul NIR-ului: transportul repartizat 200,00, cost final 3.200,00,
    cost unitar 160,00; notele 371 = 408 3.000,00 + 4428.01 = 408 630,00 + 371 = 408 200,00 + 4428.01 = 408 42,00; în fișa de magazie
    20 buc la 3.200,00."""
    f = firma_pilot
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "stocuri", "#sn-toggle")
    pg.click("#sn-toggle")
    pg.wait_for_selector("#sn-numar", timeout=20000)
    pg.fill("#sn-numar", "1")
    pg.fill("#sn-data", zi(2).isoformat())
    pg.fill("#sn-furn", MOBILA["nume"])
    pg.fill("#sn-cui", MOBILA["cui"])
    pg.select_option("#sn-factura-sosita", "false")
    pg.select_option("#nir-l0-articol", "nou")
    pg.fill("#nir-l0-denumire", MARFA)
    pg.fill("#nir-l0-cantitate", str(CANT_NIR))
    pg.fill("#nir-l0-pret_achizitie", "150")
    pg.select_option("#nir-l0-cota_tva", "21")
    pg.fill("#sn-transport", "200")
    pg.select_option("#sn-transport-cota", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('NIR salvat')", timeout=30000)
    msg = " ".join(pg.inner_text("#s-mesaj").split())
    patron.captura("salvat")
    # OMFP 1802/2014 pct.62 alin.(1): costul de achiziție = prețul + transportul atribuibil -> 3.200,00, din care accesoriu 200,00
    assert "4 note ciorne, la cost %s lei (din care accesoriu %s" % (_bani(COST_NIR), _bani(TRANSPORT)) in msg, msg
    # „NIR-urile lunii” pornesc pe luna de azi; NIR-ul din 02.09.2026 e în luna lui -> „← luna” până la 09/2026
    _la_luna(patron, "#s-prev", AN, LUNA)
    pg.click(".nir-deschide[data-numar='1']")
    pg.wait_for_selector("#nir-detaliu-linii", timeout=20000)
    celule = pg.eval_on_selector_all("#nir-detaliu-linii tbody tr", "rs => rs.map(r => [...r.cells].map(c => c.innerText.trim()))")
    note = pg.eval_on_selector_all("table.fd-tabel:last-of-type tbody tr", "rs => rs.map(r => [...r.cells].slice(1, 4).map(c => c.innerText.trim()))")
    patron.captura("detaliu")
    # OMFP 1802/2014 pct.96: costul unitar = 3.200,00 / 20 = 160,00 (CMP)
    assert celule and celule[0][-3:] == [_bani(TRANSPORT), _bani(COST_NIR), _bani(CMP)], celule
    # NIR fără factură: 408 (furnizori — facturi nesosite) și 4428 (TVA neexigibilă) până la factură (OMFP 1802/2014, funcțiunea
    # conturilor 408 și 4428); CF art.299 alin.(1) lit.a: deducerea cere factura
    assert sorted(map(tuple, note)) == sorted([("371", "408", "3.000,00"), ("4428.01", "408", "630,00"), ("371", "408", "200,00"),
                                               ("4428.01", "408", "42,00")]), note
    # [lotul 13, pct.7] numai intrările scaunului (articolul cu stocul inițial, „Marfă birou pilot”, are intrarea lui din 31.08)
    st = sql('SELECT sum(cantitate)::text, sum(valoare)::text FROM "%s".miscari_stoc WHERE tip = \'intrare\' AND articol_id = %%s' % f["schema"],
             (_articol_id(f),))
    assert st == [("20.000", "3200.00")] or (D(st[0][0]), D(st[0][1])) == (D(CANT_NIR), COST_NIR), st


@pozitii("F043", "F179", "F176")
def test_pilot_07_facturile_primite_din_e_factura(patron, firma_pilot):
    """F043, F179, F176. Pașii: Facturi -> „Facturi primite din SPV”: starea SPV — cabinetul de test nu e conectat la SPV, ecranul o spune
    și trimite la Conectare SPV (în plasă nu există SPV-ul real) -> „Importă XML UBL”: factura MF-901 a furnizorului Mobila (marfa 20 ×
    150,00 + transport 200,00, TVA 672,00) -> contul 371 -> „Validează”: aplicația propune NIR-ul nr. 1 („— propus”) -> „Leagă de NIR-ul
    ales”: nota închide 408 (408 = 401 3.872,00) și trece TVA-ul pe deductibil (4426 = 4428.01 672,00), fără al doilea 371 -> factura de
    chirie IMB-0925 (1.000 + 210) pe 612: 612 = 401 1.000,00, 4426 = 401 210,00."""
    f = firma_pilot
    pg = patron.pg
    cifre = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % f["schema"])[0][0] if c.isdigit())
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-spv", timeout=30000)
    spv = " ".join(pg.inner_text("#fp-spv").split())
    patron.captura("spv")
    assert "nu e conectat" in spv, spv
    xml = _ubl("MF-901", zi(3), MOBILA, f["nume"], cifre, [(MARFA, CANT_NIR, PRET_ACHIZITIE), ("Transport marfă", 1, TRANSPORT)])
    propus = _importa_si_valideaza(patron, f, xml, "MF-901", "371", nir=True)
    assert propus.startswith("NIR nr 1 ") and propus.endswith("— propus"), propus
    patron.captura("mobila")
    fid = sql('SELECT id FROM "%s".facturi WHERE numar = %%s' % f["schema"], ("MF-901",))[0][0]
    # nir_legare.note_factura_legata: 408 = 401 (costul + TVA-ul din NIR), 4426 = 4428.01 (CF art.299 alin.(1) lit.a: deducerea cu factura)
    assert _note(f, "i.factura_id = %s", (fid,)) == [("408", "401", "3872.00"), ("4426", "4428.01", "672.00")], _note(f, "i.factura_id = %s", (fid,))
    xml = _ubl("IMB-0925", zi(5), IMOB, f["nume"], cifre, [("Chirie spațiu comercial septembrie 2026", 1, CHIRIE)])
    _importa_si_valideaza(patron, f, xml, "IMB-0925", "612")
    patron.captura("chirie")
    fid = sql('SELECT id FROM "%s".facturi WHERE numar = %%s' % f["schema"], ("IMB-0925",))[0][0]
    assert [(_sintetic(d), _sintetic(c), s) for d, c, s in _note(f, "i.factura_id = %s", (fid,))] == [
        ("4426", "401", "210.00"), ("612", "401", "1000.00")]                 # CF art.299 alin.(1) lit.a; TVA = 1.000 × 21%


@pozitii("F018")
def test_pilot_08_partenerii_au_localitatea(patron, firma_pilot):
    """F018. Pașii: Furnizori -> furnizorii din facturile primite (Mobila, Imobiliare), fără fișă -> localitatea și județul -> „Salvează”:
    „… sunt în fișă — D406 și D394 le iau de aici.” (D406 cere localitatea fiecărui partener)."""
    pg = patron.pg
    for p in (MOBILA, IMOB):
        patron.firma(firma_pilot["nume"])
        pg.click("#fa-furnizori")
        pg.wait_for_selector(_F + "table.fd-tabel", timeout=30000)
        rand = pg.locator(_F + "table.fd-tabel tbody tr", has_text=p["cui"]).first
        rand.locator("input[id*='-oras-']").fill(p["oras"])
        rand.locator("select[id*='-judet-']").select_option(p["judet"])
        rand.locator("button[id*='-salveaza-']").click()
        pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('sunt în fișă')", timeout=30000)
        patron.captura("furnizor_%s" % p["cui"])
    assert {r[0] for r in sql('SELECT oras FROM "%s".furnizori' % firma_pilot["schema"])} >= {MOBILA["oras"], IMOB["oras"]}


@pozitii("F018")
def test_pilot_09_lista_partenerilor_cu_soldurile(patron, firma_pilot):
    """F018 (461). Pașii: fereastra firmei -> „Parteneri”: lista partenerilor firmei — furnizorii din facturi (Mobila, Imobiliare) și cel
    preluat din soldurile pe parteneri (Consultanță Înființare) -> „Fișa partenerului” la Consultanță Înființare: „Soldul din contabilitate”
    — contul 401, sold creditor 1.000,00 (soldul de preluare de la 31.08.2026, pasul 02; nicio plată încă) — și documentul lui deschis
    (factura preluată, 252). Citire: numai ecranul."""
    pg = patron.pg
    patron.firma(firma_pilot["nume"])
    pg.click("#fa-parteneri")
    pg.wait_for_selector(_F + "#pt-tabel", timeout=30000)
    lista = " ".join(pg.inner_text(_F + "#pt-tabel").split())
    patron.captura("lista")
    assert INFIINTARE["nume"] in lista and MOBILA["nume"] in lista and IMOB["nume"] in lista, lista[:2000]
    pg.locator(_F + "#pt-tabel tbody tr", has_text=INFIINTARE["nume"]).first.locator(".pt-deschide").click()
    pg.wait_for_selector(_F + "#pp-sold, " + _F + "#pp-sold-gol", timeout=30000)
    patron.captura("fisa")
    sold = [[c.strip() for c in r] for r in pg.eval_on_selector_all(
        _F + "#pp-sold tbody tr", "rs => rs.map((r) => [...r.cells].map((c) => c.innerText))")]
    # OMFP 1802/2014, funcțiunea contului 401 (sold creditor = datoria față de furnizor); soldul de preluare pe partener (pasul 02)
    assert [r for r in sold if r[0].split(".")[0] == "401"] and all(r[2:4] == ["", "1.000,00"] for r in sold if r[0].split(".")[0] == "401"), sold


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 10–17 — vânzările: facturi emise, casa, raportul Z, factura pe bon
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F172", "F045", "F046", "F252", "F126")
def test_pilot_10_factura_cu_descarcarea_stocului(patron, firma_pilot):
    """F172, F045, F046, F252, F126. Pașii: Facturi -> „Emite factură” -> data 10.09.2026, clientul Alfa (CUI, localitate) -> linia 1:
    articolul „Marfă scaun ergonomic pilot”, 10 × 300,00, 21% -> linia 2: „Servicii de montaj mobilier pilot”, 1 × 300,00 -> țara RO,
    operațiune normală -> „Emite” -> „Pleacă marfa acum?” -> „Da, pleacă marfa”: „✓ Factura E2EA nr. 1 emisă · total 3.993,00 RON · 1 articol
    descărcat din gestiune.” -> notele: 4111 = 707 3.000,00, 4111 = 704 300,00, 4111 = 4427 693,00 și descărcarea 607 = 371 1.600,00 (10 ×
    CMP 160,00) -> Istoric -> factura -> PDF: „Seria E2EA nr. 1”, totalul 3.993,00 -> „Trimite în SPV”: cabinetul nu e conectat la SPV,
    cu drumul spre Conectare SPV."""
    f = firma_pilot
    rez = _emite_pe_ecran(patron, f, zi(10), ALFA, [(MARFA, 10, 300, True), (SERVICIU, 1, 300, False)], pleaca=True)
    patron.captura("emisa")
    total = _q(sum(E1) * (1 + COTA))                                   # CF art.286 alin.(1) + art.291 alin.(1): 3.300 + 693
    # [lotul 12, 443.1] seria și numărul separat, ca în Istoric („E2EA nr. 1”), nu lipite („E2EA1”)
    assert rez.startswith("✓ Factura E2EA nr. 1 emisă · total %s RON" % _bani(total)) and "1 articol descărcat din gestiune" in rez, rez
    fid, numar = _factura(f, "1")
    f["e1"] = fid
    note = [(_sintetic(d), c, s) for d, c, s in _note(f, "i.factura_id = %s", (fid,)) if d != "607"]
    # OMFP 1802/2014: 4111 = 707 (mărfuri), 4111 = 704 (servicii), 4111 = 4427 (TVA colectată 21%)
    assert sorted(note) == sorted([("4111", "707", "3000.00"), ("4111", "704", "300.00"), ("4111", "4427", "693.00")]), note
    # OMFP 1802/2014 pct.96: ieșirea la CMP — 10 × 160,00
    assert _note(f, "l.cont_debit = '607' AND i.data = %s", (zi(10),)) == [("607", "371", str(_q(10 * CMP)))]
    pg = patron.pg
    _deschide_factura_luna(patron, f, fid)
    with pg.expect_response(lambda r: r.url.endswith("/facturi/%s/pdf" % fid), timeout=30000) as rr:
        pg.click("#fd-pdf")
    text, _t = _pdf_text(_pdf_ok(patron, rr))
    assert "Seria E2EA nr. 1" in text and _bani(total) in text, text[:2000]       # CF art.319 alin.(20): seria, numărul, totalul
    st = pg.inner_text("#fd-stare-spv")
    assert st.startswith("netrimisă în SPV · termen "), st
    pg.click("#fd-spv")
    pg.click("#ca-ok")
    pg.wait_for_function("() => (document.querySelector('#fd-spv-zona') || {innerText: ''}).innerText.includes('nu e conectat la SPV')",
                         timeout=20000)
    pg.wait_for_selector("#fd-spv-zona [data-ecran-destinatie='conectare_spv']", timeout=20000)
    patron.captura("spv")


@pozitii("F015", "F017")
def test_pilot_11_incasarea_in_casa_cu_chitanta(patron, firma_pilot):
    """F015, F017. Pașii: Casa -> „+ Dispoziție nouă” -> 12.09.2026, încasare de la client, 3.993,00, CUI-ul lui Alfa -> factura E2EA1 bifată
    -> „Adaugă”: „Dispoziția a fost salvată” și chitanța emisă -> nota 5311 = 4111 3.993,00 -> factura: PDF-ul chitanței are suma
    („3.993,00”) și suma în litere („trei mii nouă sute nouăzeci și trei de lei”)."""
    f = firma_pilot
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", zi(12).isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "3993")
    pg.fill("#c-cui", ALFA["cui"])
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_selector("#c-facturi [data-cf='%d']" % f["e1"], timeout=30000)
    pg.check("#c-facturi [data-cf='%d']" % f["e1"])
    pg.click("#c-adauga")
    pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=30000)
    t = " ".join(patron.fereastra().split())
    patron.captura("dispozitia")
    # OMFP 2634/2015: chitanța pentru încasarea în numerar; numărul ei se scrie cu seria, „<serie> nr. <n>” (ca factura)
    assert re.search(r"Chitanța (\S+ nr\. )?\d+ a fost emisă", t), t[:2000]
    assert _note(f, "i.data = %s AND l.cont_debit = '5311'", (zi(12),)) and [
        (d, _sintetic(c), s) for d, c, s in _note(f, "i.data = %s AND l.cont_debit = '5311'", (zi(12),))] == [("5311", "4111", "3993.00")]
    _deschide_factura_luna(patron, f, f["e1"])
    pg.wait_for_selector("[data-chpdf]", timeout=20000)
    with pg.expect_response(lambda r: "/chitante/" in r.url and r.url.endswith("/pdf"), timeout=30000) as rr:
        pg.click("[data-chpdf]")
    text, _t = _pdf_text(_pdf_ok(patron, rr))
    patron.captura("chitanta")
    assert "trei mii nouă sute nouăzeci și trei de lei" in text and "3.993,00" in text, text[:1500]


@pozitii("F003", "F089")
def test_pilot_12_raportul_z_si_descarcarea_lui(patron, firma_pilot):
    """F003 (raportul Z scris de contabil), F089. Pașii: Raport Z -> 15.09.2026, casa 8000000001, raportul 0042, total 21% 726,00, numerar
    726,00, card 0, 2 bonuri -> „Generează notă”: „5311 = 707 · 726,00 lei” și „707 = 4427 · 126,00 lei” (TVA inclusă: 726 × 21/121) -> la
    descărcare: articolul, 2 buc -> „Ieșire pe articol”: „Ieșire înregistrată: 320,00 lei” (2 × CMP 160,00) -> „Validează raportul Z” ->
    confirmarea cu cifrele (474): „Ai descărcat din stoc 1 ieșire la cost 320,00 lei, pentru vânzări de 600,00 lei fără TVA pe acest Z
    (adaos 88%)” -> „Da, validează raportul Z”: Z-ul e validat."""
    f = firma_pilot
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-raportz")
    pg.wait_for_selector("#z-salveaza", timeout=30000)
    for sel, v in (("#z-data", zi(15).isoformat()), ("#z-nui", CASA_Z), ("#z-nr", "0042"), ("#z-21", str(Z_TOTAL)),
                   ("#z-num", str(Z_TOTAL)), ("#z-card", "0"), ("#z-bonuri", str(Z_BONURI))):
        pg.fill(sel, v)
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('Notă generată')", timeout=30000)
    linii = " ".join(pg.inner_text("#z-nota-linii").split())
    patron.captura("nota")
    # CF art.291 alin.(1) + art.286 alin.(1): prețul cu TVA inclusă -> baza 600,00, TVA 126,00
    assert "5311 = 707 · %s lei" % _bani(Z_TOTAL) in linii and "707 = 4427 · %s lei" % _bani(Z_TVA) in linii, linii
    (zid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-%s-0042" % CASA_Z,))]
    f["z"] = zid
    pg.wait_for_selector("#z-descarcare [data-z='%d']" % zid, timeout=20000)
    pg.select_option("#zd-art-%d" % zid, str(_articol_id(f)))
    pg.fill("#zd-cant-%d" % zid, "2")
    pg.click(".zd-iesire[data-z='%d']" % zid)
    pg.wait_for_function("() => (document.querySelector('#zd-rez') || {innerText: ''}).innerText.includes('Ieșire înregistrată')", timeout=20000)
    assert "Ieșire înregistrată: %s lei" % _bani(2 * CMP) in pg.inner_text("#zd-rez"), pg.inner_text("#zd-rez")   # OMFP 1802/2014 pct.96
    _valideaza_z(patron, f, zid, 2 * CMP, Z_BAZA)
    patron.captura("validat")


AMEF_Z = ('<?xml version="1.0" encoding="UTF-8"?><msj idM="{idr}"><rB idR="{idr}" nrAv="0" nrB="1" totB="363.00" nrBC="0" totBC="0" nrA="0" '
          'totA="0" nrR="0" totR="0" nrM="0" totM="0" totTva="63.00" totTvaC="0" totTaxes="0" totTaxe="0" totNet="0" sume_serv_in="0" '
          'sume_serv_out="0" monRef="RON"><pl tipP="3" valPl="363.00" monPl="RON"/><coteZ cota="21" valOp="363.00" tva="63.00"/></rB></msj>')


@pozitii("F003")
def test_pilot_13_raportul_z_din_fisierul_amef(patron, firma_pilot):
    """F003 (importul fișierului AMEF, OPANAF 146/2018 anexa 2 secțiunea II.7). Pașii: Raport Z -> „Import fișier AMEF” -> raportul
    0041 din 14.09.2026 (1 bon, 363,00 numerar, cota 21%) -> „Importat: raportul Z din 14.09.2026, total 363,00 lei” -> secțiunea descărcării
    trece pe luna Z-ului (09/2026, C118), cu raportul 0041 printre cele nevalidate -> articolul, 1 buc -> „Ieșire pe articol”: „Ieșire
    înregistrată: 160,00 lei” (1 × CMP 160,00) -> „Validează raportul Z” -> confirmarea cu cifrele (474) -> Z-ul e validat; nota lui:
    5311 = 707 363,00 și 707 = 4427 63,00 (prețul cu TVA inclusă: 363 × 21/121)."""
    f = firma_pilot
    pg = patron.pg
    idr = "%s%s%s" % (CASA_Z, "20260914183000", "0041")              # 10 NUI + AAAALLZZHHMMSS + 4 nr raport (OPANAF 146/2018)
    patron.firma(f["nume"])
    pg.click("#fa-raportz")
    pg.wait_for_selector("#z-salveaza", timeout=30000)
    pg.set_input_files("#z-amef", {"name": "z_0041.xml", "mimeType": "text/xml", "buffer": AMEF_Z.format(idr=idr).encode("utf-8")})
    pg.wait_for_function("() => (document.querySelector('#z-amef-msg') || {innerText: ''}).innerText.includes('Importat')", timeout=30000)
    msg = " ".join(pg.inner_text("#z-amef-msg").split())
    assert "Importat: raportul Z din 14.09.2026, total %s lei" % _bani(Z2_TOTAL) in msg, msg
    (zid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-%s-0041" % CASA_Z,))]
    f["z2"] = zid
    patron.captura("importat")
    # CF art.291 alin.(1) + art.286 alin.(1): prețul cu TVA inclusă -> baza 300,00, TVA 63,00
    assert sorted((d, c, s) for d, c, s in _note(f, "i.id = %s", (zid,))) == sorted([("5311", "707", str(Z2_TOTAL)), ("707", "4427", str(Z2_TVA))])
    # [C118] descărcarea e pe luna Z-ului importat, nu pe luna de azi
    pg.wait_for_selector("#z-descarcare [data-z='%d'] #zd-art-%d" % (zid, zid), timeout=20000)
    pg.select_option("#zd-art-%d" % zid, str(_articol_id(f)))
    pg.fill("#zd-cant-%d" % zid, "1")
    pg.click(".zd-iesire[data-z='%d']" % zid)
    pg.wait_for_function("() => (document.querySelector('#zd-rez') || {innerText: ''}).innerText.includes('Ieșire înregistrată')", timeout=20000)
    assert "Ieșire înregistrată: %s lei" % _bani(CMP) in pg.inner_text("#zd-rez"), pg.inner_text("#zd-rez")   # OMFP 1802/2014 pct.96
    _valideaza_z(patron, f, zid, CMP, Z2_BAZA)
    patron.captura("validat")


@pozitii("F254")
def test_pilot_14_factura_pe_baza_bonului_fiscal(patron, firma_pilot):
    """F254. Pașii: Emite factură -> 15.09.2026, clientul Gamma -> articolul, 1 × 300,00, 21% -> „Emisă pe baza bonului fiscal”: bonul 0002
    din 15.09.2026 -> „Emite”: fără „Pleacă marfa acum?” (marfa a plecat pe bon), „✓ Factura E2EA nr. 2 emisă · total 363,00 RON”, fără descărcare
    -> factura nu are notă (vânzarea e în raportul Z: HG 1/2016 pct.97 alin.(1) — factura se emite „conform bon fiscal”)."""
    f = firma_pilot
    rez = _emite_pe_ecran(patron, f, zi(15), GAMMA, [(MARFA, 1, 300, True)], bon=("0002", zi(15)))
    patron.captura()
    assert rez.startswith("✓ Factura E2EA nr. 2 emisă · total %s RON" % _bani(sum(BON))) and "descărcat" not in rez, rez   # [443.1]
    fid, _n = _factura(f, "2")
    f["e2"] = fid
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE factura_id = %%s' % f["schema"], (fid,)) == [(0,)], "factura pe bon are notă"
    assert sql('SELECT count(*) FROM "%s".miscari_stoc WHERE factura_id = %%s' % f["schema"], (fid,)) == [(0,)], "factura pe bon a descărcat"


@pozitii("F015")
def test_pilot_15_depunerea_numerarului(patron, firma_pilot):
    """F015. Pașii: Casa -> „+ Dispoziție nouă” -> 18.09.2026, depunere la bancă, 3.000,00 -> „Adaugă”: „Dispoziția a fost salvată” -> nota
    581 = 5311 3.000,00 (plafonul de numerar nu e atins: Legea 70/2015)."""
    f = firma_pilot
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", zi(18).isoformat())
    pg.select_option("#c-cat", "depunere_banca")
    pg.fill("#c-suma", "3000")
    pg.fill("#c-doc", "Foaie de vărsământ nr. 1 din 18.09.2026")
    pg.click("#c-adauga")
    pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=30000)
    patron.captura()
    assert _note(f, "i.data = %s AND l.cont_credit = '5311'", (zi(18),)) == [("581", "5311", "3000.00")]


@pozitii("F172", "F046")
def test_pilot_16_a_doua_factura_cu_marfa(patron, firma_pilot):
    """F172, F046. Pașii: Emite factură -> 20.09.2026, clientul Beta -> articolul, 5 × 300,00, 21% -> „Emite” -> „Da, pleacă marfa”:
    „✓ Factura E2EA nr. 3 emisă · total 1.815,00 RON · 1 articol descărcat din gestiune.” -> notele 4111 = 707 1.500,00, 4111 = 4427 315,00,
    607 = 371 800,00 (5 × CMP 160,00)."""
    f = firma_pilot
    rez = _emite_pe_ecran(patron, f, zi(20), BETA, [(MARFA, 5, 300, True)], pleaca=True)
    patron.captura()
    assert rez.startswith("✓ Factura E2EA nr. 3 emisă · total %s RON" % _bani(sum(E3) * (1 + COTA))) and "descărcat" in rez, rez   # [443.1]
    fid, _n = _factura(f, "3")
    f["e3"] = fid
    note = [(_sintetic(d), c, s) for d, c, s in _note(f, "i.factura_id = %s", (fid,)) if d != "607"]
    assert sorted(note) == sorted([("4111", "707", "1500.00"), ("4111", "4427", "315.00")]), note
    assert _note(f, "l.cont_debit = '607' AND i.data = %s", (zi(20),)) == [("607", "371", "800.00")]   # OMFP 1802/2014 pct.96: 5 × 160


@pozitii("F046", "F131")
def test_pilot_17_factura_de_servicii_neincasata(patron, firma_pilot):
    """F046. Pașii: Emite factură -> 29.09.2026, clientul Alfa -> „Servicii de montaj mobilier pilot”, 1 × 300,00 -> „Emite” (fără poartă:
    serviciu): „✓ Factura E2EA nr. 4 emisă · total 363,00 RON” -> notele 4111 = 704 300,00, 4111 = 4427 63,00; scadența 29.10.2026."""
    f = firma_pilot
    rez = _emite_pe_ecran(patron, f, zi(29), ALFA, [(SERVICIU, 1, 300, False)])
    patron.captura()
    assert rez.startswith("✓ Factura E2EA nr. 4 emisă · total 363,00 RON"), rez   # [443.1]
    fid, _n = _factura(f, "4")
    f["e4"] = fid
    note = [(_sintetic(d), c, s) for d, c, s in _note(f, "i.factura_id = %s", (fid,))]
    assert sorted(note) == sorted([("4111", "704", "300.00"), ("4111", "4427", "63.00")]), note
    assert sql('SELECT data_scadenta::text FROM "%s".facturi WHERE id = %%s' % f["schema"], (fid,)) == [("2026-10-29",)]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 18 — banca
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F012", "F011", "F073")
def test_pilot_18_extrasul_de_banca_si_potrivirea(patron, firma_pilot):
    """F012, F011, F073. Pașii: Bancă -> extrasul septembrie (CSV, 6 linii) -> „6 linii importate: 4 potrivite pe facturi, 2 fără potrivire”;
    încasarea Beta 1.815,00 -> „Potrivire exactă” pe E2EA3; plata Mobila 3.872,00 și chiria 1.210,00 -> potrivire exactă pe facturile
    primite; plata Consultanță 1.000,00 -> potrivire exactă pe factura deschisă preluată (252, pasul 04); depunerea numerarului -> 5121 =
    581; comisionul -> 627 = 5121 -> „Contează” pe
    fiecare: notele 5121 = 4111 1.815, 401 = 5121 3.872 / 1.210 / 1.000, 5121 = 581 3.000, 627 = 5121 15."""
    f = firma_pilot
    pg = patron.pg
    extras = ("Data;Detalii;Suma\n"
              "05.09.2026;Plata servicii CONSULTANTA INFIINTARE CUI {c6};-1000,00\n"
              "18.09.2026;Depunere numerar casierie;3000,00\n"
              "25.09.2026;Incasare factura E2EA3 CUI {cb};1815,00\n"
              "28.09.2026;Plata factura MF-901 CUI {cm};-3872,00\n"
              "28.09.2026;Plata chirie septembrie CUI {ci};-1210,00\n"
              "30.09.2026;Comision administrare cont;-15,00\n").format(c6=INFIINTARE["cui"], cb=BETA["cui"], cm=MOBILA["cui"], ci=IMOB["cui"])
    patron.firma(f["nume"])
    _card(patron, "banca", "#bk-fisier")
    pg.set_input_files("#bk-fisier", {"name": "extras_092026.csv", "mimeType": "text/csv", "buffer": extras.encode("utf-8")})
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('importate')", timeout=30000)
    msg = " ".join(pg.inner_text("#bk-mesaj").split())
    patron.captura("import")
    assert "6 linii importate: 4 potrivite pe facturi, 2 fără potrivire" in msg, msg

    def _rand(text):
        r = pg.locator("#bk-lista .pf-frand", has_text=text).first
        r.wait_for(timeout=20000)
        return r, " ".join(r.inner_text().split())

    for text, potrivire in (("Incasare factura E2EA3", "Potrivire exactă"), ("Plata factura MF-901", "Potrivire exactă"),
                            ("Plata chirie septembrie", "Potrivire exactă"), ("CONSULTANTA INFIINTARE", "Potrivire exactă"),
                            ("Depunere numerar", "581"), ("Comision administrare", "627")):
        r, t = _rand(text)
        assert potrivire in t, (text, t)
        inainte = pg.inner_text("#bk-mesaj")
        buton = r.locator("[data-cont]").first
        buton.scroll_into_view_if_needed()
        _asteapta_nemiscat(pg, buton)            # derularea „mesajul în vedere” (api.aduInVedere, smooth) s-a oprit: clicul cade pe buton
        sub = _ce_e_sub(pg, buton)              # ce stă sub centrul butonului chiar înainte de clic
        esuate = []   # [diagnostic, pasul 18] cererea anulată de browser (ERR_ABORTED / ERR_FAILED) sau rămasă fără răspuns
        _asc = lambda q: esuate.append((q.url, q.failure)) if "/conteaza" in q.url else None   # noqa: E731
        pg.on("requestfailed", _asc)
        try:
            cid = buton.get_attribute("data-cont")   # contarea trebuie să plece pentru linia ACESTUI rând
            with pg.expect_response(lambda q: q.url.endswith("/reconciliere/%s/conteaza" % cid) and q.request.method == "POST", timeout=30000):
                buton.click()
        except Exception:
            patron.captura("clic_pierdut")
            raise AssertionError("contarea (%s) n-a primit răspuns; cereri eșuate în browser: %s; înainte de clic: %s; după: %s"
                                 % (text, esuate, sub, _ce_e_sub(pg, buton) if buton.count() else "butonul nu mai e în pagină"))
        finally:
            pg.remove_listener("requestfailed", _asc)
        # confirmarea contării = rândul ACESTEI linii ajunge „Contat…” după reîncărcarea listei (`incarca`), iar zona de mesaj spune
        # „… creată”. NU „mesajul s-a schimbat”: două plăți din aceeași zi pe aceeași notă dau același text („Notă 401=5121 creată (…)”,
        # MF-901 și chiria, 28.09) — de acolo căderea din v6–v12, la a TREIA contare (chiria), deși ea plecase și se scrisese
        pg.wait_for_function("(t) => { const r = [...document.querySelectorAll('#bk-lista .pf-frand')].find((x) => x.innerText.includes(t)); "
                             "return r && /Contat/.test(r.querySelector('.pf-frand-nume').innerText); }", arg=text, timeout=30000)
        assert "creat" in pg.inner_text("#bk-mesaj"), (text, inainte, pg.inner_text("#bk-mesaj"))
    patron.captura("contat")
    note = sorted((_sintetic(d), _sintetic(c), s) for d, c, s in _note(f, "i.sursa = 'banca'"))
    assert note == sorted([("5121", "4111", "1815.00"), ("401", "5121", "3872.00"), ("401", "5121", "1210.00"), ("401", "5121", "1000.00"),
                           ("5121", "581", "3000.00"), ("627", "5121", "15.00")]), note


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 19–23 — salariații, statul de plată, concediul medical, nota, plata pe card
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F078")
def test_pilot_19_salariatii(patron, firma_pilot):
    """F078. Pașii: Salariați -> „+ Salariat nou” (de două ori): POPA ANDREI, 8.000 lei, și MARIN ELENA, 8.800 lei — angajați la 01.09.2026,
    normă întreagă, funcția de bază, fără persoane în întreținere, contract pe durată nedeterminată, COR -> „Salvează”: „Salariat salvat.”"""
    f = firma_pilot
    pg = patron.pg
    for s in (SAL1, SAL2):
        patron.firma(f["nume"])
        _card(patron, "salariati", "#sp-salariat-nou")
        pg.click("#sp-salariat-nou")
        pg.wait_for_selector("#sn-salveaza", timeout=20000)
        for sel, v in (("#sn-nume", s["nume"]), ("#sn-prenume", s["prenume"]), ("#sn-cnp", _cnp(s["cnp"])), ("#sn-data_angajare", "2026-09-01"),
                       ("#sn-salariu_brut", str(s["brut"])), ("#sn-persoane_intretinere", "0"), ("#sn-judet_casa", "B")):
            pg.fill(sel, v)
        for sel, v in (("#sn-tip_norma", "intreaga"), ("#sn-declaratie_copii", "false"), ("#sn-functie_baza", "true"),
                       ("#sn-scutit_contrib_minim", "false"), ("#sn-tip_contract", "nedeterminata")):
            pg.click("%s-grup [data-v='%s']" % (sel, v))   # [lotul 13, 676] listele scurte = butoane alăturate
        pg.fill("#sn-cor-cauta", s["cor"])
        pg.wait_for_selector("#sn-cor-rez [data-cod='%s']" % s["cor"], timeout=20000)
        pg.click("#sn-cor-rez [data-cod='%s']" % s["cor"])
        pg.click("#sn-salveaza")
        pg.wait_for_function("() => (document.querySelector('#sn-mesaj') || {innerText: ''}).innerText.includes('Salariat salvat')",
                             timeout=30000)
        patron.captura(s["nume"].lower())
    assert sql('SELECT count(*) FROM "%s".salariati' % f["schema"]) == [(2,)]


@pozitii("F080", "F087")
def test_pilot_20_statul_de_plata_cu_concediul_medical(patron, firma_pilot):
    """F080, F087. Pașii: Salariați -> statul lunii 09/2026 -> MARIN ELENA: „Concediu” -> „+ Certificat nou”: seria PL,
    nr. 90001, cod 01 (boală obișnuită), acordat 14.09.2026, 14–18.09.2026 -> zilele propuse 5 -> nu e continuare, fără spitalizare, fără
    program național -> veniturile din 6 luni 31.250,00 pe 125 de zile (adeverința angajatorului anterior) -> „Calculează și salvează”:
    media zilnică 250,00 lei, 55%, 4 zile plătite (după diminuarea cu o zi), suportat de angajator 550,00, FNUASS 0,00, brută 550,00, CASS
    55,00, impozit 36,00, net 321,00 -> statul: POPA ANDREI brut 8.000,00 · CAS 2.000,00 · CASS 800,00 · impozit 520,00 · net 4.680,00;
    MARIN ELENA brut 6.800,00 (17 din 22 de zile) · CAS 1.700,00 · CASS 680,00 · impozit 442,00 · net 4.299,00 (salariu 3.978,00 +
    indemnizație CM 321,00)."""
    f = firma_pilot
    pg = _stat_09(patron, f)
    _salariat(pg, SAL2["nume"])
    pg.click(_F + "#ss-butoane [data-cm]")
    pg.wait_for_selector(_F + "#cm-nou", timeout=20000)
    pg.click(_F + "#cm-nou")
    pg.wait_for_selector(_F + "#cm-calc", timeout=20000)
    pg.fill(_F + "#cm-serie", "PL")
    pg.fill(_F + "#cm-numar", "90001")
    pg.select_option(_F + "#cm-cod", "01")
    pg.fill(_F + "#cm-acord", zi(14).isoformat())
    pg.fill(_F + "#cm-inceput", zi(14).isoformat())
    pg.fill(_F + "#cm-sfarsit", zi(18).isoformat())
    _propunerea_zilelor(pg, ZILE_CM)                                    # 14–18.09.2026: luni–vineri, 5 zile lucrătoare
    for sel in ("#cm-continuare", "#cm-spital", "#cm-program-national"):
        pg.click(_F + sel + "-grup [data-v='false']")                  # [lotul 13, 676] Da / Nu = butoane
    pg.fill(_F + "#cm-ven6", str(CM_VEN6))
    pg.fill(_F + "#cm-zile6", str(CM_ZILE6))
    pg.click(_F + "#cm-calc")
    pg.wait_for_selector(_F + "#cm-rezultat .panou", timeout=30000)
    rez = " ".join(pg.inner_text(_F + "#cm-rezultat").split())
    patron.captura("cm")
    assert "Concediu salvat" in rez, rez
    assert "Media zilnică %s lei" % _bani(CM_MEDIE) in rez, rez                    # OUG 158/2005 art.10 alin.(1)
    assert "Procent 55" in rez, rez                                                  # OUG 158/2005 art.17 alin.(1) lit.a
    assert "Zile plătite (după diminuare 1 zi) %d" % CM_ZILE_PLATITE in rez, rez     # OUG 91/2025 art.II alin.(1)
    assert "Suportat angajator (zile 2–6) %s lei" % _bani(CM_BRUT) in rez, rez      # OUG 91/2025 art.II alin.(1) lit.a
    assert "Suportat FNUASS (din ziua 7) 0,00 lei" in rez, rez
    assert "Indemnizație brută %s lei" % _bani(CM_BRUT) in rez, rez
    assert "CASS %s lei" % _bani(CM_CASS) in rez, rez                               # CF art.155 alin.(1) lit.i, art.157 alin.(1) lit.v
    assert "Impozit %s lei" % _bani(CM_IMPOZIT) in rez, rez                         # CF art.78 alin.(2) lit.a
    assert "Net %s lei" % _bani(CM_NET) in rez, rez
    pg = _stat_09(patron, f)
    r1, r2 = _sume(_rand_stat(pg, SAL1["nume"])), _sume(_rand_stat(pg, SAL2["nume"]))
    patron.captura("statul")
    # CF art.138 lit.a (CAS 25%), art.156 (CASS 10%), art.78 alin.(2) lit.a (impozit 10% pe brut − CAS − CASS − deducerea), art.77 alin.(3)
    # (fără deducere peste 6.325 lei)
    assert r1 == {"brut": _bani(SAL1["brut"]), "CAS": _bani(S1[0]), "CASS": _bani(S1[1]), "impozit": _bani(S1[2]), "net": _bani(S1[3])}, r1
    # Codul muncii art.159 alin.(1) (salariul pentru munca prestată): 8.800 × 17 / 22 = 6.800,00
    assert (r2["brut"], r2["CAS"], r2["CASS"], r2["impozit"]) == (_bani(SAL2_LUCRAT), _bani(S2[0]), _bani(S2[1]), _bani(S2[2])), r2
    assert "net %s (salariu %s + indemnizație CM %s)" % (_bani(S2[3] + CM_NET), _bani(S2[3]), _bani(CM_NET)) in _rand_stat(pg, SAL2["nume"])


@pozitii("F080")
def test_pilot_21_concediul_medical_arata_cas_ul(patron, firma_pilot):
    """F080 (482: „rețineri din CM neafișate”). Pașii: Salariați -> statul 09/2026 -> MARIN ELENA: „Compoziția netului” -> sub „Indemnizație
    CM (netă)” 321,00: indemnizația CM brută 550,00 și reținerile din ea, pe fel — CAS (25%) 138,00 (CF art.144: baza CAS = indemnizația, 550
    × 25% = 137,5 -> 138), CASS (10%) 55,00 (CF art.155 alin.(1) lit.i, art.157 alin.(1) lit.v), impozit 36,00 (CF art.78 alin.(2) lit.a) —,
    iar brutul minus reținerile = netul (netul se reface din ecran)."""
    from e2e_lot11_s9 import _randuri_compozitie
    pg = _stat_09(patron, firma_pilot)
    # [lotul 13, 677] fereastra salariatului: indemnizația o dată, cu brutul și netul pe același rând; reținerile ei în „Rețineri”
    _salariat(pg, SAL2["nume"])
    c = _coloane(pg)
    comp = _randuri_compozitie(c)
    patron.captura()
    asteptat = {"Indemnizație concediu medical": CM_BRUT, "reținut din indemnizație: CAS (25%)": CM_CAS,
                "reținut din indemnizație: CASS (10%)": CM_CASS, "reținut din indemnizație: impozit pe venit": CM_IMPOZIT}
    assert {k: comp.get(k) for k in asteptat} == asteptat, comp
    assert D(str(c["Indemnizație concediu medical"][1])) == CM_NET, c
    assert CM_BRUT - CM_CAS - CM_CASS - CM_IMPOZIT == CM_NET


@pozitii("F087")
def test_pilot_22_contabilizarea_statului_si_fluturasul(patron, firma_pilot):
    """F087. Pașii: statul 09/2026 -> „Fluturaș” la POPA ANDREI: PDF-ul „Fluturaș de salariu — 09/2026”, cu CAS (25%) și netul 4.680,00 ->
    „Contabilizează statul”: „Contul 421 se soldează exact cu netul fluturașilor (8.658,00 lei).” și „Contul 423 … (321,00 lei)” -> „Scrie
    nota ciornă”: nota salariilor e scrisă."""
    import base64
    import io as _io
    from pypdf import PdfReader
    f = firma_pilot
    pg = _stat_09(patron, f)
    _salariat(pg, SAL1["nume"])   # [lotul 13, 677] „Fluturaș” e butonul ferestrei salariatului
    with pg.expect_response(lambda r: "/fluturas/" in r.url, timeout=30000) as rr:
        pg.click(_F + "#ss-butoane [data-flut]")
    assert rr.value.status == 200, rr.value.status
    b64 = pg.evaluate("""async (u) => { const t = sessionStorage.getItem('iconta_token');
      const x = await fetch(u, {headers: {'Authorization': 'Bearer ' + t}}); const b = new Uint8Array(await x.arrayBuffer());
      let s = ''; for (const c of b) s += String.fromCharCode(c); return btoa(s); }""", rr.value.url)
    text = " ".join("\n".join(p.extract_text() for p in PdfReader(_io.BytesIO(base64.b64decode(b64))).pages).split())
    patron.captura("fluturas")
    assert "Fluturaș de salariu — %02d/%d" % (LUNA, AN) in text and "CAS (25%)" in text and _bani(S1[3]) in text, text[:2000]
    pg = _stat_09(patron, f)
    with pg.expect_response(lambda x: "/salarii-contare/propunere" in x.url, timeout=90000):
        pg.click(_F + "#sp-contare")
    pg.wait_for_selector("#sp-contare-zona table", timeout=30000)
    t = " ".join(patron.fereastra().split())
    patron.captura("propunerea")
    assert "Contul 421 se soldează exact cu netul fluturașilor (%s lei)." % _bani(NET_FLUTURASI) in t, t[:3000]
    assert "Contul 423 se soldează exact cu netul indemnizațiilor de concediu medical (%s lei)." % _bani(CM_NET) in t, t[:3000]
    with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=90000):
        pg.click("#sp-contare-scrie")
    _asteapta_text(patron, "Nota salariilor %02d/%d e scrisă" % (LUNA, AN))
    patron.captura("nota")
    linii = _note(f, "i.sursa = 'salarii'")
    pe = lambda d, c: sum(D(s) for x, y, s in linii if x == d and y == c)   # noqa: E731
    # D112 = nota: CAS 4315, CASS 4316, impozit 444, CAM 436 (CF art.138, 156, 78, 220^3)
    assert pe("421", "4315") + pe("423", "4315") == D112_CAS and pe("421", "4316") + pe("423", "4316") == D112_CASS, linii
    assert pe("421", "444") + pe("423", "444") == D112_IMPOZIT and pe("646", "436") == D112_CAM, linii


@pozitii("F134")
def test_pilot_23_plata_salariilor_pe_card(patron, firma_pilot):
    """F134. Pașii: statul 09/2026 -> „IBAN ⚠” la fiecare salariat -> IBAN-ul contului de salariu -> „Salvează”: „IBAN ✓” -> „Fișier plată
    card (SEPA)”: „2 plată/plăți · total 8.979,00 lei · format SEPA pain.001” (netul de plată, salariu + indemnizația CM)."""
    pg = _stat_09(patron, firma_pilot)
    for i, s in enumerate((SAL1, SAL2)):
        # [lotul 13, 673 / 677] fereastra salariatului -> „IBAN ⚠” (fereastra lui) -> „IBAN ✓” -> înapoi la stat
        _salariat(pg, s["nume"])
        pg.click(_F + "#ss-butoane [data-iban]")
        pg.fill(_F + "#iban-input", _iban_ro("BTRL", "RONCRT00P1LOT%03d" % (i + 1)))
        pg.click(_F + "#iban-save")
        pg.wait_for_function("() => { const b = [...document.querySelectorAll('.fereastra')].pop().querySelector('#ss-butoane [data-iban]');"
                             " return b && b.innerText.includes('✓'); }", timeout=30000)
        pg.click(_F + ".nav-inapoi")
        pg.wait_for_selector(_F + "#sp-tabel tbody tr.sp-rand", timeout=30000)
    pg.click(_F + "#sp-plata-card")
    pg.wait_for_selector(_F + "#plata-descarca", timeout=30000)
    zona = " ".join(patron.fereastra().split())
    patron.captura()
    assert "2 plăți · total %s lei" % _bani(NET_DE_PLATA) in zona, zona


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 24–27 — validarea notelor, casa, scadențarul
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F054", "F019")
def test_pilot_24_notele_lunii_validate(patron, firma_pilot):
    """F054, F019 (validarea notelor). Pașii: Registrul jurnal -> luna 09/2026 -> „Validează” pe fiecare notă în ciornă, în ordinea zilelor
    (casa nu coboară sub zero la nicio zi): după ultima, nicio notă nu mai are „Validează”, iar luna nu mai are ciorne."""
    f = firma_pilot
    pg = patron.pg
    _jurnal(patron, f, (AN, LUNA))
    ids = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE status <> \'validata\' AND data >= %%s AND data <= %%s '
                              "ORDER BY data, id" % f["schema"], (zi(1), zi(30)))]
    assert len(ids) >= 15, ids
    for nid in ids:
        # rândul notei, după id (unic pe pagină: un singur registru deschis) — nu după „ultima fereastră”, care se poate schimba când
        # validarea anunță schimbarea (contorul „De validat”, clopoțelul)
        (stare,), = sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (nid,))
        if stare == "validata":      # validată între timp pe alt drum (de spus în raport: n-ar trebui să se întâmple)
            continue
        rand = "tbody.tn-nota[data-nota-id='%s']" % nid   # [lotul 12, 617] rândul notei în tabelul de note („Validează” e pe rând)
        buton = "%s [data-val='%s']" % (rand, nid)
        try:
            pg.wait_for_selector(buton, timeout=30000)
        except Exception:
            patron.captura("fara_validare_%s" % nid)
            randuri, butoane = pg.locator(rand), pg.locator(buton)
            text = " ".join(randuri.first.inner_text().split()) if randuri.count() else "(rândul notei nu e în pagină)"
            raise AssertionError("nota %s (în bază: %s) n-are „Validează” vizibil în registru: %d rânduri, %d butoane (vizibil: %s); "
                                 "rândul: %s; fereastra: %s" % (nid, stare, randuri.count(), butoane.count(),
                                                                 [butoane.nth(i).is_visible() for i in range(butoane.count())],
                                                                 text[:800], patron.fereastra()[:800]))
        assert pg.is_enabled(buton), " ".join(pg.inner_text(rand).split())
        pg.locator(buton).scroll_into_view_if_needed()
        pg.click(buton)
        pg.wait_for_function("(id) => { const r = document.querySelector(`tbody.tn-nota[data-nota-id='${id}']`); "
                             "return r && !r.querySelector('[data-val]') && r.innerText.includes('Validată'); }", arg=str(nid), timeout=30000)
    patron.captura()
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE status <> \'validata\' AND data >= %%s AND data <= %%s' % f["schema"],
               (zi(1), zi(30))) == [(0,)]


@pozitii("F015")
def test_pilot_25_registrul_de_casa(patron, firma_pilot):
    """F015. Pașii: Casa -> luna 09/2026: sold la început 500,00, sold final 5.002,00 (500 + 2.420 creanța preluată a lui Delta + 3.993
    încasarea + 363 raportul Z 0041 + 726 raportul Z 0042 − 3.000 depunerea), iar rapoartele Z apar în registru."""
    pg = patron.pg
    patron.firma(firma_pilot["nume"])
    _card(patron, "casa", "#c-toggle")
    _la_luna(patron, "#c-prev", AN, LUNA)
    t = " ".join(patron.fereastra().split())
    patron.captura()
    assert pg.inner_text("#c-sold-inceput").strip() == "500,00 lei", pg.inner_text("#c-sold-inceput")
    assert pg.inner_text("#c-sold-final").strip() == "%s lei" % _bani(SOLD_CASA), pg.inner_text("#c-sold-final")
    assert "raportul Z" in t, t[:2000]


@pozitii("F131")
def test_pilot_26_scadentarul(patron, firma_pilot):
    """F131. Pașii: Facturi -> „Scadențar” („Facturi neîncasate”): E2EA nr. 4 (Alfa, 363,00 lei, scadentă 29.10.2026) e neîncasată; E2EA nr. 1
    (încasată cu chitanța) și E2EA nr. 2 (născută încasată, pe bon — HG 1/2016 pct.97 alin.(1)) nu sunt în listă; opțiunea notificărilor
    automate se vede."""
    f = firma_pilot
    pg = patron.pg
    randuri = _scadentar(patron, f)
    assert "E2EA nr. 4" in randuri.get(f["e4"], "") and ALFA["nume"] in randuri[f["e4"]] and "363,00 lei" in randuri[f["e4"]], randuri
    assert f["e1"] not in randuri and f["e2"] not in randuri, randuri
    assert pg.locator(_F + "#sc-optin").count() == 1


@pozitii("F131", "F073")
def test_pilot_27_scadentarul_stie_incasarea_prin_banca(patron, firma_pilot):
    """F131, F073 (466). Pașii: Facturi -> „Scadențar”: E2EA nr. 3 (Beta, încasată prin extrasul din 25.09.2026, nota 5121 = 4111 validată) nu mai e
    în listă."""
    f = firma_pilot
    randuri = _scadentar(patron, f)
    assert f["e4"] in randuri, ("anti-vacuu: lista scadențarului trebuie să aibă E2EA nr. 4 (neîncasată)", randuri)
    assert f["e3"] not in randuri, randuri


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 28–29 — închiderea lunii, balanța
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F061", "F118", "F054")
def test_pilot_28_inchiderea_lunii(patron, firma_pilot):
    """F061, F118, F054. Pașii: Registrul jurnal -> 09/2026 -> „+ Notă nouă”: 30.09.2026, regularizarea TVA (documentul: nota de
    regularizare nr. 1 din 30.09.2026): 4427 = 4426 882,00 și 4427 = 4423 378,00 -> „Salvează” -> „Validează” -> Închidere lună -> 09/2026:
    „Nimic nu oprește închiderea lunii.” -> „Blochează luna”: „Luna e blocată …”."""
    f = firma_pilot
    pg = patron.pg
    _jurnal(patron, f, (AN, LUNA))
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-desc", timeout=10000)
    pg.fill("#je-data", zi(30).isoformat())
    pg.fill("#je-desc", "Regularizarea TVA 09/2026")
    pg.fill("#je-doc", "Notă de regularizare TVA nr. 1 din 30.09.2026")
    pg.click("#je-plus")
    linii = pg.locator("#je-linii > div")                    # rândul adăugat cu „+ linie” n-are `data-lin` (numai cele desenate cu nota)
    linii.nth(1).wait_for(timeout=10000)
    # CF art.316 / OMFP 1802/2014 (funcțiunea conturilor 4423, 4426, 4427): TVA colectată se compensează cu cea deductibilă, iar diferența
    # e TVA de plată: 1.260 − 882 = 378
    for i, (deb, cre, s) in enumerate((("4427", "4426", TVA_DED), ("4427", "4423", TVA_PLATA))):
        lin = linii.nth(i)
        lin.locator(".je-deb").fill(deb)
        lin.locator(".je-cre").fill(cre)
        lin.locator(".je-sum").fill(str(s))
    with pg.expect_response(lambda r: r.url.split("?")[0].endswith("/jurnal") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#je-salveaza")
    assert rr.value.status < 400, rr.value.text()
    (nid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE descriere = %%s' % f["schema"], ("Regularizarea TVA 09/2026",))]
    buton = "tbody.tn-nota[data-nota-id='%s'] [data-val='%s']" % (nid, nid)     # după id, ca la pasul 24
    pg.wait_for_selector(buton, timeout=20000)
    pg.click(buton)
    pg.wait_for_function("(id) => { const r = document.querySelector(`tbody.tn-nota[data-nota-id='${id}']`); "
                         "return r && !r.querySelector('[data-val]') && r.innerText.includes('Validată'); }", arg=str(nid), timeout=30000)
    patron.captura("regularizare")
    _inchidere(patron, f)
    _la_luna(patron, "#il-prev", AN, LUNA)
    ctl = " ".join(pg.inner_text(_F + "#il-controale").split())
    patron.captura("controale")
    assert "Nimic nu oprește închiderea lunii." in ctl, ctl
    pg.wait_for_function("() => { const b = document.querySelector('.fereastra:last-of-type #il-lock'); return b && !b.disabled; }", timeout=30000)
    pg.click(_F + "#il-lock")
    pg.wait_for_function("() => ([...document.querySelectorAll('.fereastra')].pop().querySelector('#il-stare-perioada') || {}).textContent"
                         ".startsWith('Luna e blocată')", timeout=30000)
    patron.captura("blocata")
    assert sql('SELECT count(*) FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % f["schema"], (AN, LUNA)) == [(1,)]


#: soldurile finale la 30.09.2026 (debitor, creditor) — din cifrele lunii (docstringul modulului)
SOLD_CASA = D(500) + CREANTA_DELTA + D(3993) + Z2_TOTAL + Z_TOTAL - D(3000)         # 5.002: casa la 30.09.2026 (+ creanța Delta, pct.7)
SOLDURI_FINALE = {
    "1012": (None, D("10000")), "1171": (None, D("1580")), "121": (D("1000"), None),
    "371": (COST_NIR - CMP * DESCARCAT + STOC_INITIAL, None),                       # 3.200 − 18 × 160 = 320, + stocul inițial 1.000
    "4111": (D("363"), None), "4423": (None, TVA_PLATA), "421": (None, NET_FLUTURASI), "423": (None, CM_NET),
    "4315": (None, D112_CAS), "4316": (None, D112_CASS), "436": (None, D112_CAM), "444": (None, D112_IMPOZIT),
    "5121": (BANCA_INITIAL - 1000 + 3000 + 1815 - 3872 - 1210 - 15, None),         # 6.378
    "5311": (SOLD_CASA, None),                                                       # 5.002
    "607": (CMP * DESCARCAT, None), "612": (CHIRIE, None), "627": (D("15"), None), "646": (D112_CAM, None),
    "704": (None, V704), "707": (None, V707),
}
#: totalul soldurilor finale: partida dublă — creditoarele (toate conturile cu sold creditor sunt mai sus) = debitoarele (33.653)
TOTAL_SOLDURI = sum(c for _d, c in SOLDURI_FINALE.values() if c)


@pozitii("F061")
def test_pilot_29_balanta(patron, firma_pilot):
    """F061 (cartea mare). Pașii: Balanță -> 09/2026: soldurile finale ale conturilor lunii (5121 debitor 6.378,00; 5311 debitor 5.002,00; 371
    debitor 1.320,00; 1171 creditor 1.580,00; 4111 debitor 363,00; 4423 creditor 378,00; 421 creditor 8.658,00; 707 creditor 5.400,00 …); 401, 408, 4426, 4427,
    4428.01, 581 închise (fără sold); totalul soldurilor finale debitoare = creditoare = 33.653,00."""
    pg = patron.pg
    patron.firma(firma_pilot["nume"])
    pg.click("#fa-balanta")
    pg.wait_for_selector("#b-prev", timeout=30000)
    _la_luna(patron, "#b-prev", AN, LUNA)
    patron.captura(intreaga=True)
    rele = []
    for cont, (sd, sc) in SOLDURI_FINALE.items():
        c = _celule(pg, cont)
        if len(c) < 12:
            rele.append("%s: rândul lipsește (%s)" % (cont, c))
            continue
        asteptat = [_bani(sd) if sd else "0,00", _bani(sc) if sc else "0,00"]
        if c[10:12] != asteptat:
            rele.append("%s: sold final %s, așteptat %s" % (cont, c[10:12], asteptat))
    for cont in ("401", "408", "4426", "4427", "4428.01", "581"):
        c = _celule(pg, cont)
        if c and len(c) >= 12 and c[10:12] != ["0,00", "0,00"]:
            rele.append("%s: are sold %s" % (cont, c[10:12]))
    assert not rele, "\n".join(rele)
    total = " ".join(pg.inner_text("table.fd-tabel tfoot").split())
    assert total.count(_bani(TOTAL_SOLDURI)) >= 2, total       # partida dublă: totalul soldurilor debitoare = creditoare


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 30–34 — declarațiile
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F031", "F169", "F019", "F252")
def test_pilot_30_d300(patron, firma_pilot):
    """F031, F169 (poarta TVA = balanța), F019, F252. Pașii: Declarații -> D300 -> 09/2026 -> „Continuă”: validat cu DUKIntegrator, fără
    erori; rd.9 (21%): baza 6.000, TVA 1.260 (facturile E2EA1, E2EA3, E2EA4 și rapoartele Z 0041, 0042; factura pe bon nu se numără a doua
    oară); rd.24 (21%): baza 4.200, TVA 882; TVA de plată 378 -> „Trimite în coadă”: trece de poarta „TVA-ul declarației = balanța” (4427 creditor 1.260,
    4426 debitor 882) -> De validat -> „Confirmă depunerea” cu indexul SPV: „— depusă.”"""
    pg = _genereaza_declaratia(patron, firma_pilot, "d300", luna=LUNA)
    xml = _xml_pas2(pg)
    _duk_valid(patron, xml, "d300", LUNA)
    # CF art.286 alin.(1) (baza) + art.291 alin.(1) (21%); D300: rd.9 = R9, rd.24 = R22 (`core/d300.py`), lei întregi
    r9 = sum(E1) + sum(E3) + sum(E4) + Z_BAZA + Z2_BAZA
    assert (_atr(xml, "R9_1"), _atr(xml, "R9_2")) == (str(_leu(r9)), str(_leu(TVA_COL))), xml[:3000]
    assert (_atr(xml, "R22_1"), _atr(xml, "R22_2")) == (str(_leu(COST_NIR + CHIRIE)), str(_leu(TVA_DED))), xml[:3000]
    # CF art.316 / formula decontului: TVA de plată = colectată − deductibilă (R34 = R17 − R32), soldul de plată la sfârșit (R41)
    assert (_atr(xml, "R17_2"), _atr(xml, "R27_2"), _atr(xml, "R34_2"), _atr(xml, "R41_2")) == (
        str(_leu(TVA_COL)), str(_leu(TVA_DED)), str(_leu(TVA_PLATA)), str(_leu(TVA_PLATA))), xml[:3000]
    _trimite_in_coada(patron)
    patron.captura("in_coada")
    _depune(patron, firma_pilot, "D300", "PILOT-D300-092026")
    patron.captura("depusa")


@pozitii("F034", "F254")
def test_pilot_31_d394(patron, firma_pilot):
    """F034, F254. Pașii: Declarații -> D394 -> 09/2026 -> „Continuă”: validat cu DUKIntegrator, fără erori; livrările (L) pe clienți: Alfa 2
    facturi, baza 3.600, TVA 756; Beta 1, 1.500 / 315; Gamma 1 (factura pe bon), 300 / 63; achizițiile (A): Mobila 3.200 / 672, Imobiliare
    1.000 / 210; încasările prin casa de marcat (Î1, 09): 1 casă, 3 bonuri (Z 0041: 1, Z 0042: 2), total 363 + 726 − 363 (factura pe bon se
    scade din luna bonului) = 726, baza 300 + 600 − 300 = 600, TVA 63 + 126 − 63 = 126 -> „Trimite în coadă” -> depusă."""
    pg = _genereaza_declaratia(patron, firma_pilot, "d394", luna=LUNA)
    xml = _xml_pas2(pg)
    _duk_valid(patron, xml, "d394", LUNA)
    op1 = {}
    for m in re.finditer(r"<op1 ([^>]*?)/?>", xml):
        a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        op1[(a.get("tip"), a.get("cuiP"))] = (a.get("nrFact"), a.get("baza"), a.get("tva"))
    # OPANAF 2194/2025 anexa D394 (op1: tip L livrări / A achiziții, pe partener, cota 21%); CF art.291 alin.(1)
    asteptat = {("L", ALFA["cui"]): ("2", "3600", "756"), ("L", BETA["cui"]): ("1", "1500", "315"), ("L", GAMMA["cui"]): ("1", "300", "63"),
                ("A", MOBILA["cui"]): ("1", "3200", "672"), ("A", IMOB["cui"]): ("1", "1000", "210")}
    assert op1 == asteptat, (op1, xml[:3000])
    m = re.search(r"<op2 ([^>]*?)/?>", xml)
    assert m, xml[:3000]
    a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    # OPANAF 2194/2025 anexa D394 lit.G: Î1 = încasările prin AMEF „cu excepția celor pentru care s-au emis facturi”; HG 1/2016 pct.97 alin.(1)
    assert (a.get("tip_op2"), a.get("nrAMEF"), a.get("nrBF"), a.get("total"), a.get("baza21"), a.get("TVA21")) == (
        "I1", "1", str(Z_BONURI + Z2_BONURI), str(_leu(Z_TOTAL + Z2_TOTAL - sum(BON))), str(_leu(Z_BAZA + Z2_BAZA - BON[0])),
        str(_leu(Z_TVA + Z2_TVA - BON[1]))), a
    _trimite_in_coada(patron)
    _depune(patron, firma_pilot, "D394", "PILOT-D394-092026")
    patron.captura("depusa")


@pozitii("F028", "F162")
def test_pilot_32_d112(patron, firma_pilot):
    """F028, F162. Pașii: Declarații -> D112 -> 09/2026 -> „Continuă”: validat cu DUKIntegrator, fără erori; rezumatul „D112: 2 salariați -
    impozit 998,00, CAS 3.838,00, CASS 1.535,00, CAM 345,00”; în XML, obligațiile 602 = 998, 412 = 3.838, 432 = 1.535, 480 = 345, iar
    certificatul CM: cod 01, 550 suportat de angajator -> „Trimite în coadă” -> depusă."""
    pg = _genereaza_declaratia(patron, firma_pilot, "d112", luna=LUNA)
    xml = _xml_pas2(pg)
    _duk_valid(patron, xml, "d112", LUNA)
    casete = pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('.caseta-info, .dec-avert')]"
                         ".map((c) => c.innerText.trim())")
    rez = " ".join(next((c for c in casete if c.startswith("Rezumat")), "").split())
    assert ("2 salariați - impozit %s, CAS %s, CASS %s, CAM %s" % (_bani(D112_IMPOZIT), _bani(D112_CAS), _bani(D112_CASS), _bani(D112_CAM))
            in rez), casete
    oblig = {}
    for m in re.findall(r"<angajatorA ([^>]*?)/?>", xml):
        a = dict(re.findall(r'(\w+)="([^"]*)"', m))
        oblig[a.get("A_codOblig")] = a.get("A_datorat")
    # CF art.78 alin.(2) lit.a (602 impozit), art.138 lit.a (412 CAS), art.156 (432 CASS), art.220^3 alin.(1) (480 CAM)
    assert (oblig.get("602"), oblig.get("412"), oblig.get("432"), oblig.get("480")) == (
        str(D112_IMPOZIT), str(D112_CAS), str(D112_CASS), str(D112_CAM)), (oblig, xml[:3000])
    assert re.search(r'D_9="01"', xml), "certificatul CM (cod 01) lipsește din D112"
    _trimite_in_coada(patron)
    _depune(patron, firma_pilot, "D112", "PILOT-D112-092026")
    patron.captura("depusa")


@pozitii("F035")
def test_pilot_33_d406(patron, firma_pilot):
    """F035. Pașii: Declarații -> D406 -> 09/2026 (plătitor lunar: luna) -> „Continuă”: validat cu DUKIntegrator, fără erori; fișierul
    cuprinde 4 facturi de vânzare și 2 de cumpărare -> „Trimite în coadă” (D406 = balanța) -> depusă."""
    pg = _genereaza_declaratia(patron, firma_pilot, "d406", luna=LUNA)
    xml = _xml_pas2(pg)
    _duk_valid(patron, xml, "d406", LUNA)
    t = " ".join(patron.fereastra().split())
    assert "4 facturi de vânzare, 2 facturi de cumpărare" in t, t[:3000]       # OPANAF 1783/2021: SourceDocuments, toate facturile lunii
    _trimite_in_coada(patron)
    _depune(patron, firma_pilot, "D406", "PILOT-D406-092026")
    patron.captura("depusa")


@pozitii("F026")
def test_pilot_34_d100(patron, firma_pilot):
    """F026. Pașii: Declarații -> D100 -> T3/2026 -> „Continuă”: rezumatul „cont 704: 600,00 lei”, „cont 707: 5.400,00 lei” (3.000 + 1.500 +
    600 din Z 0042 + 300 din Z 0041, FĂRĂ TVA-ul Z-urilor, 126 + 63), „Baza impozabilă: 6.000,00 lei × cota 1% = cod 121: 60 lei (rotunjit la
    leu).”; XML-ul (cod 121, suma 60, cota 1) validat cu DUKIntegrator -> „Trimite în coadă” -> De validat -> „Confirmă depunerea” cu
    indexul SPV: „— depusă.”"""
    pg = _genereaza_declaratia(patron, firma_pilot, "d100", trim=3)
    t = " ".join(patron.fereastra().split())
    # CF art.53 alin.(1): baza = veniturile (TVA colectată nu e venit: OMFP 1802/2014, funcțiunea contului 4427); art.51 alin.(1): 1%
    assert "cont 704: %s lei" % _bani(V704) in t and "cont 707: %s lei" % _bani(V707) in t, t[:3000]
    assert "Baza impozabilă: %s lei × cota 1%% = cod 121: %s lei (rotunjit la leu)." % (_bani(V707 + V704), D100_IMPOZIT) in t, t[:3000]
    xml = _xml_pas2(pg)
    assert re.search(r'cod_oblig="121"[^>]*suma_dat="%s"' % D100_IMPOZIT, xml) and 'cota="1"' in xml, xml[:3000]
    _duk_valid(patron, xml, "d100", 9)
    _trimite_in_coada(patron)
    patron.captura("in_coada")
    _depune(patron, firma_pilot, "D100", "PILOT-D100-T32026")
    patron.captura("depusa")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 35 — controlul încrucișat, semaforul, termenele
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F022", "F081", "F162", "F169")
def test_pilot_35_controlul_fiscal_si_incrucisat(patron, firma_pilot):
    """F022, F081, F162, F169. Pașii: Control fiscal -> firma: D300, D112, D394, D406 pe 09/2026 sunt depuse („La zi” când pasul rulează până
    la termen, „Depuse cu întârziere” după: data depunerii e ziua rulării); termenul
    D300 și D112 pe 09/2026 e 26.10.2026 (25 octombrie 2026 e duminică); „Declarație vs contabilitate” pe 09/2026: TVA colectată (D300 și
    4427), TVA deductibilă (D300 și 4426), TVA de plată (D300 și 4423, 378,00 lei), impozitul (D112 și 444), CAS (4315), CASS (4316), CAM
    (436) coincid. Confruntarea de pe ecran e a ultimei luni încheiate: în 10/2026 e 09/2026, pe ecran; după, pasul citește aceeași sursă
    (`control_incrucisat`) pe 09/2026."""
    from core import db
    from core.control_fiscal_api import luna_confruntata
    from core import control_incrucisat as _ci
    f = firma_pilot
    pg = patron.pg
    _control_firma(patron, f)
    g = _grupuri_control(patron)
    patron.captura("control", intreaga=True)
    def grup(tip):
        return [k for k, v in g.items() for r in v if r.startswith(tip) and "%02d/%d" % (LUNA, AN) in r]

    # depuse azi (pasul 30–33): „La zi” până la termen, „Depuse cu întârziere” după — termenul D300 / D112 e 26.10.2026 (mai jos)
    termen = _dt.date(2026, 10, 26)
    for tip in ("D300", "D112"):
        asteptat = "La zi" if _dt.date.today() <= termen else "Depuse cu întârziere"
        assert [k for k in grup(tip) if k.startswith(asteptat)], (tip, asteptat, g)
    for tip in ("D394", "D406"):
        assert [k for k in grup(tip) if k.startswith(("La zi", "Depuse cu întârziere"))], (tip, g)
    termene = dict(pg.eval_on_selector_all(_F + ".cf-decl-item[data-cheie]", "els => els.map((e) => [e.dataset.cheie, "
                                           "(e.querySelector('.cf-termen') || {textContent: ''}).textContent.trim()])"))
    # CF art.323 alin.(1) (D300) și art.147 alin.(1) (D112): „până la data de 25 inclusiv a lunii următoare”; CPF art.75 + Legea 134/2010
    # art.181 alin.(2): termenul care cade într-o zi nelucrătoare se prelungește până în prima zi lucrătoare (25.10.2026 = duminică)
    for cheie in ("d300-%d-%d" % (AN, LUNA), "d112-%d-%d" % (AN, LUNA)):
        assert "termen 26.10.2026" in termene.get(cheie, ""), (cheie, termene)
    azi = _dt.date.today()
    if luna_confruntata(azi.year, azi.month) == (AN, LUNA):
        mesaje = [" ".join(x.split()) for x in pg.locator(_F + ".cf-incr-rand .cf-incr-cap").all_inner_texts()]
    else:
        with db.get_conn(f["schema"]) as c:
            mesaje = [k.get("mesaj", "") for fn in (_ci.verifica_tva, _ci.verifica_d112) for k in (fn(c, f["schema"], AN, LUNA).get("constatari") or [])]
    asteptate = ("TVA colectată: D300 și contul 4427 coincid", "TVA deductibilă: D300 și contul 4426 coincid",
                 "TVA de plată (rezultat decont): D300 și contul 4423 coincid (%s lei)" % _bani(TVA_PLATA),
                 "D112 și contul 444 coincid", "D112 și contul 4315 coincid", "D112 și contul 4316 coincid", "D112 și contul 436 coincid")
    lipsa = [a for a in asteptate if not any(a in m for m in mesaje)]
    assert not lipsa, (lipsa, mesaje)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 36–39 — luna următoare: factura în valută, concediul cod 10; pașii încă nereparați care ar scrie
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
@pozitii("F025")
def test_pilot_36_factura_in_valuta_pe_luna_urmatoare(patron, firma_pilot):
    """F025. Pașii: Emite factură -> 01.10.2026 (luna următoare: o factură în valută neîncasată la 30.09 ar cere reevaluarea la cursul BNR
    din 30.09 — OMFP 1802/2014 pct.325 alin.(1) —, care ar schimba luna-pilot) -> clientul Beta -> „Servicii de montaj mobilier pilot”, 1 ×
    100 -> Monedă EUR: ÎNAINTE de emitere, „Curs BNR EUR <curs> din 30.09.2026” (cursul din ziua anterioară), „TVA în lei” = 21,00 EUR ×
    curs și „Total în lei” = 121,00 EUR × curs, rotunjite aritmetic -> „Emite”: factura are exact cursul, TVA-ul și totalul arătate."""
    f = firma_pilot
    pg = patron.pg
    ziua, ziua_curs = _dt.date(2026, 10, 1), _dt.date(2026, 9, 30)
    _deschide_emiterea(patron, f["nume"])
    pg.fill("#em-data", ziua.isoformat())
    pg.dispatch_event("#em-data", "change")
    pg.fill("#em-cui", BETA["cui"])
    pg.fill("#em-nume", BETA["nume"])
    pg.fill("#em-adresa", BETA["adresa"])
    pg.fill("#em-oras", BETA["oras"])
    pg.select_option("#em-judet", BETA["judet"])
    _linie(pg, 0, SERVICIU, 1, 100)
    pg.select_option("#em-moneda", "EUR")
    pg.wait_for_function("() => /Curs BNR EUR/.test((document.querySelector('#em-valuta') || {innerText: ''}).innerText)", timeout=30000)
    t = " ".join(pg.inner_text("#em-valuta").split())
    patron.captura("inainte_de_emitere")
    r = sql("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = %s", (ziua_curs,))
    assert r, "cursul BNR EUR din 30.09.2026 nu e în evidența aplicației (%s)" % t
    curs = D(str(r[0][0]))
    # HG 1/2016 pct.35 alin.(1): „cursul de schimb comunicat de respectiva bancă în ziua anterioară”; CF art.290 alin.(2);
    # CF art.319 alin.(20) lit.j: TVA în lei; rotunjire aritmetică la ban
    tva_lei, total_lei = (_bani(_q(D(x) * curs)) for x in ("21.00", "121.00"))
    assert "Curs BNR EUR %s din 30.09.2026" % ("%.4f" % curs).replace(".", ",") in t, t
    assert "TVA în lei %s lei" % tva_lei in t and "Total în lei %s lei" % total_lei in t, t
    with pg.expect_response(lambda x: x.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    patron.captura("emisa")
    x = sql('SELECT curs_bnr, data_curs::text, tva_lei, total_lei FROM "%s".facturi WHERE id = %%s' % f["schema"], (fid,))[0]
    assert (D(str(x[0])), x[1], _bani(x[2]), _bani(x[3])) == (curs, ziua_curs.isoformat(), tva_lei, total_lei), x


@pozitii("F122")
def test_pilot_37_concediul_cod_10_pe_luna_urmatoare(patron, firma_pilot):
    """F122. Pașii: Salariați -> statul lunii 10/2026 (luna următoare: certificatul nu schimbă luna-pilot) -> POPA ANDREI: „Concediu” ->
    „+ Certificat nou”: cod 10 (reducerea timpului de muncă), 01–14.10.2026 (10 zile lucrătoare), avizul medicului expert 4321, media
    250,00 lei/zi (31.250 / 125), venitul realizat = 2.500,00 − 499,59 -> „Calculează și salvează”: indemnizația 499,59, rotunjită la 500
    (Normele OUG 158/2005, art.63 Exemplul nr.1: „rotunjit la 625 lei conform legii”) -> lista certificatelor: „indemnizație brută 500,00
    lei · net 292,00 lei” (500 − CAS 125 − CASS 50 − impozit 33)."""
    pg = patron.pg
    di, ds, zile = _dt.date(2026, 10, 1), _dt.date(2026, 10, 14), 10          # 1–14 octombrie 2026: 10 zile lucrătoare
    _stat_09(patron, firma_pilot, di.year, di.month)
    _salariat(pg, SAL1["nume"])
    pg.click(_F + "#ss-butoane [data-cm]")
    pg.wait_for_selector(_F + "#cm-nou", timeout=20000)
    pg.click(_F + "#cm-nou")
    pg.wait_for_selector(_F + "#cm-calc", timeout=20000)
    pg.fill(_F + "#cm-serie", "PL")
    pg.fill(_F + "#cm-numar", "91001")
    pg.select_option(_F + "#cm-cod", "10")
    pg.fill(_F + "#cm-venit", "%.2f" % (CM_MEDIE * zile - D("499.59")))
    pg.fill(_F + "#cm-acord", di.isoformat())
    pg.fill(_F + "#cm-inceput", di.isoformat())
    pg.fill(_F + "#cm-sfarsit", ds.isoformat())
    _propunerea_zilelor(pg, zile)
    for sel in ("#cm-continuare", "#cm-spital", "#cm-program-national"):
        pg.click(_F + sel + "-grup [data-v='false']")                  # [lotul 13, 676] Da / Nu = butoane
    pg.fill(_F + "#cm-ven6", str(CM_VEN6))
    pg.fill(_F + "#cm-zile6", str(CM_ZILE6))
    pg.fill(_F + "#cm-urgenta", "4321")
    pg.click(_F + "#cm-calc")
    pg.wait_for_selector(_F + "#cm-rezultat .panou", timeout=30000)
    lista = " ".join(pg.inner_text(_F + ".pf-lista").split())
    patron.captura()
    brut = _leu(D("499.59"))                                    # 500
    cas, cass = _leu(brut * D("0.25")), _leu(brut * D("0.10"))  # CF art.144; art.155 alin.(1) lit.i (cod 10)
    imp = _leu((brut - cas - cass) * D("0.10"))                 # CF art.78 alin.(2) lit.a: 32,5 -> 33
    assert "indemnizație brută %s lei · net %s lei" % (_bani(brut), _bani(brut - cas - cass - imp)) in lista, lista[:2000]


@pozitii("F043")
def test_pilot_38_factura_primita_introdusa_manual(patron, firma_pilot):
    """F043 (477). Pașii: Facturi -> „Facturi primite” -> „Introdu factura de mână” -> factura de hârtie a furnizorului Imobiliare: codul
    fiscal, numele, nr. IMB-1025 din 01.10.2026 (luna următoare: luna-pilot închisă nu se schimbă) -> linia „Chirie spațiu comercial
    octombrie 2026”, 1 × 1.000,00, cota 21% (cotele în vigoare la data facturii) -> totalul „1.210,00 lei” -> contul 612 -> „Validează” ->
    confirmarea -> „Validată.” -> nota: 612 = 401 1.000,00 și 4426 = 401 210,00 (ca factura de chirie din XML, pasul 07)."""
    f = firma_pilot
    pg = patron.pg
    ziua = _dt.date(2026, 10, 1)
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-manual", timeout=20000)
    pg.click("#fp-manual")
    pg.wait_for_selector("#pm-valideaza", timeout=20000)
    pg.fill("#pm-cui", IMOB["cui"])
    pg.fill("#pm-furnizor", IMOB["nume"])
    pg.fill("#pm-numar", "IMB-1025")
    pg.fill("#pm-data", ziua.isoformat())
    pg.dispatch_event("#pm-data", "change")
    # cotele se încarcă după data facturii (registrul de parametri fiscali); până atunci lista cotei e inactivă
    pg.wait_for_function("() => { const s = document.querySelector('#pm-l1-cota'); return s && !s.disabled && "
                         "[...s.options].some((o) => o.value === '21'); }", timeout=20000)
    pg.fill("#pm-l1-descriere", "Chirie spațiu comercial octombrie 2026")
    pg.fill("#pm-l1-cantitate", "1")
    pg.fill("#pm-l1-pret", str(CHIRIE))
    pg.select_option("#pm-l1-cota", "21")
    pg.wait_for_selector("#pm-total-cu-tva", timeout=10000)
    total = " ".join(pg.inner_text("#pm-total").split())
    assert "Total %s lei" % _bani(CHIRIE * (1 + COTA)) in total, total          # CF art.286 alin.(1) + art.291 alin.(1): 1.000 + 210
    pg.fill("#pr-cont", "612")
    patron.captura("formular")
    pg.click("#pm-valideaza")
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=20000)
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => (document.querySelector('#pr-zona') || {innerText: ''}).innerText.includes('Validată')", timeout=60000)
    patron.captura("validata")
    r = sql('SELECT id FROM "%s".facturi WHERE numar = %%s AND directie = \'primita\'' % f["schema"], ("IMB-1025",))
    assert len(r) == 1, r
    # CF art.299 alin.(1) lit.a (deducerea cu factura); OMFP 1802/2014: 612 = 401 (chiria), 4426 = 401 (TVA deductibilă 21%)
    assert sorted((_sintetic(d), _sintetic(c), s) for d, c, s in _note(f, "i.factura_id = %s", (r[0][0],))) == [
        ("4426", "401", "210.00"), ("612", "401", "1000.00")]


@pozitii("F118")
def test_pilot_39_deblocarea_lunii_cu_motiv(patron, firma_pilot):
    """F118 (483). Pașii: Închidere lună -> 09/2026 (blocată la pasul 28) -> „Deblochează luna” -> sub buton, câmpul „Motivul deblocării
    lunii 09/2026” -> „Deblochează luna” fără motiv: refuzat lângă câmp („Scrie motivul deblocării…”) -> motivul („scenariul pilot:
    corectare”) -> „Deblochează luna”: „Luna e deschisă.” și „Luna 09/2026 e deblocată. Motivul („scenariul pilot: corectare”) e în istoricul
    perioadei.” -> „Blochează luna” din nou: „Luna e blocată …” (luna-pilot rămâne închisă)."""
    f = firma_pilot
    pg = patron.pg
    _inchidere(patron, f)
    _la_luna(patron, "#il-prev", AN, LUNA)
    stare = "() => ([...document.querySelectorAll('.fereastra')].pop().querySelector('#il-stare-perioada') || {}).textContent"
    pg.wait_for_function(stare + ".startsWith('Luna e blocată')", timeout=30000)
    pg.click(_F + "#il-lock")
    pg.wait_for_selector(_F + "#bl-motiv", timeout=20000)
    pg.click(_F + "#bl-deblocheaza")                                   # fără motiv: refuzul stă lângă câmp, luna rămâne blocată
    pg.wait_for_function("() => (document.querySelector('#bl-deblocare') || {innerText: ''}).innerText.includes('Scrie motivul deblocării')",
                         timeout=20000)
    patron.captura("fara_motiv")
    assert sql('SELECT count(*) FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % f["schema"], (AN, LUNA)) == [(1,)]
    pg.fill(_F + "#bl-motiv", "scenariul pilot: corectare")
    pg.click(_F + "#bl-deblocheaza")
    pg.wait_for_function(stare + ".startsWith('Luna e deschisă')", timeout=30000)
    _asteapta_text(patron, "Luna 09/2026 e deblocată. Motivul („scenariul pilot: corectare”) e în istoricul perioadei.")
    patron.captura("deblocata")
    assert sql('SELECT count(*) FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % f["schema"], (AN, LUNA)) == [(0,)]
    pg.wait_for_function("() => { const b = document.querySelector('.fereastra:last-of-type #il-lock'); return b && !b.disabled; }", timeout=30000)
    pg.click(_F + "#il-lock")
    pg.wait_for_function(stare + ".startsWith('Luna e blocată')", timeout=30000)
    patron.captura("blocata_din_nou")
    assert sql('SELECT count(*) FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % f["schema"], (AN, LUNA)) == [(1,)]
