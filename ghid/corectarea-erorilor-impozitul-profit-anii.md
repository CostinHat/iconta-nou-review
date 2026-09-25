---
title: "Corectarea erorilor la impozitul pe profit din anii anteriori"
description: "Cum și în ce termen se poate corecta o declarație de impozit pe profit dintr-un an fiscal anterior, conform Codului de procedură fiscală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Corectarea erorilor la impozitul pe profit din anii anteriori

O eroare descoperită într-o declarație de impozit pe profit depusă cu ani în urmă (venituri omise, cheltuieli greșit încadrate, o deducere aplicată incorect) se poate corecta prin depunerea unei declarații rectificative — dar nu la infinit. Legea leagă dreptul de corectare de termenul general de prescripție a dreptului organului fiscal de a stabili creanțe fiscale.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative. [...] (5) Declarația de impunere nu poate fi depusă și nu poate fi corectată după anularea rezervei verificării ulterioare."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1), (3) și (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Termenul de prescripție la care face trimitere art. 105 este cel general, de 5 ani:

::: ghid-temei
„(1) Dreptul organului fiscal de a stabili creanțe fiscale se prescrie în termen de 5 ani, cu excepția cazului în care legea dispune altfel. (2) Termenul de prescripție a dreptului prevăzut la alin. (1) începe să curgă de la data de 1 iulie a anului următor celui pentru care se datorează obligația fiscală, dacă legea nu dispune altfel."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 110 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Coroborând cele două texte, rezultă regula practică: declarația D101 (impozit pe profit) pentru un an fiscal poate fi rectificată **până la împlinirea a 5 ani** de la data de 1 iulie a anului următor celui pentru care se datorează impozitul — de exemplu, o eroare din D101 aferentă anului 2023 poate fi corectată, în principiu, până la 1 iulie 2029.

Această regulă are însă două limite importante:

- **Anularea rezervei verificării ulterioare** (adică momentul în care organul fiscal a controlat definitiv acea perioadă și nu mai poate reveni asupra ei) blochează, de regulă, orice corectare ulterioară (art. 105 alin. 5) — chiar dacă termenul de 5 ani nu s-a împlinit încă.
- Există totuși excepții de la această blocare: corectarea rămâne posibilă „în situația în care corecția se datorează îndeplinirii sau neîndeplinirii unei condiții prevăzute de lege care impune corectarea bazei de impozitare [...]" sau atunci când o hotărâre judecătorească definitivă a modificat baza de impozitare pentru perioada respectivă (art. 105 alin. 6 lit. a) și b).

## Ce se greșește în practică

- Se presupune că orice eroare din trecut poate fi corectată oricând, ignorându-se atât termenul de prescripție de 5 ani, cât și efectul de blocare al anulării rezervei verificării ulterioare.
- Se calculează greșit momentul de la care începe să curgă prescripția — nu de la data depunerii declarației inițiale, ci de la **1 iulie a anului următor** celui pentru care se datorează impozitul.
- Se confundă corectarea unei declarații de impunere (supusă termenului de 5 ani, cu excepțiile de mai sus) cu corectarea unei declarații informative, care „poate fi corectată [...] indiferent de perioada la care se referă" (art. 105 alin. 2) — regimurile sunt diferite.
- Se depune declarația rectificativă fără să se verifice mai întâi dacă perioada respectivă a fost deja supusă unei inspecții fiscale finalizate cu anularea rezervei verificării ulterioare, caz în care rectificativa poate fi respinsă.

## Ce face iConta.eu

iConta.eu generează declarația D101 (impozit pe profit), inclusiv cu bifa de declarație rectificativă (câmpul `d_rec`), permițând refacerea și redepunerea unei declarații pentru o perioadă anterioară. Aplicația **nu verifică însă automat** dacă termenul de prescripție de 5 ani s-a împlinit sau dacă perioada respectivă a fost deja închisă printr-o inspecție fiscală cu anularea rezervei verificării ulterioare — aceste verificări, esențiale pentru a ști dacă o corecție mai e legal posibilă, rămân responsabilitatea utilizatorului sau a contabilului.

[iConta.eu](/)
