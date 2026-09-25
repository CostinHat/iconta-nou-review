---
title: "Trebuie rectificată D100 dacă rectific D205?"
description: "De ce D205 (impozitul reținut la sursă pe dividende) și D100 (obligațiile de plată la buget) sunt declarații independente, fiecare cu propriul mecanism de corectare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Trebuie rectificată D100 dacă rectific D205?

D205 și D100 par legate — ambele pot include impozitul reținut din dividende — dar sunt declarații distincte, cu obiect și mecanism de corectare separate. Corectarea uneia nu obligă automat la corectarea celeilalte.

## Temeiul legal

::: ghid-temei
„ART. 105 Corectarea declarației fiscale (1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Fiecare declarație are propriul temei și propriul mecanism de rectificare:

- **D100** („Declarație privind obligațiile de plată la bugetul de stat") e o declarație de **obligații de plată**, corectabilă prin formularul **710**, conform OPANAF 587/2016 (Anexele 2, 5 și 6).
- **D205** e o declarație **informativă**, privind impozitul reținut la sursă pe venituri plătite unor beneficiari (printre care dividendele către persoane fizice, la cota din art. 97 alin. (7) Cod fiscal) — corectarea ei nu se face prin formularul 710, ci printr-o redepunere proprie a formularului 205, marcată ca rectificativă.
- Cele două declarații au beneficiari și baze legale diferite: D205 acoperă dividendele plătite persoanelor **fizice** (art. 97 alin. (7) Cod fiscal), în timp ce poziția de dividende din D100 (cod obligație 150) privește dividendele plătite unor persoane **juridice** (art. 43 Cod fiscal) — nu e vorba de aceeași sumă declarată de două ori, ci de două obligații fiscale distincte, cu beneficiari diferiți.
- Din acest motiv, o corectare a D205 (de exemplu, o eroare de CNP sau de sumă la un beneficiar persoană fizică) nu are, prin ea însăși, niciun efect asupra unei obligații deja declarate corect în D100 — și invers. Fiecare declarație se corectează independent, dacă și numai dacă ea însăși conține o eroare.

## Ce se greșește în practică

- Se presupune că D100 și D205 „trebuie să se coreleze" automat, ca și cum ar reflecta aceeași sumă — de fapt, ele pot privi categorii diferite de beneficiari (persoane juridice vs. persoane fizice) ale aceluiași tip de venit (dividende).
- Se rectifică din prudență ambele declarații, deși doar una dintre ele conținea efectiv eroarea — fiecare rectificativă atrage propriile ei verificări și, eventual, propriile accesorii, dacă modifică o sumă de plată.
- Se ignoră că D205 și D100 au termene de depunere diferite (D205: ultima zi a lunii februarie a anului următor; D100: lunar/trimestrial, până la 25 a lunii următoare) — o corectare a uneia nu „mută" automat termenul celeilalte.

## Ce face iConta.eu

Acest ghid tratează raportul dintre două declarații distincte, nu o funcționalitate proprie a iConta.eu. Aplicația generează D100 și D205 ca fluxuri separate, fiecare din propriile date sursă (contul 457 pentru dividendele către asociați, la D205), și nu are un mecanism automat de corelare sau de avertizare între cele două — dacă una dintre ele conține o eroare, contabilul o identifică și o corectează separat, prin fluxul propriu al declarației respective.

[iConta.eu](/)
