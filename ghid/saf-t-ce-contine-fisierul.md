---
title: Ce conține fișierul SAF-T: secțiunile declarației D406
description: Ce trimite efectiv la ANAF fișierul SAF-T — plan de conturi, parteneri, jurnale, facturi cu liniile lor, plăți, active și stocuri — potrivit structurii din OPANAF 1783/2021.
published: 2026-08-13
modified: 2026-08-13
---

# Ce conține fișierul SAF-T și ce trimiți efectiv la ANAF?

Un fișier SAF-T nu e o declarație de câteva rânduri. E o copie structurată a evidenței contabile: planul de conturi, toți partenerii, toate notele contabile cu liniile lor, toate facturile cu produsele de pe ele, plățile, mijloacele fixe. Pentru o firmă mică, un fișier lunar are mii de linii. Merită să știi ce conține fiecare secțiune, pentru că de acolo vine și lista lucrurilor care trebuie puse în ordine în contabilitate înainte de prima depunere.

## Temeiul legal

::: ghid-temei
Structura fișierului este stabilită prin **OPANAF nr. 1783/2021**, care aprobă Declarația informativă D406 și schema ei tehnică. ANAF publică schema ca **fișier XSD**, împreună cu ghidul contribuabilului și cu nomenclatoarele obligatorii — conturi, unități de măsură, țări, tipuri de document, coduri de taxă.

**OPANAF nr. 407/2025** stabilește categoriile de contribuabili obligați și periodicitatea, precum și secțiunile care se raportează cu ritm propriu: **Active** anual și **Stocuri** la cererea organului fiscal.

Fișierul respectă standardul internațional **SAF-T (Standard Audit File for Tax)** dezvoltat de OCDE, adaptat la nomenclatoarele și regulile fiscale românești.
:::

## Ce conține fișierul

Fișierul are un antet și un corp împărțit pe secțiuni. Fiecare secțiune răspunde la o întrebare pe care ar pune-o un inspector fiscal.

**Antetul** — cine ești, ce perioadă acoperă fișierul, ce versiune de schemă, ce valută. Aici se declară și tipul de raportare: lunară, anuală sau la cerere.

**Fișierele de bază (Master Files)** — nomenclatoarele tale:

- **Planul de conturi** — fiecare cont folosit, cu soldurile de deschidere și de închidere
- **Clienți și furnizori** — fiecare partener, cu cod fiscal, denumire, adresă
- **Produse** — articolele din nomenclator, cu unitățile lor de măsură
- **Cote de taxă** — cotele de TVA aplicate în perioadă
- **Mijloace fixe** — pentru raportarea anuală

**Înregistrările contabile (General Ledger Entries)** — toate notele contabile ale perioadei, fiecare cu liniile ei: cont debitor, cont creditor, sumă, dată, document justificativ. Aici e cea mai mare parte a fișierului.

**Documentele-sursă (Source Documents)** — documentele din spatele înregistrărilor:

- **Facturi emise și primite**, fiecare cu **liniile ei reale**: produsul, cantitatea, unitatea de măsură, prețul unitar, cota de TVA. Nu o linie sintetică pe factură, ci fiecare poziție.
- **Plăți** — încasările și plățile, legate de documentele pe care le sting
- **Mișcări de bunuri** — intrări și ieșiri de stoc, când sunt raportabile

**Secțiuni cu ritm propriu:**

- **Active** — mijloacele fixe cu valoarea, data punerii în funcțiune, amortizarea. Se raportează **anual**.
- **Stocuri** — situația stocurilor. Se raportează **doar la cererea ANAF**.

## Ce înseamnă asta pentru evidența ta

::: ghid-exemplu
O factură de 1.000 lei către un client, pentru 200 kg de marfă la 5 lei kilogramul.

**În decontul de TVA** apare ca o cifră într-un total: bază 1.000 lei, TVA 210 lei.

**În D394** apare ca o linie cu codul fiscal al clientului: 1.000 lei bază, cota 21%.

**În SAF-T** apare complet: clientul cu datele lui din nomenclator, factura cu numărul și data ei, iar pe ea **linia de produs**: denumirea mărfii, **200** cantitate, **kg** unitate de măsură, **5 lei** preț unitar, 1.000 lei valoare, cota de taxă, contul contabil. Plus nota contabilă care a înregistrat-o, cu conturile ei.

Aceeași operațiune, trei niveluri de detaliu. SAF-T e cel care nu lasă nimic afară — și tocmai de aceea scoate la iveală ce lipsește: un produs fără unitate de măsură, un client fără cod fiscal, un cont nemapat.
:::

## Ce se greșește în practică

- **Se subestimează munca de curățenie.** Prima generare de SAF-T e, în realitate, un audit al nomenclatoarelor. Produse fără unitate de măsură, parteneri fără cod fiscal, conturi folosite dar nedefinite — toate ies la iveală deodată.
- **Se crede că facturile se raportează sintetic.** Nu. Fiecare linie de factură se raportează separat, cu cantitate și preț unitar. O factură cu 30 de poziții produce 30 de linii în fișier.
- **Se uită unitățile de măsură.** Nomenclatorul de unități e obligatoriu și limitat. O unitate proprie, inventată în firmă, nu trece validarea.
- **Se confundă Active cu Stocuri.** Activele se raportează anual, din oficiu. Stocurile doar dacă ANAF le cere expres.
- **Se lasă totul pe validator.** Validatorul verifică structura, nu adevărul cifrelor. Un fișier care trece validarea poate conține date greșite.

## Ce face iConta.eu

Fișierul se construiește direct din evidența ta: planul de conturi cu solduri, partenerii din nomenclator, notele contabile cu liniile lor, facturile cu **liniile reale de produs** — cantitate, unitate de măsură, preț unitar, cotă — reconciliate cu antetul facturii.

Nomenclatoarele obligatorii sunt mapate automat pe cele oficiale ANAF, iar rezultatul e validat pe **validatorul oficial (DUKIntegrator)** înainte să ajungă la tine.

**Ce nu se emite încă:** secțiunea **Plăți**. Modelul de date nu conține sursa de trezorerie necesară. Fișierul rămâne valid pe zero plăți, dar incomplet pentru o firmă cu încasări de raportat. La fel, contul de pe linia de factură e cel generic, nu contul real pe fiecare produs.

Le știi înainte de depunere, nu după.

Vezi și: [cine depune SAF-T și de când](/ghid/saf-t-d406-cine-depune) și [ce verifici când preiei o firmă](/ghid/ce-verifici-cand-preiei-o-firma-de-la-alt-contabil), unde curățenia nomenclatoarelor contează la fel de mult.

[iConta.eu](/)
