---
title: "Poate administratorul și contabilul să aibă simultan acces la SPV?"
description: "Da: Ordinul 660/2017 permite accesul simultan la Spațiul Privat Virtual al firmei prin certificatul reprezentantului legal, al unui reprezentant desemnat sau al unui împuternicit — fiecare cu propriul certificat calificat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate administratorul și contabilul să aibă simultan acces la SPV?

Da. Accesul la Spațiul Privat Virtual (SPV) al unei firme nu e limitat la o singură persoană — administratorul (reprezentant legal), un angajat desemnat și un contabil împuternicit pot avea, simultan, acces separat, fiecare cu propriul certificat calificat.

## Temeiul legal

::: ghid-temei
„(1) Persoanele juridice sau alte entităţi fără personalitate juridică se pot identifica în mediul electronic astfel: a) cu certificatul calificat al persoanei juridice sau al entităţii fără personalitate juridică; b) cu certificatul calificat deţinut de persoana fizică reprezentant legal al persoanei juridice sau al entităţii fără personalitate juridică; c) cu certificatul calificat deţinut de reprezentantul desemnat al persoanei juridice sau al entităţii fără personalitate juridică; d) cu certificatul calificat deţinut de împuternicitul persoanei juridice sau al entităţii fără personalitate juridică."
— OMFP 660/2017 privind Spațiul Privat Virtual, art. 15 alin. (1) (sursă: anaf_surse/omfp_660_2017.txt)

„(4) În sensul prezentului ordin, reprezentantul desemnat este persoana fizică, angajat al persoanei juridice sau al entităţii fără personalitate juridică, desemnată de către reprezentantul legal al persoanei juridice sau al entităţii fără personalitate juridică, pentru înregistrarea şi utilizarea SPV."
— OMFP 660/2017, art. 15 alin. (4) (sursă: anaf_surse/omfp_660_2017.txt)

„(1) La serviciile de comunicare electronică prin SPV au acces persoanele fizice, persoanele juridice sau alte entităţi fără personalitate juridică, direct sau prin reprezentanţii sau împuterniciţii acestora."
— OMFP 660/2017, art. 4 alin. (1) (sursă: anaf_surse/omfp_660_2017.txt)
:::

Ce rezultă practic din aceste texte:

- Firma se poate identifica în SPV pe **patru căi diferite** — certificatul propriu al persoanei juridice, certificatul administratorului (reprezentant legal), certificatul unui angajat desemnat, sau certificatul unui împuternicit (de exemplu, contabilul, cu procură/împuternicire).
- Aceste patru căi **nu se exclud reciproc** — legea nu limitează accesul la o singură persoană sau la un singur certificat activ; administratorul și contabilul își pot păstra, fiecare, propriul acces, folosit independent.
- Accesul „prin reprezentanți sau împuterniciți" (art. 4 alin. (1)) confirmă explicit că firma poate fi reprezentată în SPV de mai multe persoane, cu roluri diferite (reprezentant legal, reprezentant desemnat, împuternicit).

Condiția practică pentru fiecare persoană e deținerea unui certificat calificat propriu, înregistrat conform procedurii SPV, și — pentru contabil, dacă acționează ca împuternicit — dovada calității de împuternicit al firmei.

## Ce se greșește în practică

- Se presupune că doar administratorul poate avea acces la SPV-ul firmei, iar contabilul trebuie să lucreze exclusiv prin acces delegat de la administrator, în timp real — de fapt contabilul poate avea propriul acces independent, ca împuternicit, cu propriul certificat.
- Se crede că înregistrarea unei a doua persoane (contabilul) „dezactivează" accesul administratorului — cele patru căi de identificare din art. 15 alin. (1) sunt independente, nu se suprascriu.
- Se confundă „reprezentant desemnat" (angajat al firmei, desemnat de administrator) cu „împuternicit" (poate fi extern firmei, cum e un contabil în regim de prestări servicii) — regimul de înregistrare diferă ușor, dar ambele permit acces simultan cu al administratorului.

## Ce face iConta.eu

Această întrebare privește administrarea accesului la portalul SPV al ANAF, un serviciu extern, administrat integral de ANAF — nu ține de o funcționalitate a iConta.eu. Configurarea propriu-zisă a certificatelor și a împuternicirilor cu drept de acces la SPV se face exclusiv în portalul ANAF, conform procedurii de mai sus.

Separat de administrarea SPV la ANAF, iConta.eu are propriul conector OAuth către SPV/ANAF (folosit pentru trimiterea și primirea automată a e-Facturilor), pe care cabinetul contabil îl conectează o singură dată, cu certificatul calificat pe care alege să-l folosească — acest conector nu ține evidența cine altcineva (administrator, alți angajați) are acces direct la portalul SPV al ANAF, doar dacă certificatul conectat în aplicație are drept pe CIF-ul cerut.

[iConta.eu](/)
