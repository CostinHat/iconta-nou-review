---
title: "Cum se contabilizează un discount suportat parțial de magazin și parțial de marketplace?"
description: "Principiul contabil al reducerilor comerciale înscrise pe factură, aplicat situației în care o reducere e împărțită între vânzător și platforma de marketplace."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează un discount suportat parțial de magazin și parțial de marketplace?

Pe platformele de tip marketplace apare frecvent situația în care o promoție (un discount la produs) e finanțată din două surse: o parte din reducere e suportată de vânzător, o parte de operatorul platformei, ca stimulent de vânzări. Contabilitatea nu tratează cele două componente la fel — doar reducerea efectiv suportată de vânzător îi ajustează costul/venitul propriu.

## Temeiul legal

```
::: ghid-temei
„76. - (1) Reducerile comerciale acordate de furnizor și înscrise pe factura de achiziție ajustează în sensul reducerii costul de achiziție al bunurilor. Atunci când achiziția de produse și primirea reducerii comerciale sunt tratate împreună, reducerile comerciale primite ulterior facturării ajustează, de asemenea, costul de achiziție al bunurilor."
— OMFP nr. 1.802/2014 pentru aprobarea reglementărilor contabile privind situațiile financiare anuale individuale și consolidate, pct. 76 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::
```

Ce rezultă, aplicat la un discount împărțit între magazin și marketplace:

- **Regula generală e simplă în esență:** reducerile comerciale ajustează costul de achiziție/venitul din vânzare aferent operațiunii pe care o vizează — principiu care se aplică simetric, fie că vorbim despre furnizor-cumpărător, fie despre vânzător-client final.
- **Partea de discount suportată de vânzător** (magazin) e o reducere comercială acordată de el, care îi diminuează venitul din vânzare — se scade din prețul de vânzare, nu se înregistrează ca o cheltuială separată.
- **Partea de discount suportată de marketplace** nu e o reducere acordată de vânzător, ci un stimulent/o compensație pe care marketplace-ul o oferă vânzătorului pentru participarea la promoție — din perspectiva vânzătorului, aceasta e, de regulă, o sumă de încasat de la marketplace (un venit sau o compensare a comisionului acestuia), distinctă de vânzarea către client.
- Principiul fondului economic peste forma juridică (pct. 57 din același act) cere ca operațiunea să fie înregistrată așa cum se produce în realitate: dacă marketplace-ul rambursează efectiv vânzătorului partea lui de discount, acea sumă nu poate fi tratată ca simplă reducere de vânzare a magazinului, pentru că din perspectiva magazinului nu reprezintă o pierdere de venit, ci o compensație primită.

## Ce se greșește în practică

- Se înregistrează întregul discount ca reducere comercială a vânzătorului, deși o parte din el e finanțată de marketplace și ar trebui recunoscută separat, ca sumă de recuperat/încasat de la platformă.
- Se ignoră documentul justificativ emis de marketplace (raport de comision, notă de compensare) care ar trebui să stea la baza înregistrării separate a părții lui de discount.
- Se compensează direct, fără înregistrare distinctă, suma primită de la marketplace cu comisionul datorat acestuia — încălcând principiul necompensării (pct. 56 din OMFP 1802/2014), care cere ca elementele de venituri/cheltuieli sau creanțe/datorii să fie înregistrate distinct, nu nete.

## Ce face iConta.eu

La data acestui ghid, nu a fost găsită în `core/` nicio funcționalitate dedicată specific tranzacțiilor de tip marketplace sau împărțirii automate a unui discount între vânzător și platformă — aplicația oferă evidența contabilă generală (facturare, note contabile, TVA), pe baza căreia contabilul înregistrează manual, separat, partea de discount a magazinului și suma de compensare primită de la marketplace, conform documentelor emise de fiecare parte.

[iConta.eu](/)
