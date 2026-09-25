---
title: "Trebuie autorizate toate codurile CAEN ale unui SRL?"
description: "De ce contează fiscal codurile CAEN secundare ale unui SRL, chiar dacă nu sunt activitatea principală, potrivit regulilor de impozitare a microîntreprinderilor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Trebuie autorizate toate codurile CAEN ale unui SRL?

Autorizarea propriu-zisă a fiecărui cod CAEN (sanitar, PSI, mediu) e o chestiune de drept al societăților, reglementată la Registrul Comerțului, nu de legislația fiscală. Dar fiscal, chiar și un cod CAEN secundar — nu doar cel principal — poate schimba radical cota de impozit a unei microîntreprinderi.

## Temeiul legal

::: ghid-temei
„3%, pentru microîntreprinderile care: [...] 2. desfășoară activități, principale sau secundare, corespunzătoare codurilor CAEN: 5821 - Activități de editare a jocurilor de calculator, 5829 - Activități de editare a altor produse software, 6201 - Activități de realizare a soft-ului la comandă (software orientat client), 6209 - Alte activități de servicii privind tehnologia informației, 5510 - Hoteluri și alte facilități de cazare similare [...], 5610 - Restaurante [...]. [...] (4^3) În situația în care persoanele juridice române care desfășoară activități corespunzătoare codurilor CAEN prevăzute la alin. (1) lit. b) pct. 2 obțin venituri și din alte activități în afara celor corespunzătoare acestor coduri CAEN, cota de impozitare de 3% se aplică și pentru veniturile din aceste alte activități."
— Legea 296/2023, care modifică art. 51 alin. (1) lit. b) pct. 2 și introduce alin. (4^3) din Codul fiscal (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Câteva consecințe practice ale textului:

- Cuvântul-cheie e „**principale sau secundare**" — nu contează dacă un cod CAEN din listă e activitatea de bază sau doar una declarată suplimentar; simpla desfășurare a ei duce cota la 3%.
- Odată ce firma desfășoară efectiv o activitate din listă, **cota de 3% se extinde asupra tuturor veniturilor**, nu doar asupra celor din activitatea „sensibilă" (alin. (4^3)).
- Schimbarea de cotă se aplică **de la trimestrul** în care microîntreprinderea începe să desfășoare activitatea respectivă, nu retroactiv de la începutul anului (alin. (4^1)).
- Dacă firma încetează activitatea din listă și veniturile rămân sub 60.000 euro, revine la cota de 1% începând cu trimestrul respectiv (alin. (4^2)).

Autorizarea administrativă propriu-zisă (sanitar-veterinară, PSI, protecția muncii etc.) pentru fiecare cod CAEN declarat la înființare rămâne, în schimb, guvernată de legislația privind înregistrarea și autorizarea funcționării comercianților — un domeniu care ține de Registrul Comerțului, nu de ANAF, și pe care sursele fiscale verificate de iConta.eu nu îl acoperă.

## Ce se greșește în practică

- Se presupune că doar activitatea principală (codul CAEN de bază, cel din certificatul constatator) contează fiscal — o activitate secundară din lista de mai sus schimbă la fel de sigur cota la 3%.
- Se aplică cota de 3% retroactiv de la 1 ianuarie când, de fapt, schimbarea produce efecte doar de la trimestrul în care activitatea efectiv începe.
- Se crede că numai veniturile din codul CAEN „sensibil" sunt taxate la 3% — legea prevede explicit că toate veniturile microîntreprinderii intră sub această cotă, odată declanșată condiția.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **reține un singur cod CAEN în profilul firmei** — cel folosit pentru validarea declarațiilor care cer acest câmp (de exemplu, D112, unde codul trebuie să existe în nomenclatorul acceptat de ANAF, altfel declarația e respinsă). Aplicația **nu urmărește lista completă de coduri CAEN secundare** ale unei firme și nu determină automat, pe baza acestei liste, dacă microîntreprinderea trebuie să treacă la cota de 3% conform art. 51 alin. (1) lit. b) pct. 2 — verificarea rămâne, la acest moment, în sarcina contabilului.

[iConta.eu](/)
