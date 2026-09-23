---
title: Ce fac dacă am calculat CAS greșit?
description: Cea mai frecventă cauză a unui CAS calculat greșit e ignorarea podelei minime de contribuții (CF art.146 alin.(5^6)) sau folosirea salariului minim greșit din cele două ferestre ale 2026. Vezi cum se verifică și se recalculează.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am calculat CAS greșit?

Înainte de a corecta o declarație, verificați de unde a apărut greșeala — cele mai frecvente cauze confirmate în motorul de calcul salarial sunt fie ignorarea podelei minime de contribuții, fie folosirea salariului minim greșit pentru luna respectivă.

## Temeiul legal

::: ghid-temei
CAS nu poate fi calculat sub nivelul corespunzător salariului minim brut pe țară — regula se aplică „în baza unui contract individual de muncă cu normă întreagă SAU cu timp parțial" (Codul fiscal, art.146 alin.(5^6)) — condiția legală e nivelul venitului, nu tipul normei de lucru.
:::

## Cauzele cele mai frecvente ale unui CAS greșit

1. **Podeaua de contribuții ignorată.** Dacă venitul brut e sub salariul minim (întreg sau redus cu facilitatea aplicabilă, proratat la normă parțială), CAS nu se calculează pe brutul efectiv, ci pe podea — salariul minim aplicabil lunii, eventual redus cu facilitatea, eventual proratat pe fracțiunea de normă. Cea mai frecventă greșeală e calcularea CAS direct pe brutul mic, fără verificarea podelei.
2. **Salariul minim greșit pentru lună.** 2026 are două valori ale salariului minim — 4.050 lei (ianuarie–iunie) și 4.325 lei (iulie–decembrie). Un CAS calculat cu valoarea greșită pentru luna respectivă e o sursă frecventă de eroare, mai ales la calculele retroactive sau la regularizări.
3. **Excepțiile de la podea, aplicate greșit sau omise.** Legea exceptează explicit de la regula podelei: elevii/studenții sub 26 de ani, ucenicii sub 18 ani, persoanele cu dizabilități, pensionarii la limită de vârstă și cazurile de cumul de contracte cu bază cumulată peste minim. Aplicarea podelei la un angajat exceptat (sau, invers, omiterea podelei la un angajat care nu e exceptat) generează un CAS greșit.
4. **Facilitatea „salariul minim neimpozabil" aplicată incorect.** Facilitatea (300 sau 200 lei, după fereastră) are 4 condiții cumulative — normă întreagă, funcție de bază, brut contractual egal cu salariul minim, venit brut total sub plafon. Aplicarea ei fără îndeplinirea tuturor condițiilor (de exemplu, la un brut cu un leu peste minim) modifică incorect baza de calcul CAS.

## Ce fac dacă am descoperit greșeala

Recalculați luna respectivă pe baza corectă (podea corectă, salariu minim corect pentru fereastra din acea lună, facilitate aplicată doar dacă toate condițiile sunt îndeplinite). Diferența dintre CAS-ul declarat greșit și CAS-ul recalculat corect se regularizează, de regulă, printr-o declarație rectificativă pentru declarația care conținea CAS-ul greșit.

**De semnalat onest**: procedura efectivă de depunere a unei declarații rectificative (formular, termen, mecanism) nu face parte din codul verificat pentru acest ghid — dosarul de cercetare acoperă motorul de calcul salarial (`core/salarizare.py`), nu fluxul de corecție al declarațiilor deja depuse. Pentru pașii exacți de rectificare, verificați direct funcționalitatea de declarații a aplicației.

## Ce se greșește în practică

- Se corectează doar netul plătit angajatului, fără să se recalculeze corect CAS-ul, CASS-ul și baza impozabilă pentru luna respectivă.
- Se presupune că podeaua de contribuții se aplică doar la normă parțială — condiția legală e nivelul venitului sub minim, nu tipul normei; podeaua se aplică și la normă întreagă, dacă brutul e sub minim.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`) verifică automat podeaua de contribuții („baza_podea", liniile 292-323) de fiecare dată când brutul introdus e sub pragul corespunzător lunii — pragul vine din registrul „period-aware" `core.common.COTE`, potrivit fereastrei active (salariul minim, eventual redus cu facilitatea). Recalcularea unei luni anterioare cu datele corecte pentru acea lună (dată explicită, obligatorie pentru funcția de deducere și pentru selectarea cotelor) produce automat valoarea corectă de CAS pentru comparație cu ce a fost declarat greșit.

[iConta.eu](/)
