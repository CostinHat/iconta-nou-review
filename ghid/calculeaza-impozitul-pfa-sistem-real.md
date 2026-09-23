---
title: "Cum se calculează impozitul unui PFA în sistem real în 2026?"
description: Impozitul pe venitul unui PFA în sistem real e 10%, dar nu se aplică pe venitul brut, nici pe venitul net — se aplică pe venitul net rămas după scăderea CAS și CASS deja calculate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează impozitul unui PFA în sistem real în 2026?

Impozitul e ultimul pas din lanțul de calcul al unui PFA în sistem real, nu primul — pentru că baza lui depinde de CAS și CASS, care trebuie calculate înainte.

## Temeiul legal

::: ghid-temei
**Art. 68 alin. (1) Cod fiscal (Legea 227/2015):** *„Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."*
:::

## Lanțul de calcul, în ordine

1. **Venit net** = venit brut − cheltuieli deductibile (art. 68 alin. (1)), plafonat la zero dacă rezultatul e negativ.
2. **CAS** — calculat pe bază în trepte (12 sau 24 salarii minime), cotă 25% (art. 148, art. 138 lit. a)).
3. **CASS** — calculat liniar pe venitul net, plafonat la 60/72 salarii minime în funcție de anul de venit, cotă 10% (art. 170 alin. (1)).
4. **Baza de impozitare** = venit net − CAS − CASS.
5. **Impozitul** = 10% din baza de la pasul 4.

Ordinea contează: dacă s-ar aplica 10% direct pe venitul net, fără să se scadă CAS și CASS calculate, rezultatul ar fi mai mare decât cel corect — impozitul se calculează pe ce rămâne după contribuții, nu pe venitul net brut de contribuții.

## Ce se greșește în practică

- **Se aplică 10% pe venitul net, fără să se scadă CAS și CASS.** Baza corectă de impozitare e venitul net minus contribuțiile deja calculate, nu venitul net în sine.
- **Se calculează impozitul înainte de CAS/CASS**, într-o ordine greșită — CAS și CASS trebuie stabilite mai întâi, pentru că intră ca scăzăminte în baza impozitului.
- **Se ignoră cheltuielile limitate/plafonate legal** (de exemplu protocol, sponsorizări) la calculul venitului net — acestea nu intră automat în calcul; partea deductibilă din ele o stabilește contabilul, separat.

## Ce face iConta.eu

Fișa D212 (RIP > Fișa D212) parcurge exact acest lanț: preia venitul brut și cheltuielile deductibile din operațiunile validate ale registrului de încasări și plăți, calculează venitul net, apoi CAS și CASS pe bazele lor specifice, și abia apoi impozitul de 10% pe venitul net rămas după scăderea celor două contribuții. Cheltuielile limitate sunt raportate separat, cu avertisment explicit, pentru că partea lor deductibilă o stabilește contabilul. Fișa produce cifrele de referință — completarea efectivă a Declarației unice rămâne un pas separat.

[iConta.eu](/)
