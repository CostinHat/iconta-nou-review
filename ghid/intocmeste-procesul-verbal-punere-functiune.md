---
title: "Cum se întocmește procesul-verbal de punere în funcțiune?"
description: "De ce data punerii în funcțiune a unui mijloc fix contează pentru amortizarea fiscală și ce elemente trebuie să conțină documentul justificativ, conform Codului fiscal și normelor financiar-contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se întocmește procesul-verbal de punere în funcțiune?

Data punerii în funcțiune a unui mijloc fix nu e un detaliu administrativ — e momentul din care Codul fiscal începe să numere amortizarea. Un proces-verbal întocmit corect, cu data reală, e ceea ce apără acest calcul la un control.

## Temeiul legal

::: ghid-temei
„Amortizarea fiscală se calculează după cum urmează:
a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5)."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (12) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„2. Documentele justificative trebuie să cuprindă următoarele elemente principale: denumirea documentului; denumirea/numele și prenumele și, după caz, sediul persoanei juridice/adresa persoanei fizice care întocmește documentul; numărul documentului și data întocmirii acestuia; menționarea părților care participă la efectuarea operațiunii economico-financiare (când este cazul); conținutul operațiunii economico-financiare și, atunci când este necesar, temeiul legal al efectuării acesteia; datele cantitative și valorice aferente operațiunii economico-financiare efectuate, după caz; numele și prenumele, precum și semnăturile persoanelor care răspund de efectuarea operațiunii economico-financiare."
— OMFP 2634/2015, Anexa 1 (Norme generale), pct. 2 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Din cele două texte rezultă atât motivul pentru care procesul-verbal contează, cât și conținutul lui minim:

- **De ce contează data**: art. 28 alin. (12) lit. a) leagă direct începutul amortizării fiscale de luna următoare punerii în funcțiune — o dată greșită (prea devreme sau prea târziu) deplasează întregul calcul al amortizării deductibile pentru toată durata de utilizare a mijlocului fix.
- **Ce trebuie să conțină documentul**, ca orice document justificativ conform pct. 2 din normele generale: denumirea documentului (proces-verbal de punere în funcțiune), datele de identificare ale entității, numărul și data întocmirii, descrierea operațiunii (mijlocul fix pus în funcțiune, cu datele lui de identificare), datele cantitative/valorice (valoarea de intrare) și semnăturile persoanelor responsabile.
- Data întocmirii procesului-verbal trebuie să coincidă cu data reală a punerii efective în funcțiune — nu cu data facturii de achiziție, nu cu data recepției fizice a bunului dacă acestea preced momentul în care mijlocul fix devine efectiv utilizabil în activitate.

## Ce se greșește în practică

- Se confundă data facturii de achiziție sau data recepției cu data punerii în funcțiune — amortizarea trebuie calculată de la luna următoare celei în care mijlocul fix a devenit efectiv utilizabil, nu de la achiziție.
- Se omite semnătura persoanelor responsabile de efectuarea operațiunii, deși pct. 2 din normele generale o cere ca element obligatoriu al oricărui document justificativ.
- Se întocmește procesul-verbal la mult timp după punerea efectivă în funcțiune, ceea ce creează o discrepanță greu de justificat la control între data reală și data din document.

## Ce face iConta.eu

La data acestui ghid, nu am putut confirma din codul aplicației o funcție care să genereze automat procesul-verbal de punere în funcțiune ca document — modulele legate de mijloace fixe (`core/mijloace_fixe_import_api.py`, `core/repo_mijloace_fixe.py`) gestionează evidența activelor și calculul amortizării pe baza datei de punere în funcțiune introduse de contabil, dar întocmirea și semnarea procesului-verbal ca document justificativ rămân un pas manual, în afara aplicației.

[iConta.eu](/)
