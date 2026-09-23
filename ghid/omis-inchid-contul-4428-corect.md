---
title: Am omis să închid contul 4428 corect
description: De ce contul 4428 se poate denatura la descărcarea de gestiune global-valorică atunci când firma folosește și TVA la încasare, și ce arată codul verificat.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am omis să închid contul 4428 corect

Contul 4428 „Taxa pe valoarea adăugată neexigibilă" nu este folosit doar de metoda global-valorică. Aceeași denumire de cont apare și în regimul de TVA la încasare (art. 282 Cod fiscal), printr-un ecran manual separat. Dacă firma folosește ambele mecanisme, contul 4428 poate ajunge să amestece mișcări care nu au nicio legătură între ele.

## Temeiul legal

::: ghid-temei
„În acest cont se evidențiază, potrivit legii, taxa pe valoarea adăugată neexigibilă."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), secțiunea Plan de conturi, funcțiunea contului 4428
:::

Textul reglementării descrie funcțiunea contului 4428 la modul general, fără să separe explicit regimul specific mărfurilor ținute la preț cu amănuntul (metoda global-valorică) de alte utilizări ale aceluiași cont, cum e TVA la încasare. Separarea celor două utilizări este, deci, o problemă de organizare contabilă și de aplicație, nu una tranșată direct de text.

## Ce se greșește în practică

- Se folosește contul 4428 atât pentru notele manuale de TVA la încasare, cât și pentru descărcarea automată de gestiune, fără analitice distincte care să separe cele două fluxuri.
- Se validează descărcarea lunară de gestiune fără să se verifice dacă în aceeași perioadă au fost înregistrate și note manuale de TVA la încasare pe 4428 — caz în care rulajul contului, așa cum e citit la calculul coeficientului K, poate include mișcări care nu au legătură cu gestiunea de mărfuri.
- Se presupune că aplicația separă automat cele două surse pe cont, deși acest lucru nu e confirmat de codul verificat.

## Ce face iConta.eu

La descărcarea lunară de gestiune, aplicația calculează automat TVA neexigibilă aferentă vânzărilor lunii proporțional cu cota medie de TVA din stoc — mecanism însoțit, în codul sursă, de o notă explicită a dezvoltatorilor („proporțional din 4427 e riscant"), motiv pentru care calculul se face pe baza soldurilor efective de stoc, nu pe o presupunere de cotă unică.

Totuși, rulajele de intrare/ieșire ale conturilor 371, 378 și 4428, folosite la calculul coeficientului K, sunt citite **fără un filtru de sursă** — spre deosebire de rulajul vânzărilor (707), care este filtrat explicit doar pe sursele de gestiune (case de marcat, stocuri, facturi de marfă). Dacă firma combină metoda global-valorică cu regimul de TVA la încasare pe același cont 4428, notele manuale ale celui de-al doilea regim se adună la rulajul citit de descărcarea de gestiune, iar coeficientul K poate ieși denaturat, fără ca aplicația să semnaleze automat amestecul. Este o atenționare tehnică de verificat de contabil înainte de validare, nu o eroare confirmată pentru toate firmele — dar o firmă care folosește ambele mecanisme trebuie să verifice manual soldul 4428 înainte de a valida nota de descărcare.

[iConta.eu](/)
