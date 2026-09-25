---
title: Când trebuie depusă o declarație D406 rectificativă
description: Cum se corectează o eroare în fișierul SAF-T deja transmis la ANAF — regula declarației inițiale vs. rectificative, conținutul obligatoriu al rectificativei și perioada de grație, conform OPANAF nr. 1.783/2021.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când trebuie depusă o declarație D406 rectificativă

Declarația informativă D406 (fișierul standard de control fiscal — SAF-T) se corectează la fel ca orice altă declarație fiscală: prin depunerea unei declarații rectificative pentru aceeași perioadă de raportare. Regulile procedurale sunt stabilite prin OPANAF nr. 1.783/2021.

### Regula automată "prima e inițială, restul sunt rectificative"

Prima declarație informativă D406 validată, depusă pentru o lună sau un trimestru, este considerată **declarație inițială**. Orice declarație ulterioară depusă pentru **aceeași perioadă** (lună/trimestru) este **automat considerată declarație rectificativă** — nu există o bifă separată de "rectificativă" pe care s-o uitați; sistemul o marchează singur pe baza faptului că mai există deja o depunere pentru acea perioadă (câmpul de metadate `d_rec` din PDF conține "I" pentru inițială sau "R" pentru rectificativă).

### Când depuneți o rectificativă

Ori de câte ori constatați erori în declarația depusă inițial — erori materiale, omisiuni, date incomplete în secțiunile financiare — puteți depune declarații rectificative pentru corectarea lor. Nu există un termen limită separat pentru rectificativă în sine, dar corecția trebuie făcută cât mai curând ce eroarea e identificată, mai ales dacă afectează sume raportate care alimentează alte sisteme (RO e-TVA, controale încrucișate).

### Conținutul obligatoriu al rectificativei

Declarația rectificativă trebuie să cuprindă **toate informațiile din declarația inițială, plus corecțiile efectuate** — nu se transmit doar diferențele. Fișierul XML se regenerează integral, cu datele corecte, și se validează din nou prin Soft J (validatorul pus la dispoziție de ANAF) înainte de transmitere.

### Termenele de transmitere și perioada de grație

Termenul general pentru transmiterea D406 e ultima zi calendaristică a lunii următoare perioadei de raportare (lună sau trimestru, în funcție de perioada fiscală de TVA a contribuabilului). Contribuabilii beneficiază însă de o perioadă de grație pentru primele raportări, care nu se aplică penalizărilor pentru rectificative ulterioare acestei perioade:

| Raportare | Contribuabili cu obligație lunară | Contribuabili cu obligație trimestrială |
|---|---|---|
| 1 | 6 luni grație | 3 luni grație |
| 2 | 5 luni grație | — |
| 3 | 4 luni grație | — |
| 4 | 3 luni grație | — |
| 5 | 2 luni grație | — |

În perioada de grație, contribuabilii nu sunt sancționați contravențional conform art. 337^1 din Codul de procedură fiscală (Legea nr. 207/2015) dacă depun declarația D406 validă în termenul maxim.

### Câteva reguli practice

- Secțiunea "Active" se raportează o singură dată pe an, la termenul de depunere a situațiilor financiare anuale — dacă apare o eroare aici, rectificativa se depune tot pentru acea unică raportare anuală.
- Secțiunea "Stocuri" se raportează doar la solicitarea expresă a organului fiscal, cu un termen de minimum 30 de zile de la solicitare.
- Fiecare rectificativă trebuie semnată electronic cu certificat digital calificat, la fel ca declarația inițială, și se depune doar online prin portalul ANAF sau e-guvernare.ro.
