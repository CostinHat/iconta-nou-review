---
title: "Cine semnează nota de intrare-recepție în firmă"
description: "Cine întocmește și cine semnează Nota de recepție și constatare de diferențe (NIR), potrivit normelor privind documentele financiar-contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine semnează nota de intrare-recepție în firmă

Nota de intrare-recepție (NIR) e documentul pe care se bazează încărcarea în gestiune a bunurilor aprovizionate și înregistrarea lor în contabilitate. Deși în practică e adesea tratată ca o simplă formalitate, normele privind documentele financiar-contabile stabilesc destul de precis cine o întocmește și în ce situații e obligatorie.

## Temeiul legal

::: ghid-temei
„Nota de recepție și constatare de diferențe (NIR) servește ca: - document pentru recepția bunurilor aprovizionate; - document justificativ pentru încărcare în gestiune; - document justificativ de înregistrare în contabilitate. Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare."
— OMFP 2634/2015, Anexa 2 (Normele specifice de întocmire și utilizare a documentelor financiar-contabile), cod 14-3-1A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Formularul-model din aceleași norme (Anexa 3) arată explicit cine îl completează și îl semnează:

- Documentul se deschide cu formula „Subsemnații, **membrii comisiei de recepție**, am procedat la recepționarea valorilor materiale furnizate de...", deci constatarea cantităților și eventualelor diferențe cade în sarcina **comisiei de recepție** stabilite de entitate — nu a unei singure persoane.
- Blocul de semnături din model are două coloane distincte: „**Comisia de recepție**" (numele, prenumele și semnătura fiecărui membru) și „**Primit în gestiune**" (data și semnătura celui care preia efectiv bunurile în gestiune) — deci semnează atât comisia, cât și gestionarul.
- NIR e **obligatoriu** doar în situațiile enumerate expres în normă: bunuri din gestiuni diferite cuprinse în aceeași factură/aviz, bunuri primite spre prelucrare/custodie/păstrare, bunuri cumpărate de la persoane fizice, bunuri sosite fără documente de livrare, bunuri cu diferențe constatate la recepție și mărfuri gestionate la preț de vânzare.
- În afara acestor cazuri, recepția și încărcarea în gestiune se fac direct pe baza documentului de livrare (factură sau aviz de însoțire a mărfii), fără NIR separat.

## Ce se greșește în practică

- Se întocmește și se semnează NIR-ul de o singură persoană (de regulă gestionarul), fără constituirea unei comisii de recepție, deși modelul normat presupune mai mulți semnatari pentru constatarea eventualelor diferențe.
- Se emite NIR pentru orice recepție, deși norma îl cere obligatoriu doar în cazurile enumerate explicit — în restul situațiilor, factura sau avizul de însoțire ține deja loc de document de recepție.
- Se confundă „primit în gestiune" (semnătura gestionarului care preia bunurile) cu constatarea comisiei de recepție (care verifică cantitățile și calitatea) — sunt două roluri distincte în model, chiar dacă în firmele mici aceeași persoană poate cumula ambele funcții.

## Ce face iConta.eu

iConta.eu generează automat nota de recepție (NIR) și liniile aferente atunci când se înregistrează o recepție de stocuri, pe baza articolelor din factură/aviz, și blochează salvarea unui NIR fără nicio linie de recepție. Aplicația ține evidența digitală a documentului și a valorilor recepționate, dar nu implementează un flux separat de „comisie de recepție" cu semnături multiple — cine constată eventualele diferențe la recepția fizică și cine semnează pe hârtie rămâne o organizare internă a firmei, în afara aplicației.

[iConta.eu](/)
