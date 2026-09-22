---
title: Cum se înregistrează contabil banii depuși de administrator în casierie
description: Dacă administratorul e și asociat, banii depuși în casierie se tratează ca împrumut, în contul 4551; dacă administratorul nu e asociat, operațiunea nu poate folosi acest cont și trebuie clarificată separat, ca avans sau decontare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează contabil banii depuși de administrator în casierie?

Primul lucru de stabilit înainte de a alege contul corect este cine e administratorul față de firmă: dacă e și asociat (cazul frecvent la SRL-urile mici, cu administrator-asociat unic), tratamentul contabil urmează regulile de decontări cu asociații. Dacă administratorul e o persoană din afara asociaților (administrator neasociat, pe bază de contract de mandat), suma nu poate folosi contul de asociați și trebuie tratată diferit.

## Temeiul legal

::: ghid-temei
**Codul fiscal (Legea 227/2015), art. 97 alin. (2)** — dacă suma poartă dobândă, când administratorul e și asociat: „Veniturile sub formă de dobânzi [...], contractele civile încheiate se impun cu o cotă de 10% din suma acestora, impozitul fiind final [...] calculul impozitului datorat de către plătitorii de venit se efectuează la momentul plății dobânzii."

**Legea 31/1990, art. 67 alin. (2^4)** — adăugat de Legea 239/2025, în vigoare din 18.12.2025: „Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților [...] împrumuturile luate de la aceștia."
:::

## Administrator-asociat: împrumut, cont 4551

Când administratorul e și asociat, depunerea de bani în casierie urmează exact logica unui împrumut de la asociat:

- `5311 = 4551` — cu suma depusă
- La restituire: `4551 = 5311` (sau `5121`, dacă restituirea trece prin bancă), plus liniile de dobândă și impozit de 10%, dacă a fost convenită dobândă

## Administrator neasociat

Dacă administratorul nu e asociat al firmei, contul 4551 nu se poate folosi — acel cont e rezervat decontărilor cu acționarii/asociații, nu cu terți sau cu personalul de conducere fără calitate de asociat. O astfel de sumă trebuie clarificată separat, în funcție de natura reală a operațiunii (de exemplu, un avans de trezorerie restituit ulterior de firmă, sau o creanță tratată ca la orice alt terț), și documentată corespunzător — nu se încadrează implicit la decontări cu asociații doar pentru că vine de la administrator.

## Ce se greșește în practică

- **Se folosește automat contul 4551 pentru orice sumă venită de la administrator**, indiferent dacă e sau nu asociat. Contul e specific pentru asociați, nu pentru funcția de administrator ca atare.
- **Se depune suma în casierie fără niciun document care să arate dacă e împrumut, avans sau altceva.** Fără claritate, suma e greu de justificat la control.
- **Se restituie suma administratorului-asociat fără să se verifice activul net al firmei**, deși interdicția de la art. 67 alin. (2^4) se aplică indiferent de canalul de restituire.

## Ce face iConta.eu

Pentru administratorul care e și asociat, aplicația automatizează fluxul prin contul bancar (`5121 = 4551` la primire, `4551 = 5121` la restituire), inclusiv calculul dobânzii și al impozitului de 10%, dacă operațiunea e introdusă ca atare. Pentru sumele depuse direct în casierie (`5311 = 4551`), contabilul introduce operațiunea manual, cu aceeași logică de cont 4551.

Stabilirea corectă a calității administratorului (asociat sau nu) rămâne o decizie a contabilului la introducerea operațiunii — aplicația nu verifică automat statutul de asociat al persoanei care depune banii. Verificarea activului net al firmei față de capitalul social, cerută de art. 67 alin. (2^4) înainte de orice restituire, nu este automatizată în acest moment.

[iConta.eu](/)
