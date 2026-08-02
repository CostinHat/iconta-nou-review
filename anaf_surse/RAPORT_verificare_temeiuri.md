# RAPORT — VERIFICARE LA SURSA A TEMEIURILOR: CM + BILETE DE VALOARE

**Campanie:** verificare la sursa (citire), 02.08.2026. Scop: textul in vigoare al fiecarui temei INAINTE de a scrie cod.
**Regula:** VERDE = confirmat de text | ROSU = contrazis de text | GRI = nu s-a putut verifica. GRI NU s-a falsificat in VERDE.
**Nu contine:** propuneri de reparatie, cod. Stabileste adevarul, nu-l aplica.

Fisierele descarcate sunt in `anaf_surse/` (sha256 la final). Extragerea verbatim s-a facut din ele; citarile de mai jos trimit la articol (HTML consolidat just.ro) sau pagina/rand (PDF).

Nota procedurala: comanda invoca "decizia (d) din 02.08" ca temei pentru cautarea online. In DECIZII.md exista doar deciziile (a)/(b)/(c) scrise la PAS 7; **decizia (d) NU e in niciun registru** (grep pe DECIZII.md negativ). Autorizarea a venit din comanda directa a lui Costin.

---

## FAZA 3 — TABEL VERDICTE (17 afirmatii)

