---
title: "Casierie la micro cu numerar 2026"
description: "Cum se combină plafoanele legale de numerar cu obligația de ținere zilnică a registrului de casă, pentru o microîntreprindere care lucrează cu cash."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Casierie la micro cu numerar 2026

Regimul de impozitare micro nu schimbă cu nimic regulile de casierie — o microîntreprindere care încasează sau plătește în numerar respectă exact aceleași plafoane și aceleași documente ca orice altă firmă. Diferența practică e că, la micro, orice sumă neînregistrată corect afectează direct baza impozabilă (venitul), nu doar profitul.

## Temeiul legal

```
::: ghid-temei
„(1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi."
— Legea nr. 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 3 alin. (1) lit. c) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::
```

Reguli practice pentru casieria unei microîntreprinderi, valabile în 2026:

- **Plafonul de 5.000 lei/zi/persoană la plăți către alte firme**, cu limita totală de 10.000 lei/zi pentru toate plățile cash ale zilei, se aplică identic, indiferent dacă firma e la micro sau la profit — regimul de impozitare nu modifică regulile Legii nr. 70/2015.
- **Registrul de casă se întocmește zilnic**, pe baza documentelor justificative de încasări și plăți, și stabilește soldul de casă la sfârșitul fiecărei zile (OMFP nr. 2.634/2015, anexa 2) — o regulă contabilă, distinctă de plafoanele de numerar, dar la fel de obligatorie.
- **Fragmentarea plăților/încasărilor pentru a evita plafonul este expres interzisă** (art. 3 alin. (2)-(3) din Legea nr. 70/2015) — inclusiv fragmentarea facturilor unei singure livrări/prestări cu valoare mai mare decât plafonul.
- **Orice sumă încasată cash de o microîntreprindere intră în baza de calcul a impozitului micro**, care se aplică veniturilor, nu profitului — spre deosebire de o firmă la impozit pe profit, unde o eventuală eroare de înregistrare a unei încasări afectează doar marja, la micro afectează direct suma impozabilă.

## Ce se greșește în practică

- Se presupune că regimul micro are plafoane de numerar diferite sau mai relaxate față de o firmă la impozit pe profit — Legea nr. 70/2015 nu face nicio distincție în funcție de regimul de impozitare al firmei.
- Se ține registrul de casă cu întârziere, „la sfârșitul lunii", în loc de zilnic, cum cere norma — la o firmă cu volum mare de tranzacții cash, asta face imposibilă identificarea la timp a unei eventuale depășiri de plafon.
- Se confundă plafonul de încasare de la clienți persoane fizice (10.000 lei/zi către o persoană, potrivit art. 4 din aceeași lege) cu plafonul de 5.000 lei/zi aplicabil relațiilor firmă-firmă — cele două sunt diferite.

## Ce face iConta.eu

Modulul `core/casa.py` implementează `verifica_plafon`, care calculează, pe baza operațiunilor de casă înregistrate zilnic, dacă a fost depășit plafonul legal aplicabil fiecărei categorii de operațiune (inclusiv distincția pentru cash and carry și avansuri spre decontare), confirmat direct din cod. Alertele de plafon funcționează pe operațiunile trecute prin `core/casa_api.py`; contribuția lor la baza impozabilă a regimului micro se reflectă mai departe prin evidența generală a veniturilor, fără un modul separat care să lege explicit „plafon de numerar depășit" de „bază impozabilă micro" — legătura conceptuală rămâne una pe care contabilul o face.

[iConta.eu](/)
