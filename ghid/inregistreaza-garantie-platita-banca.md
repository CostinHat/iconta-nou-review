---
title: "Cum se înregistrează o garanție plătită prin bancă?"
description: "Tratamentul contabil al unei garanții acordate/plătite unui partener prin bancă, ca angajament extrabilanțier distinct de o plată efectivă de trezorerie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o garanție plătită prin bancă?

Simetric cu garanția primită, o firmă poate acorda o garanție unui furnizor, locator sau altui partener — de exemplu garanția de bună execuție cerută de un client, sau garanția aferentă unui contract de închiriere. Și aici tratamentul contabil depinde de un singur criteriu: e vorba de un simplu angajament asumat de firmă, sau banii chiar ies din contul bancar?

## Temeiul legal

::: ghid-temei
„Contul 801 «Angajamente acordate» [...] Cu ajutorul acestui cont se ține evidența angajamentelor acordate de către entitate (giruri, cauțiuni, garanții, alte angajamente acordate), reflectând eventuala datorie a entității față de terți, generată de angajamentele asumate. În debitul contului 801 «Angajamente acordate» se înregistrează valoarea angajamentelor în momentul acordării lor de către entitate, iar în credit, valoarea angajamentelor în momentul încetării lor."
— OMFP 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, Clasa 8 „Conturi speciale", Grupa 80 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Contul 801 (cu subcontul 8011 „Giruri și garanții acordate") e, la fel ca perechea sa 802, un cont **extrabilanțier**, în partidă simplă — folosit când firma își asumă un angajament de garantare (de exemplu un gir sau o cauțiune), fără să iasă efectiv bani din cont în acel moment.
- Dacă firma **chiar plătește** o sumă de bani prin bancă, cu titlu de garanție, care urmează să-i fie restituită ulterior (cazul din titlu, „garanție plătită prin bancă") — operațiunea nu mai e un simplu angajament extrabilanțier, ci o plată de trezorerie reală, care generează o **creanță** a firmei față de cel care a primit banii (de recuperat la încetarea garanției).

## Ce se greșește în practică

- Se înregistrează o garanție plătită direct ca o cheltuială, deși e o sumă recuperabilă, nu un cost definitiv.
- Se folosește contul extrabilanțier 8011 și pentru o garanție care a presupus o plată efectivă de bani — caz în care tratamentul corect e o creanță pe bilanț, nu o simplă evidență în partidă simplă.
- Se uită recuperarea/stornarea garanției la finalul contractului, mai ales când firma nu mai ține evidența separată a sumelor plătite drept garanție.

## Ce face iConta.eu

Motorul de calcul din `core/credite.py` (funcția `nota_garantie`) știe, la nivel de funcție pură, să genereze și nota simetrică pentru garanția acordată (`8011=891`), primind parametrul `fel="acordata"`. Onest, verificat direct în interfață: ecranul **Credite bancare** (operațiunea „Garanție") nu are, la acest moment, niciun câmp prin care contabilul să aleagă „primită" sau „acordată" — formularul trimite mereu valoarea implicită, iar rezultatul e mereu nota pentru garanție **primită** (`8021=891`). Practic, azi, din interfața iConta.eu **nu se poate genera** nota `8011=891` pentru o garanție acordată — capacitatea există în motorul de calcul, dar nu e expusă în formular.

La fel ca la garanția încasată, trebuie spus cinstit: dacă garanția se **plătește efectiv** prin bancă (banii chiar ies din contul firmei), iConta.eu nu automatizează separat acea plată de trezorerie și creanța de recuperat aferentă — funcția existentă tratează doar cazul angajamentului extrabilanțier. Plata efectivă și evidența creanței de recuperat trebuie înregistrate manual, printr-o notă contabilă obișnuită.

[iConta.eu](/)
