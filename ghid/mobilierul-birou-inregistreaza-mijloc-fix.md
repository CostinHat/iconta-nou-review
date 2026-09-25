---
title: "Mobilierul de birou se înregistrează ca mijloc fix sau obiect de inventar?"
description: "De ce mobilierul de birou nu are un răspuns unic — un scaun se încadrează diferit de un set complet de mobilier, în funcție de valoare și de modul de facturare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Mobilierul de birou se înregistrează ca mijloc fix sau obiect de inventar?

Mobilierul e, dintre exemplele obișnuite, cel mai predispus la ambiguitate, pentru că depinde masiv de cum e facturat: o piesă individuală (un scaun) și un set complet (birou + scaun + dulap, facturate împreună ca „mobilier recepție") pot avea încadrări diferite, deși ambele sunt „mobilier de birou". Durata de utilizare, în schimb, rareori e sub un an — deci pentru mobilier, valoarea e practic criteriul decisiv.

## Temeiul legal

::: ghid-temei
„(2) Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; [...] b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; [...] c) are o durată normală de utilizare mai mare de un an."
— Codul fiscal (Legea 227/2015), art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Aplicat la mobilier:

- **Fiecare piesă achiziționată separat se evaluează separat.** Un scaun de 400 lei, cumpărat singur, e clar sub prag — obiect de inventar. Nu se însumează automat cu alte achiziții de mobilier făcute în alte zile sau pe facturi diferite.
- **Un set facturat unitar se evaluează la valoarea totală a facturii**, dacă bunurile formează un ansamblu funcțional unic (de exemplu, un birou de conducere complet, vândut și facturat ca un singur produs) — aici valoarea totală poate depăși ușor pragul de 5.000 lei.
- **Condiția de durată e rareori problema, la mobilier** — un birou sau un dulap au, de regulă, o durată normală de utilizare de câțiva ani, deci condiția c) e practic mereu îndeplinită; decizia se dă aproape mereu pe valoare.
- **Data facturii fixează pragul aplicabil** — 5.000 lei de la 25.02.2026, 2.500 lei anterior.

## Ce se greșește în practică

- Se însumează artificial mai multe piese de mobilier cumpărate separat, în zile diferite, ca să depășească pragul și să justifice amortizarea, deși legea evaluează fiecare intrare la data ei.
- Se separă artificial o factură pentru un set unitar de mobilier în mai multe „bunuri" mici, ca să scape sub prag — practică riscantă, pentru că valoarea fiscală de intrare se raportează la bunul așa cum a intrat efectiv în patrimoniu.
- Se ignoră costurile de transport și montaj la stabilirea valorii fiscale de intrare a mobilierului, deși acestea intră în calculul valorii de intrare.

## Ce face iConta.eu

Din ecranul „Operațiuni speciale" → formularul „Obiecte de inventar (303)", aplicația verifică valoarea introdusă de utilizator (nu suma mai multor facturi) față de pragul legal valabil la data operațiunii, și respinge înregistrarea ca obiect de inventar dacă depășește pragul. Decizia de a introduce o piesă separat sau un set unitar la valoarea totală a facturii rămâne, în continuare, a contabilului, pe baza documentului de achiziție real — aplicația nu grupează sau desparte automat linii de factură.

Câmpul pentru durata normală de utilizare sub un an — relevant mai rar la mobilier, dar prevăzut de lege ca a treia condiție — există în motorul de calcul, dar nu e încă disponibil în formularul din interfață.

[iConta.eu](/)
