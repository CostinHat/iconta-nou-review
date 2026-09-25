---
title: "Cum verific accesoriile calculate de ANAF pentru o plată întârziată?"
description: "Nivelurile legale ale dobânzii și penalității de întârziere, pentru a verifica dacă suma calculată de ANAF pe un extras de cont este corectă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific accesoriile calculate de ANAF pentru o plată întârziată?

Când primești un extras de cont sau o decizie referitoare la obligații fiscale accesorii, suma nu e arbitrară — se calculează zilnic, cu procente fixe stabilite de lege, pornind de la ziua următoare scadenței și până la data plății. Recalcularea manuală, pe câteva exemple, e cel mai simplu mod de a verifica dacă ANAF a aplicat corect regula.

## Temeiul legal

::: ghid-temei
„(1) Dobânzile se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv. [...] (5) Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere."
— Legea 207/2015 (Codul de procedură fiscală), art. 174 alin. (1) și (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(2) Nivelul penalității de întârziere este de 0,01% pentru fiecare zi de întârziere."
— Legea 207/2015 (Codul de procedură fiscală), art. 176 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce trebuie să verifici, punctual, pe o sumă calculată de ANAF pentru o plată întârziată:

- **Dobânda**: 0,02% pentru fiecare zi de întârziere, aplicată la suma principală neachitată, de la ziua imediat următoare scadenței până la data stingerii, inclusiv.
- **Penalitatea de întârziere**: separat de dobândă, 0,01% pentru fiecare zi de întârziere — cele două se cumulează, nu se aplică alternativ.
- Dacă suma neachitată provine dintr-o **diferență stabilită de organul fiscal printr-o decizie de impunere** (nu doar dintr-o declarație depusă cu întârziere de plată), poate interveni în plus **penalitatea de nedeclarare** (0,08% pe zi, art. 181), care e o categorie distinctă, aplicabilă doar obligațiilor principale nedeclarate sau declarate incorect și stabilite de organul fiscal — nu se cumulează automat cu dobânda și penalitatea de întârziere pe aceeași sumă și pentru aceeași cauză.
- Nivelurile de dobândă/penalitate pot fi actualizate prin hotărâre de Guvern, în funcție de evoluția ratei dobânzii de referință a BNR — merită verificat, la o sumă veche, dacă procentul aplicabil perioadei respective coincide cu cel curent sau cu unul anterior, în vigoare la acea dată.

## Ce se greșește în practică

- Se calculează dobânda și penalitatea de întârziere aplicând procentul la suma inclusiv accesoriile deja acumulate, în loc de a le aplica strict la suma principală neachitată.
- Se confundă penalitatea de întârziere (0,01%/zi, pentru simpla neplată la termen) cu penalitatea de nedeclarare (0,08%/zi, aplicabilă doar sumelor stabilite suplimentar de organul fiscal prin decizie de impunere, pentru obligații nedeclarate sau declarate greșit).
- Se ignoră ziua de start a calculului — dobânda și penalitatea curg de la ziua **imediat următoare** scadenței, nu de la data scadenței înseși.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu automatizează** recalcularea independentă a accesoriilor (dobândă, penalitate de întârziere, penalitate de nedeclarare) comunicate de ANAF pe un cont sau o decizie — aplicația urmărește scadențele declarative și de plată ale firmei, dar verificarea sumei accesoriilor deja calculate de organul fiscal rămâne o operație manuală, pe baza procentelor legale de mai sus.

[iConta.eu](/)
