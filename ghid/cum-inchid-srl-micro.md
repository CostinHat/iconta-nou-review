---
title: Cum închid un SRL micro?
description: O microîntreprindere care se dizolvă cu lichidare are un termen special pentru declarația și plata impozitului pe veniturile microîntreprinderilor — până la data depunerii situațiilor financiare, nu în ritmul trimestrial obișnuit — iar aplicația nu urmărește automat acest termen.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum închid un SRL micro?

Regimul de microîntreprindere nu schimbă procedura legală de lichidare de la Legea 31/1990, dar schimbă termenul la care trebuie declarat și plătit impozitul aferent perioadei de lichidare. Legea tratează separat cazul dizolvării CU lichidare de cazul dizolvării FĂRĂ lichidare — cu termene diferite.

## Temeiul legal

::: ghid-temei
**Cod fiscal 227/2015, art.56 alin.(3)-(4):**
"(3) Persoanele juridice care se dizolvă cu lichidare, potrivit legii, în cursul aceluiași an în care a început lichidarea au obligația să depună declarația de impozit pe veniturile microîntreprinderilor și să plătească impozitul aferent până la data depunerii situațiilor financiare la organul fiscal competent. (4) Persoanele juridice care, în cursul anului fiscal, se dizolvă fără lichidare au obligația să depună declarația de impozit pe veniturile microîntreprinderilor și să plătească impozitul până la închiderea perioadei impozabile."

**Legea 31/1990, art.260 alin.(1):**
"Lichidarea societății trebuie terminată în cel mult un an de la data înregistrării în registrul comerțului a mențiunii de dizolvare."
:::

## Termenul special pentru microîntreprinderi

Dacă lichidarea se termină în același an fiscal în care a început, declarația de impozit pe veniturile microîntreprinderilor pentru acea perioadă și plata impozitului aferent nu urmează ritmul trimestrial obișnuit — se depun și se plătesc până la data la care se depun situațiile financiare de lichidare la organul fiscal.

Dacă însă firma se dizolvă **fără** lichidare (de exemplu prin fuziune sau divizare totală), termenul e diferit: declarația și plata se fac până la închiderea perioadei impozabile, nu până la depunerea unor situații financiare de lichidare care, în acest caz, nici nu există.

## Ce se greșește în practică

- Se crede că, fiind microîntreprindere plătitoare trimestrial, nu există niciun termen special la închidere — se continuă declararea "ca de obicei", ignorând termenul legat de data depunerii situațiilor financiare.
- Se confundă termenul pentru dizolvare cu lichidare (art.56 alin.3) cu cel pentru dizolvare fără lichidare (art.56 alin.4) — sunt situații și termene diferite.
- Se ignoră termenul de maximum un an pentru terminarea lichidării (art.260 alin.1 din Legea 31/1990), care influențează direct cât de lung poate fi exercițiul fiscal special.

## Ce face iConta.eu

În `core/`, motorul de declarații nu conține nicio adaptare a acestui termen special pentru microîntreprinderi aflate în lichidare. Un precedent similar există în `core/d107.py` (declarația de sponsorizări), care respinge explicit exercițiul financiar legat de dizolvare — un tipar consecvent în aplicație: exercițiul financiar de lichidare nu este tratat de motoarele de declarații verificate. iConta.eu oferă doar notele contabile de lichidare (vânzarea activelor, partajul final) — urmărirea termenului special de declarare și plată pentru impozitul pe veniturile microîntreprinderilor rămâne responsabilitatea contabilului.

[iConta.eu](/)
