---
title: Cum se regularizează avansul la factura finală de construcții?
description: Regularizarea avansului la recepția finală a lucrării stornează avansul (409/419) la cota valabilă la data livrării, iar la contracte cu avansuri/situații de plată succesive, suma corectă de regularizat este cumulul tuturor plăților anterioare — pe care sistemul nu îl calculează singur.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se regularizează avansul la factura finală de construcții?

La recepția finală a unei lucrări de construcții, factura finală trebuie să reflecte corect valoarea totală a lucrării, cu regularizarea (stornarea) tuturor avansurilor și situațiilor de plată încasate anterior. Pentru contracte cu plăți eșalonate, această regularizare are câteva capcane specifice.

## Temeiul legal

::: ghid-temei
"(4) Cota aplicabilă este cea în vigoare la data la care intervine faptul generator, cu excepția cazurilor prevăzute la art. 282 alin. (2), pentru care se aplică cota în vigoare la data exigibilității taxei."

"(6) În cazul schimbării cotei se va proceda la regularizare pentru a se aplica cota în vigoare la data livrării de bunuri sau prestării de servicii, pentru cazurile prevăzute la art. 282 alin. (2), precum și în situația prevăzută la alin. (5)."

"Contul 409 «Furnizori ‐ debitori» — ... În creditul contului 409 se înregistrează: ‐ valoarea avansurilor acordate furnizorilor, cu ocazia regularizării plăților cu aceştia (401, 404); ..."

"Contul 419 «Clienți ‐ creditori» — ... În debitul contului 419 se înregistrează: ‐ decontarea avansurilor încasate de la clienți (411); ..."
:::

## Regularizarea la recepția finală

La recepția finală a lucrării (data livrării/faptului generator), toate avansurile și situațiile de plată încasate anterior trebuie stornate din 409 sau 419, iar factura finală se emite separat, pentru valoarea totală a lucrării. Regula de cotă rămâne cea din art. 291 alin. (6): cota aplicabilă întregii operațiuni la regularizare este cea în vigoare **la data livrării** (recepția finală), nu cea de la fiecare avans în parte.

Pentru un contract cu mai multe avansuri/situații de plată succesive, punctul critic e suma de regularizat: aceasta trebuie să fie exact suma cumulată a tuturor plăților anterioare aferente acelui contract — nici mai mult, nici mai puțin. O regularizare parțială (care omite un avans anterior) lasă un sold "agățat" în 409/419 după finalizarea lucrării.

::: ghid-exemplu
Un contract de construcții are trei plăți anterioare recepției: avans inițial 50.000 lei, situație de plată 1: 80.000 lei, situație de plată 2: 70.000 lei — total 200.000 lei deja înregistrate în 409/4092. Valoarea totală a lucrării la recepție e 500.000 lei. Factura finală se emite pentru 500.000 lei, iar regularizarea trebuie să storneze exact cei 200.000 lei cumulați din cele trei plăți anterioare, nu doar ultima situație de plată.
:::

## Ce se greșește în practică

- Se regularizează doar ultimul avans/ultima situație de plată, ignorând sumele mai vechi rămase în 409/419 din plăți anterioare pe același contract.
- Se aplică la regularizare cota din data ultimului avans, în loc de cota valabilă la data recepției finale (data livrării), conform art. 291 alin. (6).
- Se emite factura finală "pe net" (doar diferența nefacturată), fără să se documenteze separat stornarea avansurilor — practică ce complică reconcilierea și controlul ulterior.
- Se presupune că sistemul urmărește automat toate plățile anterioare pe contract și calculează singur suma de regularizat — motorul contabil nu are această evidență, ea trebuie ținută separat, la nivel de contract/comandă.

## Ce face iConta.eu

Regularizarea tehnică se face prin `nota_regularizare_avans_platit(...)` (pentru avansuri plătite constructorului) sau `nota_regularizare_avans_incasat(...)` (pentru avansuri încasate de firma de construcții), care inversează liniile de avans: `401 = 409x` + `401 = 4426`, respectiv `419 = 4111` + `4427 = 4111`. Orchestrarea din `core/uc_tenants.py::nota_avans` cere explicit `data_livrare` pentru orice operație de tip "regularizare" și calculează cota pe baza acestei date, exact conform art. 291 alin. (6).

**Limitarea de reținut pentru contracte cu plăți eșalonate**: `avansuri.py` nu urmărește câte avansuri/situații de plată s-au emis pentru un contract și nu le agregă automat. La regularizare, suma trebuie să fie exact suma cumulată a tuturor plăților anterioare aferente facturii finale — această cumulare e responsabilitatea utilizatorului/aplicației care apelează motorul (UI, contabil), nu a modulului `avansuri.py` însuși, care nu are context despre facturile/plățile anterioare pentru a detecta o sumă greșită.

[iConta.eu](/)
