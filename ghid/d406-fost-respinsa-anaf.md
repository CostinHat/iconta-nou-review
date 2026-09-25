---
title: "Ce faci dacă D406 a fost respinsă de ANAF?"
description: "Procedura de corectare a unei declarații D406 (SAF-T) respinse la transmitere: identificarea erorii din fișierul de validare, corectarea și regenerarea fișierului XML."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă D406 a fost respinsă de ANAF?

Spre deosebire de alte declarații, D406 (fișierul standard de control fiscal, SAF-T) trece printr-un proces de validare tehnică strict înainte de a fi acceptată: dacă fișierul XML nu respectă structura sau conține erori de conținut, transmiterea este respinsă, iar contribuabilul primește mesaje de eroare pe care trebuie să le analizeze punctual.

## Temeiul legal

::: ghid-temei
„12. În situația în care, ca urmare a încercării de transmitere a Declarației D406, sunt primite mesaje de eroare/erori, utilizatorul trebuie să verifice cauza erorii prin analiza documentului generat de programul «Validator», fișierul SAFT.xml.err.txt. Odată identificată eroarea sau identificate erorile, se corectează problema semnalată de către utilizator și se generează un nou fișier XML. [...] 16. Formularele și fișierele SAF-T atașate pentru care nu este validată identitatea sunt respinse."
— OPANAF nr. 1.783/2021, Instrucțiuni de completare și transmitere D406 (SAF-T), pct. 12 și pct. 16 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Procedura de corectare, așa cum rezultă din instrucțiuni:

- Prima verificare este întotdeauna **fișierul `SAFT.xml.err.txt`**, generat de programul Validator — el conține exact cauza respingerii, camp cu câmp, și nu mesajul generic din portal.
- După identificarea erorii, se **corectează problema** direct la sursa datelor (contabilitate, master data) și se **regenerează** un fișier XML nou — nu se editează manual XML-ul respins, ci se reia întregul proces de generare.
- O cauză distinctă de respingere, separată de erorile de conținut, este **neconcordanța de identitate**: fișierul e respins dacă identitatea contribuabilului/plătitorului pentru care se depune declarația nu corespunde cu identitatea cu care utilizatorul e înrolat la ANAF pentru depunerea declarațiilor electronice.

## Ce se greșește în practică

- Se încearcă retransmiterea aceluiași fișier XML respins, fără corectarea cauzei semnalate în `SAFT.xml.err.txt` — fișierul va fi respins din nou, cu același mesaj de eroare.
- Se ignoră verificarea identității cu care utilizatorul e înrolat la ANAF, presupunând că respingerea se datorează exclusiv unei erori de conținut, deși cauza poate fi o simplă neconcordanță de certificat/identitate la depunere.
- Se transmite declarația chiar în ultima zi a termenului legal (ultima zi a lunii următoare perioadei de raportare), fără marjă pentru un al doilea ciclu de corectare-retransmitere, dacă prima încercare e respinsă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează fișierul XML pentru D406 cu un set extins de validări interne, aplicate **înainte** de transmitere (`core/d406.py`) — de exemplu, respinge la generare conturile care nu se regăsesc în planul de conturi declarat al firmei sau unitățile de măsură neconforme, tocmai pentru a evita o respingere ulterioară de la validatorul oficial ANAF. Dacă totuși ANAF respinge declarația la transmitere efectivă, corectarea pe baza mesajului de eroare primit și retransmiterea rămân un pas manual, realizat de contabil în afara aplicației.

[iConta.eu](/)
