---
title: "Cum caut facturile unui anumit furnizor în e-Factura?"
description: "Ce spune legea despre disponibilitatea facturilor primite prin RO e-Factura și cum se regăsesc, în practică, facturile unui furnizor anume."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum caut facturile unui anumit furnizor în e-Factura?

Toate facturile trimise printr-un emitent înregistrat în sistemul național RO e-Factura ajung la destinatar prin același canal — sistemul ANAF, nu prin email sau alt mijloc ales de furnizor. Găsirea facturilor unui anumit furnizor înseamnă, în esență, filtrarea listei de facturi primite după identitatea emitentului (nume sau CUI), fie direct în portalul ANAF (SPV), fie în aplicația de contabilitate care preia facturile prin conectorul e-Factura.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul național privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite în sistemul național privind factura electronică RO e-Factura [...]. Data comunicării este accesibilă în sistem și emitentului facturii electronice."
— OUG 120/2021 privind factura electronică RO e-Factura, art. 4 alin. (7) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce rezultă din text:

- Facturile electronice primite prin sistem rămân **disponibile pentru descărcare** în sistemul național RO e-Factura, nu doar livrate o singură dată — se pot regăsi ulterior, inclusiv pentru verificarea celor primite de la un furnizor anume.
- Destinatarul e notificat la fiecare factură nou primită, iar exemplarul original al facturii e fișierul XML însoțit de semnătura electronică a Ministerului Finanțelor — identitatea emitentului (nume, CUI) e parte din structura acelui XML, deci disponibilă pentru filtrare.
- O factură comunicată nu poate fi „returnată" în sistem — dacă destinatarul are obiecții asupra ei, procedura corectă e înștiințarea emitentului, nu ștergerea din arhiva SPV.

## Ce se greșește în practică

- Se caută facturile unui furnizor doar în căsuța de email, ignorând că exemplarul cu valoare fiscală e cel din sistemul RO e-Factura, nu eventualul PDF trimis separat de furnizor.
- Se presupune că sistemul ANAF oferă din start o căutare avansată după numele furnizorului — interfața portalului SPV are propriile limitări de filtrare, adesea mai eficient e exportul facturilor și filtrarea lor în aplicația de contabilitate.
- Se confundă „factura nu apare" cu „furnizorul nu a emis-o prin sistem" — pot exista întârzieri de notificare sau facturi respinse la validare (art. 4 alin. (5) din OUG 120/2021), care rămân nerezolvate până la corectarea erorilor de către emitent.

## Ce face iConta.eu

iConta.eu are un conector propriu către SPV (Spațiul Privat Virtual ANAF), care preia automat facturile primite prin RO e-Factura, și un ecran de facturi cu filtrare pe an, lună și direcție (emisă/primită). La verificarea codului, funcția de listare a facturilor (`lista_facturi`) nu are însă, la acest moment, un parametru dedicat de căutare explicită după numele sau CUI-ul furnizorului — datele de identificare ale terțului (`tert_nume`, `tert_cui`) sunt afișate pentru fiecare factură, dar filtrarea unei liste lungi doar după furnizor rămâne, structural, o funcție de căutare pe care nu am găsit-o implementată separat în backend.

[iConta.eu](/)
