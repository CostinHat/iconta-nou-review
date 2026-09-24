---
title: "e-Factura pentru facturarea către bugetul de stat"
description: Facturarea electronică a unei autorități contractante (relația B2G) e reglementată de OUG 120/2021 și transmisă prin sistemul RO e-Factura — o temă complet separată de D100, declarația de obligații la bugetul de stat pentru impozitul micro sau alte taxe autoimpuse.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# e-Factura pentru facturarea către bugetul de stat

E important să nu se confunde două lucruri care sună asemănător: „facturare către bugetul de stat" (o factură emisă unei instituții publice, ca parte contractantă într-o achiziție publică) și „D100 — Declarație privind obligațiile de plată la bugetul de stat" (declarația prin care o firmă își raportează propriile obligații fiscale, printre care impozitul micro). Prima e o temă de facturare electronică; a doua, o temă de declarații fiscale. Nu au legătură de conținut una cu alta.

## Temeiul legal

::: ghid-temei
„Relaţia dintre un operator economic şi autorităţi contractante, respectiv entităţi contractante - B2G - [este] tranzacţia dintre un operator economic care are calitatea de contractant sau subcontractant/subantreprenor […] şi autorităţi contractante sau entităţi contractante care primesc şi prelucrează facturi electronice." — OUG 120/2021, art. 2 alin. (1) lit. m). „Facturarea electronică în domeniul achiziţiilor publice se aplică în cazul existenţei unei relaţii B2G […]." — OUG 120/2021, art. 5.
:::

## Ce e, de fapt, facturarea către bugetul de stat

Când o firmă emite o factură către o autoritate sau entitate contractantă (o instituție publică, în calitate de beneficiar al unui contract de achiziție publică), operațiunea intră în relația „B2G" definită de OUG 120/2021 — factura se transmite prin sistemul național RO e-Factura, iar destinatarul (instituția) are obligația să o primească, descarce și prelucreze prin acest sistem. Textul de bază al OUG 120/2021 leagă această obligație de existența unei relații B2G, definită prin legislația achizițiilor publice (Legea 98/2016, 99/2016, 100/2016) — regulile tehnice de transmitere sunt aceleași ca la o factură B2B obișnuită prin RO e-Factura, doar destinatarul e o entitate publică, nu un alt operator economic. Nu am verificat aici modificările ulterioare ale OUG 120/2021 privind caracterul obligatoriu/opțional al acestui flux pentru fiecare tip de relație — pentru statutul actual (2026), verificați forma consolidată a actului.

## De ce nu are legătură cu D100

D100 e declarația prin care firma își raportează, trimestrial, propriile obligații de plată la buget (de exemplu, impozitul micro, cod obligație 121) — nu are nicio legătură cu modul în care firma își facturează clienții, publici sau privați. Emiterea unei facturi către o instituție publică nu generează, prin ea însăși, nicio obligație sau rubrică specifică în D100.

## Ce se greșește în practică

Se caută în ecranul de declarații D100 o opțiune legată de facturarea către instituții publice — nu există, pentru că sunt funcționalități separate ale aplicației (emiterea de facturi electronice, respectiv depunerea declarațiilor de obligații la buget).

## Ce face iConta.eu

Emiterea facturilor electronice prin RO e-Factura — inclusiv către o autoritate contractantă, în relația B2G — se face prin modulul de facturare/e-Factura al aplicației, distinct de motorul D100 (`core/d100.py`). Verificat direct în cod: `core/d100.py` și `core/d710.py` nu conțin nicio referire la e-Factura, iar nomenclatorul D100 (OPANAF 587/2016) nu are nicio poziție legată de facturarea electronică. Cele două funcționalități rămân separate în aplicație, la fel ca în lege.

[iConta.eu](/)
