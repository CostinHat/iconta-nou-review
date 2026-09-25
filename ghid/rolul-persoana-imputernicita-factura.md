---
title: "Rolul și persoana împuternicită în e-Factura"
description: "Temeiul general al reprezentării prin împuternicit în relația cu organul fiscal, potrivit Codului de procedură fiscală — baza legală pe care se sprijină, în practică, accesul unui împuternicit la SPV/RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Rolul și persoana împuternicită în e-Factura

Sursele verificate nu conțin procedura specifică de înrolare a unui împuternicit în Spațiul Privat Virtual (SPV) pentru RO e-Factura — ce conțin, în schimb, este temeiul general al instituției „împuternicitului" în relația contribuabilului cu organul fiscal, pe care se sprijină, în practică, orice reprezentare electronică, inclusiv cea din SPV.

## Temeiul legal

::: ghid-temei
„ART. 18 Împuterniciții
(1) în relațiile cu organul fiscal contribuabilul/plătitorul poate fi reprezentat printr-un împuternicit. Conținutul și limitele reprezentării sunt cele cuprinse în împuternicire sau stabilite de lege, după caz. Desemnarea unui împuternicit nu îl împiedică pe contribuabil/plătitor să își îndeplinească personal obligațiile prevăzute de legislația fiscală, chiar dacă nu a procedat la revocarea împuternicirii potrivit alin. (2).
(2) împuternicitul este obligat să depună la organul fiscal actul de împuternicire, în original sau în copie legalizată. Revocarea împuternicirii operează față de organul fiscal de la data depunerii actului de revocare, în original sau în copie legalizată."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 18 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce se poate confirma, onest, din acest temei pentru e-Factura:

- Reprezentarea printr-un împuternicit este o instituție **generală** a Codului de procedură fiscală, valabilă în toate relațiile cu organul fiscal — SPV, unde funcționează RO e-Factura, este canalul electronic prin care se exercită, în practică, această reprezentare pentru comunicările electronice.
- Limitele reprezentării sunt date de conținutul **actului de împuternicire** — un împuternicit poate avea acces doar la anumite operațiuni (de exemplu, doar la e-Factura), în funcție de ce a fost mandatat expres.
- Desemnarea unui împuternicit **nu îl scutește** pe contribuabil de obligațiile lui fiscale — dacă împuternicitul nu acționează (de exemplu, nu descarcă/confirmă facturile primite în SPV), răspunderea contribuabilului pentru obligațiile legale legate de e-Factura rămâne neschimbată.
- Limitare onestă: pașii tehnici exacți de înrolare a unui împuternicit specific în SPV pentru RO e-Factura (formulare, proceduri electronice de autentificare) nu sunt detaliați în sursele verificate aici — ei sunt reglementați prin proceduri ANAF separate, neincluse integral în acest corpus.

## Ce se greșește în practică

- Se presupune că accesul unui angajat sau al contabilului la contul SPV al firmei este suficient, fără un act de împuternicire formal depus la organul fiscal — art. 18 alin. (2) cere depunerea explicită a actului de împuternicire.
- Se revocă informal accesul unei persoane (de exemplu, la schimbarea contabilului), fără a depune actul de revocare la organul fiscal — revocarea produce efecte față de organul fiscal doar de la data depunerii acestui act.
- Se presupune că un împuternicit general (pentru toate obligațiile fiscale) are automat și acces la RO e-Factura, fără verificarea limitelor exacte stabilite prin actul de împuternicire.

## Ce face iConta.eu

Verificat în cod: `core/spv_conector.py`, `core/spv_poll.py`, `core/spv_receive.py`, `core/spv_refresh.py` și `core/efactura_send.py` gestionează conectarea firmei la SPV (token OAuth) și trimiterea/primirea facturilor prin RO e-Factura; nu am găsit (grep pe „imputernicit"/„reprezentant") un model separat de „persoană împuternicită" în aceste module — aplicația operează pe baza unui singur token de conectare la SPV per firmă, fără o distincție internă între contribuabil și un eventual împuternicit desemnat oficial la ANAF.

[iConta.eu](/)
