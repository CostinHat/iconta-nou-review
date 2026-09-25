---
title: "Există amendă pentru D205 depusă cu întârziere?"
description: "Contravenția și amenda aplicabilă pentru nedepunerea la termen a declarației informative D205, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Există amendă pentru D205 depusă cu întârziere?

D205 — declarația informativă privind impozitul reținut la sursă și câștigurile din investiții pe beneficiari de venit — nu are o sancțiune proprie, dedicată, în Codul de procedură fiscală. Se sancționează prin regula generală aplicabilă oricărei declarații pe care legea o cere, dar contribuabilul nu o depune la termen.

## Temeiul legal

::: ghid-temei
„(1) Constituie contravenții următoarele fapte, dacă nu au fost săvârșite în astfel de condiții încât să fie considerate, potrivit legii, infracțiuni: [...] b) neîndeplinirea de către contribuabil/plătitor la termen a obligațiilor de declarare prevăzute de lege, a bunurilor și veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuțiilor și a altor sume, precum și orice informații în legătură cu impozitele, taxele, contribuțiile, bunurile și veniturile impozabile, dacă legea prevede declararea acestora; [...]
(2) [...] d) cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii și mari și cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice, în cazul săvârșirii faptei prevăzute la alin. (1) lit. a), b) și i) - m)."
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (1) lit. b) și alin. (2) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă concret pentru o firmă care depune D205 cu întârziere:

- **Fapta se încadrează la art. 336 alin. (1) lit. b)** — orice obligație de declarare prevăzută de lege, neîndeplinită la termen, inclusiv informații despre impozite reținute la sursă (categoria din care face parte D205).
- **Amenda diferă în funcție de categoria contribuabilului**: 1.000-5.000 lei pentru contribuabilii mijlocii și mari, respectiv 500-1.000 lei pentru celelalte persoane juridice și pentru persoanele fizice.
- **Nu există o reducere sau o perioadă de grație specifică pentru D205** în acest text — sancțiunea se aplică din momentul constatării nedepunerii la termenul legal, potrivit regulii generale.
- **Contravenția e distinctă de eventualele diferențe de impozit reținut la sursă** care ar putea rezulta dintr-o declarație incorectă sau incompletă — amenda de mai sus privește strict nedepunerea/depunerea cu întârziere, nu conținutul greșit al declarației.

## Ce se greșește în practică

- Se presupune că D205, fiind o declarație „doar informativă", nu are sancțiune pentru întârziere — de fapt, regula generală de la art. 336 alin. (1) lit. b) acoperă orice obligație de declarare prevăzută de lege, inclusiv cele informative.
- Se ignoră diferența de amendă în funcție de categoria contribuabilului (mijlociu/mare versus restul) — firma nu-și verifică din timp propria încadrare pentru a estima riscul real.
- Se amână depunerea D205 considerând-o secundară față de declarațiile cu impact direct de plată (D100, D112), deși sancțiunea contravențională se aplică independent de existența unei sume de plată.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează D205 prin `core/d205.py` (`calcul_d205()`, `build_xml()`, `genereaza()`) și urmărește scadența declarației în `core/control_fiscal_api.py`, prin apelul `scadente.scadenta_data("d205", an)`, semnalând firma dacă termenul a fost depășit. Aplicația nu calculează însă și nu afișează cuantumul amenzii posibile pentru nedepunerea la termen — urmărirea scadenței arată doar dacă declarația e restantă, nu și riscul financiar concret al întârzierii, potrivit art. 336.

[iConta.eu](/)
