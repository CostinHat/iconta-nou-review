---
title: "Cum repar erorile de validare SAF-T?"
description: "Pașii oficiali de corectare a erorilor la transmiterea Declarației informative D406 (SAF-T), potrivit instrucțiunilor ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum repar erorile de validare SAF-T?

O eroare de validare la transmiterea SAF-T (Declarația informativă D406) nu se repară prin retrimiterea aceluiași fișier sau prin corecții parțiale — instrucțiunile ANAF descriu un ciclu clar: identifici eroarea, corectezi sursa, regenerezi integral fișierul și reiei procesul de la capăt.

## Temeiul legal

::: ghid-temei
„12. În situația în care, ca urmare a încercării de transmitere a Declarației D406, sunt primite mesaje de eroare/erori, utilizatorul trebuie să verifice cauza erorii prin analiza documentului generat de programul «Validator», fişierul SAFT.xml.err.txt. Odată identificată eroarea sau identificate erorile, se corectează problema semnalată de către utilizator şi se generează un nou fişier XML. Cu fişierul nou-obţinut se reiau paşii prezentaţi la pct. 5 şi 6, pentru validarea şi generarea Declaraţiei informative D406, începând cu pasul 1. Dacă nu s-au primit mesaje de eroare, declaraţia este pregătită pentru semnarea electronică şi transmitere.
[...]
24. În cazul în care un contribuabil/plătitor a primit o recipisă în care se menţionează că încărcarea s-a realizat cu erori, acesta este responsabil să corecteze respectivele erori în fişierul XML generat în format SAF-T şi să retransmită declaraţia reluând paşii descrişi la pct. 5 şi 6."
— OPANAF 1783/2021, Anexa — Instrucțiuni de completare și transmitere a Declarației informative D406, pct. 12 și pct. 24 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Pașii concreți, așa cum rezultă din instrucțiuni:

- **La respingerea în programul Validator**: se analizează fișierul `SAFT.xml.err.txt`, generat automat, care indică exact eroarea/erorile — pasul următor nu e retrimiterea fișierului, ci corectarea sursei de date și **regenerarea integrală** a fișierului XML.
- **La respingerea după încărcare** (recipisă cu mențiunea de erori): la fel, contribuabilul corectează fișierul XML și retransmite, reluând întregul proces de validare și generare de la pasul 1, nu doar zona afectată.
- **Nu sunt admise corecții parțiale**: dacă e nevoie de o declarație rectificativă (pentru corectarea unei erori materiale constatate ulterior, nu la transmitere), aceasta trebuie să cuprindă **toate informațiile din declarația inițială**, plus cele corectate — nu doar înregistrările sau câmpurile modificate.
- Declarațiile depuse ulterior primei declarații validate, pentru aceeași perioadă (lună/trimestru), sunt considerate **automat rectificative** — nu trebuie marcate manual ca atare.

## Ce se greșește în practică

- Se încearcă retransmiterea aceluiași fișier XML, neschimbat, presupunând că eroarea a fost temporară — instrucțiunile cer explicit corectarea sursei și regenerarea fișierului înainte de o nouă transmitere.
- Se transmit corecții parțiale (doar înregistrările sau câmpurile despre care se crede că au fost greșite) — regula interzice expres acest lucru: declarația rectificativă trebuie să cuprindă tot conținutul declarației inițiale, plus corecțiile.
- Se ignoră fișierul de erori (`SAFT.xml.err.txt`) generat de Validator, încercând să ghicească sursa problemei în loc să-l citească direct pentru localizarea exactă a erorii.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează fișierul XML pentru Declarația D406 (SAF-T) pe baza datelor contabile introduse, dar corectarea unei erori de validare semnalate de Validatorul ANAF rămâne un proces manual: identificarea cauzei în fișierul de erori, corectarea datei-sursă din contabilitate și regenerarea declarației.

[iConta.eu](/)
