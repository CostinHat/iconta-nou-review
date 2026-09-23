---
title: "Transferul de stocuri între gestiuni: documente"
description: Documentul justificativ pentru un transfer de marfă între gestiuni depinde de un singur criteriu legal - dacă gestiunile sunt în aceeași incintă sau dispersate teritorial. Ce document trebuie emis, în fiecare caz, și ce face iConta.eu la nivel de înregistrare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Transferul de stocuri între gestiuni: documente

Când marfa trece dintr-o gestiune în alta, întrebarea „ce document fac?" are un singur criteriu de decizie: gestiunile sunt în aceeași incintă sau sunt dispersate teritorial. Nu contează dacă gestiunile aparțin aceleiași firme sau ce fel de marfă se transferă — contează doar distanța fizică dintre ele.

## Temeiul legal

::: ghid-temei
„În cazul utilizării ca bon de transfer între două gestiuni aflate în incinta entității, bonul de predare, transfer, restituire se întocmește pe măsură ce se efectuează transferul. Transferul se efectuează numai între gestiuni din incinta aceleiași entități. În cazul gestiunilor dispersate teritorial se întocmește Aviz de însoțire a mărfii (cod 14-3-6A)."

— OMFP 2634/2015, Anexa 2, pct. 189 (Bonul de predare, transfer, restituire, cod 14-3-3A)

„Avizul de însoțire a mărfii servește ca: [...] dispoziție de transfer al valorilor materiale de la o gestiune la alta, dispersate teritorial, ale aceleiași entități; [...] În cazul transferului de bunuri între gestiunile aceleiași entități, dispersate teritorial, [...] Avizul de însoțire a mărfii va purta mențiunea «Fără factură», după caz."

— OMFP 2634/2015, Anexa 2, pct. 199 (Avizul de însoțire a mărfii, cod 14-3-6A)
:::

Cele două texte fixează exact granița: **Bonul de predare, transfer, restituire (14-3-3A)** e documentul corect doar când ambele gestiuni sunt „în incinta entității" — practic aceeași clădire sau curte, fără deplasare pe drum public. În orice altă situație — gestiuni la adrese diferite, chiar dacă aparțin aceleiași firme — documentul obligatoriu e **Avizul de însoțire a mărfii (14-3-6A)**, tocmai pentru că bunul circulă pe drum public și are nevoie de document de însoțire pe timpul transportului.

## Ce se greșește în practică

- Se folosește Bonul de predare-transfer-restituire pentru transferuri între puncte de lucru aflate la adrese diferite, deși textul de la pct. 189 limitează explicit acest formular la gestiuni „din incinta aceleiași entități".
- Se transportă marfă între gestiuni dispersate teritorial fără niciun document de însoțire, expunând transportul unui control rutier fără justificare a mărfii aflate în mașină.
- Se confundă transferul intern (fără factură, „Fără factură" pe aviz) cu o livrare care ar necesita factură — avizul de transfer între gestiuni ale aceleiași entități nu e o vânzare, deci nu generează TVA.

## Ce face iConta.eu

Funcția de transfer între gestiuni din iConta.eu (F138, Tier 1) înregistrează mișcarea de stoc: o ieșire din gestiunea sursă și o intrare în gestiunea destinație, ambele la costul mediu ponderat (CMP) curent, aceeași cantitate și valoare, fără notă contabilă (transferul fizic e neutru pe valorizare — nu e nici consum, nici achiziție). Câmpul de document al mișcării e text liber: fie numele documentului emis de dvs. (de exemplu „Aviz 14-3-6A nr. 25"), fie, dacă îl lăsați gol, un text generat automat de forma „transfer {gestiune sursă}->{gestiune destinație}".

Aplicația nu generează un formular tipizat 14-3-3A sau 14-3-6A ca document/PDF propriu-zis — verificat direct în codul motorului de stocuri, nu există nicio funcție care să producă un asemenea document. Transferul înregistrat în iConta.eu e evidența internă de stoc; documentul justificativ pentru circulația fizică a mărfii (mai ales cel obligatoriu pe drum, avizul de însoțire) rămâne de întocmit separat, după criteriul de mai sus.

[iConta.eu](/)
