---
title: "Greșeala de a nu înregistra veniturile din diferențe de curs"
description: "Ce se întâmplă când se omit veniturile din diferențe de curs valutar (cont 765) și de ce afectează atât rezultatul contabil, cât și baza impozabilă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu înregistra veniturile din diferențe de curs

O greșeală frecventă, mai des decât omisiunea pierderilor: se înregistrează diligent pierderile din curs valutar (665), dar se „uită" câștigurile (765) — mai ales la creanțe încasate la un curs favorabil sau la reevaluarea unor solduri care s-au apreciat. Rezultatul: un rezultat contabil subevaluat, fără justificare legală.

## Temeiul legal

::: ghid-temei
„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Textul legii nu face nicio distincție între venituri și cheltuieli din curs valutar — ambele „trebuie recunoscute", fără excepție pentru câștiguri.
- Regula de semn arată clar când apare un venit (765): la o **creanță** sau un **disponibil**, când cursul crește față de cel din evidență; la o **datorie**, când cursul scade.
- Omiterea sistematică a veniturilor din 765, păstrând doar cheltuielile din 665, subevaluează atât rezultatul contabil al perioadei, cât și, la impozit pe profit, baza de calcul (art. 19 alin. (1) Cod fiscal — rezultatul fiscal pornește de la rezultatul contabil complet, nu selectiv).
- La microîntreprinderi, omiterea veniturilor din 765 nu are efect direct asupra bazei impozabile lunare (acestea se scad oricum, conform art. 53), dar denaturează regularizarea din trimestrul IV, unde diferența netă cumulată se adaugă înapoi la bază.

## Ce se greșește în practică

- Se înregistrează notele de decontare doar când rezultă o pierdere, „din prudență", omițând sistematic cazurile favorabile.
- Se omite reevaluarea lunară a disponibilităților în valută (conturi bancare, casierie) atunci când cursul BNR a crescut față de luna anterioară — exact situația care generează venit, nu cheltuială.
- Se compensează manual, în afara contabilității, un câștig cu o pierdere din altă operațiune, în loc să se înregistreze ambele separat, pe conturile lor corecte.

## Ce face iConta.eu

Motorul `core/diferente_curs.py` nu face nicio distincție de tratament între câștig și pierdere — funcția `diferenta()` aplică aceeași regulă de semn indiferent de rezultat și generează nota cu linia pe 765 (venit) la fel de automat ca pe 665 (cheltuială), fie la decontare, fie la reevaluarea lunară. Riscul de omisiune descris mai sus nu vine din motorul de calcul, ci din faptul că operațiunile trebuie inițiate manual de contabil, din ecranul „Operațiuni speciale" — dacă o decontare sau o reevaluare nu e introdusă deloc în aplicație, niciun venit din 765 nu se generează, indiferent dacă era favorabil sau nu.

[iConta.eu](/)
