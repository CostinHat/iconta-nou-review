---
title: "Cum se declară o operațiune triunghiulară în D300?"
description: "Unde apar, în decontul de TVA, livrarea cu cod T a cumpărătorului revânzător și achiziția beneficiarului final dintr-o operațiune triunghiulară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară o operațiune triunghiulară în D300?

O operațiune triunghiulară implică trei firme din state membre diferite, dar bunurile circulă direct de la primul furnizor la beneficiarul final — firma din mijloc (cumpărătorul revânzător) nu se înregistrează în scopuri de TVA în statul de destinație, ci raportează operațiunea printr-un cod special. În D300, asta înseamnă rânduri distincte, în funcție de rolul jucat de firma românească în lanț.

## Temeiul legal

::: ghid-temei
„Rândul 1 - se înscriu informaţiile preluate din jurnalul de vânzări privind baza de impozitare pentru livrările intracomunitare de bunuri, scutite conform art. 294 alin. (2) lit. a) şi d) din Codul fiscal, şi pentru livrările intracomunitare de bunuri cu cod T, efectuate în cadrul unei operaţiuni triunghiulare de cumpărătorul revânzător, prevăzute la art. 276 alin. (5) din Codul fiscal... Rândul 5 - se înscriu informaţiile preluate din jurnalul de cumpărări privind baza de impozitare pentru achiziţiile intracomunitare de bunuri taxabile în România, precum şi baza de impozitare pentru achiziţiile de bunuri efectuate de către beneficiarul unei livrări ulterioare efectuate în cadrul unei operaţiuni triunghiulare, pentru care acesta este obligat la plata taxei conform art. 307 alin. (4) din Codul fiscal..."
— Instrucțiunile de completare a decontului de TVA (formular 300), aprobate prin OPANAF 174/2026 (sursă: anaf_surse/opanaf_174_2026_d300.txt)
:::

Cum se poziționează firma românească, în funcție de rolul din lanțul triunghiular:

- **Dacă firma românească e cumpărătorul revânzător** (verigă din mijloc, care cumpără dintr-un stat membru și revinde direct către un beneficiar dintr-un alt stat membru, fără ca bunurile să tranziteze România): livrarea ei intracomunitară, efectuată cu **codul T**, se raportează la **rândul 1** al decontului, alături de livrările intracomunitare scutite obișnuite.
- **Dacă firma românească e beneficiarul final** al livrării efectuate în cadrul unei operațiuni triunghiulare (deci bunurile ajung direct în România, iar firma e obligată la plata taxei prin taxare inversă, conform art. 307 alin. (4) din Codul fiscal): achiziția se raportează la **rândul 5**, împreună cu achizițiile intracomunitare de bunuri taxabile obișnuite.
- Codul T marchează, în evidența TVA a cumpărătorului revânzător, faptul că livrarea beneficiază de simplificarea specifică operațiunii triunghiulare — fără această mențiune, operațiunea riscă să fie tratată ca o achiziție intracomunitară urmată de o livrare intracomunitară obișnuită, cu obligații de înregistrare TVA suplimentare în statul de destinație.
- Rândurile aferente (1 și 5) preiau valorile direct din jurnalele de vânzări, respectiv de cumpărări, deci corectitudinea raportării în D300 depinde de marcarea corectă a operațiunii triunghiulare încă din momentul înregistrării facturii.

## Ce se greșește în practică

- Se raportează operațiunea ca o achiziție intracomunitară obișnuită urmată de o livrare intracomunitară obișnuită, fără marcarea codului T, pierzând astfel simplificarea specifică operațiunii triunghiulare.
- Se declară livrarea cumpărătorului revânzător la un rând generic din decont, fără să se verifice dacă instrucțiunile cer, pentru operațiunile cu cod T, încadrarea specifică la rândul dedicat.
- Se confundă rolul de cumpărător revânzător (verigă intermediară) cu cel de beneficiar final — cele două poziții generează raportări complet diferite în D300 (rândul 1, respectiv rândul 5).

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează decontul de TVA (D300) pe baza operațiunilor înregistrate în jurnalele de vânzări și cumpărări ale firmei, dar **nu automatizează** identificarea și marcarea automată a unei operațiuni triunghiulare cu cod T — contabilul trebuie să marcheze manual această natură a operațiunii la înregistrarea facturii, pentru ca aplicația să o încadreze corect în rândul corespunzător al decontului.

[iConta.eu](/)
