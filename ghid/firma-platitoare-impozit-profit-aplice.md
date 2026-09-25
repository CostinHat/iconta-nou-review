---
title: "Poate o firmă plătitoare de impozit pe profit să aplice amortizarea accelerată?"
description: "Condițiile din Codul fiscal pentru aplicarea metodei de amortizare accelerată, disponibilă doar pentru anumite categorii de mijloace fixe."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate o firmă plătitoare de impozit pe profit să aplice amortizarea accelerată?

Amortizarea accelerată e o metodă fiscală permisă de Codul fiscal, dar nu nelimitat — legea o rezervă anumitor categorii de active și impune un mod de calcul specific pentru primul an de utilizare. Da, o firmă plătitoare de impozit pe profit poate aplica amortizarea accelerată, dar doar în condițiile prevăzute expres.

## Temeiul legal

::: ghid-temei
„(8) În cazul metodei de amortizare accelerată, amortizarea se calculează după cum urmează: a) pentru primul an de utilizare, amortizarea nu poate depăși 50% din valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix; b) pentru următorii ani de utilizare, amortizarea se calculează prin raportarea valorii rămase de amortizare a mijlocului fix la durata normală de utilizare rămasă a acestuia."
— Codul fiscal (Legea 227/2015), art. 28 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text:

- **Da**, un contribuabil plătitor de impozit pe profit poate opta pentru amortizarea accelerată — metoda e prevăzută în același articol care reglementează amortizarea fiscală pentru mijloacele fixe amortizabile, în general.
- **Pentru primul an de utilizare**, amortizarea nu poate depăși **50% din valoarea fiscală** de la data intrării mijlocului fix în patrimoniu — o limită maximă, nu o valoare fixă obligatorie.
- **Pentru anii următori**, amortizarea revine la un calcul liniar pe valoarea rămasă, raportată la durata normală de utilizare rămasă — nu se continuă cu rate accelerate în fiecare an.
- Legea prevede și o variantă **superaccelerată** (art. 28 alin. (8^1), introdus prin OUG 8/2026), cu plafon de 65% în primul an, aplicabilă doar activelor noi puse în funcțiune în 2026, din subgrupele 2.1 (echipamente tehnologice) sau 2.4 (animale/plantații).
- Metoda accelerată nu e disponibilă pentru orice categorie de mijloc fix: art. 28 alin. (5) rezervă amortizarea liniară exclusiv construcțiilor (lit. a), permite liniară/degresivă/**accelerată** doar echipamentelor tehnologice (lit. b), iar pentru „orice alt mijloc fix" (mobilier, aparatură de măsură, mijloace de transport) rămân disponibile doar liniara și degresiva, fără accelerata.
- Contribuabilii care aplică anumite scutiri de impozit pe profit (ex. scutirea pentru profitul reinvestit, în anumite condiții) pot avea restricții privind opțiunea pentru amortizare accelerată/superaccelerată pentru activele respective (art. 22 alin. (9), cu excepții punctuale pentru anumite subgrupe în 2026).

## Ce se greșește în practică

- Se aplică 50% amortizare în fiecare an de utilizare, nu doar în primul — legea limitează procentul de 50% strict la primul an.
- Se presupune că amortizarea accelerată e disponibilă pentru orice mijloc fix — de fapt e permisă doar pentru echipamente tehnologice (subgrupa 2.1); pentru construcții e obligatorie amortizarea liniară, iar pentru mobilier, aparatură sau mijloace de transport rămân doar liniara și degresiva.
- Se confundă amortizarea accelerată cu cea superaccelerată (introdusă prin OUG 8/2026) — au plafoane diferite pentru primul an (50%, respectiv 65%) și condiții diferite de eligibilitate (superaccelerata cere activ nou, pus în funcțiune în 2026, din subgrupa 2.1 sau 2.4).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **calculează amortizarea fiscală a mijloacelor fixe pe toate cele patru metode** — liniară, degresivă, accelerată și superaccelerată — în modulul `core/d406_active.py`, inclusiv regula celor 50% din valoarea fiscală în primul an pentru metoda accelerată (art. 28 alin. (8)) și 65% pentru superaccelerata (art. 28 alin. (8^1)). Aplicația **verifică și restricția pe categorie de activ**: refuză metoda accelerată pentru construcții sau pentru mijloace fixe din afara subgrupei 2.1, respectând explicit art. 28 alin. (5) din Codul fiscal.

[iConta.eu](/)