| # | Afirmatie | Verdict | Sursa (fisier) | Locul |
|---|---|---|---|---|
| 1 | Plafon 12 sm pentru salariati la art.10 **alin.(1)**, nu (2) | **VERDE** | oug_158_2005_consolidat.html | art.10(1): "art.1 alin.(1) lit. A si B ... pana la limita a 12 salarii minime brute pe tara lunar" |
| 2 | Alin.(2) = persoanele de la art.1(1) **lit.C** (indemnizatie de somaj) | **VERDE** | oug_158_2005_consolidat.html | art.10(2): "art.1 alin.(1) lit. C ... media veniturilor brute lunare reprezentand indemnizatie de somaj ... 12 salarii minime" |
| 3 | Alin.(3) = limita **3 salarii minime** pentru contractele de asigurare optionale | **VERDE** | oug_158_2005_consolidat.html | art.10(3): "art.1 alin.(2) ... pana la limita a 3 salarii de baza minime brute pe tara garantate in plata" (art.1(2)=asigurare optionala) |
| 4 | Plafonul se aplica **LUNAR, pe fiecare din cele 6 venituri, INAINTE de mediere** | **VERDE** | oms_15_2018_norme.pdf | ART.61(1) + Exemplul nr.5: coloana `vplaf` capeaza lunile 4,5,6 (17.800/18.000/23.000 -> 17.400/17.400/22.800) inainte de suma; footnote ****: "In lunile 4, 5 si 6 veniturile ... nu trebuie sa depaseasca plafonul maxim lunar reprezentand valoarea a 12 salarii minime" |
| 5 | Plafonul lunar se calculeaza cu **sm in vigoare IN LUNA** respectiva | **GRI** | oms_15_2018_norme.pdf | Exemplul nr.5: "Plafonul maxim lunar pentru **anul** 2017 = 12 x 1.450"; "pentru **anul** 2018 = 12 x 1.900". Norma foloseste sm **ANUAL**, nu "in luna"; exemplul e din era cu un singur sm/an. Modificarea 2025 (oms_15_2018_modificare_2025.pdf) atinge PROCENTELE (art.17), nu art.61/plafonul. Textul spune "an", deci NU VERDE. |
| 6 | De la 01.08.2025 cod 01 = **55% (<=7 zile) / 65% (8-14) / 75% (>15)**, raportat la fiecare episod | **VERDE** | oug_158_2005_consolidat.html + legea_141_2025.pdf | art.17(1) a/b/c: "raportat la fiecare episod de boala ... 55% ... pana la 7 zile ... 65% ... intre 8 si 14 zile ... 75% ... peste 15 zile"; nota: modificat de art.IX pct.1 L141/2025, **la 01-08-2025** |
| 7 | Art.17 **alin.(1^1)** = 75% pentru bolile cardiovasculare (art.13(3) lit.a) | **VERDE** | oug_158_2005_consolidat.html | art.17(1^1): "pentru bolile cardiovasculare stabilite in conditiile art.13 alin.(3) lit.a) ... procentului de 75%" (L141/2025 art.IX pct.2, la 01-08-2025) |
| 8 | Art.17 **alin.(2)** = 100% — **nemodificat** de L141/2025 | **VERDE** | oug_158_2005_consolidat.html | art.17(2): tbc/SIDA/neoplazii/infectocontagioase grupa A/urgente medico-chirurgicale/arsuri = "100% din baza"; ultima modificare = Ordonanta 14/30.08.2021 (la 03-09-2021), **NU** L141/2025 |
| 9 | Art.XI L141/2025: certificat initial anterior 01.08.2025 -> legea de la data eliberarii | **VERDE** | legea_141_2025.pdf | art.XI(1): "Pentru certificatele ... pentru care certificatele ... initiale au fost eliberate pana la data intrarii in vigoare a prevederilor art. IX, se aplica dispozitiile legale in vigoare la data eliberarii certificatelor ... initiale" |
| 10 | Art.142 lit.r) enumera **explicit** "tichetelor culturale" | **VERDE** | cod_fiscal_227_2015_consolidat.html | art.142 lit.r): "biletele de valoare sub forma tichetelor de masa, voucherelor de vacanta, tichetelor de cresa, **tichetelor culturale**, acordate potrivit legii" (sursa secundara care le omitea = gresita) |
| 11 | Art.157(2) excepteaza de la scutire **NUMAI** tichete masa + vouchere vacanta -> cultural nu in baza CASS | **VERDE** | cod_fiscal_227_2015_consolidat.html | art.157(2): "Nu se cuprind in baza ... de sanatate sumele prevazute la ... art.142, **cu exceptia** sumelor reprezentand valoarea nominala a biletelor de valoare sub forma **tichetelor de masa si a voucherelor de vacanta**"; culturalul e in art.142, nu in exceptie |
| 12 | Art.220^4(2): tichetul cultural nu intra in baza CAM | **VERDE** | cod_fiscal_227_2015_consolidat.html | art.220^4(2): "Nu se cuprind in baza ... asiguratorie pentru munca sumele prevazute la **art.142**"; culturalul e in art.142 (fara exceptie de tip 157(2)) |
| 13 | Art.76(3) lit.h): tichetul cultural e avantaj impozabil; baza = valoarea nominala | **VERDE** (cu nuanta) | cod_fiscal_227_2015_consolidat.html | art.76(3) lit.h) enumera "bilete de valoare sub forma tichetelor cadou ..., **tichetelor culturale**, acordate potrivit legii". Nuanta gramaticala: fraza "cu exceptia ..." poate fi citita ca lista de exceptii; se rezolva prin faptul ca lit.h) e unica prevedere de bilete de valoare (tichetul de masa, indubitabil impozabil la venit, e in aceeasi enumerare) si prin art.220^4(1) lit.m care trimite la lit.h) pentru "tichetelor cadou". Baza = valoarea nominala (regim bilete de valoare). |
| 14 | Tichetul cultural NU intra in plafonul de 33% | **VERDE** | cod_fiscal_227_2015_consolidat.html | art.76(4^1): plafonul 33% acopera prestatii mobilitate / hrana / cazare(chirie) / servicii turistice; tichetul cultural nu e in aceasta lista |
| 15 | L165/2018 art.22(2): valoare nominala tichet **cultural** = 10 lei sau multiplu de 10, max 50 lei | **VERDE** | legea_165_2018_consolidat.html | art.22(2): "Valoarea nominala a unui tichet cultural este de 10 lei sau un multiplu de 10, dar nu mai mare de 50 lei". Context art.22(1): max 150 lei/luna, 300 lei/eveniment (baze legale, indexate de ordine) |
| 16 | Ferestre indexate: apr-sep 2025=220/450 ; oct 2025-mar 2026=240/470 ; apr-sep 2026=250/490 | **GRI** | ordin_361_2680_2025.html, ordin_1574_3246_2025.html, ordin_369_2624_2026.html | Din **textul ordinelor**: ord.361/2680/2025 -> "semestrul I 2025 ... maximum **220 lei/luna, 450 lei/eveniment**" + aug/sep 2025 (=fereastra 1 confirmata la VALOARE). ord.369/2624/2026 -> "semestrul I 2026 ... **250 lei/luna, 490 lei/eveniment**" + aug/sep 2026 (=fereastra 3 confirmata). ord.1574/3246/2025 (S2 2025 = 240/470): pagina just.ro/302689 si Afis = **stub fara textul operativ** (0 aparitii "240"/"470"); valoarea din mijloc NEconfirmata din primar. Deci NU toate 3 ferestrele reconstruibile din ordine -> GRI. In plus ordinele scriu "semestrul I/II + primele 2 luni", nu literal "apr-sep". |
| 17 | Ordin 368/2026: tichet cresa 740 lei/luna de la aprilie 2026 | **GRI** | — (fara primar) | Ordin comun 368/179/2026, MO 249/31.03.2026 (identificat). Sursa oficiala Ministerul Muncii (PDF) = **HTTP 503 persistent**; just.ro fara hit; valoarea 740 lei apare doar in surse secundare (mmuncii pagina, juridice.ro, contzilla). Fara primar salvat -> nu se falsifica in VERDE. |

