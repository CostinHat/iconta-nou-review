---
title: "Inventarul la finele lunii la amănunt: metoda corectă"
description: "De ce la finele lunii, la metoda global-valorică, procedura corectă este descărcarea de gestiune, nu un inventar fizic — și când are loc, de fapt, inventarul."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Inventarul la finele lunii la amănunt: metoda corectă

Titlul cere „metoda corectă" de inventar la finele lunii, la comerțul cu amănuntul. Pe baza dosarului tehnic verificat, lucrurile trebuie separate clar: ce se întâmplă lunar la metoda global-valorică **nu este un inventar fizic**, ci o descărcare de gestiune (un calcul contabil). Inventarul fizic propriu-zis este un proces distinct.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 291 alin. (5): „Inventarul intermitent nu se utilizează în comerțul cu amănuntul în situația în care se aplică metoda global-valorică."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Legea interzice explicit inventarul intermitent (o metodă de evidență contabilă în care stocul se calculează periodic, nu permanent) la comerțul cu amănuntul care aplică metoda global-valorică. Cu alte cuvinte, contul 371 „Mărfuri" trebuie ținut **permanent**, cu intrări și ieșiri înregistrate continuu — nu reconstituit lunar printr-o numărătoare fizică ce ar ține loc de evidență contabilă.

Ce se întâmplă efectiv la finele lunii este calculul coeficientului de repartizare (pct. 286 alin. 4) și generarea notei de descărcare (607/378/4428), pe baza rulajelor deja înregistrate — nu o numărătoare a mărfii din raft.

## Ce se greșește în practică

- Confuzia dintre „descărcarea de gestiune" (un calcul contabil lunar, obligatoriu la metoda global-valorică) și „inventarul fizic" (o numărătoare periodică a stocului, cu scop de verificare).
- Încercarea de a înlocui rulajele contabile permanente cu un inventar intermitent la finele fiecărei luni — interzis explicit de pct. 291 alin. (5) pentru cei care aplică metoda global-valorică.

## Ce face iConta.eu

Funcția `descarca_luna` (`core/stocuri_api.py`) generează automat, ca ciornă, nota lunară de descărcare de gestiune, pe baza rulajelor cumulate de la 1 ianuarie — nu pe baza unei numărători fizice. Pentru inventarul fizic propriu-zis (plus/minus constatate prin numărătoare), conform cercetării care stă la baza acestui ghid, aplicația tratează diferențele **doar pe perechea de conturi 371 ↔ 607**, la valoarea de înregistrare, fără nicio distincție sau repartizare pe conturile 378 (adaos) sau 4428 (TVA neexigibilă) pentru gestiunile ținute global-valoric. Nu există în cod niciun parametru sau ramură care să trateze diferit un plus/minus la un articol dintr-o gestiune global-valorică față de una simplă la preț de achiziție — o limitare de reținut la interpretarea rezultatului unui inventar fizic într-o astfel de gestiune.

[iConta.eu](/)
