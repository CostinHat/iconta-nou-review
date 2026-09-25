---
title: "Amortizarea mijloacelor fixe la firma micro: se deduce"
description: "De ce amortizarea unui mijloc fix nu reduce impozitul datorat de o microîntreprindere, câtă vreme baza de impozitare a acesteia e formată din venituri, nu din profit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea mijloacelor fixe la firma micro: se deduce

Pentru o firmă plătitoare de impozit pe profit, amortizarea unui mijloc fix e o cheltuială care reduce baza impozabilă. La o microîntreprindere, mecanismul nu funcționează la fel — impozitul de 1% se aplică pe venituri, nu pe diferența venituri-cheltuieli, deci amortizarea, ca orice altă cheltuială, nu are efect direct asupra sumei de plătit.

## Temeiul legal

::: ghid-temei
„(1) Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Codul fiscal (Legea 227/2015), art. 51 alin. (1), în forma aplicabilă de la 01.01.2026 (OUG 89/2025, art. I pct. 4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Baza pe care se aplică această cotă e definită separat, la art. 53, printr-o listă exhaustivă de scăderi din veniturile totale — listă care **nu include amortizarea** ca element deductibil:

::: ghid-temei
„(1) Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile aferente costurilor serviciilor în curs de execuție; c) veniturile din producția de imobilizări corporale și necorporale; [...]"
— Codul fiscal (Legea 227/2015), art. 53 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Lista continuă cu venituri din subvenții, provizioane, diferențe de curs valutar, despăgubiri, dividende primite de la o persoană juridică română etc. — toate sunt **venituri** scăzute din baza impozabilă, niciuna nu e o **cheltuială** dedusă. Amortizarea, fiind o cheltuială contabilă, nu apare nicăieri în această listă și nu reduce baza de calcul a celor 1%. Ea rămâne relevantă doar pentru evidența contabilă a firmei (valoarea rămasă a activului, situațiile financiare), nu pentru calculul impozitului micro.

## Ce se greșește în practică

- Se calculează amortizarea lunară cu gândul că reduce automat impozitul de plătit, ca la o firmă pe profit — la micro, impozitul se calculează direct pe veniturile din perioadă, indiferent de amortizarea înregistrată.
- Se caută o „deducere pentru investiții" similară cu facilitățile de la impozitul pe profit — la micro, mecanismele de facilitate diferă (de exemplu excluderea din baza impozabilă a veniturilor din producția de imobilizări corporale, art. 53 alin. (1) lit. c), care privește o situație diferită, nu achiziția unui mijloc fix).
- Se renunță la înregistrarea amortizării „pentru că oricum nu e deductibilă" — obligația de amortizare contabilă (OMFP 1802/2014, Cod fiscal art. 28) rămâne valabilă indiferent de regimul fiscal, pentru corectitudinea situațiilor financiare și a valorii rămase a activelor.

## Ce face iConta.eu

Motorul de import/migrare a registrului de mijloace fixe (F059, `core/mijloace_fixe_import_api.py`) preia, la trecerea unei firme în iConta.eu, valoarea de intrare, durata și amortizarea deja cumulată a fiecărui activ, indiferent de regimul fiscal al firmei (micro sau impozit pe profit) — nu există în cod nicio ramificație care să trateze diferit amortizarea în funcție de acest regim. Aplicația continuă să calculeze și să evidențieze amortizarea contabilă a activelor și pentru firmele micro, pentru că evidența rămâne necesară indiferent dacă amortizarea reduce sau nu impozitul datorat.

Ce nu face aplicația e o verificare sau un avertisment specific de tipul „amortizarea nu se deduce la micro" — calculul impozitului pe veniturile microîntreprinderii, cu excluderile din art. 53, e o funcție separată de motorul de mijloace fixe, iar legătura conceptuală dintre cele două rămâne, azi, o informație pe care contabilul o aplică manual.

[iConta.eu](/)
