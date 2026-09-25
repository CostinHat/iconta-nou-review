---
title: "Cum se completează D112 pentru un salariat cu normă întreagă?"
description: "Baza minimă de calcul a contribuției de asigurări sociale pentru un salariat cu normă întreagă, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se completează D112 pentru un salariat cu normă întreagă?

Tipul de normă (întreagă sau parțială) nu e doar o mențiune informativă în contractul de muncă — influențează direct baza minimă de calcul a contribuției de asigurări sociale (CAS) raportată în D112.

## Temeiul legal

::: ghid-temei
„Contribuția de asigurări sociale datorată de către persoanele fizice care obțin venituri din salarii sau asimilate salariilor, în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial, calculată potrivit alin. (5), nu poate fi mai mică decât nivelul contribuției de asigurări sociale calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra salariului de bază minim brut pe țară în vigoare în luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ."
— Legea 227/2015 (Codul fiscal), art. 146 alin. (5^6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret pentru completarea D112:

- Pentru un salariat cu **normă întreagă**, baza de calcul a CAS nu poate fi mai mică decât contribuția calculată la nivelul **întregului salariu minim brut pe țară** din luna respectivă — chiar dacă venitul brut efectiv realizat (de exemplu, din cauza zilelor de concediu medical) a fost mai mic.
- Pentru un salariat cu **timp parțial**, aceeași bază minimă se calculează **proporțional cu numărul zilelor lucrătoare din lună în care contractul a fost activ**, nu la nivelul integral al salariului minim.
- Regula se aplică distinct de eventuale facilități fiscale legate de norma întreagă (de exemplu, scutiri condiționate de încadrarea la funcția de bază cu normă întreagă și salariu egal cu minimul pe economie) — acestea au condiții și perioade de aplicare proprii, care trebuie verificate separat, an de an, în actul normativ care le instituie.
- Diferența dintre CAS calculată pe venitul efectiv și CAS calculată la nivelul bazei minime obligatorii (dacă venitul efectiv e sub minim) se suportă, după caz, conform regulilor din același articol — de aceea baza minimă corectă e esențială pentru a nu subdeclara CAS în D112.

## Ce se greșește în practică

- Se calculează CAS direct pe venitul brut efectiv realizat, fără să se verifice dacă acesta e sub baza minimă obligatorie de la art. 146 alin. (5^6), rezultând o subdeclarare.
- Se aplică baza minimă integrală (salariul minim pe economie) și pentru salariați cu timp parțial, deși legea cere proporționalizarea cu zilele lucrătoare din contract.
- Se confundă baza minimă de calcul CAS (regulă permanentă, art. 146) cu facilitățile temporare legate de salariul minim (introduse și limitate în timp prin acte normative separate), aplicând sau omițând-o pe baza unei premise greșite despre valabilitatea ei.

## Ce face iConta.eu

Am verificat în `core/salarizare.py`: aplicația **calculează automat baza minimă de CAS** conform art. 146 alin. (5^6)-(5^7), diferențiat pentru salariat cu normă întreagă (parametrul `norma_intreaga=True`, baza raportată la salariul minim brut pe economie din luna respectivă) și pentru timp parțial (proporțional). Codul citează explicit acest temei în comentarii („CF art.146 alin.(5^6)/(5^7)") și rezultatul e preluat direct în generarea D112.

[iConta.eu](/)
