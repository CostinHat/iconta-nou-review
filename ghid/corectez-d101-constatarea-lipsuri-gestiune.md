---
title: "Cum corectez D101 după constatarea unor lipsuri de gestiune?"
description: "Procedura de corectare a declarației de impozit pe profit și tratamentul de TVA al lipsurilor din gestiune constatate la inventariere."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez D101 după constatarea unor lipsuri de gestiune?

O lipsă de gestiune descoperită după depunerea Declarației 101 (impozit pe profit) pune două probleme distincte: ajustarea TVA-ului dedus inițial la achiziția bunurilor lipsă și corectarea declarației de impozit pe profit dacă lipsa afectează rezultatul fiscal deja declarat.

## Temeiul legal

::: ghid-temei
„(6) În baza art. 304 alin. (1) lit. c) din Codul fiscal, persoana impozabilă realizează o ajustare pozitivă sau, după caz, trebuie să efectueze o ajustare negativă a taxei deductibile în situații precum: a) bunuri lipsă în gestiune din alte cauze decât cele prevăzute la art. 304 alin. (2) din Codul fiscal. În cazul bunurilor lipsă din gestiune care sunt imputate, sumele imputate nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA, indiferent dacă pentru acestea este sau nu obligatorie ajustarea taxei;"
— HG 1/2016 (Normele metodologice de aplicare a Codului fiscal), pct. 78 alin. (6) lit. a) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)

„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1), (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ordinea practică a corecției:

1. **Se stabilește dacă lipsa e imputabilă sau neimputabilă.** Dacă bunurile lipsă din gestiune se constată, la inventariere, din alte cauze decât cele exceptate de art. 304 alin. (2) din Codul fiscal (perisabilități în limitele legale, degradare calitativă dovedită, expirare, calamități etc.), TVA-ul dedus inițial la achiziția lor trebuie **ajustat** (art. 304 alin. 1 lit. c).
2. **Dacă lipsa e imputată unei persoane** (angajat, gestionar), suma imputată nu e considerată contravaloarea unei operațiuni în sfera TVA — deci nu se colectează TVA pe suma imputată, indiferent dacă TVA-ul dedus inițial trebuia sau nu ajustat.
3. **Impactul asupra impozitului pe profit** apare din valoarea contabilă a lipsei (cheltuiala cu bunurile lipsă, plus eventuala ajustare de TVA, dacă nu e recuperabilă de la gestionar) — dacă aceste sume nu au fost reflectate corect în rezultatul fiscal deja declarat prin D101, declarația se corectează.
4. **Corectarea propriu-zisă a D101** se face prin declarație rectificativă, conform regulii generale de la art. 105 din Codul de procedură fiscală — în termenul de prescripție de 5 ani (art. 110), fără o procedură specială diferită pentru acest caz.

## Ce se greșește în practică

- Se ajustează TVA-ul pentru lipsuri de gestiune care se încadrează, de fapt, în excepțiile de la art. 304 alin. (2) (de exemplu perisabilități în limitele legale) — caz în care ajustarea nu e obligatorie.
- Se colectează TVA pe suma imputată gestionarului, tratând-o greșit ca pe o vânzare — normele metodologice exclud explicit sumele imputate din sfera TVA.
- Se corectează doar decontul de TVA aferent lunii constatării, uitând că impactul asupra rezultatului fiscal anual cere, separat, o rectificativă la D101 dacă suma afectează un exercițiu financiar deja declarat.

## Ce face iConta.eu

Modulul de inventariere din iConta.eu (`core/inventariere.py`) înregistrează constatările de plusuri/minusuri la inventar, iar generatorul D101 (`core/d101.py`) calculează impozitul pe profit pe baza datelor contabile introduse pentru perioada respectivă. La data acestui ghid, aplicația **nu automatizează** distincția dintre lipsuri imputabile și neimputabile pentru ajustarea TVA (art. 304 alin. 6 lit. a) și nici generarea automată a unei declarații D101 rectificative — contabilul introduce manual ajustările rezultate din inventariere, iar pentru corecția declarației deja depuse folosește fluxul general de rectificare aplicabil oricărei declarații.

[iConta.eu](/)
