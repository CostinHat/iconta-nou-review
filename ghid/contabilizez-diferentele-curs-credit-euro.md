---
title: Cum contabilizez diferențele de curs la un credit în euro?
description: Diferența de curs valutar la un credit în euro se recunoaște lunar (reevaluarea soldului la cursul BNR de la sfârșitul lunii) și la fiecare plată; pentru o datorie, cursul crescut înseamnă pierdere pe 665, cursul scăzut înseamnă câștig pe 765.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum contabilizez diferențele de curs la un credit în euro?

Un credit în euro generează diferențe de curs în două momente diferite: la fiecare decontare (plata unei rate sau a dobânzii) și, indiferent dacă a existat vreo plată, la reevaluarea lunară a soldului rămas. Regula de semn e simplă, dar se inversează frecvent în practică — de aceea merită tratată separat de mecanica de bază a creditului.

## Temeiul legal

::: ghid-temei
„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar. (2) Atunci când creanța sau datoria în valută este decontată în decursul aceleiași luni în care a survenit, întreaga diferență de curs valutar este recunoscută în acea lună. Atunci când creanța sau datoria în valută este decontat[ă într-o lună ulterioară] ...”

— *OMFP 1802/2014, pct. 322.*

„În creditul contului 162 ... se înregistrează: ... – diferențele nefavorabile de curs valutar ... (665). În debitul contului 162 ... se înregistrează: ... – diferențele favorabile de curs valutar ... (765).”

— *OMFP 1802/2014, Capitolul 16, funcțiunea contului 162 „Credite bancare pe termen lung”.*
:::

## Regula de semn, pas cu pas

Creditul e o **datorie** a firmei față de bancă — regula de semn pentru datorii e inversă față de creanțe sau disponibilități:

- **Cursul BNR crește** (leul se depreciază) → soldul creditului, exprimat în lei, crește → **pierdere** din curs valutar → `665 = cont_credit`.
- **Cursul BNR scade** (leul se apreciază) → soldul creditului, exprimat în lei, scade → **câștig** din curs valutar → `cont_credit = 765`.

Diferența se calculează întotdeauna ca produs între suma rămasă în valută și variația de curs (curs nou minus curs vechi), nu ca diferență între solduri absolute — altfel rambursările parțiale denaturează calculul.

::: ghid-exemplu
Un credit are un sold rămas de 8.000 EUR, înregistrat la cursul de evidență 5,00 lei/EUR. La sfârșitul lunii, cursul BNR e 4,95 lei/EUR (leul s-a apreciat). Diferența = 8.000 × (5,00 − 4,95) = 400 lei, favorabilă pentru firmă (datoria valorează mai puțin în lei) → `1621 = 765`, 400 lei.

Luna următoare, firma plătește o rată de 1.000 EUR la cursul zilei, 5,03 lei/EUR. Soldul de evidență de dinainte de plată era 4,95 lei/EUR pentru cei 1.000 EUR rambursați (4.950 lei), dar plata efectivă costă 5.030 lei → diferență nefavorabilă de 80 lei → `665 = 5121`, 80 lei, alături de nota de rambursare `1621 = 5121`, 4.950 lei.
:::

## Ce se greșește în practică

- Se inversează sensul: se înregistrează câștig când cursul crește, ca și cum creditul ar fi o creanță — pentru o datorie, e exact invers.
- Se calculează diferența pe soldul total al creditului din bilanț, nu pe soldul rămas efectiv în valută la data reevaluării (după eventuale rambursări parțiale).
- Se omite reevaluarea de sfârșit de lună atunci când nu a avut loc nicio plată — pct. 322 cere recunoașterea lunară a diferenței, nu doar la decontare.
- Se reevaluează doar principalul, ignorând dobânda angajată și neplătită aflată pe 1682, dacă a fost calculată tot în valută.

## Ce face iConta.eu

Motorul dedicat diferențelor de curs, `core/diferente_curs.py`, implementează exact această regulă de semn: funcția `diferenta(valoare_valuta, curs_initial, curs_final, tip)` calculează câștigul/pierderea în funcție de `tip` (`"creanta"`, `"disponibil"` sau `"datorie"`) — pentru `"datorie"`, un curs final mai mare produce cont `"665"`, iar unul mai mic produce cont `"765"`, exact invers față de creanțe și disponibilități.

Pentru reevaluarea lunară a soldului unui credit, se folosește funcția `reevaluare_sold(sold_valuta, curs_evidenta, curs_bnr_sfarsit_luna, tip, cont_sold)`, apelată din use-case-ul `reevaluare_valuta()` pe ruta `/tenants/{tenant_id}/reevaluare-valuta`; nota generată e datată în ziua reevaluării, cu descrierea „Reevaluare solduri valuta la [data] (curs BNR)”. Pentru diferența apărută la o plată efectivă (rată sau dobândă), funcția `nota_decontare(valoare_valuta, curs_factura, curs_decontare, tip, cont_tert, cont_banca)` generează atât nota de plată, cât și linia de diferență de curs, într-o singură operațiune.

[iConta.eu](/)
