---
title: Cum se tratează un autoturism cumpărat de PFA?
description: Autoturismul folosit mixt de un PFA se amortizează integral după regulile generale, dar cheltuielile de funcționare (combustibil, întreținere, reparații) sunt deductibile doar 50%, dacă nu există foaie de parcurs care să justifice folosirea exclusivă în activitate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează un autoturism cumpărat de PFA?

Autoturismul este, probabil, activul care generează cele mai multe confuzii în contabilitatea unui PFA, pentru că îi corespund două regimuri fiscale diferite, care nu trebuie amestecate: regimul de amortizare a valorii de achiziție și regimul de deductibilitate limitată a cheltuielilor de funcționare.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 68 alin. (5) lit. j): "cheltuielile de funcționare, întreținere și reparații, aferente autoturismelor folosite de contribuabil sau membru asociat sunt deductibile limitat potrivit alin. (7) lit. k) la cel mult un singur autoturism aferent fiecărei persoane".

Codul fiscal, art. 68 alin. (7) lit. k): "50% din cheltuielile aferente vehiculelor rutiere motorizate care nu sunt utilizate exclusiv în scopul desfășurării activității și a căror masă totală maximă autorizată nu depășește 3.500 kg și nu au mai mult de 9 scaune de pasageri ... sunt integral deductibile pentru [taxi, curierat, pază, agenți de vânzări etc.] ... Cheltuielile care intră sub incidența acestor prevederi nu includ cheltuielile privind amortizarea."

HG 1/2016 (Norme metodologice), pct. 7 alin. (7): "În sensul prevederilor art. 68 alin. (7) lit. k) din Codul fiscal, ... Dacă vehiculele respective nu sunt utilizate exclusiv în scopul desfășurării activității, se limitează la 50% dreptul de deducere a cheltuielilor efectuate conform art. 68 alin. (4) și (5) din Codul fiscal legate de aceste vehicule, cu excepția cheltuielilor privind amortizarea pentru care se aplică regulile privind amortizarea prevăzute la art. 28 titlul II din Codul fiscal, după caz. ... În vederea acordării deductibilității integrale la calculul venitului net anual, justificarea utilizării vehiculelor se efectuează pe baza documentelor justificative și prin întocmirea foii de parcurs."

Codul fiscal, art. 28 alin. (6): amortizarea liniară "se stabilește prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix amortizabil."
:::

## Două regimuri, nu unul

Textul de lege e explicit pe acest punct, la ultima teză din HG 1/2016 pct. 7 alin. (7): plafonul de 50% se aplică cheltuielilor de funcționare, întreținere și reparații — **nu** amortizării. Amortizarea autoturismului urmează integral regulile generale de la art. 28 din Codul fiscal, indiferent dacă vehiculul e folosit exclusiv sau mixt.

::: ghid-exemplu
Un PFA cumpără un autoturism de 60.000 lei, folosit atât în activitate, cât și personal, fără foaie de parcurs care să ateste utilizare exclusivă. Amortizarea liniară anuală (pe durata normală de funcționare din catalog) se deduce integral, an de an. În schimb, cheltuielile cu combustibilul, service-ul și asigurarea RCA/CASCO din anul respectiv se deduc doar în proporție de 50%.
:::

Dacă PFA-ul întocmește foaie de parcurs și poate dovedi utilizarea exclusivă în scopul activității, cheltuielile de funcționare devin deductibile integral — dar doar pentru un singur autoturism pe persoană (art. 68 alin. (5) lit. j).

## Ce se greșește în practică

- Se aplică plafonul de 50% și la cheltuiala cu amortizarea, deși legea exclude explicit amortizarea de la această limitare.
- Se deduc integral cheltuielile de funcționare fără foaie de parcurs, doar pe considerentul că mașina "e a firmei".
- Se deduc cheltuieli pentru mai mult de un autoturism per persoană la rata integrală, deși limita legală e "cel mult un singur autoturism aferent fiecărei persoane".
- Se confundă prețul de achiziție cu o cheltuială curentă deductibilă imediat, în loc să fie recuperat prin amortizare pe durata normală de funcționare.
- Nu se verifică pragul valoric al mijlocului fix (vezi ghidul despre mijloacele fixe) înainte de a decide dacă autoturismul se amortizează sau se trece direct pe cheltuială.

## Ce face iConta.eu

Amortizarea autoturismului se calculează prin `registru_inventar(conn, schema, an)` din `core/rip_api.py`, pe baza datelor din tabela `mijloace_fixe` (valoare, dată PIF, durata normală de funcționare în luni) — amortizare liniară pe lunile scurse, conform formulei `amortizabil * luni / dnf_luni`. Partea de cheltuieli de funcționare supusă plafonului de 50% se înregistrează separat, ca plată, în categoria `cheltuiala_limitata` din `CATEGORII_PLATA`; fișa de calcul D212 (`fisa_d212`) exclude automat aceste sume din calcul, raportându-le distinct, iar aplicarea plafonului de 50% (sau a deducerii integrale, pe baza foii de parcurs) rămâne decizia contabilului.

[iConta.eu](/)
