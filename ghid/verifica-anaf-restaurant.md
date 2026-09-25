---
title: "Ce verifică ANAF la un restaurant?"
description: "Punctele specifice HoReCa urmărite la control: bacșișul evidențiat pe bonul fiscal, aparatul de marcat și raportul Z."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce verifică ANAF la un restaurant?

Restaurantele și barurile (CAEN 5610 și 5630) au, pe lângă obligațiile fiscale generale, un set de reguli specifice legate de bacșiș și de aparatele de marcat electronice fiscale (AMEF). Acestea sunt printre primele puncte verificate la un control HoReCa, pentru că au formulare stricte de evidențiere.

## Temeiul legal

::: ghid-temei
„Prin bacșiș se înțelege orice sumă de bani oferită în mod voluntar de client, în plus față de contravaloarea bunurilor livrate sau a serviciilor prestate de către operatorii economici care desfășoară activități corespunzătoare codurilor CAEN: 5610 - «Restaurante», 5630 - «Baruri și alte activități de servire a băuturilor». [...] Pentru operatorii economici prevăzuți la alin. (1), bacșișul încasat de la clienți se evidențiază pe bonul fiscal, indiferent de modalitatea de încasare a acestuia."
— OUG 28/1999, art. 2^3 alin. (1) și (2), introdus prin Legea 376/2022 art. I pct. 1 (sursă: anaf_surse/legea_376_2022_modificarea_completarea_ordonantei_urgenta_guvernului.txt)
:::

Ce urmărește efectiv inspectorul la un restaurant/bar:

- **Nota de plată cu rubrici de bacșiș** (0-15% din consumație sau sumă fixă), înmânată clientului înainte de bonul fiscal (art. 2^3 alin. 3) — lipsa ei e o abatere de sine stătătoare.
- **Bacșișul ca articol distinct pe bonul fiscal**, introdus în baza de date a AMEF sub denumirea „bacșiș" (art. 2^3 alin. 6), niciodată amestecat cu prețul produselor.
- **Interdicția de condiționare**: livrarea/prestarea nu poate fi condiționată de acordarea bacșișului (art. 2^3 alin. 4).
- **Distribuirea integrală a bacșișului către salariați**, pe evidență nominală (art. 2^3 alin. 8), cu impozit reținut la sursă la momentul distribuirii (art. 2^3 alin. 10) — nu poate rămâne venit al firmei (art. 2^3 alin. 9) și nu poate fi recalificat ca venit salarial (art. 2^3 alin. 10).
- **Raportul Z** al aparatului de marcat, ca dovadă a totalurilor zilnice pe cote de TVA și pe metode de plată.

## Ce se greșește în practică

- Bacșișul e trecut la vânzări de produse, ceea ce umflă baza de TVA a firmei pentru o sumă care legal nu e o livrare/prestare.
- Bacșișul încasat cu cardul rămâne în conturile de venituri ale firmei în loc să fie evidențiat pe un analitic distinct de datorii, gata de distribuire.
- Se omite reținerea la sursă a impozitului pe venit datorat de salariat la momentul distribuirii bacșișului (art. 115 CF, la care trimite art. 2^3 alin. 10).

## Ce face iConta.eu

iConta.eu are un motor dedicat pentru bacșiș HoReCa (`core/bacsis.py`), care generează notele contabile la încasare (461=462, cu contrapartida 5121/5311 pentru card/numerar) și la distribuire către salariați (reținere impozit 10% în contul 446, plată netă către salariați), conform Legii 376/2022 și art. 115 din Codul fiscal. Aplicația poate importa și Raportul Z direct din fișierul AMEF (format p7b sau XML, conform OPANAF 146/2018), extrăgând totalurile pe cote de TVA și pe metode de plată. Ce nu face: nu generează automat nota de plată cu rubricile de bacșiș pentru client — acel formular ține de configurarea aparatului de marcat, nu de aplicația de contabilitate.

[iConta.eu](/)
