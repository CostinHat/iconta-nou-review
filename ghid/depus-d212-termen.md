---
title: "Ce fac dacă am depus D212 după termen?"
description: "Nedepunerea la termen a D212 e contravenție (amendă 50-500 lei), iar ANAF poate stabili din oficiu obligațiile prin estimare — depunerea imediată, chiar tardivă, limitează ambele riscuri."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am depus D212 după termen?

Depunerea cu întârziere nu anulează obligația — dimpotrivă, declanșează două riscuri distincte: o contravenție cu amendă și, dacă întârzierea se prelungește, posibilitatea ca organul fiscal să stabilească el însuși, prin estimare, obligațiile datorate.

## Temeiul legal

::: ghid-temei
„În cazul persoanelor fizice nedepunerea la termenele prevăzute de lege a declarațiilor de venit, precum și a declarației unice privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice constituie contravenție și se sancționează cu amendă de la 50 lei la 500 lei."
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Organul fiscal stabilește baza de impozitare și creanța fiscală aferentă, prin estimarea rezonabilă a bazei de impozitare, folosind orice probă și mijloc de probă prevăzute de lege, ori de câte ori acesta nu poate determina situația fiscală corectă."
— Legea 207/2015, art. 106 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt), coroborat cu art. 107 (stabilirea din oficiu ca urmare a nedepunerii declarației de impunere)
:::

Pașii recomandați odată ce termenul a fost depășit:

- Depune declarația cât mai repede — cu cât întârzierea e mai mare, cu atât crește riscul ca ANAF să treacă la stabilirea din oficiu (art. 107), pe o bază estimată, de regulă mai puțin favorabilă decât venitul real.
- Calculează și achită sumele datorate (impozit, CAS, CASS) — depunerea cu întârziere nu suspendă curgerea dobânzilor și penalităților de întârziere aferente sumelor neplătite la termen.
- Ține cont că amenda pentru nedepunere (50-500 lei) e independentă de eventualele penalități de întârziere la plată — sunt sancțiuni cu temeiuri diferite.
- Dacă întârzierea a apărut din cauza unei erori tehnice la depunerea electronică inițială, verifică dacă se încadrează în excepția de la art. 103 alin. (5) din Legea 207/2015, care poate păstra data depunerii inițiale.

## Ce se greșește în practică

- Se amână depunerea suplimentar, „până se lămurește situația" — orice zi în plus mărește riscul unei stabiliri din oficiu, mai greu de contestat decât o declarație depusă chiar și tardiv.
- Se presupune că amenda contravențională se aplică automat, indiferent de circumstanțe — constatarea și aplicarea sancțiunii țin de organul fiscal, dar depunerea imediată rămâne cea mai bună apărare.
- Se ignoră dobânzile și penalitățile de întârziere la plata sumelor datorate, concentrându-se doar pe amenda pentru nedepunere.

## Ce face iConta.eu

D212 e o declarație manuală în iConta.eu (`core/d212.py`) — aplicația nu urmărește calendarul de scadență și nu semnalează contribuabilului că termenul de 25 mai a fost depășit. Motorul de calcul (`core/d212_engine.py`, `core/rip_api.py`) poate produce oricând fișa de calcul CAS/CASS/impozit pentru veniturile anilor verificați (2025, 2026), inclusiv pentru o depunere tardivă, dar nu calculează dobânzile sau penalitățile de întârziere aferente plății cu întârziere — acestea rămân în sarcina evidenței fiscale ținute de contabil.

[iConta.eu](/)
