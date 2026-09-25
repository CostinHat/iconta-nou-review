---
title: "Micro pentru firmele care vând pe platforme online"
description: "Regimul micro se aplică identic firmelor care vând prin magazin propriu sau prin platforme/marketplace-uri online — condițiile legale nu diferă după canalul de vânzare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Micro pentru firmele care vând pe platforme online

Canalul de vânzare — magazin propriu, platformă proprie de tip WooCommerce sau marketplace terț — nu schimbă condițiile de încadrare la impozitul pe veniturile microîntreprinderilor. Ce contează e cifra de afaceri realizată, structura acționariatului și existența a cel puțin un salariat, exact ca la orice altă firmă.

## Temeiul legal

::: ghid-temei
„c) a realizat venituri care nu au depăşit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile; [...] g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3)."
— Codul fiscal (Legea 227/2015), art. 47 alin. (1) lit. c), g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Codul fiscal (Legea 227/2015), art. 51 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce nu se schimbă pentru o firmă care vinde pe platforme online:

- Plafonul de venituri (100.000 euro, verificat la cursul de închidere a exercițiului financiar în care s-au înregistrat veniturile) se calculează la fel, indiferent dacă vânzările vin din magazin fizic, site propriu sau marketplace — nu există un plafon separat sau majorat pentru comerțul electronic.
- Condiția de a avea cel puțin un salariat (art. 47 alin. (1) lit. g)) se aplică identic; o firmă „doar online", fără angajați, riscă să nu se încadreze la micro exact ca oricare alta.
- Cota de impozit rămâne 1% din veniturile totale, indiferent de canal — un marketplace nu creează un regim fiscal distinct pentru firma-vânzător.

Ce diferă, în schimb, e organizarea evidenței: vânzările prin platforme terțe implică de regulă un intermediar (marketplace-ul) care reține comisioane și, uneori, colectează plata în numele vânzătorului — venitul impozabil rămâne însă valoarea totală a vânzării către client, nu suma netă încasată după comision, iar comisionul platformei se înregistrează separat, ca o cheltuială deductibilă.

## Ce se greșește în practică

- Se raportează la venit doar suma netă încasată de la marketplace, după reținerea comisionului — venitul impozabil e valoarea integrală a vânzării, comisionul intrând la cheltuieli.
- Se presupune că vânzările printr-o platformă din alt stat membru UE schimbă regimul micro aplicabil firmei — regimul micro e determinat de rezidența fiscală a firmei și de cifra ei de afaceri totală, nu de locul platformei prin care vinde.
- Se omite condiția salariatului doar pentru că activitatea „e automatizată" prin platformă — legea nu face excepție pentru comerțul online.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un conector pentru WooCommerce (`core/woocommerce.py`), care importă comenzile din platformă și le transformă automat în facturi în aplicație (idempotent, pe numărul comenzii). Aplicația **nu verifică însă automat** condițiile de încadrare la regimul micro (plafonul de venituri, condiția salariatului) și nu distinge automat comisionul de platformă de venitul brut al vânzării — aceste calcule și verificări rămân responsabilitatea contabilului, pe baza evidenței contabile generale oferite de aplicație.

[iConta.eu](/)
