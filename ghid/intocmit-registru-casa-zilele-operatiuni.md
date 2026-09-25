---
title: "Trebuie întocmit registru de casă în zilele fără operațiuni?"
description: "Norma spune doar că registrul de casă «se întocmește zilnic, pe baza documentelor justificative» — fără să precizeze explicit dacă o zi fără nicio încasare sau plată cere un rând propriu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Trebuie întocmit registru de casă în zilele fără operațiuni?

Întrebarea pare simplă, dar norma contabilă nu o tranșează literal. Textul oficial spune că registrul „se întocmește zilnic", ceea ce poate fi citit fie ca „un rând pentru fiecare zi calendaristică", fie ca „zilnic, atunci când există ce înregistra" — cele două citiri duc la practici diferite.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP nr. 2634/2015, anexa 2, secțiunea „Registrul de casă" (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

- Norma leagă întocmirea registrului de **existența documentelor justificative de încasări și plăți** — nu descrie o obligație separată de a genera un rând „zero" pentru o zi fără nicio mișcare de numerar.
- Scopul declarat al registrului e „stabilirea soldului de casă la sfârșitul fiecărei zile" — ceea ce practic înseamnă că soldul de la finalul ultimei zile cu operațiuni rămâne valabil și pentru zilele următoare fără mișcări, până la următoarea operațiune.
- **Această interpretare nu e literă expresă de lege** — corpusul de acte verificat pentru acest ghid nu conține o normă sau un punct de vedere oficial care să răspundă explicit la cazul „zi calendaristică fără nicio operațiune de casă". E o interpretare rezonabilă, sprijinită pe formularea „pe baza documentelor justificative", nu un răspuns citat verbatim din lege.

## Ce se greșește în practică

- Se presupune, fără verificare, că „zilnic" înseamnă literal fiecare zi calendaristică, inclusiv weekendurile și zilele fără nicio tranzacție — și se pierde timp completând rânduri goale.
- Invers, se lasă goluri în numerotarea paginilor registrului fizic, fără nicio explicație — ceea ce poate ridica întrebări la un control, chiar dacă lipsa operațiunilor e reală.
- Se confundă „zi fără operațiuni de casă" cu „zi de inactivitate a firmei" — o firmă poate avea activitate normală (facturi emise, plăți prin bancă) într-o zi în care pur și simplu nu a avut nicio mișcare de numerar prin casierie.

## Ce face iConta.eu

Ecranul „card Casa" construiește registrul lunar (`GET /tenants/{id}/casa/registru`) direct din operațiunile existente în `casa_operatiuni` pentru luna cerută — aplicația **nu generează automat rânduri pentru zilele fără nicio operațiune**. Practic, indiferent de interpretarea legală de mai sus, iConta.eu urmează varianta „un rând doar acolo unde există o operațiune reală", fără o linie de sold „zero" pentru zilele fără mișcări.

[iConta.eu](/)
