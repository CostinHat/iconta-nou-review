---
title: "Cum verific D100 cu obligațiile din contabilitate?"
description: "Ce cere legea contabilității pentru verificarea lunară a sumelor din declarații față de evidența contabilă, și ce anume face iConta.eu pe acest subiect."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D100 cu obligațiile din contabilitate?

Înainte de a depune D100, orice sumă declarată trebuie să corespundă cu ce arată efectiv evidența contabilă a firmei — o balanță de verificare la zi, conturile de TVA, salarii sau impozit corect închise. Aceasta e o verificare **premergătoare depunerii**, diferită de corectarea unei declarații deja depuse greșit.

## Temeiul legal

::: ghid-temei
„Articolul 22 Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare."
— Legea contabilității nr. 82/1991, art. 22 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

- Balanța de verificare lunară e instrumentul legal prin care o firmă confirmă că înregistrările contabile sunt corecte — și, implicit, baza pe care se calculează sumele declarate ulterior la ANAF.
- Evidența fiscală și cea contabilă se supun acelorași reguli de bază: „Contribuabilul/Plătitorul este obligat să evidențieze veniturile realizate și cheltuielile efectuate din activitățile desfășurate, prin întocmirea registrelor sau a oricăror altor documente prevăzute de lege" — Codul de procedură fiscală (Legea 207/2015), art. 109 alin. (5).
- Organul fiscal are dreptul să ia în calcul orice evidență relevantă a contribuabilului: „Organul fiscal poate lua în considerare orice evidențe relevante pentru impozitare ținute de contribuabil/plătitor" — aceeași sursă, art. 109 alin. (7) — motiv suplimentar pentru care sumele din declarație și cele din contabilitate trebuie să coincidă.

## Ce se greșește în practică

- Se declară o sumă „estimată" sau reportată din perioada anterioară, fără să se confrunte cu balanța de verificare efectivă a lunii pentru care se depune declarația.
- Se descoperă neconcordanța abia după depunere, ceea ce transformă o simplă verificare într-o corecție ulterioară (rectificativă), cu toate implicațiile ei — inclusiv eventuale dobânzi, dacă diferența e în minus.
- Se confundă „verificarea premergătoare" cu „corectarea unei declarații depuse" — sunt etape diferite: prima previne eroarea, a doua o repară după ce a ajuns deja la ANAF.

## Ce face iConta.eu

Verificarea sumelor din D100 față de evidența contabilă **nu este** o funcție a declarației rectificative 710, tratată în acest ghid mai general. Formularul 710 descris în restul acestei serii de ghiduri intervine abia **după** ce D100 a fost deja depusă greșit; el generează și validează XML-ul corecției (coduri 121 și 103), dar nu compară sumele cu contabilitatea și nu declanșează, prin el însuși, o reconciliere.

Verificarea premergătoare există, dar nu ca ecran separat pe care contabilul îl consultă înainte de depunere, ci ca poartă automată, integrată direct în generarea declarației: de fiecare dată când se generează un D100, aplicația recalculează independent baza impozabilă din veniturile efectiv contabilizate (contul 70x, doar din note validate) și o confruntă cu suma obținută de generator. Dacă cele două nu coincid, D100 **nu se generează** — aplicația oprește procesul cu un mesaj care arată ambele valori (suma generatorului și suma recalculată din contabilitate) și cere verificarea agregării/notelor, în loc să lase să iasă o declarație a cărei sumă nu se leagă de contabilitate.

[iConta.eu](/)
