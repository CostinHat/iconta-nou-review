---
title: "Ajustarea TVA la stocuri când firma devine neplătitoare"
description: "Dacă TVA dedusă la achiziția stocurilor trebuie ajustată atunci când firma iese din regimul de plătitor de TVA cu bunurile respective încă nevândute."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ajustarea TVA la stocuri când firma devine neplătitoare

Dacă o firmă a dedus TVA la achiziția unor bunuri de natura stocurilor și, înainte de a le vinde, iese din regimul de plătitor de TVA, dreptul de deducere aferent acelor bunuri nevândute se pierde — iar legea cere ajustarea taxei deja deduse, nu păstrarea ei.

## Temeiul legal

::: ghid-temei
„În condițiile în care regulile privind livrarea către sine sau prestarea către sine nu se aplică, deducerea inițială se ajustează în următoarele cazuri: [...] c) persoana impozabilă își pierde sau câștiga dreptul de deducere a taxei pentru bunurile mobile nelivrate și serviciile neutilizate."
— Legea nr. 227/2015 (Codul fiscal), art. 304 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **Stocurile intră sub art. 304**, nu sub art. 305 — acesta din urmă privește doar bunurile de capital (imobilizări), nu bunurile mobile de natura stocurilor, care au propria regulă de ajustare.
- **Momentul relevant e pierderea dreptului de deducere**, adică data de la care firma nu mai e înregistrată în scopuri de TVA — bunurile "nelivrate" la acel moment (rămase în stoc, nevândute) declanșează ajustarea.
- **Ajustarea funcționează în ambele sensuri**: și la pierderea, și la câștigarea ulterioară a dreptului de deducere (de exemplu la o reînregistrare în scopuri de TVA), art. 304 alin. (1) lit. c) acoperind simetric ambele situații.

## Ce se greșește în practică

- Se presupune că ajustarea TVA la ieșirea din regim se aplică doar mijloacelor fixe (bunuri de capital, art. 305), omițând stocurile, care au propriul temei la art. 304.
- Se ignoră ajustarea pentru stocurile aflate încă în gestiune la data pierderii calității de plătitor de TVA, considerând greșit că regularizarea se face doar la vânzarea efectivă ulterioară.
- Se confundă bunurile "distruse, pierdute sau furate", care sunt expres exceptate de la ajustare (art. 304 alin. (2) lit. a)), cu stocurile pur și simplu nevândute la momentul ieșirii din regim, care nu beneficiază de aceeași excepție.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu calculează automat ajustarea TVA la stocuri în cazul trecerii firmei de la statutul de plătitor la neplătitor de TVA — modulele de TVA (`core/tva_incasare.py` și altele din familia `tva_*`) gestionează regimuri speciale de TVA existente, dar identificarea stocurilor rămase nevândute la data ieșirii din regim și calculul ajustării aferente rămân o operațiune manuală a contabilului.

[iConta.eu](/)
