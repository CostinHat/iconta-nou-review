---
title: "Ce penalități sunt pentru nedepunerea D205"
description: "Cum se sancționează nedepunerea în termen a declarației informative D205 privind impozitul reținut la sursă pe beneficiari de venit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce penalități sunt pentru nedepunerea D205

D205 e o declarație informativă, depusă de plătitorii de venituri pentru a raporta impozitul reținut la sursă pe fiecare beneficiar. Nedepunerea ei în termen nu e o simplă întârziere administrativă — Codul de procedură fiscală o încadrează expres ca faptă contravențională, cu amendă proprie.

## Temeiul legal

::: ghid-temei
„(1) Constituie contravenții următoarele fapte, dacă nu au fost săvârșite în astfel de condiții încât să fie considerate, potrivit legii, infracțiuni: [...] b) neîndeplinirea de către contribuabil/plătitor la termen a obligațiilor de declarare prevăzute de lege, a bunurilor și veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuțiilor și a altor sume, precum și orice informații în legătură cu impozitele, taxele, contribuțiile, bunurile și veniturile impozabile, dacă legea prevede declararea acestora [...]
(2) Contravențiile prevăzute la alin. (1) se sancționează astfel: [...] d) cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii și mari și cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice, în cazul săvârșirii faptei prevăzute la alin. (1) lit. a), b) și i) - m)."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 336 alin. (1) lit. b) și alin. (2) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- **D205, ca declarație informativă a plătitorului de venit**, intră sub fapta generică de la art. 336 alin. (1) lit. b) — neîndeplinirea la termen a obligațiilor de declarare prevăzute de lege — sancționată conform alin. (2) lit. d).
- **Amenda diferă în funcție de mărimea contribuabilului**: 1.000–5.000 lei pentru contribuabilii mijlocii și mari, respectiv 500–1.000 lei pentru celelalte persoane juridice și pentru persoanele fizice.
- **Declarația informativă poate fi corectată oricând**, indiferent de perioada la care se referă (art. 105 alin. (2) din același cod) — dar corectarea ulterioară nu înlătură sancțiunea pentru nedepunerea inițială în termen, dacă fapta a fost deja constatată.

## Ce se greșește în practică

- Se presupune că D205, fiind "doar informativă" și fără sumă de plată asociată direct, nu atrage sancțiuni — art. 336 nu face această distincție, sancționând orice nerespectare a obligațiilor de declarare prevăzute de lege.
- Se depune declarația cu întârziere fără să se solicite reducerea amenzii prin plata în termenul legal de 15 zile de la comunicarea procesului-verbal (jumătate din minimul amenzii), acolo unde procedura contravențională generală o permite.
- Se confundă regimul sancționator al D205 cu cel al declarațiilor recapitulative de TVA (art. 337), care are alte cuantumuri de amendă — sunt fapte contravenționale distincte, cu texte de lege diferite.

## Ce face iConta.eu

Modulul D205 din iConta.eu (`core/d205.py`) generează declarația pe baza reținerilor la sursă înregistrate în aplicație, dar nu urmărește automat termenul de depunere și nu emite alerte legate de sancțiunea contravențională pentru nedepunere — urmărirea termenului legal și depunerea efectivă la ANAF rămân responsabilitatea contabilului.

[iConta.eu](/)
