---
title: "Diferențele de la casa de marcat vs gestiune"
description: "Ce obligă legea când vânzările raportate de casa de marcat nu se potrivesc cu descărcarea de gestiune, conform OMFP 2861/2009."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențele de la casa de marcat vs gestiune

Un magazin sau un restaurant compară, la un moment dat, vânzările raportate de aparatul de marcat electronic fiscal (AMEF) cu cantitățile scăzute din gestiune pe baza acelorași vânzări. Când cele două nu coincid, legea nu lasă loc de improvizație: diferența constatată declanșează obligația de inventariere.

## Temeiul legal

::: ghid-temei
„2. - (1) În temeiul prevederilor Legii contabilității nr. 82/1991, republicată, entitățile au obligația să efectueze inventarierea elementelor de natura activelor, datoriilor și capitalurilor proprii deținute, la începutul activității, cel puțin o dată în cursul exercițiului financiar pe parcursul funcționării lor, în cazul fuziunii sau încetării activității, precum și în următoarele situații: [...] b) ori de câte ori sunt indicii că există lipsuri sau plusuri în gestiune, care nu pot fi stabilite cert decât prin inventariere."
— OMFP 2861/2009, Anexa 1 (Normele privind inventarierea), pct. 2 alin. (1) lit. b) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Ce înseamnă asta pentru o diferență casă de marcat–gestiune:

- O neconcordanță între vânzările raportate de AMEF (Raportul fiscal de închidere zilnică) și cantitățile scăzute teoretic din gestiune **e chiar situația-tip** vizată de lege — un indiciu de lipsă sau plus care nu poate fi stabilit cert altfel decât prin inventariere.
- Constatarea diferenței **obligă la inventariere**, nu doar o permite — legea nu lasă la latitudinea contabilului dacă declanșează sau nu verificarea, odată ce indiciul există.
- Rezultatul inventarierii (plus sau minus real, cauza lui — eroare de scanare, furt, produs vândut sub preț fără bon, stricăciune) se documentează prin lista de inventariere și, după caz, prin proces-verbal, și abia atunci se face înregistrarea contabilă a diferenței constatate.

## Ce se greșește în practică

- Se "corectează" gestiunea direct, prin ajustarea manuală a unei cantități, fără inventariere și fără documentul care să justifice diferența — o intervenție nedocumentată nu rezistă la un control.
- Se ignoră diferențe mici, repetate, considerate "erori de rotunjire" — indiciul de lipsă/plus declanșează obligația de inventariere indiferent de mărimea sumei, dacă se repetă sistematic.
- Se confundă raportul Z (vânzările zilei, în valoare) cu descărcarea reală de gestiune pe articole — cele două se pot decupla dacă articolele nu sunt corect mapate în sistemul de gestiune, iar diferența constatată nu e neapărat o lipsă reală, ci o eroare de configurare.

## Ce face iConta.eu

La data acestui ghid, `core/amef_import.py` conține `parseaza_raport_z()`, care citește raportul Z (XML) exportat de aparatele de marcat electronice fiscale, iar `core/stocuri_cv_api.py` oferă `inventar()` pentru operațiunea de inventariere a gestiunii (compară soldul scriptic cu faptul numărat și propune nota contabilă de plus/minus, la CMP). Aplicația nu are însă un mecanism automat de **reconciliere** între vânzările raportate de AMEF și descărcarea de gestiune pe articole, care să semnaleze diferențele și să declanșeze inventarierea cerută de OMFP 2861/2009 — compararea celor două fluxuri și decizia de a inventaria rămân, azi, în sarcina contabilului.

[iConta.eu](/)
