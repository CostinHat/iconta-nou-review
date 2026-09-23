---
title: "Cum se contabilizează garanția încasată pentru rezervarea unui eveniment la restaurant?"
description: "De ce o garanție rambursabilă de rezervare nu este același lucru cu un avans, și când devine totuși avans supus TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează garanția încasată pentru rezervarea unui eveniment la restaurant?

Nu orice sumă încasată înainte de eveniment este un avans în sensul TVA. Diferența contează: dacă suma e rambursabilă și doar garantează rezervarea, nu este avans; dacă se aplică drept plată parțială a prețului final, devine avans.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: […] b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora” — Cod fiscal, art. 282 alin. (2) lit. b)
:::

Definiția legală de mai sus leagă noțiunea de avans strict de „contravaloarea bunurilor și serviciilor” — adică de o sumă care reprezintă efectiv plata (parțială sau integrală) a prestației. O garanție de rezervare rambursabilă, care se restituie clientului dacă evenimentul are loc normal și nu acoperă vreo penalizare, nu îndeplinește această definiție cât timp rămâne rambursabilă: nu este „contravaloare”, ci o sumă deținută cu titlu de siguranță. Ea devine avans abia din momentul în care este reținută și aplicată ca plată a serviciului (de exemplu, la anularea rezervării de către client, sau la aplicarea ei pe factura finală) — din acel moment se aplică regula de mai sus, iar TVA devine exigibilă la data respectivă.

## Ce se greșește în practică

Greșeala tipică este colectarea TVA încă de la încasarea garanției, ca și cum ar fi un avans, deși suma rămâne rambursabilă la acel moment — sau, la polul opus, omiterea colectării TVA în momentul în care garanția e efectiv reținută și transformată în plată a serviciului.

## Ce face iConta.eu

Motorul de avansuri al iConta (F009) generează nota 4111 = 419 + 4427 doar pentru sumele introduse ca avans — adică sume care reprezintă plată pentru o livrare/prestare viitoare. Dosarul de cercetare al acestei funcționalități nu confirmă un cont sau o notă dedicată pentru garanții de rezervare pur rambursabile — evidențierea lor separată de avansurile propriu-zise nu ține de F009. Din momentul în care garanția este reținută și aplicată ca plată, ea trebuie introdusă ca avans, iar iConta o tratează, de atunci, la fel ca orice alt avans încasat.

[iConta.eu](/)
