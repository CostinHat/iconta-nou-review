---
title: Greșeli la sponsorizare: fără contract și fără deducere corectă
description: Lipsa contractului scris (obligatoriu potrivit Legii nr. 32/1994) și deducerea greșită a plafonului fiscal sunt cele două erori care riscă cel mai mult creditul de sponsorizare — fiecare poate anula integral avantajul, nu doar reduce suma dedusă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Greșeli la sponsorizare: fără contract și fără deducere corectă

Sponsorizarea e una dintre puținele cheltuieli care se scad direct din impozitul pe profit datorat, nu doar din baza impozabilă — ceea ce o face atractivă, dar și sensibilă la greșeli de formă. Două categorii de erori revin constant: lipsa unui contract valabil și calculul greșit al sumei deductibile. Fiecare, separat, poate anula tot creditul, nu doar diminua avantajul.

## Temeiul legal

::: ghid-temei
„Contractul de sponsorizare se încheie în forma scrisă, cu specificarea obiectului, valorii și duratei sponsorizării, precum și a drepturilor și obligațiilor părților.”

— *Legea nr. 32/1994 privind sponsorizarea, art. 1 alin. (2).*

„Facilitățile prevăzute în prezenta lege nu se acordă în cazul: a) sponsorizării reciproce între persoane fizice sau juridice; b) sponsorizării efectuate de către rude ori afini până la gradul al patrulea inclusiv; c) sponsorizării unei persoane juridice fără scop lucrativ de către o altă persoană juridică care conduce sau controlează direct persoana juridică sponsorizată.”

— *Legea nr. 32/1994 privind sponsorizarea, art. 6.*

„Persoanele fizice sau juridice din România nu pot efectua activități de sponsorizare sau de mecenat din surse obținute de la buget.”

— *Legea nr. 32/1994 privind sponsorizarea, art. 3 alin. (1).*

„i) ... contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea..., scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele: 1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri...; 2. valoarea reprezentând 20% din impozitul pe profit datorat. ... doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală.*
:::

## Greșeala 1: fără contract scris valabil

Legea nr. 32/1994 cere explicit forma scrisă, cu trei elemente obligatorii: **obiectul**, **valoarea** și **durata** sponsorizării, plus drepturile și obligațiile părților. Fără contract, sau cu un contract incomplet, organul fiscal poate contesta însăși calificarea cheltuielii drept sponsorizare — indiferent cum a fost înregistrată contabil sau cât de corect a fost calculat plafonul.

În plus, legea exclude explicit anumite situații de la facilitate, chiar dacă există contract: sponsorizarea reciprocă între aceleași părți, sponsorizarea către rude/afini până la gradul al patrulea, sponsorizarea unei entități fără scop lucrativ de către o persoană juridică care o conduce sau o controlează direct, și sponsorizarea din surse obținute de la buget.

## Greșeala 2: deducerea greșită a plafonului

Chiar cu un contract valabil, creditul se pierde parțial sau integral dacă plafonul nu e calculat corect:

- **Plafonul nu e un singur calcul, ci un minim din două.** Corect: `min(0,75% × cifra de afaceri; 20% × impozitul pe profit datorat)`. Greșit: se folosește doar unul dintre cele două criterii.
- **Condiția de Registru se verifică la data contractului, nu la data plății.** Dacă beneficiarul e o entitate fără scop lucrativ sau unitate de cult, trebuie să fie înscris(ă) în Registrul entităților/unităților de cult exact la data încheierii contractului — o înscriere ulterioară nu „repară" un contract semnat înainte.
- **Se pierde din vedere data sponsorizării.** Procentul de 0,75% e valabil doar din 03.02.2022; pentru sponsorizări mai vechi, procentul legal era 0,5%, cu mecanism de reportare pe 7 ani, nu de redirecționare D177.

::: ghid-exemplu
O firmă semnează un contract de sponsorizare cu o asociație în martie 2026, dar asociația se înscrie în Registrul entităților/unităților de cult abia în aprilie 2026, la o lună după semnare. Chiar dacă firma calculează corect plafonul (`min(0,75% CA; 20% impozit)`) și respectă toate celelalte condiții, întregul credit este nedatorat — condiția de Registru nu e îndeplinită la data relevantă (încheierea contractului), iar o înscriere ulterioară nu schimbă acest rezultat.
:::

## Ce se greșește în practică

- Se acordă sponsorizarea doar pe bază de factură sau ordin de plată, fără un contract scris care să specifice obiectul, valoarea și durata.
- Se verifică înscrierea în Registru la data plății sau la data depunerii D101, nu la data încheierii contractului.
- Se calculează plafonul dintr-un singur criteriu (doar cifra de afaceri sau doar impozitul pe profit), în loc de minimul dintre cele două.
- Se sponsorizează o entitate aflată sub excluderile art. 6 din Legea nr. 32/1994 (de exemplu, o entitate controlată direct de firma sponsor), fără să se verifice această interdicție.
- Se înregistrează sponsorizarea generic, ca „donație” sau „protocol”, fără evidență distinctă — ceea ce face imposibilă justificarea ulterioară a sumei eligibile pentru credit.

## Ce face iConta.eu

Funcția `credit_sponsorizare(cifra_afaceri, impozit_profit, sponsorizari_efectuate, tip_impozit="profit", beneficiar_in_registru=True, la_data=None)` din `core/sponsorizari.py` respinge explicit creditul dacă `beneficiar_in_registru=False`: rezultatul e credit 0, cu o notă de respingere — motorul reflectă corect faptul că lipsa înscrierii anulează întregul credit, nu doar excedentul. Ce motorul **nu poate verifica automat** este dacă acel parametru reflectă corect data încheierii contractului (nu data plății), și nici dacă există efectiv un contract scris valid, sau dacă beneficiarul se încadrează la excluderile din art. 6 al Legii nr. 32/1994 — acestea rămân verificări manuale, în afara calculului.

Pentru înregistrarea contabilă, `nota_sponsorizare(suma, mod)` generează `6582 = 401` pentru sponsorizarea pe bază de contract sau `6582 = 5121` pentru plata directă, izolând suma de alte cheltuieli — dar folosirea corectă a acestei funcții nu înlocuiește verificarea condițiilor de fond ale contractului și ale beneficiarului, descrise mai sus.

[iConta.eu](/)
