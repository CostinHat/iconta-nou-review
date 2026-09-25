---
title: "Fraudă cu facturi false de la furnizori 2026"
description: "Ce spune legea despre înregistrarea în contabilitate a unor cheltuieli care nu au la bază operațiuni reale sau a unor facturi fictive de la furnizori, și consecințele penale ale evaziunii fiscale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Fraudă cu facturi false de la furnizori 2026

Facturile de la furnizori care „acoperă" cheltuieli fără operațiune reală în spate — bunuri niciodată livrate, servicii niciodată prestate — nu sunt doar o problemă de deductibilitate fiscală. Legea le tratează ca infracțiune de evaziune fiscală, indiferent dacă firma care le înregistrează este cea care le-a comandat sau doar victima unui furnizor de rea-credință.

## Temeiul legal

::: ghid-temei
„(1) Constituie infracțiuni de evaziune fiscală și se pedepsesc cu închisoare de la 3 la 10 ani și interzicerea unor drepturi sau cu amendă următoarele fapte săvârșite în scopul sustragerii de la îndeplinirea obligațiilor fiscale: [...] c) evidențierea, în actele contabile, în factura electronică sau în alte documente legale, a cheltuielilor care nu au la bază operațiuni reale ori evidențierea altor operațiuni fictive;"
— Legea nr. 241/2005 pentru prevenirea și combaterea evaziunii fiscale, art. 9 alin. (1) lit. c) (sursă: anaf_surse/legea_241_2005.html)
:::

Câteva precizări relevante pentru o firmă care descoperă facturi false primite de la un furnizor:

- Infracțiunea vizează **evidențierea** cheltuielilor fictive în contabilitate, deci se comite din momentul înregistrării documentului, nu doar din momentul deducerii fiscale a sumei.
- Pedeapsa (închisoare de la 3 la 10 ani și interzicerea unor drepturi, sau amendă) se aplică faptelor săvârșite „în scopul sustragerii de la îndeplinirea obligațiilor fiscale" — elementul de intenție contează în calificarea faptei.
- Alături de litera c), art. 9 alin. (1) sancționează și fapte conexe: ascunderea bunului sau sursei impozabile (lit. a), omisiunea evidențierii operațiunilor comerciale sau veniturilor realizate (lit. b), alterarea sau distrugerea actelor contabile (lit. d) — situații care apar frecvent împreună cu facturile fictive, într-un lanț de fraudă.

## Ce se greșește în practică

- Se presupune că răspunderea aparține exclusiv furnizorului „fantomă", ignorând faptul că înregistrarea și deducerea cheltuielii de către beneficiar poate atrage propria răspundere, dacă se dovedește că beneficiarul știa sau ar fi trebuit să știe că operațiunea e fictivă.
- Se descoperă factura suspectă abia la controlul fiscal, deși verificări simple (existența reală a furnizorului, corespondența dintre factură și livrarea/prestarea efectivă, plata prin cont bancar) ar fi semnalat problema din timp.
- Se confundă o eroare de facturare de bună-credință (de exemplu, o factură emisă din greșeală, pe un alt client) cu o operațiune fictivă intenționată — distincția contează pentru calificarea juridică a faptei.

## Ce face iConta.eu

Pentru acest subiect nu am identificat în cod o funcție de detectare automată a facturilor false sau a furnizorilor fictivi (de exemplu, verificare încrucișată cu ANAF privind existența/statutul furnizorului). Aplicația are un modul de alerte pentru control fiscal (`core/alerte_control_fiscal.py`), dar acesta compară date deja introduse între declarații (TVA, salarii) pentru a semnala inconsistențe interne, nu verifică realitatea operațiunilor din spatele facturilor primite — depistarea unei fraude cu facturi false rămâne, la acest moment, în sarcina contabilului și a verificărilor sale de bună-credință.

[iConta.eu](/)