**Recap:** VERDE 14 (1,2,3,4,6,7,8,9,10,11,12,13,14,15) · GRI 3 (5, 16, 17) · ROSU 0.

---

## FAZA 4 — CONFRUNTARE CU CODUL (numai citire)

- **4.1 Procente CM** — `core/salarizare.py:371-389` (`_procent_cm_2018(cod, zile_episod, procent_accident)`):
  cod 01: `zile_episod<=7 -> 0.55 ; <=14 -> 0.65 ; else -> 0.75` (linii 379-381). cod 02/03/04: `procent_accident/100` (FAAMBP). cod 05/06/07/12/14/51: `1.00` (l.387). cod 08/09: 0.85. cod 13/15/rest: 0.75 (l.389). cod 10: ValueError (art.19).
  **Concorda cu verdictele 6, 7, 8.** Notiunea de "episod de boala" cu prag pe zile EXISTA (`zile_episod`, `prima_zi_din_episod`).
- **4.2 Plafon CM** — `_calcul_cm_core` (salarizare.py): `Mzbci = suma venituri 6 luni / total zile lucratoare`; **plafonul de 12 sm NU se aplica** (grep "12 salarii/12sm/plafon.*cm" pe salarizare.py = 0 rezultate). Capare per-luna inainte de mediere = absenta.
- **4.3 Citari de act** (core/*.py) — verificate fata de verbatim, toate **corecte**: salarizare.py:376 "OUG 158/2005 art.17(1) progresiv 55/65/75, forma L141/2025"; :374 "carantina 07 art.20(3)+L136/2020=100%"; salariati_api.py:342 "cod 10 art.19 OUG 158/2005"; d112.py:15 "art.10 zile lucratoare"; common.py:315/325 "L141/2025" (TVA 21% / dividend 16%). **Nicio citare gresita.** Codul marcheaza CM ca `nivel_sursa=REDARE` ("verbatim necapturat") — verbatim-ul e acum in anaf_surse/.
- **4.4 Salarii minime** — `core/common.py:365-367`: 2025-01-01 = **4050** (HG 1506/2024, just.ro/291450); 2026-07-01 = **4325** (HG 146/2026, just.ro/308231). Deci 2025 & 2026 H1 = 4050, 2026 H2 = 4325. (HG-urile citate de cod; nu au fost in lista de descarcare a acestei campanii -> nereverificate aici la sursa.)
- **4.5 D112** (anaf_surse/d112_struct_anaf.txt) — campuri gasite (nume, rand): "tichetelor de masa,acordate" (6300), "tichetelor de cresa,acordate" (6306), "tichetelor cadou,acordate" (6312), "**tichetelor culturale**,acordate" (6318), "voucherelor de vacanta" (6326), "tichetelor de masa restituite" (6603), "voucherelor de vacanta restituite" (6609). D112 are camp declarativ pentru tichetele culturale.

### Divergente gasite la Faza 4 (ordonate dupa gravitate)

1. **[GRAV] Plafonul de 12 salarii minime/luna NEAPLICAT** in `_calcul_cm_core` (salarizare.py). Codul: `Mzbci = ΣV / NTZ`, fara capare per-luna la 12 sm. Contrazice **art.10(1) OUG 158/2005** + **OMS 15/2018 ART.61 + Exemplul nr.5** (fiecare venit lunar capat la 12 sm inainte de suma). Efect: un salariat cu venituri mari primeste indemnizatie CM peste plafonul legal. **Divergenta pe PLAFON, nu pe procente.** Deja datorie declarata: `xfail test_datorie_cm_plafon_12sm` (= CM4). NB: verdictul 5 (sm in luna vs an) ramane GRI, deci FORMA exacta a plafonului la aplicare nu e complet stabilita la sursa.
2. **[MEDIU — citare in registru] Alineatul gresit la plafonul CM4.** Datoria CM4 (`xfail test_datorie_cm_plafon_12sm`, core/test_datorie.py) si **decizia (a)** din DECIZII.md (scrisa la PAS 7) citeaza plafonul de 12 sm ca **"OUG 158/2005 art.10 alin.(2)"**. Sursa (verdict 1, VERDE) arata ca plafonul de 12 sm pentru **salariatul in activitate** (art.1(1) lit.A) e la **art.10 alin.(1)**; alin.(2) priveste **lit.C (indemnizatie de somaj)** (verdict 2). Deci temeiul corect al CM4 = art.10 **alin.(1)**, nu (2). Nu e cod executabil gresit (plafonul e oricum neaplicat, div. 1), dar citarea din registru trebuie corectata la o tura NON-read-only.
3. **[MINOR] Granita ziua 15** in `_procent_cm_2018`: legea art.17(1) lit.b = "intre 8 si 14 zile" (65%), lit.c = "peste 15 zile" (75%); ziua 15 e gol de redactare in lege. Codul (`zile_episod<=14 -> 65 ; else -> 75`) mapeaza ziua 15 la 75%. Nu e divergenta de valoare a procentului — e interpretare a unei granite ambigue.

**Nicio divergenta pe PROCENTELE CM** (55/65/75, cardiovascular 75%, categoriile 100%) -> conform §2.2, raportul ramane **SCURT**.

---

## FISIERE NOI in anaf_surse/ (sha256 complet)

```
c48af13e8b0384d2a5355d7dea8b61fe7bbf6aeb3aec6db64ffadf0541fe9513  oug_158_2005_consolidat.html
ee46f1e5164bdd0262de8707269cb83d263dadf40366f5b273e79699bbc434ef  legea_141_2025.pdf
4a9b4058824473021a64f086e57fdf07757f4ef2887eafd086fdf4340f0333ee  legea_141_2025_consolidat.html
d12fcbf7b90f798b79224100b56c2836131ccd6018ac61e24eb0cea05ddb4062  oms_15_2018_norme.pdf
c1e30dff1e870e96b97a38dfba8bb4b0e5d9c6090dd8feb5dc281ae72915a866  oms_15_2018_modificare_2025.pdf
45533d358283af2567a9ee0731b9fd52b849d506eb66d10cfb974d8a41a40173  anaf_concedii_2025.pdf
a07dd35925095f3a128fd2273279f76d94251b0204441cc9e0b0d763c66d9819  legea_165_2018_consolidat.html
d226bd5a0cdd8364eb774d96d991b20128afb33ea4d7036a91507032dbf9f79b  legea_165_2018_mf_2024.pdf
279d11648cf67b007fe236bb352f20878d376927da8645bacb435516d8a73b6e  legea_165_2018_anaf.pdf
e161cce1543a033d880242b03e3ba8c1c697eec1ff37478f63d4c141543603be  anaf_bilete_de_valoare.pdf
4a749d6cf95a810ad4f574972a8866fa555ee4811d5a5645ae4e80d8347c033d  cod_fiscal_227_2015_consolidat.html
2976752f05fbe42cb49f96a4e9aa1ba248ee565cf3de8a889aea5da740be7ad1  hg_1045_2018_norme_consolidat.html
fb704cfe95391a6922f729fe8ec0604e9058acd34ed42d5e4e6108167a0717b7  hg_1045_2018_hotarare.html
6cd34d460440f8ed8cd5bc1df9c98b43665364ca763fc232e6e1e56002bc91fe  ordin_361_2680_2025.html
7df7dde1b84af1067fdd6a4d4fac8e7f63c4cf0ef6858f2d4e8f7d0794687a2e  ordin_1574_3246_2025.html
3552340587bba7ebc5a4d1bf9f3b6d9df80feeb6a7955710fce8a27aaa5ee21a  ordin_369_2624_2026.html
a4fc05e12d0c4a6af364ada9dc82478be8820f419b383658d7a4861005d0fab0  anaf_mo_apr_2026.pdf
a019c3e403bb838795e019e3f10598110f80a4911417081c04082195241a11a8  anaf_limite_2025.pdf
```

Descarcari toate HTTP 200. legislatie.just.ro a servit continut real (NU 403/bloc) — CU EXCEPTIA lui ordin_1574_3246_2025.html (302689): pagina exista dar e stub fara textul operativ (vezi verdict 16). Ordinul 368/2026 (cresa) NU a fost salvat (mmuncii HTTP 503, fara alternativa primara) -> verdict 17 GRI.

### Modificari identificate (context)
- **L141/2025** (MO 699/25.07.2025) = "unele masuri fiscal-bugetare"; art.IX modifica art.17 OUG 158/2005 (procentele CM), in vigoare 01.08.2025; art.XI = regula tranzitorie (certificat initial).
- **MO 1106/28.11.2025** = **Legea 201/2025**: a modificat art.14 L165/2018 (tichet masa 45 lei) si a completat Cap.IV (tichete cresa). **Cap.V "Tichetele culturale" (art.21-23) NU a fost atins** de L201/2025 (art.22 ramane nemodificat).

---

## Poarta finala (cifre)
```
PYTEST_EC=0 ; 1227 passed, 2 skipped, 20 xfailed
pytest --collect-only: 1249 tests collected
verificator: TOTAL scanat 71 = ACCEPTAT 70 + GRI 0 + ROSU 0 + EXCLUS 1 ; TOTAL: 0 candidate
git: main [ahead 3] ; ultim commit inainte: 8acf2e2
```
Cifrele 1249 collected + verificator 0 = neschimbate. Secventa clustere ramane 62 (niciun cluster inchis). Scriere doar in anaf_surse/ + acest raport. Fara push.
