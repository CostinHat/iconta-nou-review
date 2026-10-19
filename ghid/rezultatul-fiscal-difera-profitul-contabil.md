---
title: "De ce rezultatul fiscal diferă de profitul contabil?"
description: "Mecanismul legal prin care profitul din contul de profit și pierdere se transformă în baza de calcul a impozitului pe profit, cu deducerile și cheltuielile nedeductibile prevăzute de Codul fiscal."
published: 2026-09-24
modified: 2026-10-18
poarta: v1
---

# De ce rezultatul fiscal diferă de profitul contabil?

Profitul contabil e rezultatul din bilanț, calculat după regulile contabile (OMFP 1802/2014). Rezultatul fiscal e altceva — baza pe care se aplică efectiv impozitul pe profit — și Codul fiscal îl obține pornind de la profitul contabil, dar ajustându-l cu elemente pe care legea le tratează diferit de contabilitate.

## Temeiul legal

::: ghid-temei
„Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. La stabilirea rezultatului fiscal se iau în calcul și elemente similare veniturilor și cheltuielilor, potrivit normelor metodologice, precum și pierderile fiscale care se recuperează în conformitate cu prevederile art. 31."
— Legea nr. 227/2015 privind Codul fiscal, art. 19 (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Formula din articol arată exact unde apar diferențele față de profitul contabil:

- **Se scad veniturile neimpozabile** — venituri pe care legea le exclude explicit din baza de impozitare, deși contabil sunt venituri normale (de exemplu, anumite venituri din anularea provizioanelor nedeductibile la constituire).
- **Se scad deducerile fiscale** — sume pe care legea le permite scăzute suplimentar, fără corespondent contabil direct.
- **Se adaugă cheltuielile nedeductibile** — cheltuieli recunoscute contabil (deci reduc profitul contabil), dar pe care legea nu le acceptă la calculul impozitului (amenzi, penalități, o parte din cheltuielile de protocol/sponsorizare peste limită, provizioane nedeductibile etc.).
- **Elemente similare veniturilor/cheltuielilor** — ajustări tehnice (de exemplu, cele legate de active în curs de execuție) care nu apar ca atare în contul de profit și pierdere, dar intră în calculul fiscal.
- **Pierderea fiscală reportată** (art. 31) — se scade separat, chiar dacă în contabilitate rezultatele anilor anteriori nu se "reportează" în calculul profitului curent în același mod.

Practic, profitul contabil e punctul de plecare, nu rezultatul final: rezultatul fiscal e întotdeauna profitul contabil plus/minus ajustările pe care Codul fiscal le impune explicit.

## Ce se greșește în practică

- Se declară la impozitul pe profit direct profitul contabil din balanță, fără parcurgerea listei de venituri neimpozabile și cheltuieli nedeductibile din Codul fiscal.
- Se omit cheltuielile nedeductibile "mici" (amenzi, penalități contractuale nedeductibile, o parte din protocol) pentru că, contabil, ele deja au fost înregistrate corect ca cheltuială — dar tocmai de-asta trebuie adăugate înapoi la calculul fiscal.
- Se calculează rezultatul fiscal o singură dată, la final de an, deși art. 19 alin. (2) cere calculul trimestrial/anual, cumulat de la începutul anului fiscal — o eroare la un trimestru se propagă în toate cele următoare.

## Ce face iConta.eu

La calculul obligației de impozit pe profit din declarația D100, iConta.eu pornește de la diferența contabilă venituri minus cheltuieli, cumulată de la 1 ianuarie (art. 41 CF), și o transformă în rezultat fiscal cu ajustările din art. 19 și următoarele pe care le scrii, pe trimestrul în care s-au produs, în ecranul „Registrul de evidență fiscală” al firmei, secțiunea „Ajustări fiscale”: venituri neimpozabile, deduceri fiscale, cheltuieli nedeductibile. Pierderea fiscală din anii anteriori se recuperează cel mult 70% (art. 31 alin. (1)). Rezumatul declarației arată pe rânduri rezultatul contabil, ajustările, pierderea recuperată și impozitul cumulat, iar aceleași ajustări intră și în D101. Ce rămâne la contabil e încadrarea: aplicația nu decide singură ce cheltuială e nedeductibilă sau ce venit e neimpozabil.

[iConta.eu](/)
