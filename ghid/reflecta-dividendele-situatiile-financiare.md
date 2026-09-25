---
title: "Cum se reflectă dividendele în situațiile financiare"
description: "Traseul contabil al dividendelor — de la repartizarea profitului până la datoria față de asociați — potrivit reglementărilor contabile românești și funcțiunii conturilor 129, 117 și 457."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se reflectă dividendele în situațiile financiare

Dividendele nu apar dintr-o singură înregistrare, ci parcurg un traseu în trei pași prin planul de conturi: de la profitul repartizat, prin rezultatul reportat, până la datoria efectivă față de acționari/asociați.

## Temeiul legal

::: ghid-temei
„Contul 457 «Dividende de plată» Cu ajutorul acestui cont se ține evidența dividendelor datorate acționarilor/asociaților corespunzător aportului la capitalul social. Contul 457 «Dividende de plată» este un cont de pasiv. În creditul contului 457 «Dividende de plată» se înregistrează: – dividendele datorate acționarilor/asociaților din profitul realizat în exercițiile precedente (117). [...] În debitul contului 457 «Dividende de plată» se înregistrează: – sumele achitate acționarilor/asociaților, reprezentând dividende datorate acestora (512, 531); – impozitul pe dividende (446)."
— OMFP nr. 1.802/2014, Capitolul 16, funcțiunea contului 457 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Practic, în situațiile financiare, dividendele parcurg următorul traseu contabil:

- La închiderea exercițiului, profitul net apare în contul **121 „Profit sau pierdere"**, apoi este preluat în **117 „Rezultatul reportat"**.
- Repartizarea profitului pentru dividende se face din rezultatul reportat (117), iar suma stabilită prin hotărârea adunării generale a acționarilor/asociaților ajunge în **457 „Dividende de plată"** — un cont de datorii, care reflectă exact obligația firmei față de asociați până la plata efectivă.
- Impozitul pe dividende, datorat bugetului de stat, se înregistrează separat, în contul **446 „Alte impozite, taxe și vărsăminte asimilate"**, pe seama sumei brute din 457.
- Dacă dividendele sunt repartizate în cursul exercițiului financiar (interimar), înainte de aprobarea situațiilor financiare anuale, ele se înregistrează inițial în contul **463 „Creanțe reprezentând dividende repartizate în cursul exercițiului financiar"**, urmând să fie regularizate pe seama contului 457 după aprobarea situațiilor financiare anuale.
- Dacă un asociat lasă dividendele cuvenite la dispoziția firmei, sumele se transferă din 457 în **455 „Sume datorate acționarilor/asociaților"**.

În bilanț, soldul contului 457 rămas neplătit la data raportării apare la datorii pe termen scurt, iar contul de profit și pierdere nu este afectat — dividendele sunt o repartizare a profitului deja realizat, nu o cheltuială a exercițiului.

## Ce se greșește în practică

- Se înregistrează dividendele direct ca o cheltuială a exercițiului curent, ceea ce distorsionează rezultatul — corect, ele diminuează rezultatul reportat (117), nu contul de profit și pierdere al perioadei.
- Se omite regularizarea dividendelor interimare (contul 463) după aprobarea situațiilor financiare anuale, lăsând soldul contului nejustificat la finalul anului.
- Se confundă impozitul pe dividende (înregistrat prin 446, ca datorie separată către bugetul de stat) cu suma netă efectiv datorată asociaților din 457 — cele două sunt componente distincte ale aceleiași repartizări.

## Ce face iConta.eu

iConta.eu are un motor dedicat pentru decontările cu asociații (conturile 455/456/457/463) care generează automat notele contabile de mai sus — atât pentru dividendele anuale (1171/457), cât și pentru cele interimare (463/456) — și calculează impozitul pe dividende la cota în vigoare la data distribuirii. Aplicația nu emite însă hotărârea AGA de aprobare a dividendelor; acel document rămâne în afara contabilității propriu-zise.

[iConta.eu](/)
