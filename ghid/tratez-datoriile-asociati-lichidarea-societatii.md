---
title: "Cum tratez datoriile față de asociați la lichidarea societății?"
description: "Trei tipuri de solduri (împrumut, dividend aprobat neplătit, dividend interimar neregularizat) trebuie stinse separat — partajul de lichidare nu le preia automat în calcul."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez datoriile față de asociați la lichidarea societății?

Înainte de partajul final din lichidare, firma poate avea mai multe tipuri de datorii deja înregistrate față de asociați — nu doar capitalul social și rezervele care se împart la sfârșit.

## Temeiul legal

::: ghid-temei
„Contabilitatea decontărilor între entitățile din cadrul grupului și cu acționarii/asociații cuprinde operațiunile care se înregistrează reciproc și în aceeași perioadă de gestiune [...], precum și decontările între acționari/asociați și entitate privind capitalul social, dividendele cuvenite acestora, alte decontări cu acționarii/asociați [...]." — OMFP 1802/2014, pct. 347
:::

În practică, o firmă poate ajunge la lichidare cu până la trei tipuri de solduri față de asociați, fiecare pe un cont diferit:

- **4551** — sume împrumutate de la asociat, nerestituite încă;
- **457** — dividende aprobate (anual) dar neplătite;
- **463** — dividende interimare distribuite în cursul anului, neregularizate încă prin situațiile financiare anuale.

Partajul propriu-zis de lichidare înregistrează restituirea capitalului social (1012=456, neimpozabilă la asociat) și calculează impozitul, la cota de dividend valabilă, doar pe câștigul din rezervele și profiturile rămase (106x/1171=456), cu plată netă către asociat — dar nu preia automat aceste trei solduri preexistente în formula lui. Ele rămân datorii separate, care trebuie stinse (împrumutul, prin restituire) sau clarificate (dividendele, prin plată sau regularizare) fie înaintea partajului, fie ca parte a plății datoriilor din etapa premergătoare acestuia.

## Ce se greșește în practică

Greșeala tipică e tratarea acestor solduri ca și cum ar dispărea automat odată cu declanșarea lichidării sau ca și cum ar fi incluse deja în calculul partajului. Nu sunt — fiecare tip de sold are propria notă contabilă de stingere, separată de partajul final.

## Ce face iConta.eu

Soldurile de pe 4551, 457 și 463 provin din funcționalitatea de decontări cu asociații (F039): nota de împrumut, respectiv nota de dividend/regularizare. Stingerea lor — restituirea împrumutului (4551=5121, cu dobânda și impozitul reținut, dacă e cazul) sau plata/regularizarea dividendelor — se face tot prin această funcționalitate. Lichidarea și radierea firmei sunt acoperite de o funcționalitate separată, cu propria logică de partaj al capitalului social și al rezervelor/profiturilor rămase; aceasta din urmă nu citește și nu stinge automat soldurile de pe 4551/457/463 — ele trebuie tratate explicit, înainte.

[iConta.eu](/)
