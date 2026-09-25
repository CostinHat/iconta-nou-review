---
title: "Greșeala de a amesteca banii firmei cu cei personali"
description: "De ce cheltuielile plătite din contul firmei în interesul personal al asociatului sunt nedeductibile la impozitul pe profit, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeala de a amesteca banii firmei cu cei personali

„E firma mea, banii sunt tot ai mei" e raționamentul care stă în spatele uneia dintre cele mai frecvente greșeli contabile la firmele mici. Din punct de vedere fiscal, contul firmei și contul personal al asociatului sunt însă patrimonii distincte, iar folosirea banilor firmei în scop personal are consecințe fiscale directe.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: [...] cheltuielile făcute în favoarea acționarilor sau asociaților, altele decât cele generate de plăți pentru bunurile livrate sau serviciile prestate contribuabilului, la prețul de piață pentru aceste bunuri sau servicii;"
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (4) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă mecanismul de sancționare fiscală a amestecului de patrimonii:

- Orice cheltuială plătită din contul firmei, în beneficiul personal al asociatului/acționarului — facturi personale plătite din bani de firmă, cumpărături fără legătură cu activitatea, folosirea unui bun al firmei fără plată — este **nedeductibilă** la calculul impozitului pe profit.
- Excepția din text este strictă: rămân deductibile doar plățile efectuate către asociat/acționar **pentru bunuri livrate sau servicii prestate efectiv firmei, la prețul de piață** — adică atunci când asociatul e, de fapt, un furnizor sau prestator al firmei, nu doar beneficiar al banilor acesteia.
- Dincolo de nedeductibilitate, sumele folosite fără justificare economică pot fi recalificate de organul fiscal drept avantaje în natură sau, în anumite situații, dividende — cu impozitare suplimentară la nivelul asociatului, pe lângă pierderea deducerii la firmă.
- Distincția patrimonială contează și pentru răspunderea limitată a asociaților unui SRL — amestecul sistematic al banilor firmei cu cei personali poate submina chiar argumentul răspunderii limitate în caz de litigiu sau insolvență.

## Ce se greșește în practică

- Se plătesc cheltuieli personale ale asociatului direct din contul firmei, fără nicio justificare economică, și se înregistrează ca și cheltuieli deductibile ale acesteia.
- Se retrag bani din firmă „pentru nevoi personale", fără să fie tratați ca dividende, avans spre decontare sau împrumut către asociat, ci pur și simplu ca o cheltuială oarecare.
- Se presupune că orice plată către asociat e automat deductibilă, fără să se verifice dacă asociatul a livrat efectiv un bun sau a prestat un serviciu real firmei, la preț de piață.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul dedicat decontărilor cu asociații (`core/decontari_asociati.py`), cu funcții pentru înregistrarea împrumuturilor acordate/primite de la asociați (`nota_imprumut_asociat`) și a notelor de dividend (`core/dividende_curs.py`), care permit tratarea corectă — ca împrumut, avans sau distribuire de dividende — a sumelor puse la dispoziția sau retrase de asociat. Aplicația **nu clasifică automat** o cheltuială plătită din contul firmei drept „în favoarea asociatului" și nu o exclude din calculul impozitului pe profit doar pe baza contului bancar folosit — încadrarea corectă a fiecărei plăți rămâne o decizie a contabilului, pe baza documentelor justificative.

[iConta.eu](/)
