---
title: "Cum se declară dividendele plătite în valută?"
description: "Cursul de schimb BNR aplicabil la calculul impozitului pe dividende atunci când plata efectivă se face în valută, conform reglementărilor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară dividendele plătite în valută?

Un dividend aprobat în lei, dar plătit efectiv unui asociat în valută (de exemplu unui asociat nerezident, prin transfer în euro sau dolari), nu se declară la cursul de la data aprobării distribuirii, ci la cursul de schimb valabil în ziua în care are loc efectiv operațiunea de plată.

## Temeiul legal

::: ghid-temei
„319. - O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii."
— OMFP nr. 1.802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate), pct. 319 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din regula generală de conversie rezultă tratamentul pentru dividendele plătite în valută:

- **Distribuirea** dividendului (aprobarea sa, înregistrată în creditul contului 457) e o operațiune separată de **plata** efectivă — dacă între cele două momente trece timp, iar plata se face în valută, plata se înregistrează la cursul BNR din ziua plății, nu din ziua distribuirii.
- Impozitul pe dividende (16% asupra dividendului brut, potrivit modificărilor aduse de Legea nr. 141/2025) se calculează și se reține la data plății, prin urmare baza de impozitare în lei rezultă din conversia la cursul BNR valabil în acea zi, nu la cursul din momentul aprobării distribuirii.
- Eventualele diferențe de curs valutar între data la care s-a înregistrat obligația de plată (creditul 457) și data plății efective se recunosc distinct, la venituri sau cheltuieli financiare din diferențe de curs, potrivit regulilor generale de contabilizare a operațiunilor în valută.
- Termenul de virare a impozitului rămâne cel general — până la data de 25 inclusiv a lunii următoare celei în care se face plata — indiferent de moneda în care s-a efectuat plata.

## Ce se greșește în practică

- Se calculează impozitul pe dividende la cursul de la data aprobării distribuirii (AGA), nu la cursul din ziua plății efective în valută.
- Se omite înregistrarea diferenței de curs valutar apărute între distribuire și plată, tratând suma ca fiind identică în lei la ambele momente.
- Se confundă termenul de virare a impozitului (25 a lunii următoare plății) cu data distribuirii aprobate în AGA, decalând greșit scadența.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează impozitul pe dividende ponderat pe fiecare tranșă de plată, potrivit distribuirilor înregistrate (`core/dividende_curs.py`, funcția `impozit_ponderat`), care potrivește FIFO plățile pe distribuirile deschise și aplică cota de impozit valabilă la data fiecărei plăți. Pentru conversia sumelor plătite în valută, aplicația se bazează pe cursurile BNR gestionate în `core/curs_bnr.py`. Introducerea corectă a monedei de plată și verificarea faptului că suma din extrasul bancar corespunde cursului BNR din ziua plății rămân, însă, o verificare manuală a contabilului la momentul înregistrării plății.

[iConta.eu](/)
