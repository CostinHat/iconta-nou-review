---
title: "Prima declarație a unei firme noi: ce depun"
description: Prima declarație depinde de regimul fiscal ales la înregistrare — vectorul fiscal se stabilește direct la ANAF, înainte ca semaforul de conformare să poată evalua ceva.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Prima declarație a unei firme noi: ce depun

Nu există o singură „primă declarație" valabilă pentru orice firmă nouă — ce se depune întâi depinde de regimul fiscal stabilit la înregistrare (microîntreprindere sau impozit pe profit) și de opțiunea privind TVA. Aceste alegeri se fac direct la ANAF, la înregistrarea firmei — ele nu sunt ceva ce un instrument de urmărire a conformării le stabilește, ci ceva ce trebuie deja stabilit pentru ca un asemenea instrument să poată evalua corect obligațiile.

## Temeiul legal

::: ghid-temei
„Contribuabilii care nu sunt înregistraţi în scopuri de TVA transmit Declaraţia informativă D406 trimestrial."

*(OPANAF nr. 1783/2021, Anexa 4, pct. 3)*
:::

Un exemplu concret al acestui principiu: chiar și o firmă nou-înființată, fără nicio operațiune încă, e obligată la D406 (SAF-T) de la momentul la care obligația devine aplicabilă categoriei ei de contribuabil (din 2025, tuturor firmelor) — independent de TVA, doar periodicitatea diferă.

## Ce determină prima declarație efectivă

- **Regim micro** → prima declarație de impozit e D100, trimestrială.
- **Regim impozit pe profit** → prima declarație e D101, dar abia la finalul primului an fiscal (anual, nu din prima lună).
- **Cu angajați de la înființare** → D112 apare ca obligație din prima lună cu salariat activ.
- **Înregistrare în scopuri de TVA** → D300/D394 apar din prima perioadă fiscală de TVA.
- **D406 (SAF-T)** → aplicabilă de la înființare, cu periodicitate dependentă de statutul de TVA (lunar sau trimestrial).

## Ce se greșește în practică

- Se așteaptă ca prima declarație să fie D101, indiferent de regimul fiscal — pentru firmele pe micro, prima declarație relevantă e D100, nu D101.
- Se confundă stabilirea vectorului fiscal (opțiunea de TVA, regimul de impozitare) cu depunerea unei declarații periodice — vectorul fiscal se stabilește la înregistrarea firmei la ANAF, înainte ca vreo declarație periodică să devină relevantă.
- Se ignoră D406 la o firmă abia înființată, considerând-o „prea nouă" pentru SAF-T — obligația nu are o perioadă de grație legată de vechimea firmei.

## Ce face iConta.eu

Semaforul F022 (`core/control_fiscal_api.py`) evaluează obligațiile declarative pornind de la profilul fiscal al firmei (regim, statut de TVA, existența de salariați) — dar acest profil trebuie completat mai întâi, cu datele deja stabilite la ANAF. Dacă regimul fiscal nu e completat, semaforul nu poate decide între D100 și D101 și marchează starea ca „nu se poate verifica" (gri), cu motivul explicit, nu ca „la zi". Stabilirea propriu-zisă a vectorului fiscal la înregistrarea firmei rămâne un pas anterior, făcut direct la ANAF, nu prin acest modul.

[iConta.eu](/)
