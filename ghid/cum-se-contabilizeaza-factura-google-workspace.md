---
title: Cum se contabilizează factura Google Workspace?
description: Factura Google Workspace primită de o firmă română neplătitoare de TVA de la Google Ireland Limited declanșează obligația de taxare inversă conform art. 307 alin. (2) și trebuie declarată în Secțiunea 4.1 a D301.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se contabilizează factura Google Workspace?

Factura de abonament Google Workspace este emisă, pentru clienții din România, de Google Ireland Limited — o entitate stabilită în alt stat membru UE. Pentru o firmă română neplătitoare de TVA, această factură nu este o simplă cheltuială de contabilizat: ea declanșează obligația de a calcula și declara TVA prin taxare inversă.

## Temeiul legal

::: ghid-temei
**Articolul 278 alin. (2)**: Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]

**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

Instrucțiuni OPANAF 592/2016: În secțiunea 4.1 se preiau din secțiunea 4 doar achizițiile de servicii intracomunitare, pentru care beneficiarul este obligat la plata taxei pe valoarea adăugată conform art. 307 alin. (2) din Codul fiscal.
:::

## De la contabilizare la obligația de declarare

Contabilizarea propriu-zisă a facturii (înregistrarea cheltuielii) este un pas separat de obligația fiscală care apare automat, prin efectul art. 278 alin. (2) și art. 307 alin. (2): pentru că beneficiarul (firma română) își are sediul activității economice în România, locul prestării serviciului este considerat România, iar firma română — nu Google Ireland Limited — este cea obligată la plata TVA aferentă acestei achiziții.

Această obligație de plată prin taxare inversă este independentă de valoarea facturii — nu există un plafon sub care Google Workspace să fie scutit de această regulă — și se declară în Secțiunea 4.1 a D301, ca achiziție de servicii intracomunitare de la un furnizor stabilit în UE (Irlanda).

::: ghid-exemplu
Abonament Google Workspace de 6 EUR/lună, curs BNR la data exigibilității 4,9700 lei/EUR.

Baza = 6 × 4,9700 = 29,82 lei
TVA (21%, cotă standard din 01.08.2025) = 29,82 × 21% = 6,26 lei

Baza și TVA se raportează în Secțiunea 4.1 din D301 pentru luna în care a luat naștere exigibilitatea taxei.
:::

## Ce se greșește în practică

- Factura este contabilizată doar ca o cheltuială obișnuită, fără a se sesiza obligația de taxare inversă și declarare în D301.
- Se așteaptă acumularea mai multor facturi pentru a "depăși un plafon" înainte de a solicita înregistrarea specială art. 317 — deși pentru servicii nu există niciun plafon.
- Se aplică cursul de schimb de la data facturii Google, în loc de cursul valabil la data exigibilității taxei.
- Se omite solicitarea codului special de TVA (art. 317) înainte de primirea primei facturi Google Workspace, ceea ce poate duce la înregistrare din oficiu de către organul fiscal.
- Se declară operațiunea în Secțiunea 4 generică, deși furnizorul (Google Ireland Limited) este stabilit în UE, iar operațiunea aparține Secțiunii 4.1.

## Ce face iConta.eu

Aplicația calculează automat baza de impozitare (`baza = round(val_valuta × curs, 0)`), cu rotunjire aritmetică (`ROUND_HALF_UP`), și refuză generarea declarației dacă lipsește cursul valutar sau dacă acesta este zero ori negativ — cursul trebuie introdus manual de contabil, valabil la data exigibilității, aplicația nu îl preia automat de la BNR sau BCE. Pentru operațiunile de tip servicii intracomunitare (Secțiunea 4.1), aplicația face rollup automat al bazei și TVA în totalul Secțiunii 4, conform instrucțiunilor OPANAF 592/2016.

Introducerea operațiunii este blocată dacă firma este marcată în vectorul fiscal drept plătitoare de TVA (D301 este exclusiv pentru neplătitori). Aplicația nu validează însă automat că furnizorul introdus este efectiv stabilit în UE — câmpul de țară al partenerului este opțional și liber — astfel încât încadrarea corectă în Secțiunea 4.1 (și nu 4) rămâne responsabilitatea contabilului.

[iConta.eu](/)
