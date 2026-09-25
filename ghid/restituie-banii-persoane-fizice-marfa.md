---
title: "Cum se restituie banii unei persoane fizice pentru marfa returnată?"
description: "Plafonul de 10.000 lei pentru restituirea în numerar către o persoană fizică, și excepția pentru cine nu are cont bancar, conform Legii 70/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se restituie banii unei persoane fizice pentru marfa returnată?

Un client persoană fizică aduce înapoi un produs și cere banii înapoi, în numerar. Regula pare simplă, dar legea pune o limită — cu o excepție care depinde de o declarație a clientului, nu de voința comerciantului.

## Temeiul legal

::: ghid-temei
„(2) În cazul returnării de bunuri de către persoanele fizice și, respectiv, neprestării de servicii către persoanele fizice, restituirea sumelor aferente poate fi efectuată în numerar în limita a 10.000 lei, sumele care depășesc acest plafon putând fi restituite numai prin instrumente de plată fără numerar. Prin excepție, în cazul în care, la data restituirii, persoanele fizice declară pe propria răspundere că nu mai dețin cont bancar, restituirea se poate face integral în numerar, indiferent de nivelul sumei care trebuie restituită."
— Legea 70/2015, art. 9 alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce înseamnă concret:

- **Regula generală**: restituirea în numerar către o persoană fizică, pentru marfă returnată, e limitată la **10.000 lei**. Ce depășește plafonul se restituie doar prin instrument fără numerar (virament în contul clientului).
- **Excepția**: dacă la data restituirii clientul **declară pe propria răspundere** că nu deține cont bancar, comerciantul poate restitui **integral în numerar**, oricât de mare ar fi suma — dar declarația trebuie luată și păstrată ca document justificativ.
- Fără această declarație, comerciantul nu poate restitui peste plafon în numerar, indiferent de motivele invocate verbal de client — legea cere forma scrisă, pe propria răspundere.

## Ce se greșește în practică

- Se restituie orice sumă în numerar, fără verificarea plafonului de 10.000 lei și fără nicio declarație, considerând că restituirea "nu e o plată obișnuită" — legea o tratează exact ca o plată în numerar către persoană fizică, supusă plafonului.
- Se invocă excepția (lipsa contului bancar) fără a lua efectiv declarația scrisă pe propria răspundere a clientului — la un control, absența documentului face imposibilă justificarea restituirii integrale peste plafon.
- Se confundă acest plafon cu cel de la art. 9 alin. (1), aplicabil restituirilor către alte firme pentru facturi stornate (5.000/10.000 lei) — cele două situații (persoană fizică vs. persoană juridică) au reguli distincte.

## Ce face iConta.eu

La data acestui ghid, `core/casa.py` nu are o funcție dedicată „restituire marfă către persoană fizică". Motorul de calcul (`verifica_plafon()`) distinge, la nivel de parametru (`partener_tip`), o plată către persoană fizică și o verifică față de plafonul `PLAFON_PF` de 10.000 lei — dar API-ul expus, `core/casa_api.py`, are doar cinci categorii fixe de operațiuni (`incasare_client`, `plata_furnizor`, `ridicare_banca`, `depunere_banca`, `avans_decontare`), niciuna dedicată unei restituiri către o persoană fizică, iar tabela `casa_operatiuni` nu reține deloc tipul de partener (pf/pj). În fluxul curent al registrului de casă, o astfel de restituire nu are deci o categorie proprie, iar verificarea automată a plafonului de 10.000 lei nu se declanșează pe această cale. Excepția pentru clientul fără cont bancar, cu declarația pe propria răspundere aferentă, nu e tratată deloc de aplicație — rămâne, azi, o decizie și o documentare integral manuală a comerciantului.

[iConta.eu](/)
