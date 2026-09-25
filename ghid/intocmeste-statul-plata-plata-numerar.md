---
title: "Cum se întocmește statul de plată pentru plata în numerar"
description: "Regulile Codului muncii pentru plata salariului în bani, inclusiv în numerar, și cum se întocmește statul de plată indiferent de canalul prin care ajung banii la salariat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se întocmește statul de plată pentru plata în numerar

Multe firme mici plătesc încă parte din salariați în numerar, la casierie, nu prin virament bancar. Legea nu tratează asta ca pe un regim separat de calcul — salariul brut, contribuțiile și impozitul se calculează la fel, indiferent cum ajung banii efectiv la salariat. Ce diferă e doar modul de dovadă a plății.

## Temeiul legal

::: ghid-temei
„(1) Salariul se plăteşte în bani cel puţin o dată pe luna, la data stabilită în contractul individual de muncă, în contractul colectiv de muncă aplicabil sau în regulamentul intern, după caz.
(2) Plata salariului se poate efectua prin virament într-un cont bancar, în cazul în care aceasta modalitate este prevăzută în contractul colectiv de muncă aplicabil.
(3) Plata în natura a unei părţi din salariu, în condiţiile stabilite la art. 160, este posibila numai dacă este prevăzută expres în contractul colectiv de muncă aplicabil sau în contractul individual de muncă."
— Legea 53/2003 (Codul muncii), art. 161 alin. (1)-(3) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

- Legea pornește de la premisa că salariul se plătește „în bani" — numerarul e forma implicită, nu una specială care ar cere reguli de calcul diferite; virament bancar se face doar dacă e prevăzut expres în contractul colectiv sau individual.
- Plata în natură (nu în numerar și nu prin virament) e permisă doar dacă e prevăzută expres în contract — nu se poate improviza pe loc.
- Statul de plată rămâne documentul care arată CE se datorează salariatului; el nu se schimbă în funcție de canalul prin care banii ajung efectiv la el.

## Ce se greșește în practică

- Se caută în aplicații de contabilitate o funcție separată „mod de plată numerar", pornind de la ideea greșită că brutul, contribuțiile sau impozitul s-ar calcula altfel la cash față de card — legea nu face această distincție.
- Se emite chitanța de plată în numerar fără să existe și statul de plată semnat, deși ambele documente sunt cerute: statul arată suma datorată, chitanța sau semnătura dovedesc plata efectivă.
- Se plătește o parte din salariu în natură (bunuri, produse) fără să existe o prevedere expresă în contractul individual sau colectiv de muncă, ceea ce nu e permis de lege.

## Ce face iConta.eu

Statul de plată din iConta.eu calculează brut→net identic, indiferent cum ajunge suma netă la salariat — nu există în aplicație niciun concept separat de „metodă de plată" sau „plată numerar". Ce contează pentru calcul e doar baza contractuală, deducerile, tichetele și cotele fiscale ale lunii; canalul de plată nu intervine în formulă.

Singurul câmp din stat legat de un mod de plată e IBAN-ul salariatului, folosit exclusiv pentru a genera fișierul bancar de plată pe card (funcționalitate separată, F134 — fișier SEPA opțional). Dacă firma plătește în numerar, acest fișier pur și simplu nu se generează pentru salariații respectivi; asta nu afectează statul de plată sau fluturașul, care rămân documentele de întocmit și predat salariatului, la fel indiferent de canal.

[iConta.eu](/)
