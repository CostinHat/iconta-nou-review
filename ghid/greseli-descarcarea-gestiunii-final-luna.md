---
title: Greșeli la descărcarea gestiunii la final de lună
description: Cele mai frecvente greșeli tehnice și contabile la descărcarea lunară de gestiune global-valorică și cum le evită iConta.eu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeli la descărcarea gestiunii la final de lună

Descărcarea de gestiune la metoda global-valorică (mărfuri ținute la preț cu amănuntul, conturile 371/378/4428) nu e o simplă notă contabilă — e rezultatul unui calcul cumulat pe tot exercițiul financiar. Tocmai de aceea, o greșeală mică la o lună se poate propaga în lunile următoare, pentru că fiecare lună pornește de la soldurile reale, nu de la o valoare presupusă.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (4)
:::

Formula legală e explicit **cumulată de la începutul exercițiului financiar**, nu calculată izolat pe luna curentă. Asta înseamnă că soldurile inițiale și rulajele conturilor 371, 378 și 4428 trebuie să fie corecte în fiecare lună anterioară pentru ca luna curentă să iasă corect — o eroare nedepistată la o lună se transmite mai departe.

## Ce se greșește în practică

- **Se rulează descărcarea fără să existe solduri inițiale introduse** pentru 371/378/4428, pe firme aflate la primul an de utilizare a aplicației — coeficientul K iese distorsionat pentru că numitorul sau numărătorul pornesc de la zero în loc de soldul real.
- **Se confundă „cumulat pe exercițiu" cu „doar luna curentă"** — coeficientul K se calculează mereu cumulat de la 1 ianuarie, dar vânzările (contul 707) care se descarcă sunt filtrate strict pe luna curentă. Amestecarea celor două noțiuni duce la interpretări greșite ale rezultatului.
- **Se validează nota de descărcare fără o verificare prealabilă a coeficientului K** — odată ce nota trece din starea de ciornă în starea validată, aplicația refuză explicit orice editare sau ștergere a ei.
- **Se ignoră riscul de poluare a contului 4428** atunci când firma combină metoda global-valorică cu regimul de TVA la încasare (ambele folosesc contul 4428, dar prin mecanisme diferite) — rulajele 371, 378 și 4428 citite la descărcarea lunară nu sunt filtrate pe sursă, spre deosebire de rulajul de vânzări (707), care este filtrat explicit. Dacă firma are ambele mecanisme active, notele manuale de TVA la încasare pot denatura coeficientul K fără ca aplicația să semnaleze acest lucru.
- **Se așteaptă o notă de descărcare și în lunile fără vânzări** — dacă nu există vânzări (707) în luna respectivă, nu e o eroare de aplicație: nu se generează nicio notă contabilă „pe zero".

## Ce face iConta.eu

Motorul de calcul (`core/stocuri.py`) calculează coeficientul K strict cumulat de la 1 ianuarie, folosind soldurile inițiale (din tabela de solduri inițiale, dacă există) și rulajele reale din notele contabile deja **validate**. Vânzările lunii sunt citite separat, filtrate pe sursele relevante (case de marcat/gestiune/facturi de marfă), doar pentru luna curentă. Dacă numitorul formulei ajunge zero sau negativ, sau dacă rezultatul ar da un cost al mărfurilor vândute negativ, aplicația refuză să calculeze și afișează o eroare explicită către contabil, în loc să întoarcă o valoare implicită greșită. Nota de descărcare propusă de aplicație rămâne ciornă până la validarea manuală a contabilului — exact acel moment fiind ultima ocazie de a verifica soldurile înainte ca nota să devină nemodificabilă.

[iConta.eu](/)
