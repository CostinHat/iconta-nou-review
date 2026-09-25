---
title: "Cum se sincronizează stocul WooCommerce cu gestiunea din iConta?"
description: "Legea contabilității cere evidența cantitativă și valorică a stocurilor — dar conectorul WooCommerce al iConta.eu nu are, azi, nicio legătură cu modulul de gestiune."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se sincronizează stocul WooCommerce cu gestiunea din iConta?

Un magazin WooCommerce ține, de regulă, propriul lui stoc — cantitatea disponibilă din fiecare produs, scăzută automat la fiecare comandă finalizată. Firma are însă și o obligație contabilă separată: evidența stocurilor în propria contabilitate, indiferent de canalul prin care se vinde.

## Temeiul legal

::: ghid-temei
„Contabilitatea imobilizărilor se ține pe categorii și pe fiecare obiect de evidență. (2) Contabilitatea stocurilor se ține cantitativ și valoric sau numai valoric, în condițiile stabilite de reglementările legale."
— Legea 82/1991 (Legea contabilității), art. 12 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

- Obligația de evidență a stocurilor e generală — se aplică oricărei firme cu activitate de vânzare de bunuri, indiferent dacă vinde printr-un magazin fizic, o platformă online sau ambele.
- Legea lasă alegerea între evidență „cantitativ și valoric" sau „numai valoric", în funcție de reglementările contabile aplicabile firmei respective (de regulă, dimensiunea și complexitatea activității).
- Obligația e independentă de orice sincronizare tehnică între un magazin online și o aplicație de contabilitate — chiar dacă nu există automatizare, evidența stocurilor tot trebuie ținută.

## Ce se greșește în practică

- Se presupune că, odată ce comenzile WooCommerce sunt importate automat ca facturi în iConta, stocul din gestiune se actualizează implicit — nu se întâmplă.
- Se ține stocul doar în interiorul WooCommerce (contorul de cantitate disponibilă al platformei), fără nicio reflectare în contabilitatea firmei, ceea ce nu acoperă obligația legală de evidență.
- Se caută în iConta.eu un ecran dedicat „stoc WooCommerce", presupunând că funcționalitatea de import al comenzilor include și gestiunea de stoc.

## Ce face iConta.eu

Conectorul WooCommerce al iConta.eu (cronul zilnic, plus sincronizarea manuală) face exclusiv un singur lucru: citește comenzile finalizate din magazin și le transformă în facturi emise. **Nu există nicio legătură cu un modul de stoc sau gestiune** — verificat exhaustiv în codul conectorului, care nu conține niciun apel către evidența de stocuri. Dacă firma ține gestiune de stocuri în iConta.eu, ea rămâne complet separată de acest import automat și trebuie actualizată prin mijloace proprii, indiferent de sincronizarea comenzilor WooCommerce.

[iConta.eu](/)
