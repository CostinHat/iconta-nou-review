---
title: "Cum se raportează modernizarea unui mijloc fix în SAF-T"
description: "Ce prevede Codul fiscal despre recalcularea amortizării la o investiție ulterioară asupra unui mijloc fix și cum se leagă de obligația generală de raportare SAF-T."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează modernizarea unui mijloc fix în SAF-T

O investiție ulterioară care îmbunătățește parametrii tehnici ai unui mijloc fix deja în funcțiune (modernizare, extindere, upgrade) nu e o achiziție nouă din perspectivă fiscală — e o recalculare a amortizării activului existent. Iar tot ce ține de evidența contabilă și fiscală, inclusiv acest tip de recalculare, intră sub obligația generală de raportare prin fișierul standard de control fiscal.

## Temeiul legal

::: ghid-temei
„ART. 59^1 Obligația de depunere a fișierului standard de control fiscal
(1) Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fișierul standard de control fiscal."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 59^1 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Amortizarea fiscală se calculează după cum urmează: [...] d) pentru investițiile efectuate la mijloacele fixe existente, sub forma cheltuielilor ulterioare realizate în scopul îmbunătățirii parametrilor tehnici inițiali și care conduc la obținerea de beneficii economice viitoare, amortizarea fiscală se calculează pe baza valorii rămase majorate cu investițiile efectuate, a metodei de amortizare utilizată pentru mijlocul fix îmbunătățit, pe durata normală de utilizare rămasă."
— Legea nr. 227/2015 (Codul fiscal), art. 28 alin. (12) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

**Limitare declarată:** cele două texte dau, împreună, principiul — orice modernizare afectează amortizarea fiscală (valoare rămasă majorată, pe durata rămasă) și, ca element din evidența contabilă și fiscală, intră sub obligația generală de raportare SAF-T. Sursele verificate **nu conțin însă un articol distinct, tehnic, al ordinelor ANAF care reglementează structura fișierului D406 (OPANAF nr. 1783/2021 și modificările lui), care să detalieze exact cum se marchează o modernizare** (ca element separat sau ca majorare a valorii activului existent) în secțiunea de active fixe a SAF-T. Ce rezultă cert din principiile de mai sus:

- Modernizarea **nu se raportează ca achiziție de mijloc fix nou** — ea majorează valoarea rămasă neamortizată a activului deja existent, iar amortizarea se recalculează pe durata rămasă a acestuia.
- Excepție: dacă durata normală de utilizare a activului îmbunătățit era deja expirată la momentul investiției, se stabilește o durată nouă de către o comisie tehnică sau un expert independent — situație în care recalcularea amortizării pleacă de la o bază diferită.

## Ce se greșește în practică

- Se raportează modernizarea ca intrare separată de mijloc fix, cu propria durată de amortizare de la zero — legea cere majorarea valorii rămase a activului existent, nu crearea unui activ nou.
- Se ignoră recalcularea amortizării pe durata rămasă, continuând să se aplice cota inițială la valoarea majorată, ceea ce alungește artificial perioada de recuperare fiscală a investiției.
- Se presupune că obligația SAF-T privind activele are propriile reguli, separate de Codul fiscal — de fapt SAF-T raportează exact ce rezultă din aplicarea corectă a regulilor de amortizare din Codul fiscal, nu o metodologie proprie.

## Ce face iConta.eu

Verificat în cod: modulul `core/d406_active.py` calculează amortizarea mijloacelor fixe pentru raportarea în D406/SAF-T, cu tratament explicit pentru reevaluare (recalculare de la zero, pe durata rămasă, cu temei OMFP 1802/2014 pct. 111-116). Aplicația **nu conține, la acest moment, un tratament separat pentru investițiile ulterioare/modernizările** care majorează valoarea rămasă a unui mijloc fix existent (nu am găsit în cod nicio referire la „investiție", „îmbunătățire" sau „modernizare" în acest modul) — recalcularea amortizării ca urmare a unei modernizări, conform art. 28 alin. (12) lit. d) din Codul fiscal, rămâne, deocamdată, o operațiune realizată manual de contabil.

[iConta.eu](/)
