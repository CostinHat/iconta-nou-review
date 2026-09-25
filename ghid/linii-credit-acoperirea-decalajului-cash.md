---
title: "Linii de credit pentru acoperirea decalajului de cash 2026"
description: "Ce spune Codul fiscal despre deductibilitatea dobânzii la liniile de credit folosite pentru acoperirea decalajelor de trezorerie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Linii de credit pentru acoperirea decalajului de cash 2026

O linie de credit (o formă de credit revolving, trasă și rambursată în funcție de nevoile de trezorerie) e instrumentul obișnuit prin care firmele acoperă decalajul dintre momentul plății furnizorilor/salariilor și momentul încasării de la clienți. Dincolo de decizia financiară de a contracta o astfel de linie, contabilul trebuie să știe și limita legală până la care dobânda plătită pentru ea rămâne deductibilă la impozitul pe profit.

## Temeiul legal

::: ghid-temei
„(1) În sensul prezentului articol, diferența dintre costurile excedentare ale îndatorării, astfel cum sunt definite potrivit art. 40^1 pct. 2, și plafonul deductibil prevăzut la alin. (4) este dedusă limitat în perioada fiscală în care este suportată, până la nivelul a 30% din baza de calcul stabilită conform algoritmului prevăzut la alin. (2). [...] (4) Contribuabilul are dreptul de a deduce, într-o perioadă fiscală, costurile excedentare ale îndatorării până la plafonul deductibil reprezentat de echivalentul în lei al sumei de 1.000.000 euro."
— Codul fiscal (Legea 227/2015), art. 40^2 alin. (1) și (4), Titlul II, Capitolul III^1 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Tradus pentru o linie de credit de trezorerie:

- Dobânda plătită pentru o linie de credit e, ca orice altă cheltuială cu dobânda, o componentă a „costurilor îndatorării". Regula de la art. 40^2 nu interzice deducerea ei, ci **limitează** deducerea „costurilor excedentare ale îndatorării" — adică partea cu care cheltuielile cu dobânzile depășesc veniturile din dobânzi.
- Există un **plafon de siguranță (safe harbour) de 1.000.000 euro**: până la acest nivel, costurile excedentare ale îndatorării se deduc integral, indiferent de rezultatul calculului de 30%. Pentru majoritatea firmelor mici și mijlocii care folosesc o linie de credit doar pentru acoperirea unui decalaj sezonier de cash, dobânda rămâne, în practică, integral deductibilă.
- Peste plafonul de 1.000.000 euro, partea excedentară se deduce doar **până la 30% dintr-o bază de calcul** stabilită potrivit alin. (2) (diferența dintre veniturile și cheltuielile contabile ale perioadei, corectată cu venituri neimpozabile și anumite cheltuieli — practic un indicator apropiat de EBITDA fiscal).
- Costurile excedentare nededuse într-o perioadă fiscală nu se pierd automat — regula prevede un mecanism de reportare (alin. (7), menționat direct în textul plafonului de la alin. (4)).

## Ce se greșește în practică

- Se presupune că orice dobândă la un credit bancar sau la o linie de credit e automat integral deductibilă la impozitul pe profit, ignorând complet testul de la art. 40^2, chiar dacă în practică, sub plafonul de 1.000.000 euro, rezultatul e de multe ori același.
- Se calculează plafonul de 30% fără să se scadă mai întâi cei 1.000.000 euro de „safe harbour" — regula se aplică doar diferenței care depășește acest prag, nu întregului cost al îndatorării.
- Se confundă „linia de credit" (o facilitate de trezorerie pe termen scurt, cu tragere/rambursare flexibilă) cu „creditul de investiții" — regimul fiscal de deductibilitate a dobânzii e același (art. 40^2 nu distinge după destinația creditului, cu excepția regimului special pentru tranzacțiile cu persoane afiliate care nu finanțează imobilizări), dar planificarea trezoreriei diferă complet.

## Ce face iConta.eu

Acest subiect ține de gestiunea trezoreriei și de limitarea deductibilității dobânzii pe termen scurt, nu de funcționalitatea F086 (sponsorizări și credit fiscal) cercetată pentru acest ghid — F086 privește exclusiv creditul fiscal obținut prin sponsorizare, un mecanism complet diferit de deductibilitatea dobânzii la un credit bancar. Cercetarea de față a verificat direct în cod doar motorul de sponsorizări și garda de plafon din D101 (`core/sponsorizari.py`, `core/d101.py`); nu avem, în acest dosar, nicio verificare a vreunui modul din iConta.eu care să calculeze plafonul costurilor excedentare ale îndatorării (art. 40^2) sau să simuleze o linie de credit, așa că nu afirmăm aici nici că aplicația automatizează acest calcul, nici că nu-l automatizează — subiectul rămâne, pentru moment, în afara cercetării verificate disponibile.

[iConta.eu](/)
