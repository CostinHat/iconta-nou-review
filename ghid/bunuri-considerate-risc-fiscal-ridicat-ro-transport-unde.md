---
title: "Ce bunuri sunt considerate cu risc fiscal ridicat în RO e-Transport și unde se stabilește lista?"
description: "Lista nu e în ordonanță, ci într-un ordin al președintelui ANAF (Ordinul 802/2022), pe coduri NC: legume, fructe, băuturi, sare și ciment, îmbrăcăminte, încălțăminte, fier și oțel."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Ce bunuri sunt considerate cu risc fiscal ridicat în RO e-Transport și unde se stabilește lista?

OUG 41/2022 nu enumeră bunurile. Ea trimite la un **ordin al președintelui ANAF**, iar acesta este Ordinul ANAF nr. 802/2022. Anexa ordinului stabilește categoriile prin **codurile din Nomenclatura combinată (NC)**, nu prin denumirea comercială a produsului. Încadrarea se face deci după codul tarifar al fiecărui bun.

Contează din două motive. Transportul rutier pe teritoriul național se declară doar pentru bunurile din listă. Transporturile rutiere internaționale (achiziții și livrări intracomunitare, import, export) se declară însă pentru orice bunuri, nu doar pentru cele din listă (art. 1 alin. (2)).

## Temeiul legal

::: ghid-temei
„transportul rutier pe teritoriul național al bunurilor cu risc fiscal ridicat - transportul rutier pe drumurile publice, având punct de plecare și punct de sosire pe teritoriul României, al bunurilor stabilite ca fiind din categoria celor cu risc fiscal ridicat prin ordin al președintelui Agenției Naționale de Administrare Fiscală, indiferent de modul de organizare a transportului;"
— OUG 41/2022, art. 2 pct. 2 (sursă: anaf_surse/oug_41_2022.txt)

„(2) Prin ordin al președintelui Agenției Naționale de Administrare Fiscală emis în termen de 15 zile de la data intrării în vigoare a prezentei ordonanțe de urgență se stabilesc bunurile cu risc fiscal ridicat transportate rutier care fac obiectul monitorizării prin Sistemul RO e-Transport."
— OUG 41/2022, art. 15 alin. (2) (sursă: anaf_surse/oug_41_2022.txt)
:::

::: ghid-temei
„Se stabilesc bunurile cu risc fiscal ridicat transportate rutier care fac obiectul monitorizării prin Sistemul RO e-Transport, astfel cum sunt prevăzute în anexa care face parte integrantă din prezentul ordin."
— Ordinul ANAF nr. 802/2022, art. 1 (sursă: anaf_surse/ordin_802_2022.html)
:::

Categoriile din anexa Ordinului ANAF nr. 802/2022, în forma publicată:

1. Legume, plante, rădăcini și tuberculi alimentari: NC 0701–0714.
2. Fructe comestibile, coji de citrice sau de pepeni: NC 0801–0814.
3. Băuturi, lichide alcoolice și oțet: NC 2201–2208. Sunt exceptate produsele accizabile în regim suspensiv, cu e-DA.
4. Sare, sulf, pământuri și pietre, ipsos, var și ciment: NC 2505 și 2517.
5. Îmbrăcăminte tricotată sau croșetată: NC 6101–6117.
6. Îmbrăcăminte netricotată: NC 6201–6212 și 6214–6217.
7. Încălțăminte și părți ale acesteia: NC 6401–6405.
8. Fontă, fier și oțel: NC 7213 și 7214.

Alte reguli care decid obligația:

- **Partida mixtă.** Dacă în aceeași partidă sunt și bunuri din listă, și bunuri din afara ei, se declară **toate** bunurile din partidă (art. 12 alin. (1)).
- **Excepții.** Ordonanța exceptează, printre altele, transporturile sub e-DA/e-DAS și coletele poștale (art. 16).
- **Organizarea transportului nu contează.** Obligația există „indiferent de modul de organizare a transportului”: cu vehicul propriu, cu transportator contractat sau cu mașina clientului.

::: ghid-exemplu
SC Exemplu SRL, distribuitor de materiale de construcții, încarcă într-un camion ciment (NC 2523), bare de oțel (NC 7214) și gresie (NC 6907), toate pentru un singur client din țară. Barele de oțel sunt pe listă, deci partida este mixtă. SC Exemplu SRL declară în RO e-Transport **toate cele trei** produse din partidă, nu doar barele de oțel.
:::

## Ce se greșește în practică

- **Se caută produsul după denumire, nu după codul NC.** „Ciment” din lista de categorii înseamnă doar codurile 2505 și 2517 menționate expres, nu orice poziție tarifară a cimentului. Se verifică codul exact.
- **Se declară doar bunurile din listă dintr-o partidă mixtă.** Art. 12 cere declararea tuturor bunurilor din partidă.
- **Se aplică lista și la transporturile internaționale.** După extinderea sistemului, transportul rutier internațional se declară pentru orice bunuri.
- **Nu se verifică forma actuală a ordinului.** Lista poate fi modificată prin ordin ANAF. Înainte de încadrare, se verifică forma în vigoare la data transportului.

## Ce face iConta.eu

Pe cardul e-Transport, iConta.eu cere pentru fiecare bun **codul tarifar (NC)**, denumirea, cantitatea, greutățile și valoarea fără TVA. Fără ele, XML-ul notificării nu se generează. Aplicația nu compară automat codurile NC cu lista din Ordinul ANAF nr. 802/2022. Decizia dacă un transport intern trebuie declarat rămâne a contabilului.

[iConta.eu](/)
