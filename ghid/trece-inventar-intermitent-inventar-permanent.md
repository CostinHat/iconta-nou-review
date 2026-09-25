---
title: "Cum se trece de la inventar intermitent la inventar permanent?"
description: "Diferența dintre metoda inventarului intermitent și cea a inventarului permanent pentru obiectele de inventar, conform OMFP 1802/2014, și ce metodă folosește efectiv iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se trece de la inventar intermitent la inventar permanent?

Reglementările contabile recunosc două metode distincte de evidențiere a stocurilor de natura obiectelor de inventar (și, în general, a materiilor prime și materialelor): metoda inventarului permanent, în care fiecare mișcare trece prin conturile de stocuri, și metoda inventarului intermitent, în care intrările se înregistrează direct pe cheltuială, iar stocurile se ajustează doar la sfârșitul perioadei, pe baza inventarierii fizice.

## Temeiul legal

::: ghid-temei
„În situația aplicării inventarului intermitent: Stocurile existente la începutul exercițiului financiar, precum și intrările în cursul perioadei de materii prime, materiale consumabile, materiale de natura obiectelor de inventar se înregistrează direct în debitul conturilor 601 «Cheltuieli cu materiile prime», 602 «Cheltuieli cu materialele consumabile» și 603 «Cheltuieli privind materialele de natura obiectelor de inventar». Conturile 301 «Materii prime», 302 «Materiale consumabile» și 303 «Materiale de natura obiectelor de inventar» se debitează numai la sfârșitul perioadei cu valoarea la preț de înregistrare a materiilor prime, materialelor consumabile, materialelor de natura obiectelor de inventar, existente în stoc, stabilită pe baza inventarului [...]"
— OMFP 1802/2014, reglementări contabile — funcționarea contului 303, metoda inventarului intermitent (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.html)
:::

Diferența față de metoda permanentă, pe scurt:

- **Inventar permanent** (metoda descrisă în general la achizițiile de obiecte de inventar): fiecare achiziție intră mai întâi pe contul de stoc (303 = 401), iar valoarea trece pe cheltuială abia la darea în folosință (603 = 303). Stocul e mereu actualizat, mișcare cu mișcare.
- **Inventar intermitent**: achizițiile intră direct pe cheltuială (603 = 401), fără să treacă prin contul de stoc, iar contul 303 se debitează doar la finalul perioadei, cu valoarea stabilită prin inventariere fizică a stocului rămas.
- **Alegerea metodei e o politică contabilă a firmei**, aprobată de administrator, care se stabilește o dată și se aplică consecvent — legea nu detaliază o procedură pas cu pas de „trecere" de la o metodă la alta, aceasta fiind tratată ca o schimbare de politică contabilă, cu regulile generale aplicabile modificării politicilor contabile.
- Trecerea de la o metodă la alta trebuie documentată în notele explicative, cu motivul schimbării și efectul ei asupra rezultatelor raportate.

## Ce se greșește în practică

- Se amestecă cele două metode în aceeași perioadă — unele achiziții intră pe stoc, altele direct pe cheltuială, fără o politică contabilă clară și consecventă.
- Se schimbă metoda de la o lună la alta, în funcție de comoditate, în loc să fie o decizie stabilă de politică contabilă, documentată.
- Se aplică metoda intermitentă fără inventariere fizică reală la sfârșitul perioadei — fără această inventariere, contul 303 nu poate fi ajustat corect, iar cheltuiala lunii rămâne denaturată.

## Ce face iConta.eu

Modulul de obiecte de inventar din iConta.eu implementează **exclusiv metoda inventarului permanent**: orice achiziție generată prin formularul „Obiecte de inventar (303)" intră întotdeauna pe contul 303 (303 = 401), niciodată direct pe cheltuială la cumpărare. Aplicația **nu are** un comutator, o opțiune de profil al firmei sau un flux separat pentru metoda inventarului intermitent, și nici o funcție de „trecere" de la o metodă la alta — acest concept nu apare implementat în cod. Firmele care aplică metoda inventarului intermitent trebuie să-și gestioneze acele înregistrări în afara acestui modul.

[iConta.eu](/)
