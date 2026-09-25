---
title: "Cum se contabilizează diferențele dintre raportul casei de marcat și terminalul POS?"
description: "Cum se tratează contabil o diferență între încasările pe card raportate de casa de marcat și cele confirmate de terminalul POS/bancă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează diferențele dintre raportul casei de marcat și terminalul POS?

Raportul Z al casei de marcat arată ce a fost vândut și încasat pe fiecare tip de plată, inclusiv card. Terminalul POS și extrasul bancar arată ce a fost efectiv decontat de bancă. Când cele două nu coincid — din cauza unei tranzacții eșuate, a unui comision interbancar sau a unei erori de operare — diferența trebuie clarificată, nu ignorată.

## Temeiul legal

::: ghid-temei
„În cazul documentelor financiar-contabile la care nu se admit corecturi, cum sunt cele pe baza cărora se primește, se eliberează sau se justifică numerarul, ori al altor documente pentru care normele de utilizare prevăd asemenea restricții, documentul întocmit greșit se anulează și se păstrează sau rămâne în carnetul respectiv."
— OMFP nr. 2.634/2015, Norme generale, pct. 15 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Practic, o diferență între raportul casei de marcat și decontul POS/bancar are, de regulă, una dintre aceste cauze:

- **Comisionul reținut de procesatorul de plăți** — suma decontată de bancă e mai mică decât valoarea raportată de casa de marcat, cu diferența egală cu comisionul de procesare (cont 627, cheltuieli cu serviciile bancare).
- **Tranzacții refuzate sau anulate la POS**, dar rămase înregistrate pe casa de marcat dintr-o eroare de operare — bonul greșit se anulează (nu se corectează prin editare), conform normei de mai sus.
- **Decalajul de decontare** — vânzarea prin card apare pe raportul Z în ziua vânzării, dar decontarea bancară efectivă poate ajunge în extras cu o zi sau două întârziere.
- Diferențele neexplicate rămân, temporar, pe un cont de clarificări (473), până la identificarea cauzei exacte.

## Ce se greșește în practică

- Se ajustează manual suma din raportul Z al casei de marcat ca să „se potrivească" cu extrasul bancar — documentele fiscale generate de AMEF nu admit astfel de corecturi directe.
- Se ignoră comisionul de procesare ca sursă normală de diferență, tratând orice neconcordanță ca pe o eroare care trebuie „reparată" în evidență.
- Se lasă diferența neexplicată în cont de clarificări la nesfârșit, fără investigarea cauzei reale (tranzacție refuzată, decalaj de decontare, comision).

## Ce face iConta.eu

iConta.eu importă raportul Z al aparatului de marcat electronic fiscal, cu defalcarea pe tipuri de plată (inclusiv card), și procesează separat extrasele bancare, detectând automat comisioanele bancare din descrierea liniilor de extras. Corelarea exactă, tranzacție cu tranzacție, între o vânzare pe card raportată de casa de marcat și decontarea ei efectivă din extrasul bancar rămâne, la data acestui ghid, o verificare manuală a contabilului.

[iConta.eu](/)
