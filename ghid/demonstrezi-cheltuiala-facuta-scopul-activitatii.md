---
title: "Cum demonstrezi că o cheltuială este făcută în scopul activității economice?"
description: "Legea condiționează deducerea unei cheltuieli de scopul ei economic, nu de existența unei liste fixe de cheltuieli permise — proba stă în documentele justificative și în legătura cu obiectul de activitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum demonstrezi că o cheltuială este făcută în scopul activității economice?

Codul fiscal nu dă o listă exhaustivă de cheltuieli deductibile — folosește un criteriu general: cheltuiala trebuie făcută „în scopul desfășurării activității economice". La un ONG cu activitate economică, această demonstrație contează dublu: pe lângă deductibilitate, trebuie și separată corect de cheltuielile activității fără scop patrimonial, care nu se scad din venitul economic impozabil.

## Temeiul legal

::: ghid-temei
„Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice, inclusiv cele reglementate prin acte normative în vigoare, precum și taxele de înscriere, cotizațiile și contribuțiile datorate către camerele de comerț și industrie, organizațiile patronale și organizațiile sindicale."
— art. 25 alin. (1) din Legea 227/2015 (Codul fiscal) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Criteriul legal e funcțional, nu formal: contează dacă cheltuiala servește efectiv activității economice, nu dacă apare pe o listă predefinită.
- Proba practică se face prin: documentul justificativ (factură, contract, proces-verbal de recepție), legătura obiectivă cu obiectul de activitate economică declarat și, dacă e cazul, evidența că bunul/serviciul achiziționat a fost folosit efectiv în activitatea economică, nu în cea fără scop patrimonial.
- La un ONG cu ambele tipuri de activitate, sarcina suplimentară e separarea: o cheltuială făcută exclusiv pentru activitatea fără scop patrimonial (de exemplu, organizarea unei acțiuni statutare gratuite) nu e deductibilă la calculul impozitului pe profit al activității economice, chiar dacă în sine ar respecta art. 25 alin. (1).

## Ce se greșește în practică

- Se deduc, la activitatea economică, cheltuieli făcute integral pentru scopul statutar (fără scop patrimonial) al organizației, doar pentru că trec prin aceleași conturi bancare.
- Se consideră suficientă existența unei facturi, fără să se documenteze și legătura cu activitatea economică (contract, obiect de activitate, utilizare efectivă).
- Se ignoră cheltuielile mixte — folosite parțial pentru activitatea economică, parțial pentru cea fără scop patrimonial — deducându-le integral sau, la polul opus, refuzându-le integral, în loc să fie alocate proporțional.

## Ce face iConta.eu

Funcționalitatea de contabilitate ONG din iConta.eu (`core/ong.py`) tratează exclusiv latura de **venituri**: clasificarea veniturilor fără scop patrimonial pe conturile din grupa 73 și calculul plafonului de scutire pentru veniturile economice (art. 15 alin. 2-3 Cod fiscal). **Aplicația nu are nicio funcție dedicată** de analiză sau alocare a cheltuielilor între cele două activități ale unui ONG, nici de verificare a scopului economic al unei cheltuieli — demonstrarea și documentarea rămân integral în sarcina contabilului, pe baza documentelor justificative.

[iConta.eu](/)
