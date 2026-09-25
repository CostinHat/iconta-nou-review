---
title: "Cum se înregistrează schimbul valutar la casa de schimb?"
description: "La ce curs se înregistrează în contabilitate o operațiune de schimb valutar, indiferent de cursul comercial practicat de casa de schimb."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează schimbul valutar la casa de schimb?

Contabilitatea nu urmărește cursul comercial afișat de casa de schimb — orice tranzacție în valută, inclusiv un schimb valutar, se înregistrează inițial la cursul BNR din ziua operațiunii, iar diferența față de cursul real practicat de casa de schimb devine venit sau cheltuială financiară distinctă.

## Temeiul legal

::: ghid-temei
„O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii."
— OMFP 1802/2014, pct. 319 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Mecanismul contabil complet, din normă:

- **Înregistrarea inițială** a operațiunii de schimb se face la cursul BNR al zilei (pct. 319), indiferent de cursul comercial cu care casa de schimb a cumpărat sau a vândut efectiv valuta.
- **Diferența dintre cursul BNR și cursul real practicat** de casa de schimb se recunoaște ca venit sau cheltuială din diferențe de curs valutar, în luna în care apare operațiunea: „Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial [...] trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar" (pct. 322 alin. 1).
- **Lichidarea unui depozit constituit în valută** urmează aceeași logică: „Lichidarea depozitelor constituite în valută se efectuează la cursul de schimb valutar comunicat de Banca Națională a României, de la data operațiunii de lichidare" (pct. 296 alin. 1) — regulă aplicabilă și schimbului valutar de disponibilități.

## Ce se greșește în practică

- Se înregistrează operațiunea de schimb valutar direct la cursul comercial oferit de casa de schimb, fără să se treacă întâi prin cursul BNR al zilei — pierzându-se astfel evidența separată a diferenței de curs (câștig sau pierdere reală din operațiunea de schimb).
- Se compensează „net" suma primită în lei cu suma în valută predată, fără să se evidențieze distinct venitul sau cheltuiala financiară din diferența de curs (pct. 322).
- Se confundă cursul BNR al zilei operațiunii cu cursul BNR al ultimei zile bancare a lunii, folosit doar pentru evaluarea disponibilităților rămase în sold la finele lunii (pct. 325), nu pentru tranzacțiile deja decontate.

## Ce face iConta.eu

iConta.eu are un modul dedicat cursului BNR (`core/curs_bnr.py`) folosit la contarea facturilor și operațiunilor în valută. Nu am identificat însă în cod o funcție specifică pentru operațiunea de schimb valutar la casa de schimb (cu evidențierea separată a diferenței dintre cursul comercial practicat și cursul BNR al zilei) — o astfel de operațiune, dacă apare, se înregistrează în prezent ca notă contabilă introdusă manual de contabil, cu aplicarea regulilor generale de curs valutar din aplicație.

[iConta.eu](/)
