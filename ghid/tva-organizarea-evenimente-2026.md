---
title: "TVA la organizarea de evenimente în 2026"
description: "Serviciile legate de acordarea accesului la evenimente culturale, artistice, sportive sau similare (târguri, expoziții) urmează o regulă specială de loc al prestării TVA — locul unde se desfășoară efectiv evenimentul, nu locul beneficiarului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA la organizarea de evenimente în 2026

Pentru cele mai multe servicii B2B, TVA se impozitează unde e stabilit clientul. Serviciile legate de evenimente — acces la conferințe, târguri, expoziții, spectacole — fac excepție de la această regulă generală: legea le leagă de locul fizic unde se desfășoară evenimentul. Regula a fost rafinată în 2025, cu o distincție explicită între prezența fizică și cea virtuală.

## Temeiul legal

::: ghid-temei
„locul în care activitățile se desfășoară efectiv, în cazul serviciilor principale și auxiliare legate de activități culturale, artistice, sportive, științifice, educaționale, de divertisment sau de activități similare, cum ar fi târgurile și expozițiile, inclusiv în cazul serviciilor prestate de organizatorii acestor activități, altele decât cele transmise pe internet sau puse la dispoziție printr-o altă modalitate virtuală, prestate către persoane neimpozabile;"
— Codul fiscal (Legea 227/2015), art. 278 alin. (5) lit. f) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„locul în care evenimentele se desfășoară efectiv, pentru serviciile legate de acordarea accesului la evenimente culturale, artistice, sportive, științifice, educaționale, de divertisment sau alte evenimente similare, cum ar fi târgurile și expozițiile, precum și pentru serviciile auxiliare legate de acordarea acestui acces, altele decât cele la care prezența este virtuală, prestate unei persoane impozabile."
— Codul fiscal, art. 278 alin. (6) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru clienți persoane neimpozabile (B2C — participanți persoane fizice), toate serviciile principale și auxiliare legate de eveniment se impozitează unde are loc efectiv evenimentul (art. 278 alin. (5) lit. f)).
- Pentru clienți persoane impozabile (B2B — o firmă care cumpără acces la un târg sau congres), regula specială se limitează la serviciile de acordare a accesului și la cele auxiliare acestui acces (art. 278 alin. (6) lit. b)); alte servicii legate de eveniment, dar care nu țin de accesul propriu-zis, pot rămâne sub regula generală (locul unde e stabilit beneficiarul).
- Participarea virtuală sau transmisă online e exclusă explicit din ambele reguli speciale, de la 1 septembrie 2025 (OG 22/2025) — un bilet la o conferință urmărită exclusiv online nu mai intră sub regula „locul evenimentului", ci sub regulile pentru servicii furnizate electronic.

## Ce se greșește în practică

- Se aplică regula generală B2B (locul beneficiarului) pentru bilete de acces la un târg sau eveniment vândute unei firme dintr-un alt stat membru — greșit: regula specială (locul evenimentului) are prioritate pentru acest tip de serviciu.
- Se tratează la fel accesul fizic și cel virtual la același eveniment — de la 1 septembrie 2025 legea le tratează diferit, iar aplicarea vechii reguli unitare duce la un loc de impozitare greșit pentru participarea online.
- Se presupune că orice serviciu facturat de organizatorul evenimentului (de exemplu o consultanță de organizare, separată de bilet) intră automat sub regula specială — aceasta vizează serviciile principale și auxiliare legate direct de eveniment sau de accesul la el, nu orice serviciu facturat de aceeași firmă.

## Ce face iConta.eu

Pentru servicii intracomunitare B2B, iConta.eu clasifică prestările către persoane impozabile din UE conform regulii generale a locului prestării (art. 278 alin. (2) — sediul beneficiarului), reflectată în motorul de raportare D300/D390 (`core/d300.py`), care reclasifică automat astfel de prestări ca servicii, declarate la rândurile 3 și 3.1 din D390, cu observația explicită „locul prestării în afară României, 0%". Aplicația nu are însă nicio logică dedicată excepției de la art. 278 alin. (5) lit. f) și alin. (6) lit. b) pentru serviciile legate de evenimente — nu există în cod niciun marcaj de tipul „acces la eveniment" sau „loc de desfășurare a evenimentului" care să direcționeze automat aceste operațiuni spre regula specială. O firmă care vinde acces la un eveniment din România unei firme din alt stat membru trebuie să aplice manual regula corectă (loc = România, TVA românească), fără niciun sprijin din partea aplicației la acest pas de clasificare.

[iConta.eu](/)
