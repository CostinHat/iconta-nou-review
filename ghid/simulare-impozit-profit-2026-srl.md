---
title: "Simulare impozit pe profit 2026 pentru un SRL"
description: "Cota de impozit pe profit rămâne 16% în 2026. Impozitul minim pe cifra de afaceri (IMCA, redus temporar la 0,5% în 2026) se aplică doar firmelor cu cifră de afaceri de peste 50.000.000 euro — nu unui SRL obișnuit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Simulare impozit pe profit 2026 pentru un SRL

Pentru majoritatea firmelor la regim de profit, impozitul din 2026 se calculează exact ca înainte — 16% din profitul impozabil. Discuția despre impozitul minim pe cifra de afaceri (IMCA), des invocată în presa fiscală, privește însă doar contribuabilii mari, nu un SRL obișnuit.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Codul fiscal (Legea 227/2015), art. 17

„(1) Contribuabilii, alții decât cei prevăzuți la art. 15, care înregistrează în anul precedent o cifră de afaceri de peste 50.000.000 euro și care în anul de calcul determină un impozit pe profit [...] mai mic decât impozitul minim pe cifra de afaceri [...], sunt obligați la plata impozitului pe profit la nivelul impozitului minim pe cifra de afaceri. [...]
(16) Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin. (3) este 0,5%."
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (1) și (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă pentru simularea impozitului unui SRL în 2026:

- Regula generală rămâne cota de **16%** aplicată profitului impozabil (rezultatul contabil ajustat cu deducerile și cheltuielile nedeductibile din Codul fiscal) — aceasta e baza oricărei simulări pentru o firmă obișnuită.
- Impozitul minim pe cifra de afaceri (IMCA) intervine **doar** pentru firmele cu o cifră de afaceri de peste **50.000.000 euro** în anul precedent — un prag mult peste realitatea unui SRL tipic, care astfel nu intră deloc în calculul IMCA.
- Pentru anul fiscal 2026, cota folosită în formula IMCA (pentru cei câțiva contribuabili cărora chiar li se aplică) este redusă temporar la **0,5%**, față de cota standard de 1% — dar, din nou, doar pentru firmele care depășesc pragul de cifră de afaceri.

## Ce se greșește în practică

- Se aplică, din precauție, calculul IMCA și pentru un SRL obișnuit, cu cifră de afaceri de câteva sute de mii sau milioane de lei, deși pragul legal de 50.000.000 euro exclude aproape orice IMM din acest calcul.
- Se estimează impozitul pe profit doar din marja netă a firmei, fără să se pornească din rezultatul fiscal real — ajustat cu cheltuielile nedeductibile (protocol peste limită, provizioane nedeductibile etc.) și cu pierderea fiscală reportată.
- Se confundă IMCA (impozitul minim pe cifra de afaceri, pentru contribuabilii mari) cu alte impozite minime similare din Codul fiscal (de exemplu impozitul pe construcții speciale, la o cotă diferită) — sunt mecanisme separate, cu formule și praguri proprii.

## Ce face iConta.eu

iConta.eu **nu oferă un simulator separat** de impozit pe profit pentru scenarii ipotetice. D101 (declarația anuală) este însă funcționalitate live: calculează impozitul pe profit din balanța reală a firmei, aplică pierderea reportată și, acolo unde e cazul, calculează și compară IMCA cu impozitul clasic. Pentru un SRL obișnuit, sub pragul de 50.000.000 euro cifră de afaceri, calculul relevant din aplicație rămâne cel al impozitului clasic de 16% aplicat rezultatului fiscal din balanță.

[iConta.eu](/)
