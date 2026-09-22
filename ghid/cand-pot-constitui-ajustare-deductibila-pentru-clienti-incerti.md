---
title: Când pot constitui ajustare deductibilă pentru clienți incerți?
description: Ajustarea pentru un client incert devine deductibilă la 30% după 270 de zile de la scadență, sau la 100% dacă debitorul e în faliment/insolvență declarată — cu condiția ca acesta să nu fie afiliat și creanța să nu fie garantată.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Când pot constitui ajustare deductibilă pentru clienți incerți?

Constituirea contabilă a ajustării pentru un client incert (cont 491) se poate face oricând sunt îndeplinite condițiile de recunoaștere din reglementările contabile — la fiecare inventariere, dacă valoarea probabilă de încasare e mai mică decât valoarea din evidență. Momentul din care ajustarea devine și **deductibilă fiscal** e însă distinct, și depinde de vechimea creanței sau de stadiul de insolvență al debitorului.

## Temeiul legal

::: ghid-temei
"Evaluarea la inventar a creanțelor și a datoriilor se face la valoarea lor probabilă de încasare sau
de plată. Diferențele constatate în minus între valoarea de inventar stabilită la inventariere și
valoarea contabilă a creanțelor se înregistrează în contabilitate pe seama ajustărilor pentru
deprecierea creanțelor."

"ajustările pentru deprecierea creanțelor, înregistrate potrivit reglementărilor contabile aplicabile,
reprezentând sume datorate de clienții interni și externi pentru produse, semifabricate, materiale,
mărfuri vândute, lucrări executate și servicii prestate, în limita unui procent de 30% din valoarea
acestor ajustări, altele decât cele prevăzute la lit. d)-f), h) și i), dacă creanțele îndeplinesc
cumulativ următoarele condiții:
1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței;
2. nu sunt garantate de altă persoană;
3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului;"
:::

## Constituire contabilă vs. deducere fiscală

Cele două momente nu coincid:

- **Constituirea contabilă** se face imediat ce, la inventariere, se constată că valoarea probabilă de încasare e sub valoarea contabilă a creanței (client aflat în litigiu, întârziat la plată, cu probleme financiare vizibile etc.) — nu trebuie să aștepți 270 de zile pentru a recunoaște contabil riscul.
- **Deducerea fiscală** a ajustării deja constituite devine posibilă doar când creanța, cumulativ, e neîncasată de peste 270 de zile de la scadență, nu e garantată de altcineva și debitorul nu e persoană afiliată — atunci deducerea e de 30% din valoarea ajustării. Dacă între timp debitorul intră în faliment declarat (persoană juridică) sau insolvență (persoană fizică), deducerea sare la 100%.

Până la îndeplinirea condițiilor de mai sus, ajustarea rămâne constituită contabil, dar nedeductibilă fiscal — nu se pierde, doar se amână recunoașterea fiscală până la momentul relevant.

## Ce se greșește în practică

- Se așteaptă 270 de zile pentru a constitui *contabil* ajustarea, deși recunoașterea contabilă trebuie făcută mai devreme, de îndată ce riscul e evident.
- Se deduce fiscal ajustarea imediat ce e constituită contabil, fără verificarea celor trei condiții cumulative.
- Se ignoră condiția de neafiliere — o creanță la o firmă din același grup nu poate genera niciodată deducere pe acest temei.
- Se confundă termenul de 270 de zile cu termenul de la data facturii, în loc de data scadenței contractuale.

## Ce face iConta.eu

Funcția `deductibilitate_creanta` din `core/provizioane.py` primește numărul de zile de depășire a scadenței, precum și marcajele „garantată", „afiliată" și „faliment declarat", și întoarce procentul de deducere aplicabil (0%, 30% sau 100%) plus temeiul textual corespunzător. O creanță garantată sau afiliată primește întotdeauna 0%, indiferent de vechime; sub pragul de 270 de zile și fără faliment declarat, procentul e tot 0% ("sub 270 zile ... nedeductibil încă"). Nota contabilă la constituire e generată automat prin `nota_ajustare_creanta` (6814=491).

[iConta.eu](/)
