---
title: "Cum se raportează transferurile între gestiuni în D406?"
description: Răspunsul scurt și verificat direct în cod - transferul între gestiuni nu apare în D406 sub nicio formă, nici în raportarea lunară, nici în raportarea de stocuri la cererea ANAF. De ce, și ce înseamnă asta practic.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se raportează transferurile între gestiuni în D406?

Răspunsul scurt: **nu se raportează.** Un transfer de marfă între două gestiuni ale aceleiași firme nu produce nicio informație distinctă în D406, indiferent de câte transferuri faceți într-o lună. Documentul justificativ al transferului (vezi mai jos criteriul aceeași incintă/gestiuni dispersate) rămâne, dar în fișierul D406 nu se vede.

## Temeiul legal

::: ghid-temei
„În cazul utilizării ca bon de transfer între două gestiuni aflate în incinta entității, bonul de predare, transfer, restituire se întocmește pe măsură ce se efectuează transferul. Transferul se efectuează numai între gestiuni din incinta aceleiași entități. În cazul gestiunilor dispersate teritorial se întocmește Aviz de însoțire a mărfii (cod 14-3-6A)."

— OMFP 2634/2015, Anexa 2, pct. 189 (Bonul de predare, transfer, restituire, cod 14-3-3A)

„Avizul de însoțire a mărfii servește ca: [...] dispoziție de transfer al valorilor materiale de la o gestiune la alta, dispersate teritorial, ale aceleiași entități [...]"

— OMFP 2634/2015, Anexa 2, pct. 199 (Avizul de însoțire a mărfii, cod 14-3-6A)
:::

Aceste texte stabilesc obligația de a documenta transferul fizic al mărfii — dar D406 (declarația informativă SAF-T) e o raportare separată, cu structură proprie, și obligația de a emite bon de transfer sau aviz de însoțire nu înseamnă automat că mișcarea respectivă ajunge și în fișierul XML depus la ANAF.

## De ce nu apare transferul în D406

Există trei motive, toate verificate direct în structura declarației:

1. **Secțiunea de mișcări de bunuri (MovementOfGoods) din D406 lunar este întotdeauna goală.** Standardul SAF-T prevede această secțiune ca obligatorie structural, dar autogolită („self-closed") în raportarea lunară — nu conține nicio linie, indiferent de câte mișcări de stoc (transferuri, intrări, ieșiri) au avut loc în lună.
2. **Secțiunea de stoc fizic (PhysicalStock) nu se generează deloc în D406 lunar.** Aceasta e componenta din schema SAF-T („2.10", opțională „la cerere") care ar putea reflecta, teoretic, stocul pe gestiune la un moment dat. În raportarea lunară obișnuită, nu se completează.
3. **Există un raport separat de stocuri, generat la o cerere distinctă (nu la depunerea lunară), dar acesta nu diferențiază pe gestiune.** Toate locațiile/gestiunile ajung agregate sub un singur identificator de gestiune generic în acel raport separat, chiar dacă firma are mai multe puncte de lucru active în evidența de stoc.

Practic: dacă un control ANAF verifică D406-ul lunar depus, nu găsește acolo transferurile între gestiuni — nici valoric, nici cantitativ, nici pe gestiune. Documentul justificativ al transferului (bonul 14-3-3A sau avizul 14-3-6A, după caz) rămâne singura dovadă a mișcării, independent de D406.

## Ce se greșește în practică

- Se crede că, odată emis avizul de însoțire sau bonul de transfer, mișcarea „intră automat" și în D406 — nu intră, cele două sunt complet independente.
- Se așteaptă ca secțiunea de stoc din D406 să arate un istoric al transferurilor între puncte de lucru — secțiunea respectivă (PhysicalStock) fie nu se generează în raportarea lunară, fie, atunci când se generează separat la cerere, nu diferențiază pe gestiune.
- Se renunță la documentul justificativ fizic pe motiv că „oricum se vede în D406" — exact invers: fiindcă D406 nu îl arată, documentul de circulație a mărfii (14-3-3A/14-3-6A) rămâne singura dovadă opozabilă la un control.

## Ce face iConta.eu

Transferul între gestiuni din iConta.eu (F138) generează exclusiv o mișcare internă de stoc (ieșire din gestiunea sursă + intrare în gestiunea destinație, la CMP curent), fără notă contabilă — deci nu are cum să apară în Registrul jurnal și, prin construcție, nici în secțiunea de mișcări de bunuri a D406-ului lunar, care rămâne goală indiferent de operațiunile de acest tip. Raportul separat de stocuri „la cerere ANAF" nu grupează rezultatele pe gestiune — agregă totul pe articol, indiferent de câte locații a folosit firma. Dacă aveți nevoie să dovediți circulația mărfii între gestiuni, documentul de referință e cel emis conform criteriului aceeași incintă/dispersare teritorială (bon 14-3-3A sau aviz 14-3-6A), nu D406.

[iConta.eu](/)
