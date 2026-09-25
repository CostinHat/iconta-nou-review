---
title: "Cum se contabilizează sumele blocate de bancă?"
description: "De ce sumele indisponibilizate printr-o poprire bancară rămân în contul 512, ca activ al firmei, și ce cere reglementarea contabilă pentru o imagine fidelă a situației."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează sumele blocate de bancă?

Când o parte din soldul contului bancar e indisponibilizată — printr-o poprire a ANAF, de exemplu — apare întrebarea dacă suma blocată trebuie „scoasă" din contul 512 și mutată în altă parte a contabilității, pentru a arăta că firma nu mai poate dispune liber de ea.

**Limitare declarată**: sursele ANAF consultate pentru acest ghid nu conțin o normă contabilă explicită, dedicată sumelor indisponibilizate în conturile bancare curente (spre deosebire, de exemplu, de acreditive, care au propriul cont distinct, 541). Planul de conturi general (OMFP 1802/2014) nu prevede un subcont separat pentru „disponibilități blocate" în cadrul contului 512. Ce se poate confirma cu certitudine e principiul general de recunoaștere a activelor și cerința de imagine fidelă, din care decurge practica uzuală.

## Temeiul legal

::: ghid-temei
„18. - (2) [...] a) un activ reprezintă o resursă controlată de către entitate ca rezultat al unor evenimente trecute, de la care se așteaptă să genereze beneficii economice viitoare pentru entitate. Un activ este recunoscut în contabilitate și prezentat în bilanț atunci când este probabilă realizarea unui beneficiu economic viitor de către entitate și activul are un cost sau o valoare care poate fi evaluat/evaluată în mod credibil; [...]
24. - Situațiile financiare anuale trebuie să ofere o imagine fidelă a activelor, datoriilor, poziției financiare și a profitului sau pierderii entității.
25. - Dacă aplicarea prevederilor prezentelor reglementări nu este suficientă pentru a oferi o imagine fidelă a activelor, a datoriilor, a poziției financiare și a profitului sau pierderii entității, în notele explicative la situațiile financiare sunt furnizate informațiile suplimentare necesare pentru respectarea cerinței respective."
— OMFP 1802/2014, pct. 18 alin. (2) lit. a) și pct. 24-25 (Reglementări contabile privind situațiile financiare anuale individuale) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă, cu prudență, din aceste principii pentru sumele blocate de bancă:

- **Suma rămâne, contabil, activul firmei** — firma nu și-a pierdut proprietatea asupra banilor din cont; a pierdut doar, temporar, dreptul de a dispune liber de ei. Recunoașterea în contul 512 „Conturi curente la bănci" nu se schimbă doar pentru că suma e indisponibilizată.
- **Restricția de utilizare nu justifică, prin ea însăși, scoaterea sumei din bilanț sau reclasificarea ei într-un cont de altă natură** — activul e în continuare controlat de firmă, doar exercitarea acelui control e restricționată temporar.
- **Problema reală e cea de la pct. 24-25**: dacă simpla prezentare în 512 nu oferă o imagine fidelă a situației (pentru că cititorul situațiilor financiare nu poate ști din bilanț că o parte din disponibilități e indisponibilizată), informația trebuie prezentată **suplimentar, în notele explicative** — nu prin mutarea sumei într-un alt cont din bilanț.
- **Analitice interne** (o subdiviziune a contului 512 pentru „disponibil blocat prin poprire") pot ajuta la urmărire, dar rămân o decizie de organizare a evidenței analitice a firmei, nu o cerință a planului de conturi general.

## Ce se greșește în practică

- Se mută suma indisponibilizată într-un cont de creanțe sau de altă natură, ca și cum firma ar fi pierdut controlul activului — de fapt, banii rămân activul firmei, doar temporar indisponibili pentru plăți.
- Se omite orice mențiune în notele explicative despre existența unei sume blocate, deși pct. 24-25 cer explicit informații suplimentare atunci când simpla înregistrare contabilă nu oferă, singură, o imagine fidelă a situației firmei.
- Se confundă sumele blocate printr-o poprire cu garanțiile constituite voluntar (ex. garanții de bună execuție) — regimul contabil poate diferi, iar tratarea lor identică, fără analiză, poate induce în eroare cititorul situațiilor financiare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu prelucrează extrasele bancare prin `core/banca.py` și `core/banca_parser.py`, dar nu are o funcționalitate care să identifice sau să marcheze distinct sumele indisponibilizate printr-o poprire bancară — toate sumele din extras intră în contul 512 conform mișcărilor reale, fără o clasificare separată pentru „disponibil blocat". Semnalarea unei asemenea situații în notele explicative, conform pct. 24-25, rămâne o operațiune manuală a contabilului.

[iConta.eu](/)
