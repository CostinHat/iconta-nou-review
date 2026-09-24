---
title: Cum închid vectorul fiscal înainte de radierea societății?
description: Nu există în iConta o funcționalitate de „închidere a vectorului fiscal" — la radiere, contul păstrează ultimul vector salvat, iar radierea propriu-zisă se face în procedura legală externă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum închid vectorul fiscal înainte de radierea societății?

Întrebarea presupune un pas care nu există în aplicație — vectorul fiscal nu se „închide" separat la radierea unei societăți, pentru că nu are, în iConta, o noțiune de status „radiat".

## Temeiul legal

::: ghid-temei
Radierea unei societăți urmează procedura legală de lichidare/dizolvare (OMFP 897/2015, Legea 31/1990 — art. 227 și următoarele, Legea 85/2014 pentru insolvență), depusă la ONRC/ANAF — un proces complet separat de evidența internă a vectorului fiscal din iConta, care nu are un temei legal propriu de „închidere".
:::

Cercetarea la sursă confirmă direct absența funcționalității: `core/vector_fiscal_api.py` are doar două funcții — `citeste` și `salveaza` — fără nicio noțiune de „închis" sau „radiat". Nici motorul de lichidare (`core/lichidare.py`, care implementează monografiile de valorificare active, încasare creanțe, plată datorii, rezultat pe cont 121, partaj) nu atinge deloc `firma_profil` sau vectorul fiscal.

Practic, asta înseamnă: radierea societății se face integral prin procedura legală externă (ONRC pentru dizolvare/lichidare, ANAF pentru scoaterea din evidențele fiscale) — nu printr-un pas din iConta. În aplicație, contul firmei rămâne, după radiere, cu ultimul vector fiscal valabil salvat; nu apare niciun câmp sau status distinct care să marcheze firma drept „radiată".

Dacă întrebarea vine din nevoia de a opri generarea declarațiilor pentru firma radiată, soluția practică nu e „închiderea vectorului", ci oprirea depunerii de declarații odată ce radierea a fost confirmată de ANAF — un pas administrativ, nu unul reflectat automat de aplicație.

## Ce se greșește în practică

- Se caută un buton sau o funcție de „închidere a vectorului" înainte de radiere — nu există, iar căutarea repetată consumă timp fără rezultat.
- Se presupune că vectorul fiscal trebuie modificat manual la radiere (de exemplu, golit sau resetat) — nu e necesar și nu are efect asupra procedurii legale de radiere.
- Se confundă radierea firmei la ONRC/ANAF cu un pas administrativ ce trebuie reflectat obligatoriu în iConta — cele două rămân, conform cercetării de față, complet separate.

## Ce face iConta.eu

Nu există, confirmat direct din cod, nicio funcționalitate de „închidere a vectorului fiscal" sau un status de firmă „radiată" în `firma_profil`. Radierea societății e un proces legal extern (ONRC/ANAF), pe care iConta nu îl automatizează sau reflectă printr-un câmp dedicat — contul firmei rămâne cu ultimul vector salvat.

[iConta.eu](/)
