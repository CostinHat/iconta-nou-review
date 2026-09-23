---
title: "Importul de bunuri din afara UE: TVA și declarare 2026"
description: TVA la import are trei moduri de tratare — plată la vamă, autolichidare prin certificat de amânare sau cost pentru neplătitori — și declararea corectă în D300 are, la acest moment, o limitare cunoscută pentru operațiunile non-UE.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Importul de bunuri din afara UE: TVA și declarare 2026

Importul de bunuri din afara Uniunii Europene presupune calcularea unei baze de TVA distincte de prețul facturii externe și, apoi, alegerea uneia dintre cele trei moduri prin care legea permite tratarea TVA-ului: plată directă la vamă, autolichidare prin certificat de amânare, sau, pentru neplătitori, includerea taxei în costul bunului.

## Temeiul legal

::: ghid-temei
„(1) Baza de impozitare pentru importul de bunuri este valoarea în vamă a bunurilor, stabilită conform legislației vamale în vigoare, la care se adaugă orice taxe, impozite, comisioane și alte taxe datorate în afara României, precum și cele datorate ca urmare a importului bunurilor în România, cu excepția taxei pe valoarea adăugată care urmează a fi percepută."

— Codul fiscal (Legea 227/2015 consolidat), art. 289 alin. (1)
:::

::: ghid-temei
„(4) Prin excepție de la prevederile alin. (3), nu se face plata efectivă la organele vamale pentru: a) importurile efectuate de persoanele impozabile înregistrate în scopuri de TVA conform art. 316, care îndeplinesc cumulativ condițiile prevăzute la alin. (4^1) și care au obținut certificat de amânare de la plată [...]
(5) Persoanele impozabile prevăzute la alin. (4) evidențiază taxa aferentă bunurilor importate în decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 326 alin. (4)-(5)
:::

Certificatul de amânare nu e disponibil oricui: condițiile cumulative de la art. 326 alin. (4^1) includ, printre altele, un plafon de minimum 50 milioane lei importuri din țări terțe în ultimele 6 luni, o vechime de cel puțin 6 luni a înregistrării în scopuri de TVA și lipsa datoriilor fiscale restante. Fără certificat, TVA se plătește la vamă (art. 326 alin. 3) și se deduce ulterior pe baza declarației vamale de import (art. 299 alin. 1 lit. c).

## Ce se greșește în practică

- Se presupune că certificatul de amânare e o simplă bifă disponibilă oricărei firme plătitoare de TVA, ignorând plafonul de 50 milioane lei importuri și celelalte condiții cumulative de la art. 326 alin. (4^1).
- Se lasă cota de TVA la valoarea "implicită" din memorie, fără verificare, deși o operațiune de import poate avea o cotă diferită de cea standard curentă, mai ales dacă se lucrează retroactiv.
- Se introduce procentul taxei vamale ca sumă în bani, nu ca procent din valoarea vamală, ceea ce umflă artificial baza de TVA.

## Ce face iConta.eu

Ecranul „Import extracomunitar (DVI)" calculează baza de TVA (valoare vamală + taxe vamale + accize + accesorii) și taxa aferentă, cu cota declarată explicit de contabil la fiecare operațiune (fără valoare implicită). În funcție de statutul firmei și de existența certificatului de amânare, aplicația generează automat una din cele trei note contabile: 4426=4427 (autolichidare, certificat de amânare), 4426=446 (TVA plătită la vamă, dedusă pe baza DVI) sau TVA inclus în costul bunului, pentru neplătitori. Dacă se bifează certificatul de amânare la o firmă neplătitoare de TVA, aplicația respinge combinația, întrucât acest certificat e disponibil doar persoanelor înregistrate în scopuri de TVA conform art. 316 — dar aplicația **nu verifică** plafonul de 50 milioane lei sau celelalte condiții de la art. 326 alin. (4^1); confirmarea eligibilității rămâne responsabilitatea contabilului.

Pentru declararea în D300: la data acestei cercetări, aplicația **nu populează automat rândul de TVA la import (rd.21) pentru operațiunile cu parteneri din afara UE** — acestea rămân clasificate generic pe rd.26 (neimpozabil), indiferent de modul de tratare a TVA calculat de motorul de import. Este o limitare de stare curentă a aplicației, nu o regulă fiscală, iar contabilul trebuie să verifice manual încadrarea corectă în decont.

[iConta.eu](/)
