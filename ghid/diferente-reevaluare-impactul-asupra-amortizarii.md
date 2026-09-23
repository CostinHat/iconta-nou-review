---
title: Diferențe din reevaluare și impactul asupra amortizării
description: O creștere sau o scădere din reevaluare se înregistrează diferit (rezervă vs. cheltuială), dar în ambele cazuri schimbă valoarea netă de la care pornește amortizarea ulterioară a activului.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Diferențe din reevaluare și impactul asupra amortizării

Diferența dintre valoarea justă și valoarea contabilă netă a unui mijloc fix, la reevaluare, nu se înregistrează la fel indiferent de semn — o creștere și o scădere urmează reguli distincte, iar istoricul reevaluărilor anterioare ale aceluiași activ poate schimba tratamentul. În ambele cazuri însă, rezultatul devine noua bază de la care amortizarea repornește.

## Temeiul legal

::: ghid-temei
"Dacă rezultatul reevaluării este o creștere față de valoarea contabilă netă, atunci aceasta se tratează astfel: ca o creștere a rezervei din reevaluare [...], dacă nu a existat o descreștere anterioară recunoscută ca o cheltuială aferentă acelui activ; sau ca un venit care să compenseze cheltuiala cu descreșterea recunoscută anterior la acel activ. Dacă rezultatul reevaluării este o descreștere a valorii contabile nete, aceasta se tratează ca o cheltuială cu întreaga valoare a deprecierii, atunci când în rezerva din reevaluare nu este înregistrată o sumă referitoare la acel activ (surplus din reevaluare) sau ca o scădere a rezervei din reevaluare [...], cu minimul dintre valoarea acelei rezerve și valoarea descreșterii, iar eventuala diferență rămasă neacoperită se înregistrează ca o cheltuială." — OMFP 1802/2014, pct. 111 alin. (1)-(2)
:::

Pe scurt, cele două ramuri:

- **Creștere**: dacă activul n-a avut o descreștere anterioară recunoscută drept cheltuială, întreaga creștere merge în rezerva din reevaluare (cont 105). Dacă a existat o descreștere anterioară, creșterea o compensează mai întâi prin cont de venituri (755), până la nivelul acelei descreșteri — restul, dacă rămâne, merge tot pe rezervă (105).
- **Scădere**: dacă activul are deja o rezervă din reevaluare, scăderea o consumă mai întâi (105), în limita soldului ei — eventualul rest neacoperit devine cheltuială (655). Dacă nu există rezervă pe acel activ, întreaga scădere e cheltuială (655).

Sumele de natura veniturilor/cheltuielilor din reevaluare se prezintă separat în contul de profit și pierdere, în conturile 755, respectiv 655 (OMFP 1802/2014 pct. 111 alin. (3)).

Efectul asupra amortizării ulterioare e același, indiferent de semn: amortizarea cumulată se elimină din valoarea brută, iar de la data reevaluării activul se amortizează pe noua valoare netă (justă), pe durata rămasă (OMFP 1802/2014 pct. 103-104). Fiscal, atenție la asimetrie: o creștere intră în baza de amortizare fiscală, dar o scădere sub costul istoric nu coboară baza fiscală sub acel cost — valoarea fiscală rămasă neamortizată "se recalculează până la nivelul celei stabilite pe baza costului de achiziție" (Legea 227/2015, art. 7 pct. 44 lit. c).

## Ce se greșește în practică

- Se citează pct. 113 sau pct. 114 din OMFP 1802/2014 pentru mecanismul creștere/scădere — punctele acestea tratează alte subiecte (pct. 113: limitele reducerii rezervei; pct. 114: cedarea parțială a terenurilor/clădirilor reevaluate). Temeiul corect al tratamentului creștere/scădere e **pct. 111 alin. (1) și (2)**.
- Se trece automat toată creșterea pe rezervă (105), fără să se verifice dacă activul are o descreștere anterioară recunoscută ca cheltuială — caz în care partea de compensare trebuie să treacă prin 755, nu direct prin 105.
- Se continuă, după reevaluare, amortizarea fiscală pe valoarea contabilă redusă, ignorând că, la o descreștere, baza fiscală rămâne la costul istoric (art. 7 pct. 44 lit. c).

## Ce face iConta.eu

Motorul de reevaluare calculează corect ambele ramuri: la creștere, compensează mai întâi o eventuală pierdere anterioară înregistrată pe 655 (venitul aferent intră pe 755, restul pe 105); la scădere, consumă mai întâi soldul rezervei 105 aferente activului, iar restul intră pe 655. Sumele de pornire — soldul contului 105 pentru acel activ și eventuala pierdere anterioară pe 655 — se introduc de operator; aplicația nu le interoghează automat din contabilitate, așa că un contabil care le completează greșit obține un rezultat acceptat necondiționat, fără o verificare încrucișată cu soldurile reale.

[iConta.eu](/)
