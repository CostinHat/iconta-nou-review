---
title: "Cum se contabilizează taxele de fulfillment reținute de marketplace?"
description: "Principiul contabil pentru recunoașterea veniturilor brute din vânzări versus comisioanele reținute de un marketplace, conform OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează taxele de fulfillment reținute de marketplace?

Când un marketplace (Amazon, eMAG și altele similare) reține din suma decontată taxele de fulfillment, comision și alte costuri, întrebarea contabilă e dacă vânzătorul înregistrează venitul brut din vânzare sau doar suma netă primită. Reglementările contabile dau un răspuns clar de principiu, chiar dacă nu tratează explicit cazul „marketplace".

## Temeiul legal

::: ghid-temei
„432. - Sumele colectate de o entitate în numele unor terțe părți, inclusiv în cazul contractelor de agent, comision sau mandat comercial încheiate potrivit legii, nu reprezintă venit din activitatea curentă, chiar dacă din punct de vedere al taxei pe valoarea adăugată persoanele care acționează în nume propriu sunt considerate cumpărători revânzători. În această situație, veniturile din activitatea curentă sunt reprezentate de comisioanele cuvenite."
— OMFP 1802/2014, pct. 432 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Textul reglementează explicit relația din perspectiva intermediarului (agent/comisionar) — regula relevantă pentru vânzătorul care folosește un marketplace e complementară și rezultă din același principiu de recunoaștere brută a veniturilor (pct. 431, 433):

- pentru **vânzătorul** care își vinde produsele prin marketplace, vânzarea rămâne, în relația cu clientul final, o vânzare proprie — venitul din activitatea curentă se recunoaște la **valoarea brută a vânzării** (prețul plătit de client), nu la suma netă primită după reținerea comisioanelor de fulfillment;
- taxele de fulfillment, comisionul de platformă și alte costuri reținute de marketplace se înregistrează **separat, ca o cheltuială** a vânzătorului (servicii prestate de terți), nu se scad direct din venit — practica de a înregistra doar suma netă decontată („net accounting") distorsionează atât cifra de afaceri raportată, cât și baza de TVA aferentă serviciilor primite de la marketplace;
- dacă marketplace-ul acționează efectiv ca un **comisionar/agent** care vinde în nume propriu (model diferit, mai rar la platformele de tip fulfillment), atunci se aplică direct pct. 432: vânzătorul recunoaște venitul din vânzare, iar suma reținută de platformă reprezintă comisionul ei, nu venitul vânzătorului.
- sursele verificate nu conțin o reglementare specifică „marketplace" sau „fulfillment" — interpretarea de mai sus se bazează pe principiile generale de recunoaștere a veniturilor (pct. 431-433), aplicabile prin analogie.

## Ce se greșește în practică

- Se înregistrează în contabilitate doar suma netă primită în cont de la marketplace, fără a reconstitui separat venitul brut din vânzare și cheltuiala cu comisioanele/fulfillment-ul — cifra de afaceri raportată iese subevaluată, cu efecte inclusiv asupra plafoanelor fiscale (TVA, micro) calculate pe cifra de afaceri.
- Se tratează taxele reținute de marketplace ca simplă „reducere de preț" a vânzării, în loc de cheltuială cu serviciile primite — de regulă, marketplace-ul emite propria factură pentru comisioane, distinctă de vânzarea către clientul final.
- Se omite verificarea TVA-ului aferent facturii de comision emise de marketplace (adesea o platformă cu sediul în alt stat membru UE), ceea ce poate implica taxare inversă și obligații declarative suplimentare (D390, de exemplu).

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o integrare automată dedicată platformelor de tip marketplace/fulfillment care să reconcilieze automat vânzarea brută cu taxele reținute — vânzările și facturile de comision se introduc separat de utilizator, urmând principiul general de recunoaștere brută descris mai sus, fără un modul specific pentru acest scenariu.

[iConta.eu](/)
