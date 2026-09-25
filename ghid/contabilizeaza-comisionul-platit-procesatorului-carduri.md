---
title: "Cum se contabilizează comisionul plătit procesatorului de carduri?"
description: "Contul folosit pentru comisionul reținut de un procesator de plăți cu cardul și diferența dintre comisionul vizibil în extrasul bancar și cel reținut direct din încasare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează comisionul plătit procesatorului de carduri?

Firmele care acceptă plăți cu cardul (POS fizic sau plăți online, prin procesatori precum cei folosiți de magazinele web) plătesc un comision pentru fiecare tranzacție. Întrebarea revine des: pe ce cont se înregistrează acest comision?

## Temeiul legal

::: ghid-temei
„Contul 627 «Cheltuieli cu serviciile bancare și asimilate» Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 «Cheltuieli cu serviciile bancare și asimilate» se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512); [...] – sume clarificate trecute pe cheltuieli (473)."
— OMFP 1802/2014, funcțiunea contului 627 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Comisionul plătit unui procesator de carduri (bancă emitentă de POS, sau un procesator online) se încadrează în categoria cheltuielilor cu serviciile bancare și asimilate — deci se înregistrează pe **contul 627**, în contrapartidă cu banca (512) sau cu debitori diverși (471), în funcție de modul în care apare comisionul:

- Dacă procesatorul virează în contul firmei **suma brută** a tranzacțiilor și reține comisionul separat, ca linie distinctă vizibilă în extrasul bancar (adesea descrisă cu „comision", „taxă administrare" etc.), înregistrarea e directă: 627 = 5121, la data reținerii.
- Dacă procesatorul virează firmei **suma netă** (încasare minus comision reținut direct din decontarea zilnică, tipic la plățile online prin platforme de tip payment gateway), extrasul bancar arată doar suma netă încasată — comisionul nu apare ca linie separată vizibilă. În acest caz, pentru a reflecta corect atât venitul brut din vânzare, cât și cheltuiala cu comisionul (fără să se piardă TVA colectat aferent prețului de vânzare integral), înregistrarea completă presupune atât factura/venitul din vânzare la valoarea integrală, cât și 627 = 4111/461 pentru comisionul reținut, pe baza raportului de decontare (settlement report) emis de procesator, care e documentul justificativ pentru operațiune.

## Ce se greșește în practică

- Se înregistrează în contabilitate doar suma netă încasată în bancă, fără să se reconstituie separat venitul brut din vânzare și cheltuiala cu comisionul — ceea ce subevaluează atât cifra de afaceri, cât și cheltuielile deductibile.
- Se omite raportul de decontare (settlement report) al procesatorului ca document justificativ pentru comision, mulțumindu-se cu extrasul bancar, care de multe ori nu detaliază separat fiecare tranzacție și comisionul aferent.
- Se contabilizează comisionul pe un cont generic de „alte cheltuieli" (628) în loc de 627, pierzând astfel gruparea corectă a cheltuielilor bancare și asimilate în situațiile financiare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu recunoaște automat, la importul extraselor bancare, operațiunile descrise cu cuvinte-cheie precum „comision", „taxa adm" sau „speze" și le clasifică direct pe contul 627 în contrapartidă cu banca (627 = 5121). Această automatizare acoperă comisioanele **vizibile ca linie separată în extrasul bancar** — pentru comisioanele reținute direct de un procesator de plăți online, înainte ca suma netă să ajungă în bancă, aplicația nu reconstituie automat separarea venit brut/comision din raportul de decontare al procesatorului; această înregistrare rămâne manuală, pe baza documentului emis de procesator.

[iConta.eu](/)
