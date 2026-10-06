---
title: "Imobilizările în curs de execuție și amortizarea activelor noi se scad din baza de calcul a IMCA?"
description: "Da: formula IMCA scade I (imobilizări în curs din 2024) și A (amortizarea contabilă a activelor noi din 2024), doar pentru categoriile eligibile și cu obligația de păstrare a activelor."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Imobilizările în curs de execuție și amortizarea activelor noi se scad din baza de calcul a IMCA?

Da. Formula impozitului minim pe cifra de afaceri (IMCA) are doi indicatori care reduc baza tocmai pentru firmele care investesc. **I** reprezintă imobilizările în curs de execuție înregistrate începând cu 1 ianuarie 2024. **A** reprezintă amortizarea contabilă la cost istoric a activelor achiziționate sau produse de la aceeași dată. Ambele se scad după veniturile care se scad (Vs).

Scăderea are însă condiții. Activele trebuie să facă parte din categoriile eligibile stabilite prin ordin al ministrului finanțelor, iar firma trebuie să le păstreze o perioadă minimă. Dacă activul e înstrăinat prea devreme, IMCA se recalculează cu accesorii.

## Temeiul legal

::: ghid-temei
„I - valoarea imobilizărilor în curs de execuție ocazionate de achiziția/producția de active, înregistrate în evidența contabilă începând cu data de 1 ianuarie 2024, respectiv începând cu prima zi a anului fiscal modificat care începe în anul 2024;"
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (3), indicatorul I (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„A - amortizarea contabilă la nivelul costului istoric aferentă activelor achiziționate/produse începând cu data de 1 ianuarie 2024/prima zi a anului fiscal modificat care începe în anul 2024. Nu se cuprinde în acest indicator amortizarea contabilă a activelor incluse în valoarea indicatorului I."
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (3), indicatorul A (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„au obligația de a păstra în patrimoniu activele respective cel puțin o perioadă egală cu jumătate din durata de utilizare economică, stabilită potrivit reglementărilor contabile aplicabile, dar nu mai mult de 5 ani."
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (15) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Ce înseamnă concret:

- **Doar investițiile din 2024 încoace.** Imobilizările în curs și activele intrate înainte de 1 ianuarie 2024, sau înainte de primul an fiscal modificat început în 2024, nu reduc baza.
- **Doar categoriile eligibile.** Activele luate în calcul pentru I și A sunt cele stabilite prin ordin al ministrului finanțelor, după criterii legate de natura activității (art. 18^1 alin. (12)). Nu orice mijloc fix intră.
- **Fără dublă scădere.** Amortizarea activelor deja cuprinse în I nu se mai scade și în A.
- **Cost istoric.** A este amortizarea contabilă la cost istoric, nu amortizarea fiscală și nu amortizarea valorilor reevaluate.
- **Valoarea negativă.** Dacă după scăderi formula dă un rezultat negativ, IMCA este zero (alin. (4)).
- **Păstrarea activelor.** Firma trebuie să păstreze activele cel puțin jumătate din durata de utilizare economică, dar nu mai mult de 5 ani. Altfel recalculează IMCA de la trimestrul sau anul scăderii, plătește accesorii și depune declarație rectificativă. Excepții: reorganizări, lichidare/faliment, distrugere sau furt dovedite, scoatere din patrimoniu impusă de lege (alin. (15)).

Pentru 2026, cota IMCA este 0,5% (art. 18^1 alin. (16)). Articolul se aplică până la 31 decembrie 2026, respectiv până la sfârșitul anului fiscal modificat care se încheie în 2027 (alin. (17)). Exemplul 1 din norme (HG 1/2016, pct. 4^1 alin. (2)) arată scăderea lui I și A cu cota de 1%. Pentru 2026 se folosește 0,5%.

::: ghid-exemplu
SC Exemplu SA, peste pragul de 50.000.000 euro, are cumulat în 2026:

- VT: 500.000.000 lei; Vs: 20.000.000 lei;
- I (lucrări în curs la o linie de producție eligibilă, înregistrate în 2026): 30.000.000 lei;
- A (amortizarea contabilă a utilajelor eligibile puse în funcțiune în 2024–2026): 10.000.000 lei.

IMCA = 0,5% × (500.000.000 − 20.000.000 − 30.000.000 − 10.000.000) = 0,5% × 440.000.000 = 2.200.000 lei.

Fără I și A, IMCA ar fi fost 0,5% × 480.000.000 = 2.400.000 lei.
:::

## Ce se greșește în practică

- În A se include amortizarea tuturor mijloacelor fixe, și a celor intrate înainte de 2024.
- Se scad active care nu fac parte din categoriile eligibile stabilite prin ordinul ministrului finanțelor.
- Aceeași investiție se scade o dată în I și încă o dată în A.
- Un activ scăzut din bază se vinde înainte de termenul de păstrare, fără recalcularea IMCA și fără declarație rectificativă.

## Ce face iConta.eu

iConta.eu calculează IMCA în D101, validată pe validatorul oficial ANAF, după formula cotă × (VT − Vs − I − A). Cota e aleasă după anul fiscal, iar rezultatul negativ e trecut la zero. Valorile I și A se introduc de contabil. Aplicația nu selectează automat activele eligibile și nu urmărește termenul de păstrare a lor.

[iConta.eu](/)
