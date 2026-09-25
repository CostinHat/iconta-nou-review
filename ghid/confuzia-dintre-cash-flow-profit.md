---
title: "Confuzia dintre cash-flow și profit: greșeală de management"
description: "De ce o firmă poate avea profit contabil pozitiv și, în același timp, un sold de bani proiectat negativ peste câteva săptămâni — și unde se vede asta în iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Confuzia dintre cash-flow și profit: greșeală de management

Una dintre cele mai costisitoare confuzii de management la firmele mici este să tratezi profitul din contul de profit și pierdere ca și cum ar fi bani disponibili în cont. Profitul e o mărime contabilă, calculată pe bază de angajamente — venituri și cheltuieli recunoscute la momentul tranzacției, nu la momentul plății. Cash-flow-ul e altceva: banii care chiar intră și ies din conturi, la datele reale de încasare și plată.

## Temeiul legal

::: ghid-temei
„(1) Principiul contabilității de angajamente. Efectele tranzacțiilor și ale altor evenimente sunt recunoscute atunci când tranzacțiile și evenimentele se produc (și nu pe măsură ce numerarul sau echivalentul său este încasat sau plătit) și sunt înregistrate în contabilitate și raportate în situațiile financiare ale perioadelor aferente. (2) Trebuie să se țină cont de veniturile și cheltuielile aferente exercițiului financiar, indiferent de data încasării veniturilor sau data plății cheltuielilor."
— OMFP 1802/2014, pct. 53 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Chiar textul reglementării explică sursa confuziei:

- Profitul se recunoaște la data facturii (livrare/prestare), nu la data încasării — o factură emisă în decembrie și neîncasată încă intră deja în profitul anului, deși banii n-au ajuns în cont.
- Cheltuielile intră în calculul profitului la data angajării lor (recepția bunului/serviciului), nu la data plății — o factură de furnizor neplătită scade deja profitul, chiar dacă plata e programată abia peste 60 de zile.
- Rezultatul: profit contabil pozitiv poate coexista perfect cu lipsă de bani în cont, dacă încasările întârzie sau plățile sunt concentrate în timp.

## Ce se greșește în practică

- Se ia decizia de a distribui dividende sau de a face o investiție „pentru că avem profit", fără să se verifice separat dacă există și lichiditate disponibilă pentru asta.
- Se interpretează un profit lunar bun ca semn că firma „stă bine", deși soldul de bani poate fi deja tensionat din cauza unor încasări întârziate de la clienți mari.
- Se ignoră faptul că amortizarea (o cheltuială contabilă fără plată efectivă de cash) scade profitul, dar nu afectează deloc soldul din bancă — și invers, ratele de capital la un credit afectează cash-ul, dar nu apar ca cheltuială în contul de profit și pierdere.

## Ce face iConta.eu

În portalul clientului, ecranul „Cifrele firmei" pune vizual, una sub alta, exact cele două mărimi care se confundă: rândul „Profit" (calculat contabil, pe bază de angajamente, din `documente_api.balanta`) și, imediat dedesubt, secțiunea „Previziune bani (8 săptămâni)" — proiecția de cash pe scadențe, generată de motorul `core/cashflow.py`. Astfel poți avea, pe același ecran, un profit contabil pozitiv și, câteva rânduri mai jos, un sold de bani proiectat care devine negativ peste 3-4 săptămâni — colorat automat cu roșu în interfață. Proiecția e explicit etichetată în aplicație drept „estimare pe scadențele facturilor — orientativ", nu o certitudine, iar ecranul e strict informativ: nu există niciun buton de acțiune, nu se pot programa plăți sau amâna facturi din el.

[iConta.eu](/)
