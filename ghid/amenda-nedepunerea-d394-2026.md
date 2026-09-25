---
title: "Amenda pentru nedepunerea D394 în 2026"
description: "Amenda pentru nedepunerea D394 rămâne cea din Codul de procedură fiscală, art. 336: 1.000-5.000 lei pentru contribuabili mijlocii și mari, 500-1.000 lei pentru ceilalți, inclusiv persoane fizice."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amenda pentru nedepunerea D394 în 2026

D394 nu are o amendă proprie, numită explicit în lege — se sancționează prin regula generală a declarațiilor informative din Codul de procedură fiscală, cu cuantumuri diferite după mărimea contribuabilului.

## Temeiul legal

::: ghid-temei
„19. declarație informativă - actul întocmit de contribuabil/plătitor referitor la orice informații în legătură cu impozitele, taxele și contribuțiile sociale, bunurile și veniturile impozabile, precum și în legătură cu evidențele contabile și fiscale, inclusiv fișierul standard de control fiscal, dacă legea prevede declararea acestora, altele decât cele prevăzute la pct. 18."
— Legea 207/2015 (Codul de procedură fiscală), art. 1 pct. 19 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„neîndeplinirea de către contribuabil/plătitor la termen a obligaţiilor de declarare prevăzute de lege, a bunurilor şi veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuţiilor şi a altor sume, precum şi orice informaţii în legătură cu impozitele, taxele, contribuţiile, bunurile şi veniturile impozabile, dacă legea prevede declararea acestora"
— Legea 207/2015, art. 336 alin. (1) lit. b) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii şi mari şi cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice, precum şi pentru persoanele fizice, în cazul săvârşirii faptei prevăzute la alin. (1) lit. a), b) şi i) - m)"
— Legea 207/2015, art. 336 alin. (2) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Cum se leagă textele: D394 e o declarație creată prin ordin ANAF (OPANAF 2194/2025), sub temeiul general al art. 59 din Codul de procedură fiscală, care se încadrează în definiția de la art. 1 pct. 19 — „declarație informativă". Nedepunerea ei la termen intră sub contravenția de la art. 336 alin. (1) lit. b), iar amenda aplicabilă e cea de la alin. (2) lit. d):

- **1.000–5.000 lei** — pentru persoanele juridice încadrate în categoria contribuabililor mijlocii și mari.
- **500–1.000 lei** — pentru celelalte persoane juridice, precum și pentru persoanele fizice.

Nu am găsit în corpusul legal disponibil un cuantum specific, numit explicit „D394", separat de această încadrare generală — este o interpretare cu temei, bazată pe definiția explicită de la pct. 19, nu un text care numește literal „D394".

## Ce se greșește în practică

- Se caută o amendă specifică „pentru D394" în text, numită ca atare — nu există; sancțiunea vine din regula generală a declarațiilor informative.
- Se presupune un cuantum unic pentru toți contribuabilii — de fapt diferă după categoria contribuabilului (mijlociu/mare vs. restul).
- Se ignoră faptul că D394 se depune „inclusiv dacă în această perioadă nu au fost realizate operațiuni" — deci nedepunerea unei declarații „pe zero" e sancționabilă la fel ca a uneia cu operațiuni.

## Ce face iConta.eu

Termenul de depunere D394 (ziua 30 a lunii următoare, cu excepția lunii ianuarie) e urmărit intern (`core/scadente.py`), iar semaforul de conformare fiscală al aplicației compară declarațiile datorate, din vectorul fiscal al firmei, cu cele depuse.

**iConta.eu nu aplică și nu calculează amenzi** — acestea sunt stabilite exclusiv de organul fiscal, în cazul constatării contravenției. Aplicația generează declarația și o validează local prin validatorul oficial ANAF (DUK), dar depunerea efectivă, la termen sau cu întârziere, rămâne manuală, prin portalul SPV.

[iConta.eu](/)
