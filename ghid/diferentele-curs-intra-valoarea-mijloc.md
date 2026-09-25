---
title: "Diferențele de curs intră în valoarea unui mijloc fix cumpărat în valută?"
description: "Nu: un mijloc fix e element nemonetar, înregistrat o singură dată la cursul BNR din data tranzacției. Diferențele de curs ulterioare apar doar la decontarea datoriei către furnizor și se recunosc la 665/765, nu în valoarea activului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Diferențele de curs intră în valoarea unui mijloc fix cumpărat în valută?

Nu. Valoarea mijlocului fix rămâne fixă, la cursul de schimb din data înregistrării inițiale. Diferențele de curs care apar ulterior — la plata datoriei către furnizor — se recunosc separat, ca venit sau cheltuială financiară, nu se adaugă la costul activului.

## Temeiul legal

::: ghid-temei
„315. - (1) Prin elemente monetare se înțelege disponibilitățile bănești și activele/datoriile de primit/de plătit în sume fixe sau determinabile. [...] (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale; și provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."
— OMFP 1802/2014, pct. 315 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)

„319. - O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii."
— OMFP 1802/2014, pct. 319 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)

„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Mecanismul complet, din cele trei texte:

- **Mijlocul fix** e explicit un element **nemonetar** (pct. 315 alin. (3)) — nu se reevaluează la cursul valutar, indiferent cum fluctuează cursul după achiziție.
- Valoarea lui se stabilește **o singură dată**, la cursul BNR din data tranzacției (pct. 319), și rămâne fixă contabil, oricât timp trece.
- **Datoria** către furnizor (dacă mijlocul fix a fost cumpărat pe credit comercial, nu plătit imediat) e însă un element **monetar** — la decontarea ei (plata efectivă), orice diferență între cursul de la înregistrare și cursul de la plată se recunoaște ca venit sau cheltuială financiară (765/665), separat de costul activului.

Practic: costul mijlocului fix nu se „ajustează" niciodată din cauza cursului valutar, indiferent dacă plata furnizorului se face imediat sau eșalonat.

## Ce se greșește în practică

- Se ajustează valoarea contabilă a mijlocului fix la fiecare plată către furnizor, în funcție de cursul zilei — greșit: activul rămâne la valoarea inițială, doar datoria (nu activul) generează diferențe de curs.
- Se confundă „diferență de curs la decontarea datoriei" cu „reevaluarea mijlocului fix" — sunt operațiuni complet diferite: prima e monetară (datoria), a doua nu se aplică deloc mijloacelor fixe.
- Se omite recunoașterea diferenței de curs la plata datoriei, considerând-o „parte din prețul mijlocului fix" — diferența trebuie recunoscută distinct, la 665/765, în luna în care apare.

## Ce face iConta.eu

Motorul de diferențe de curs (`core/diferente_curs.py`) acceptă strict trei tipuri de element: creanță, disponibil, datorie — un apel cu „mijloc fix" sau „stoc" ridică eroare, exact conform regulii de mai sus (elementele nemonetare nu intră în acest calcul). Pentru **datoria** către furnizorul mijlocului fix, dacă plata se face în valută la un curs diferit de cel din evidență, aplicația calculează corect diferența prin operațiunea „Decontare în valută" (`decontare_valuta`), cu tip „datorie", generând automat nota contabilă cu diferența pe 665/765.

Valoarea propriu-zisă a mijlocului fix, la înregistrarea inițială, se stabilește separat, la cursul BNR din data tranzacției — acest pas nu ține de motorul de diferențe de curs, ci de fluxul obișnuit de înregistrare a achiziției.

[iConta.eu](/)
