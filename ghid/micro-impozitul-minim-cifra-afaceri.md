---
title: "Micro și impozitul minim pe cifra de afaceri: se confundă"
description: "De ce impozitul micro (Titlul III, plafon 100.000 euro) și impozitul minim pe cifra de afaceri — IMCA (art. 18^1, prag 50.000.000 euro) nu se pot aplica niciodată aceleiași firme."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro și impozitul minim pe cifra de afaceri: se confundă

Cele două noțiuni sunt confundate frecvent pentru că ambele se raportează la „venituri"/„cifră de afaceri" și ambele au apărut din nevoia de a limita optimizarea fiscală — dar sunt reglementate în titluri diferite ale Codului fiscal, se adresează unor firme de dimensiuni complet diferite și nu se pot aplica niciodată simultan aceleiași societăți.

## Temeiul legal

::: ghid-temei
„Contribuabilii, alții decât cei prevăzuți la art. 15, care înregistrează în anul precedent o cifră de afaceri de peste 50.000.000 euro și care în anul de calcul determină un impozit pe profit [...] mai mic decât impozitul minim pe cifra de afaceri stabilit potrivit prevederilor alin. (3), sunt obligați la plata impozitului pe profit la nivelul impozitului minim pe cifra de afaceri."
— Legea 227/2015, art. 18^1 alin. (1), Titlul II (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea 227/2015, art. 52 alin. (1), Titlul III (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Diferența e de scară și de mecanism:

- **Impozitul micro** (Titlul III) se aplică firmelor **sub** 100.000 euro venituri anuale (plafon redus prin OUG 8/2026 de la 25.02.2026); cota e 1% pe venituri.
- **Impozitul minim pe cifra de afaceri — IMCA** (art. 18^1, Titlul II) se aplică firmelor plătitoare de impozit pe profit **cu peste 50.000.000 euro** cifră de afaceri, ca „plasă de siguranță" pentru cazul în care impozitul pe profit calculat normal (16%) ar ieși mai mic decât 1% din (venituri totale minus anumite scăderi).

Cele două praguri (100.000 euro și 50.000.000 euro) fac imposibilă coexistența: o firmă cu venituri sub 100.000 euro rămâne, dacă vrea, microîntreprindere și e la ani-lumină de pragul IMCA; o firmă care ajunge la 50.000.000 euro cifră de afaceri a depășit, cu mult timp în urmă, plafonul de 100.000 euro și a devenit plătitoare de impozit pe profit conform art. 52. IMCA nu poate „ajunge" niciodată la o microîntreprindere.

## Ce se greșește în practică

- Se crede că IMCA e o variantă „pentru firme mari" a impozitului micro, ca și cum ar fi din aceeași familie de reglementare — sunt titluri diferite (II vs. III), cu scop și mecanism total diferite.
- Se calculează greșit eligibilitatea pentru micro folosind formula IMCA (venituri totale minus scăderi specifice, cu cotă de 1%/0,5%), deși baza de calcul a impozitului micro e reglementată separat, la art. 53.
- Se aplică, eronat, IMCA unei firme mici doar pentru că are un an cu profit mic sau pierdere — IMCA se aplică exclusiv contribuabililor plătitori de impozit pe profit care depășesc pragul de 50.000.000 euro cifră de afaceri.

## Ce face iConta.eu

iConta.eu calculează atât baza impozitului micro (venituri din orice sursă, conform art. 53), cât și, separat, eligibilitatea și formula IMCA (art. 18^1) — aplicația verifică dacă cifra de afaceri a anului precedent depășește pragul de 50.000.000 euro și calculează impozitul minim pe cifra de afaceri (IMCA = cotă × (VT − Vs − I − A)) pentru firmele plătitoare de impozit pe profit care se încadrează la această obligație. Cele două calcule sunt implementate ca module separate, exact pentru că se adresează unor categorii de firme diferite, care nu se suprapun niciodată.

[iConta.eu](/)
