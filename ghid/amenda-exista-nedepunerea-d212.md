---
title: "Ce amendă există pentru nedepunerea D212?"
description: "Nedepunerea la termen a D212 se sancționează contravențional cu amendă de la 50 la 500 lei, aplicabilă și asocierilor fără personalitate juridică la nivelul amenzii pentru persoane fizice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce amendă există pentru nedepunerea D212?

Amenda pentru nedepunerea D212 la termen e stabilită într-un interval fix, relativ modest comparativ cu alte contravenții fiscale — dar nu e singura consecință a întârzierii, iar organul fiscal poate acționa suplimentar prin stabilirea din oficiu a obligațiilor.

## Temeiul legal

::: ghid-temei
„În cazul persoanelor fizice nedepunerea la termenele prevăzute de lege a declarațiilor de venit, precum și a declarației unice privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice constituie contravenție și se sancționează cu amendă de la 50 lei la 500 lei."
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„În cazul asocierilor și al altor entități fără personalitate juridică, contravențiile prevăzute la alin. (1) se sancționează cu amenda prevăzută pentru persoanele fizice."
— Legea 207/2015, art. 336 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce trebuie reținut din text:

- Intervalul amenzii e 50-500 lei, stabilit special pentru persoane fizice, diferit (de regulă mai mic) decât amenzile aplicabile persoanelor juridice pentru alte tipuri de nedepuneri.
- Regula se aplică inclusiv „declarațiilor de venit" în general, nu doar D212 explicit — orice declarație de venit a persoanei fizice nedepusă la termen intră sub aceeași sancțiune.
- Asocierile fără personalitate juridică (de exemplu, o asociere între mai multe PFA-uri) se sancționează, pentru nedepunere, cu amenda specifică persoanelor fizice, nu cu cea pentru persoane juridice.
- Amenda contravențională e distinctă de eventualele dobânzi și penalități de întârziere calculate pentru sumele de plată declarate cu întârziere — cele două se cumulează.

## Ce se greșește în practică

- Se confundă amenda pentru nedepunere (50-500 lei) cu penalitățile de întârziere la plată, care se calculează separat, pe zi de întârziere, asupra sumelor efectiv datorate.
- Se presupune că o asociere de PFA-uri fără personalitate juridică riscă amenzi „de firmă", mult mai mari — legea trimite explicit la amenda pentru persoane fizice.
- Se ignoră faptul că, dincolo de amendă, întârzierea prelungită poate declanșa stabilirea din oficiu a bazei de impozitare de către organul fiscal (art. 107 din aceeași lege), pe o bază estimată.

## Ce face iConta.eu

D212 e o declarație manuală în iConta.eu (`core/d212.py`) — aplicația nu calculează și nu afișează amenda contravențională pentru nedepunere, care se stabilește de organul fiscal, nu de contribuabil. Motorul de calcul (`core/d212_engine.py`) produce corect CAS, CASS și impozitul datorat, indiferent de momentul depunerii, dar rămâne în sarcina contabilului să urmărească termenul legal și riscul contravențional asociat unei depuneri tardive.

[iConta.eu](/)
