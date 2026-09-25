---
title: "e-Factura 500: erori de server SPV și cum le tratez"
description: "Ce înseamnă o eroare de server la încărcarea unei facturi în SPV, ce spune legea despre nefuncționarea sistemului și cum se retrimite corect."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura 500: erori de server SPV și cum le tratez

Când încarci o factură în RO e-Factura și serverul ANAF răspunde cu o eroare de tip server (cod HTTP 5xx, nu o respingere de structură), factura nu a fost acceptată — dar nici nu s-a pierdut. Vestea proastă e că nicio aplicație nu poate „repara" un server ANAF picat; vestea bună e că legea prevede exact ce se întâmplă cu obligația ta de transmitere cât timp sistemul e indisponibil.

## Temeiul legal

::: ghid-temei
„(1) În situaţia în care sistemul naţional privind factura electronică RO e-Factura nu este funcţional timp de minimum 24 de ore, obligaţia de transmitere prevăzută la art. 10 alin. (1) [...] se suspendă până la repunerea în funcţiune a sistemului. (2) [...] cu condiţia transmiterii ulterioare [...] a facturilor electronice emise. (3) Perioadele de nefuncţionare [...] vor fi publicate pe paginile de internet ale [ANAF] şi [Ministerului Finanţelor]."
— OUG 115/2023, art. LXXI (modifică art. 10 alin. (1) din OUG 120/2021) (sursă: anaf_surse/oug_115_2023_consolidat.html)
:::

- O eroare de server izolată, la o singură încercare, **nu** declanșează suspendarea legală — aceea se aplică doar dacă sistemul e nefuncțional cel puțin 24 de ore consecutive.
- Cât timp nefuncționarea nu a atins pragul de 24 de ore, termenul de 5 zile lucrătoare pentru transmitere (OUG 89/2025) continuă să curgă normal — o eroare de server nu îți oprește ceasul.
- Dacă nefuncționarea depășește 24 de ore, ANAF și Ministerul Finanțelor au obligația să publice perioadele de nefuncționare pe propriile site-uri — acolo găsești confirmarea oficială, nu doar propria experiență cu eroarea.
- Odată ce sistemul revine, ai obligația să transmiți facturile emise în perioada de nefuncționare — suspendarea amână termenul, nu îl anulează.

## Ce se greșește în practică

- Se presupune că orice eroare de server îndreptățește automat amânarea nelimitată a trimiterii — de fapt doar nefuncționarea de minimum 24 de ore suspendă obligația legală.
- Se abandonează factura după prima eroare, fără reîncercare — majoritatea erorilor de server sunt trecătoare și dispar la o nouă încercare peste câteva minute sau ore.
- Se confundă o eroare de server (5xx, problemă la ANAF) cu o respingere de structură (factura are o problemă de conținut) — cele două cer reacții complet diferite: la eroare de server reîncerci aceeași factură; la respingere de structură o corectezi întâi.
- Se ignoră publicarea oficială a perioadelor de nefuncționare și se justifică întârzierea doar „din auzite" — dovada corectă e anunțul de pe site-ul ANAF/MF.

## Ce face iConta.eu

La trimiterea unei facturi, iConta validează întâi structura la validatorul public ANAF, fără token — dacă structura nu e validă, nu se încarcă nimic („nu trimitem gunoi"). Dacă structura e validă, factura ajunge la ANAF printr-un singur apel de încărcare; dacă acel apel se termină cu o eroare de server, factura primește starea **„nok" (respinsă de ANAF)**, cu mesajul brut primit de la ANAF afișat lângă factură, iar semaforul devine roșu.

Important de știut: aplicația **nu reîncearcă automat** trimiterea și nu are niciun cron care să retrimită singur o factură căzută pe eroare de server — retrimiterea e mereu manuală. Spre deosebire de stările „în prelucrare"/„trimisă", starea „nok" nu blochează butonul „Trimite în SPV" — poți apăsa din nou oricând, iar factura nu se dublează, pentru că trimiterea anterioară nu a fost una „vie" (nu are recipisă/în prelucrare). Dacă erorile persistă mai mult de câteva ore, verifică anunțurile oficiale de nefuncționare pe site-ul ANAF înainte de a insista cu reîncercări repetate.

[iConta.eu](/)
