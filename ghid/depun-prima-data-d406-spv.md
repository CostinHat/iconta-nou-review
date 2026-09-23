---
title: "Cum depun prima dată D406 în SPV"
description: Pașii oficiali pentru prima transmitere a D406 în Spațiul Privat Virtual — generare XML, validare, PDF semnat electronic și transmitere — potrivit Anexei 3 la OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum depun prima dată D406 în SPV

Procedura tehnică de depunere e aceeași indiferent dacă e prima D406 sau a zecea — diferă doar statutul declarației (inițială, la prima depunere pentru o perioadă) și, eventual, perioada de grație aplicabilă.

## Temeiul legal

::: ghid-temei
„Transmiterea Declaraţiei informative D406 se poate face de către contribuabilii/plătitorii cu obligaţia de depunere, începând cu prima zi calendaristică a lunii următoare perioadei pentru care obligaţia devine activă, până la data-limită de depunere - ultima zi a lunii care urmează perioadei pentru care se face raportarea." — OPANAF nr. 1783/2021, Anexa 3, pct. 13.

„Prima Declaraţie informativă D406 validată, depusă pentru o lună sau un trimestru de către un contribuabil/plătitor este considerată declaraţie iniţială." — Anexa 3, pct. 18.
:::

## Pașii, în ordine

Procedura descrisă de ordin (Anexa 3, pct. 1-9) urmează patru pași:

1. **Generarea fișierului XML**, conform schemei oficiale.
2. **Validarea** cu instrumentul oficial ANAF, denumit în ordin „Validator" (Soft J).
3. **Generarea PDF-ului**, cu fișierul XML atașat, semnat electronic.
4. **Transmiterea**, prin Spațiul Privat Virtual (SPV) sau prin e-guvernare.ro.

Pentru prima depunere a unei firme pentru o perioadă dată, declarația devine automat inițială — nu trebuie marcată separat ca atare. Termenul-limită e ultima zi calendaristică a lunii următoare perioadei raportate, dar transmiterea poate fi făcută oricând începând cu prima zi a acelei luni următoare (Anexa 3, pct. 13) — nu trebuie așteptată ultima zi.

## Ce se greșește în practică

- Se încearcă transmiterea fișierului XML brut, nesemnat, direct în SPV — procedura cere generarea PDF-ului cu XML-ul atașat și semnătura electronică, nu doar XML-ul.
- Se sare peste pasul de validare cu instrumentul oficial, iar eventualele erori structurale sunt descoperite abia după transmitere.
- Se presupune că prima depunere trebuie făcută chiar în prima zi posibilă — termenul-limită e ultima zi a lunii următoare, nu prima.

## Ce face iConta.eu

iConta.eu generează fișierul XML din evidența contabilă și îl validează cu DUKIntegrator — instrumentul de validare structurală folosit și de ANAF — înainte ca fișierul să fie pus la dispoziție pentru transmitere. Pasul final, de transmitere efectivă prin SPV, rămâne o acțiune separată, cu certificatul digital al contribuabilului sau al împuternicitului.

[iConta.eu](/)
