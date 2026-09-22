---
title: Cum tratez fiscal un client intrat în insolvență?
description: Insolvența unui client declanșează separat dreptul la deducere 100% a ajustării de creanță (impozit pe profit, la faliment declarat) și dreptul la ajustarea bazei de TVA (la data hotărârii de faliment sau confirmării planului de reorganizare) — două regimuri distincte, fiecare cu condițiile lui.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum tratez fiscal un client intrat în insolvență?

Când un client intră în insolvență sau faliment, se declanșează în paralel două regimuri fiscale independente: unul la impozitul pe profit (deducerea ajustării pentru creanța neîncasată) și unul la TVA (ajustarea bazei de impozitare pentru TVA colectată și neîncasată). Cele două au temeiuri legale diferite, condiții diferite și momente diferite de aplicare — nu se confundă și nu se aplică automat unul din celălalt.

## Temeiul legal

::: ghid-temei
"ajustările pentru deprecierea creanțelor înregistrate potrivit reglementărilor contabile aplicabile,
în limita unui procent de 100% din valoarea creanțelor, altele decât cele prevăzute la lit. d), e),
f), h) și i), dacă creanțele îndeplinesc cumulativ următoarele condiții:
1. sunt deținute la o persoană juridică asupra căreia este declarată procedura de deschidere a
falimentului, pe baza hotărârii judecătorești prin care se atestă această situație, sau la o persoană
fizică asupra căreia este deschisă procedura de insolvență pe bază de: – plan de rambursare a
datoriilor; – lichidare de active; – procedură simplificată;
2. nu sunt garantate de altă persoană;
3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului;"

"în cazul în care contravaloarea bunurilor livrate sau a serviciilor prestate nu se poate încasa ca
urmare a intrării în faliment a beneficiarului sau ca urmare a punerii în aplicare a unui plan de
reorganizare admis și confirmat printr-o sentință judecătorească, prin care creanța creditorului este
modificată sau eliminată. Ajustarea este permisă începând cu data pronunțării hotărârii judecătorești
de confirmare a planului de reorganizare, iar, în cazul falimentului beneficiarului, începând cu data
sentinței sau, după caz, a încheierii, prin care s-a decis intrarea în faliment [...] Ajustarea se
efectuează în termen de 5 ani de la data de 1 ianuarie a anului următor [...]"

"h) pierderile înregistrate la scoaterea din evidență a creanțelor, pentru partea neacoperită de
provizion, potrivit art. 26, precum și cele înregistrate în alte cazuri decât următoarele: [...]
2. procedura de faliment a debitorilor a fost închisă pe baza hotărârii judecătorești; [...]"
:::

## Trei momente, trei tratamente

1. **La deschiderea procedurii (hotărâre judecătorească de faliment sau insolvență declarată)** — ajustarea contabilă pentru deprecierea creanței devine deductibilă 100% la impozitul pe profit (art. 26 alin. (1) lit. j)), cu condiția ca aceeași creanță să nu fie garantată și să nu fie la un afiliat.
2. **Tot atunci (sau la confirmarea planului de reorganizare)** — se poate ajusta baza de impozitare a TVA pentru contravaloarea neîncasată, în termen de 5 ani de la 1 ianuarie a anului următor datei hotărârii (art. 287 lit. d)). Acesta e un regim separat, cu termen și mecanism propriu, care nu depinde de deducerea de la impozitul pe profit.
3. **La închiderea procedurii de faliment prin hotărâre judecătorească** — dacă mai rămâne o parte din creanță neacoperită de ajustare, aceasta devine deductibilă la scoaterea din evidență (art. 25 alin. (4) lit. h) pct. 2).

## Ce se greșește în practică

- Se face ajustarea de TVA automat, doar pentru că firma a înregistrat deja 100% ajustare la impozitul pe profit — cele două nu sunt condiționate una de cealaltă, fiecare are propriile condiții și proceduri.
- Se așteaptă termenul de 270 de zile (specific impozitului pe profit, pentru creanțe negarantate/neafiliate, altă situație decât falimentul) înainte de a acționa, deși la faliment declarat deducerea de 100% e disponibilă imediat, fără prag de zile.
- Se omite ajustarea de TVA în termenul de 5 ani de la 1 ianuarie a anului următor hotărârii, pierzând dreptul de ajustare.
- Se scoate creanța din evidență și se deduce toată pierderea înainte de închiderea propriu-zisă a procedurii de faliment prin hotărâre judecătorească.

## Ce face iConta.eu

`core/provizioane.py` calculează procentul de deducere a ajustării de creanță la impozitul pe profit prin `deductibilitate_creanta(..., faliment_declarat=True)`, care întoarce 100% (cu condiția negarantării și neafilierii) și generează nota contabilă 6814=491. Aplicația nu calculează ajustarea bazei de TVA (art. 287) și nu modelează scoaterea din evidență a creanței la închiderea procedurii de faliment (art. 25 alin. (4) lit. h)) — ambele rămân operațiuni separate, de tratat manual, conform termenelor și condițiilor de mai sus.

[iConta.eu](/)
