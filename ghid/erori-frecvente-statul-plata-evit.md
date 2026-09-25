---
title: "Erori frecvente la statul de plată și cum le evit"
description: "Cele mai frecvente semnale de eroare de pe statul de plată lunar — tichete de masă blocate, plafon de tichete de vacanță depășit, cadouri impozabile, bază de calcul lipsă — cu temeiul legal al fiecăruia."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Erori frecvente la statul de plată și cum le evit

Statul de plată lunar nu e doar o listă de cifre calculate de motorul de salarizare — el trebuie să reflecte corect reguli din mai multe acte normative în același timp: tichetele de masă legate de pontaj, plafonul anual al tichetelor de vacanță, pragul de neimpozitare a cadourilor, baza contractuală a fiecărui salariat. Majoritatea erorilor reale nu sunt greșeli de calcul, ci date de intrare incomplete sau depășiri de plafon netrecute la timp prin sistem.

## Temeiul legal

::: ghid-temei
„Salariații beneficiază lunar de un număr de tichete de masă cel mult egal cu numărul de zile lucrate, iar acest număr nu poate depăși numărul de zile lucrătoare din luna pentru care se acordă tichetele."
— HG 1045/2018, Normele metodologice, art. 10 alin. (3) (sursă: anaf_surse/hg_1045_2018_norme_consolidat.txt)
:::

- **Tichete de masă vs. pontaj**: legea leagă explicit numărul de tichete de zilele efectiv lucrate — dacă pontajul lunii nu e confirmat, angajatorul nu are cum să știe câte zile s-au lucrat, deci nu poate acorda tichetele fără riscul de a depăși plafonul legal.
- **Cadouri impozabile**: Codul fiscal exclude din baza de calcul a contribuțiilor cadourile în bani și/sau în natură „în măsura în care valoarea acestora pentru fiecare persoană în parte, cu fiecare ocazie [...], nu depășește 300 lei" (art. 142 lit. b) Cod fiscal). Peste acest prag, sau la un eveniment care nu e prevăzut de lege (Paște, Crăciun, 8 martie, 1 iunie), cadoul devine impozabil integral.
- **Plafonul tichetelor de vacanță**: „Nivelul maxim al sumelor care pot fi acordate salariaților sub forma de tichete de vacanță este contravaloarea a 6 salarii de bază minime brute pe țară garantate în plată, pentru un salariat, în decursul unui an fiscal" (OUG 8/2009, art. 1 alin. (4)). Plafonul e anual, nu lunar — se cumulează pe toate lunile în care s-au acordat tichete de vacanță.
- **Baza contractuală lipsă**: dacă salariul contractual al unui angajat nu e completat sau e zero, calculul brut→net nu are de la ce porni; un stat de plată cu bază lipsă e incoerent prin definiție, nu doar „o valoare mică".

## Ce se greșește în practică

- Se acordă tichetele de masă înainte de confirmarea pontajului lunii, „ca să nu întârzie plata" — riscul e exact situația pe care norma o vrea evitată: mai multe tichete decât zilele efectiv lucrate.
- Se oferă un cadou peste 300 lei sau cu ocazia unui eveniment nelegal (de exemplu o aniversare a firmei) și se tratează, din reflex, ca neimpozabil, la fel ca darurile de Paște sau Crăciun.
- Se pierde din vedere plafonul ANUAL al tichetelor de vacanță pentru că fiecare lună pare, izolat, sub limită — depășirea apare doar la însumare pe tot anul fiscal.
- Se lasă salariul contractual necompletat pentru un angajat nou, cu gândul „îl completez la prima lună de salariu efectiv" — dar statul de plată al lunii curente tot trebuie generat.

## Ce face iConta.eu

Statul de plată lunar (`stat_plata()`) produce, pentru fiecare salariat, nu doar cifrele brut/net, ci și semnale explicite de calitate a datelor, calculate din exact aceleași reguli de mai sus: bază contractuală lipsă sau zero, tichete de masă blocate din lipsa confirmării pontajului (conform art. 10 alin. (3) citat mai sus), depășirea plafonului anual de tichete de vacanță și cadou impozabil (peste prag sau la un eveniment nelegal). Aceste semnale se afișează pe rândul salariatului, nu tăcut — scopul lor e ca eroarea să fie vizibilă înainte ca fluturașul să fie emis și predat.

O precizare importantă pentru contabili: pe fluturașul unui salariat care are DOAR tichete culturale sau de creșă (fără tichete de masă sau de vacanță), rândul care arată impozitul reținut pe aceste tichete nu apare separat în compoziția afișată, deși suma e deja scăzută corect din salariul net calculat. Cifra finală e corectă; ce lipsește e explicația pe rând a acelei componente pentru acest caz particular — merită verificată suma totală, nu doar rândurile individuale, când singurele facilități ale unui salariat sunt tichetele culturale sau de creșă.

[iConta.eu](/)
