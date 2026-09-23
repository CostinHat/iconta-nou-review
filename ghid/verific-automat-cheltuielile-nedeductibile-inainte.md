---
title: "Cum verific automat cheltuielile nedeductibile înainte de D101?"
description: Cheltuielile nedeductibile din D101 sunt, în cea mai mare parte, ajustări fiscale manuale ale contabilului — cu o excepție automată reală, măsurată: cheltuiala cu impozitul pe profit (cont 691), semnalată dacă rândul 23 rămâne necompletat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific automat cheltuielile nedeductibile înainte de D101?

Cea mai mare parte a răspunsului e „nu se verifică automat" — dar există o excepție concretă, cu impact măsurat, care merită cunoscută în detaliu.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: a) cheltuielile proprii ale contribuabilului cu impozitul pe profit datorat, inclusiv cele reprezentând diferențe din anii precedenți sau din anul curent, precum și impozitele pe profit sau pe venit plătite în străinătate. [...]" — Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (4) lit. a).
:::

## Regula generală: intrări manuale

Cheltuielile nedeductibile din D101 (rândurile 23-34 ale formularului) sunt, pentru marea majoritate a categoriilor, **ajustări fiscale introduse manual** de contabil — nu se derivă automat dintr-o scanare a conturilor de cheltuieli. Decizia despre ce e nedeductibil și în ce sumă rămâne, prin natura ei, o decizie fiscală profesională.

Există totuși module dedicate care calculează automat partea nedeductibilă pentru **categorii specifice**, atunci când tranzacția respectivă e introdusă prin ecranul ei dedicat: sponsorizările (partea nedeductibilă contabil, cu credit fiscal separat la impozit), provizioanele constituite peste condițiile legale, și perisabilitățile peste limita admisă. Aceste calcule rulează la introducerea tranzacției, nu ca o verificare unică, de ansamblu, înainte de depunerea D101.

## Excepția automată reală: contul 691

Există un singur semnal automat, la nivelul întregii declarații: cheltuiala cu impozitul pe profit (cont 691) e ea însăși nedeductibilă, conform art. 25 alin. (4) lit. a) de mai sus, și are propriul rând în formular (rd. 23). Contul 691 e un cont de cheltuială (clasa 6) și intră normal în baza contabilă — deci, dacă rândul 23 rămâne necompletat, impozitul declarat iese **mai mic** decât cel datorat, în tăcere.

Din acest motiv, dacă rulajul debitor al contului 691 e mai mare decât zero, iar rândul 23 al declarației e zero, se afișează un avertisment explicit care cere confirmarea contabilului. Nu e completare automată — suma exactă rămâne o decizie a lui (poate viza alt an, sau poate trece prin alt cont la grupurile fiscale) — dar omisiunea nu mai trece nesemnalată.

Impactul măsurat pe un caz real: pentru o notă de impozit de 15.200 lei înregistrată în contul 691 și necompletată la rândul 23, declarația a ieșit cu 12.768 lei — cu 2.432 lei mai puțin decât impozitul real datorat.

## Ce se greșește în practică

- Se presupune că toate categoriile de la rândurile 23-34 sunt verificate automat, pentru că una dintre ele (691) e — celelalte rămân intrări manuale, fără cross-check.
- Se ignoră avertismentul despre contul 691, considerându-l „doar o notă", când de fapt semnalează o subevaluare directă a impozitului datorat.
- Se presupune că modulele pentru sponsorizări, provizioane sau perisabilități acoperă „toate" cheltuielile nedeductibile — acoperă doar categoria pentru care au fost construite, la momentul introducerii tranzacției respective.

## Ce face iConta.eu

Calculează automat nedeductibilul pentru categoriile cu module dedicate (sponsorizări, provizioane, perisabilități), la introducerea tranzacției. Pentru restul cheltuielilor nedeductibile, oferă câmpurile de ajustare fiscală ale D101, completate de contabil. Un singur semnal e activ la nivel de declarație: dacă există cheltuială cu impozitul pe profit (cont 691) și rândul 23 e necompletat, aplicația avertizează explicit, cu suma exactă, înainte de depunere.

[iConta.eu](/)
