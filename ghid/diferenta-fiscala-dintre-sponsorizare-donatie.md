---
title: "Care este diferența fiscală dintre sponsorizare și donație?"
description: "Regimul fiscal distinct al sponsorizării (Legea 32/1994), cu credit fiscal direct din impozitul pe profit, față de o donație obișnuită, fără acest regim special."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este diferența fiscală dintre sponsorizare și donație?

„Sponsorizare" și „donație" sunt uneori folosite interschimbabil în vorbirea curentă, dar fiscal sunt tratate complet diferit. Diferența nu ține de suma implicată sau de intenția firmei, ci de forma legală în care actul e făcut.

## Temeiul legal

::: ghid-temei
„cheltuielile de sponsorizare și/sau mecenat, acordate potrivit legii; contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea [...] și ale Legii bibliotecilor nr. 334/2002 [...], scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele: 1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri [...]; 2. valoarea reprezentând 20% din impozitul pe profit datorat."
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (4) lit. i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce diferență face, concret, forma actului:

- **Sponsorizarea**, făcută printr-un contract conform Legii nr. 32/1994, e o cheltuială **nedeductibilă** la calculul profitului impozabil (nu intră direct în cheltuielile deductibile), dar beneficiază de un **credit fiscal**: firma scade suma direct din **impozitul pe profit datorat**, în limita minimului dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat. Practic, e o reducere a impozitului de plată, nu o simplă cheltuială care scade baza impozabilă.
- O **donație obișnuită**, care nu e făcută printr-un contract de sponsorizare conform Legii nr. 32/1994 (de exemplu, un transfer de bani sau bunuri fără acest cadru contractual specific), **nu beneficiază de acest regim special** — Codul fiscal nu prevede pentru donații un credit fiscal echivalent celui de la art. 25 alin. (4) lit. i). Fără o astfel de prevedere expresă, o donație rămâne, de regulă, o cheltuială fără drept de deducere la calculul impozitului pe profit, judecată prin regula generală de la art. 25 alin. (1) (cheltuieli efectuate în scopul desfășurării activității economice) — un test pe care o donație pură, fără contraprestație și fără legătură cu activitatea firmei, îl trece greu.
- Condiția suplimentară pentru sponsorizările către entități fără scop lucrativ (inclusiv unități de cult): beneficiarul trebuie să fie înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale — fără această înscriere, chiar și o sponsorizare „de bună-credință" își pierde dreptul la creditul fiscal.
- Pentru **microîntreprinderi**, facilitatea fiscală a sponsorizării (creditul din impozit) a fost **eliminată** — sponsorizarea rămâne, la acest regim, o simplă cheltuială, fără credit fiscal și fără declarația D177 de redirecționare asociată regimului de profit.

## Ce se greșește în practică

- Se tratează orice transfer de bani către o organizație nonprofit ca „sponsorizare" cu drept la credit fiscal, fără verificarea existenței unui contract conform Legii nr. 32/1994 — fără acest contract, transferul e o simplă donație, fără regimul fiscal special.
- Se aplică regimul de credit fiscal al sponsorizării și la nivelul unei microîntreprinderi, ignorând faptul că această facilitate a fost eliminată pentru regimul micro — sponsorizarea rămâne, acolo, doar o cheltuială obișnuită.
- Se ignoră condiția de înscriere a beneficiarului în registrul entităților eligibile la data contractului — o sponsorizare către o entitate care nu figurează în acest registru la momentul respectiv nu dă drept la credit fiscal, indiferent de scopul ei.

## Ce face iConta.eu

La data acestui ghid, motorul de sponsorizări din iConta.eu (`core/sponsorizari.py`) calculează plafonul de credit fiscal — minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit — și marchează explicit că, pentru microîntreprinderi, facilitatea e eliminată, tratând sponsorizarea acolo ca simplă cheltuială. Pentru donații obișnuite, fără contract de sponsorizare conform Legii nr. 32/1994, aplicația nu aplică niciun credit fiscal, tratându-le ca orice altă cheltuială introdusă manual.

[iConta.eu](/)
