---
title: "Impozitul pe profit pentru ONG cu activitate economică"
description: "Pas cu pas, cum se calculează impozitul pe profit datorat de un ONG pentru veniturile din activitatea economică, potrivit art. 15 Cod fiscal și normelor de aplicare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitul pe profit pentru ONG cu activitate economică

Când un ONG desfășoară și o activitate economică (vânzări, servicii, chirii), acea parte nu mai e automat scutită — se calculează un plafon de venituri neimpozabile suplimentare, iar tot ce depășește plafonul se impozitează cu cota standard. Normele metodologice la Codul fiscal descriu exact pașii de calcul.

## Temeiul legal

::: ghid-temei
„(1) Organizațiile nonprofit care obțin venituri, altele decât cele menționate la art. 15 alin. (2) din Codul fiscal, și care depășesc limita prevăzută la alin. (3) plătesc impozit pe profit pentru profitul impozabil corespunzător acestora. Determinarea rezultatului fiscal se face în conformitate cu prevederile titlului II din Codul fiscal. [...]
b) determinarea veniturilor neimpozabile prevăzute la art. 15 alin. (3) din Codul fiscal, prin parcurgerea următorilor pași: (i) calculul sumei în lei reprezentând echivalentul a 15.000 euro prin utilizarea cursului mediu de schimb valutar EUR/RON comunicat de Banca Națională a României pentru anul fiscal respectiv; (ii) calculul valorii procentului de 10% din veniturile prevăzute la lit. a); (iii) stabilirea veniturilor neimpozabile prevăzute la art. 15 alin. (3) din Codul fiscal ca fiind valoarea cea mai mică dintre sumele stabilite conform precizărilor anterioare;
c) stabilirea veniturilor neimpozabile prin adunarea sumelor de la lit. a) și b);
d) determinarea veniturilor impozabile prin scăderea din totalul veniturilor a celor de la lit. c), precum și a celorlalte venituri neimpozabile prevăzute de titlul II din Codul fiscal;"
— HG 1/2016, norma la art. 15 pct. 3 din Codul fiscal (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Concret, calculul impozitului pe profit datorat de un ONG cu activitate economică urmează acești pași:

1. Se însumează veniturile neimpozabile de la art. 15 alin. (2) — cotizații, donații, sponsorizări, fonduri publice etc.
2. Se calculează plafonul suplimentar de la alin. (3): minimul dintre **15.000 EUR** (la cursul mediu anual EUR/RON comunicat de BNR) și **10% din veniturile neimpozabile** de la pasul 1.
3. Din totalul veniturilor economice ale anului se scade acest plafon — ce rămâne e venitul impozabil.
4. Se scad cheltuielile deductibile aferente acestor venituri (art. 25 Cod fiscal) — obținându-se profitul impozabil.
5. Impozitul pe profit datorat = profitul impozabil × **16%** (cota prevăzută la art. 17 Cod fiscal).

## Ce se greșește în practică

- Se calculează plafonul de 15.000 EUR la cursul de la 31 decembrie, în loc de **cursul mediu anual BNR**, cerut explicit de normă — eroare care denaturează plafonul, de obicei în minus.
- Se aplică 16% direct pe veniturile economice brute, fără să se scadă mai întâi plafonul de scutire și cheltuielile deductibile aferente.
- Se omite depunerea declarației anuale de impozit pe profit (D101) atunci când veniturile economice depășesc plafonul de scutire, pe motiv că organizația e „ONG, deci scutită".

## Ce face iConta.eu

Calculatorul din ecranul „Operațiuni ONG" implementează exact pașii b)-c) de mai sus: primește veniturile economice ale anului, veniturile neimpozabile ale anului și cursul EUR, calculează plafonul ca minimul dintre 15.000 EUR × curs și 10% din veniturile neimpozabile, scade acest plafon din veniturile economice și estimează impozitul de 16% pe diferență, folosind rotunjire aritmetică (nu bancară) potrivit regulilor de rotunjire fiscală. **iConta.eu nu calculează** partea de la pasul 4 (cheltuielile deductibile aferente veniturilor economice, alocate potrivit unei metode raționale) și nu depune D101 — estimarea din aplicație acoperă doar plafonul de venit neimpozabil, nu întregul calcul al profitului impozabil. Astăzi, acest calculator e accesibil doar printr-un apel API direct, nefiind încă expus prin câmpuri în formularul din ecran.

[iConta.eu](/)
