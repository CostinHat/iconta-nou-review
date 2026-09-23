---
title: "Declararea TVA la import prin D301 sau în vamă"
description: D301 nu se aplică importului extracomunitar de bunuri — e declarația pentru achiziții intracomunitare și operațiuni cu taxare inversă. TVA la import se plătește la vamă sau, cu certificat de amânare, se reflectă în D300.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Declararea TVA la import prin D301 sau în vamă

Întrebarea "prin D301 sau în vamă" pornește de la o premisă greșită: D301 nu este declarația prin care se raportează TVA la importul de bunuri din afara Uniunii Europene. Alternativa reală, pentru acest tip de operațiune, este între plata la vamă și reflectarea în decontul de TVA (D300), nu între D300 și D301.

## Temeiul legal

::: ghid-temei
„(3) Taxa pentru importuri de bunuri, cu excepția importurilor scutite de taxă, se plătește la organul vamal în conformitate cu reglementările în vigoare privind plata drepturilor de import.
(4) Prin excepție de la prevederile alin. (3), nu se face plata efectivă la organele vamale pentru: a) importurile efectuate de persoanele impozabile înregistrate în scopuri de TVA conform art. 316, care îndeplinesc cumulativ condițiile prevăzute la alin. (4^1) și care au obținut certificat de amânare de la plată, conform procedurii stabilite prin ordin al ministrului finanțelor publice; [...]
(5) Persoanele impozabile prevăzute la alin. (4) evidențiază taxa aferentă bunurilor importate în decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 326 alin. (3)-(5)
:::

Regula de bază (alin. 3) este plata TVA direct la organul vamal. Excepția (alin. 4) permite unei categorii restrânse de firme — cele cu certificat de amânare de la plată — să nu mai plătească efectiv la vamă, ci să înscrie taxa în decontul de TVA, simultan ca taxă colectată și ca taxă deductibilă (alin. 5, autolichidare). Decontul la care se referă legea este **D300**, nu D301.

D301 are un obiect complet diferit: declararea de către persoane neînregistrate normal în scopuri de TVA (conform art. 316) a unor operațiuni specifice — achiziții intracomunitare de bunuri, achiziții de mijloace de transport noi, achiziții de produse accizabile și anumite servicii intracomunitare (art. 150). Importul de bunuri din afara Uniunii Europene nu se regăsește printre tipurile de operațiuni acoperite de D301.

## Ce se greșește în practică

- Se caută în D301 o rubrică pentru TVA la import de bunuri extracomunitare — D301 nu tratează acest tip de operațiune, ci exclusiv achiziții intracomunitare, mijloace de transport noi, produse accizabile și servicii intracomunitare, pentru persoane neînregistrate normal în scopuri de TVA.
- Se presupune că certificatul de amânare de la plata TVA în vamă e disponibil oricărei firme plătitoare de TVA, fără verificarea plafonului de minimum 50 milioane lei importuri din țări terțe în ultimele 6 luni și a celorlalte condiții cumulative de la art. 326 alin. (4^1).
- Se confundă D300 cu D301 ca denumire, deși obiectul lor e complet diferit: D300 e decontul general de TVA (unde apare, prin excepție, TVA la import cu certificat de amânare), D301 e declarația specială pentru operațiuni ale persoanelor neînregistrate normal în scopuri de TVA.

## Ce face iConta.eu

Pentru importul extracomunitar, aplicația nu propune D301 ca variantă de declarare — motorul de import generează, în funcție de situația firmei, fie o notă contabilă cu TVA plătită la vamă și dedusă pe baza declarației vamale de import (4426=446), fie, dacă firma are certificat de amânare, o notă cu autolichidare integrală (4426=4427), fie TVA inclus în costul bunului pentru neplătitori. Aplicația respinge combinația "certificat de amânare" pentru o firmă neplătitoare de TVA (art. 316), dar **nu verifică plafonul de 50 milioane lei** și celelalte condiții cumulative de la art. 326 alin. (4^1) — eligibilitatea pentru certificat trebuie confirmată manual de contabil înainte de a bifa opțiunea.

De precizat și o limitare curentă la nivel de declarare D300: la data acestei cercetări, aplicația nu populează automat rândul de TVA la import (rd.21) în D300 pentru operațiunile cu parteneri din afara UE — acestea rămân clasificate generic pe rd.26, indiferent de modul de tratare a TVA calculat la import. Este o limitare de stare curentă, nu o regulă fiscală, și necesită verificare manuală a raportării în decont.

[iConta.eu](/)
