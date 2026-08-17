Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968); cluster 1 (import salariu) LIVRAT

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_005 (P2, Constructii Profit Trim SRL) cap-coada cu Playwright (captura PRIVITA +
axe-core + mobil pe fiecare ecran atins - Regula 14 integral), REPARAND ce gasesti; ce gasesti pe o firma cauta pe
toate (Regula 13). Valorile fiscale se verifica la sursa (anaf_surse/*_struct + XSD + DUK), NU se cer de la Costin.
Fiecare gard nou: mutatie probata RED pe cod vechi, prin rulare. DS inainte de orice cod de interfata, cu capitolul citat.
PUNCTUL LA CARE AM RAMAS: cluster 1 LIVRAT (import salariu_brut obligatoriu, 5dd0dc2). RAMAS, in ordinea comenzii:
- **FRONT A (URMATORUL CLUSTER) - semnal brut=0 pe Stat de plata**: salariatul Ionescu Marin (tenant_005) are
  salariu_istoric.salariu_brut=0 -> Stat de plata 08/2026 afiseaza "brut 0 · net 0 · cost 825" TACIT (825 =
  cas_suprataxa 589.29 + cass_suprataxa 235.71, podeaua sub-minim art.146(5^6)/168(6^1) pe baza zero). Importul
  ACUM blocheaza brut=0 (cluster 1), dar ecranul Stat de plata NU semnaleaza datele reziduale cu brut=0 (MEMORY §13:
  data lipsa se spune explicit, nu se calculeaza tacit). De construit semnalul pe ecranul Stat de plata (firme.js:777,
  randul cardului de salariat) - DS cap.6 (mesaj de stare / avertisment). Pana atunci D112 P2 e degenerat (baza 0).
- **FRONT B - restul straturilor de migrare (8 din 9)**: doar stratul Salariati auditat cap-coada. NEatinse:
  import firme, Vector fiscal, Solduri initiale, Solduri parteneri, Asociati, Mijloace fixe, Istoric declaratii,
  Plan de conturi, Articole/stoc initial. Fiecare: import->preview->salvare->confirmare->ecran, cu blocaje provocate.
- **FRONT C - operarea P2**: Facturi/Banca/Casa neauditate in adancime. Observat: "2 facturi emise necontabilizate"
  (T6 taxare inversa 40000 + factura normala 12100 din 08.2026 NU sunt contabilizate pe cont 70x -> D100 nu se
  depune pe zero, CORECT semnalat). De verificat fluxul de contare a facturilor emise (Registru jurnal / contare).
- **FRONT D - declaratiile ramase la XML+DUK**: DONE (DUK valid) D300 Q2/Q3, D394 Q2/Q3 (codPR 27 taxare inversa
  cladiri_terenuri, VERIFICAT in XML), D406 L9. D100 blocheaza CORECT pe zero. RAMAS: D112 (dupa FRONT A), D101/D205
  anuale, Bilant S1005 (blocat CORECT de "Nr. registrul comertului lipsa" - profil incomplet, mesaj precis pe Date firma).
  Wizardul de declaratii pas 3 (coada/depunere) NEATINS.

## FOUR-WAY (de confirmat de urmatoarea tura)
Comit livrat: 5dd0dc2 (import salariu_brut obligatoriu). Poarta verde: 2276 passed / 4 skipped / 16 xfailed,
verificator TOTAL 0. Post-commit a publicat pe origin/main + backup/lant-2026-08-17 SI a restartat iconta-nou
(start-time 13:51:46 > commit 13:43:28). HEAD = origin/main = backup = 5dd0dc2. RUNNING confirmat BEHAVIORAL:
dupa restart importul fara salariu RESPINGE (era acceptat inainte). versiune.stare() da running=null/necunoscut
(mecanismul nu citeste commitul viu), dar divergent=False + start-time > commit + proba vizuala = RUNNING pe 5dd0dc2.
PREDARE (aceasta) = commit separat dupa cluster 1.

## LIVRAT (cluster RED-probat + vizual/DUK)
1. **Import salariati: salariu_brut obligatoriu si > 0** (5dd0dc2). `salariati_import_api.verifica_randuri` valida
   CNP/data/norma/ore/judet/IBAN dar NU salariul: coloana de salariu absenta / celula goala -> parser `_numar`
   intoarce 0.0 TACIT (default fabricat, DS cap.17), iar `creeaza_salariat` il bloca deja (#8) - doua cai de scriere
   pe acelasi camp cu invariant diferit. Comentariul din verifica_randuri (~linia 189) recunostea explicit gaura
   ("brut 1500 la norma intreaga sub minim... toate au intrat, migrarea a zis gata"). Reparat: verifica_randuri
   respinge brut lipsa/0/negativ (motiv salariu_lipsa), poarta unica. Mesaj VIZIBIL prin gateazaPreview/.caseta-atentie
   (cap.5): "rand 2: <nume>: salariul de baza lipseste sau nu e mai mare ca 0 - intra in D112 si pe fluturas...".
   Gard test_salariu_brut_lipsa/negativ_e_respins (RED probat: stash cod -> [] acceptat; GREEN dupa). axe/mobil pe
   ecranul de import (preview respins): fara-eticheta 0, title-only STRICT 0 (mesajul NU e title-only); pre-existent
   contrast 13 noduri, tinte <44px 11, info-touch 2. DS v2.32. Registre GARZI/DECIZII/TESTE/ISTORIC actualizate.

## FRONTURI DESCHISE (gasite aceasta tura)
1. **brut=0 tacit pe Stat de plata** (FRONT A de mai sus) - datele reziduale, semnalul pe ecran. NEREPARAT.
2. **facturi emise necontabilizate** (FRONT C) - fluxul de contare a facturilor emise pe 70x. De cercetat.

## VERIFICAT SI CURAT (nu sunt defecte)
- Vectorul fiscal P2: regim_fiscal='profit', platitor_tva=True, tip_decont='T', operatiuni_ic=False - corect;
  D300/D394 se genereaza pe trimestru (luna de sfarsit) si trec DUK.
- Dropdown declaratii P2: d301/d390 arata explicit "nu se datoreaza" cu motivul (neplatitor / fara IC). Corect.
- Date firma: banner "Profil incomplet - 1 camp obligatoriu lipseste: Nr. registrul comertului - blocheaza Bilant
  S1005" - mesaj precis (ce/unde/consecinta). Corect.
- Casete SEPA/REGES indisponibile pe Salariati: motiv VIZIBIL prin .caseta-info (nu title-only) - fix mostenit t001, corect.

## BACKLOG (mostenit din tenant_001, tot deschis)
Vezi predarea tenant_001 in git (inainte de 5dd0dc2): D112 podea part-time (FRONT #1 t001, cere autoritate externa),
E7 cod boala 17, umbrire strat migrare, mesaj TVA semafor diacritice, D406 SAF-T micro. Infra vizuala (contrast,
tinte <44px) - Costin da ordinea.
