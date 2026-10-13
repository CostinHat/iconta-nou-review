---
title: "La ce curs se înregistrează o plată bancară în valută?"
description: "Explică regula legală a cursului BNR aplicabil unei plăți în valută și modul în care iConta.eu determină automat cursul corect."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# La ce curs se înregistrează o plată bancară în valută?

Ca și la o încasare, o plată în valută se convertește în lei la cursul BNR valabil la data operațiunii — nu la un curs ales arbitrar sau la cursul afișat de bancă în extrasul de cont.

Regula e simetrică pentru încasări și plăți: se folosește ultimul curs BNR comunicat, valabil la data operațiunii. Exemplul din norma metodologică arată clar cum poate diferi cursul aplicabil de data unei formalități ulterioare (ex. o factură emisă la 10.03 pentru o livrare din 20.02 folosește cursul de la 20.02, nu pe cel din 10.03) — aceeași logică se aplică și la o plată decontată ulterior operațiunii care a generat-o.

## Ce se greșește în practică

Cele mai frecvente greșeli: folosirea cursului de vânzare/cumpărare al băncii comerciale (relevant doar dacă în contract e stipulat expres că se decontează la cursul unei bănci comerciale — în lipsa unei asemenea mențiuni contractuale, se aplică automat cursul BNR/BCE) sau confundarea datei plății cu data operațiunii care a generat obligația de plată.

## Ce face iConta.eu

Motorul de curs alege pentru orice dată dată ca parametru ultimul curs BNR comunicat cu data cursului ≤ data respectivă, folosind sursa oficială BNR. Dacă cel mai recent curs disponibil e mai vechi de 5 zile calendaristice (prag intern de produs, nu regulă fiscală), aplicația semnalează explicit "curs prea vechi" în loc să îl aplice tăcut; pentru monede necotate de BNR sau când serviciul e indisponibil, situația e afișată clar. Rotunjirea se face cu „calcul zecimal exact” și ROUND_HALF_UP, conform regulii fiscale de rotunjire.

Ca și la încasări, această regulă de curs e implementată în iConta.eu în principal pentru conversia sumelor pe facturi în valută și în declarațiile care depind de ele (D300, D390, D394, D406) — cursul aplicat automat e cel al facturii, nu al zilei plății efective, dacă cele două diferă. Un curs manual poate fi introdus explicit, cu data comunicării lui și autorul modificării.

[iConta.eu](/)
