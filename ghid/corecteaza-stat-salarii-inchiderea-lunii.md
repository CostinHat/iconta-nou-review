---
title: Cum se corectează un stat de salarii după închiderea lunii
description: Pontajul lunii nu se blochează prin „Blocare perioade" (F118), ci separat, în momentul în care D112 e depusă la ANAF pe luna respectivă. Corecția, după acel moment, se face prin declarație rectificativă, nu prin editare liberă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se corectează un stat de salarii după închiderea lunii

Titlul ăsta ascunde o confuzie frecventă: „închiderea lunii" pentru salarii nu e legată de funcția „Blocare perioade" din Registru jurnal, care privește evidența contabilă generală. Pontajul și statul de salarii au propriul blocaj, declanșat de un eveniment diferit: **depunerea D112**.

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. (...) Declarațiile (...) pot fi corectate prin depunerea unei declarații rectificative." — Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1) și (3)
:::

D112 e o declarație cu obligații de plată (contribuții sociale, impozit pe venit), deci corectarea ei urmează regimul declarației de impunere — se poate depune rectificativă în termenul de prescripție a dreptului organului fiscal de a stabili creanțe fiscale (5 ani, cu excepțiile prevăzute de lege).

## Ce blochează efectiv editarea în iConta.eu

Editarea unei zile de pontaj se verifică, per firmă, astfel: dacă D112 a fost deja înregistrată ca depusă pentru luna respectivă (evidența depunerilor, `public.declaratii_depuse`), editarea e refuzată, cu mesajul: *„Pontajul lunii nu se poate modifica: D112 e deja depusă la ANAF. Corectează prin rectificativă (nu prin editare liberă)."*

Această verificare **nu are nicio legătură cu „Blocare perioade"** (funcția de la Registru jurnal, F118). E un mecanism separat, aplicativ, legat strict de faptul declarat la ANAF — nu de tabelul „perioade blocate" folosit pentru notele contabile. O lună de pontaj poate rămâne editabilă chiar dacă luna contabilă e blocată, și invers: poate fi blocată la editare (D112 depusă) chiar dacă luna contabilă e încă deschisă.

## Ce se greșește în practică

- Se caută soluția în „Blocare perioade" (Registru jurnal), crezând că închiderea contabilă a lunii afectează și pontajul — cele două sunt necorelate în cod.
- Se încearcă editarea directă a unei zile de pontaj după depunerea D112 și, primind refuzul, se caută o cale ocolitoare (ștergere/reintroducere) — care nu există; singura cale e rectificativa.
- Se presupune că o corecție mică (o zi de concediu medical trecută greșit) nu merită o rectificativă — de fapt, orice modificare care schimbă baza de calcul a contribuțiilor sau a impozitului pe venit odată depusă D112 trece exclusiv prin acest canal.

## Ce face iConta.eu

Editarea pontajului unei luni pentru care D112 a fost deja marcată ca depusă e blocată explicit, cu un mesaj care numește cauza reală (D112 depusă) și direcția de rezolvare (rectificativă) — nu e un refuz generic „perioadă blocată". Corectarea propriu-zisă a datelor deja declarate se face prin declarație rectificativă D112, în termenul de prescripție prevăzut de Codul de procedură fiscală; aplicația nu oferă o rută de suprascriere directă a unei perioade deja raportate la ANAF.

[iConta.eu](/)
