---
title: "Cum conectez magazinul WooCommerce la iConta?"
description: "Pașii reali pentru a lega un magazin WooCommerce de iConta.eu, plus limita practică a validării: salvarea configurației nu testează conexiunea la magazin."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum conectez magazinul WooCommerce la iConta?

Dacă vinzi printr-un magazin WooCommerce, iConta.eu poate prelua automat comenzile și le poate transforma în facturi emise, fără să introduci manual fiecare vânzare. Conectarea se face o singură dată, din ecranul „Magazin online", și presupune trei informații pe care le iei chiar din administrarea magazinului tău WordPress/WooCommerce.

## Temeiul legal

Conectarea unui magazin online la o aplicație de contabilitate e o operațiune pur tehnică, de configurare — nu există un act normativ care să reglementeze *cum* se face această conectare. Regulile fiscale (conținutul obligatoriu al facturii, termenele de emitere etc.) se aplică facturilor rezultate din comenzi, nu procedurii de conectare în sine, motiv pentru care acest ghid nu citează un temei legal pentru pasul de conectare — ar fi un citat corect în litera lui, dar fără legătură cu întrebarea pusă.

## Ce se greșește în practică

- Se presupune că, odată salvate URL-ul magazinului, Consumer Key și Consumer Secret, conexiunea e deja testată și funcțională — de fapt, salvarea validează doar *formatul* URL-ului (trebuie să înceapă cu `http`/`https` și să conțină un punct în domeniu), nu face niciun apel real către magazin.
- Se descoperă abia la prima sincronizare (automată sau manuală) că o cheie a fost copiată greșit sau că magazinul e temporar inaccesibil — eroarea de conectare nu apare la salvarea configurației.
- Se așteaptă apariția facturilor doar a doua zi dimineață, fără să se știe că există și un buton de sincronizare manuală, disponibil oricând.

## Ce face iConta.eu

Din ecranul „Magazin online", completezi trei câmpuri: **URL-ul magazinului**, **Consumer Key** și **Consumer Secret** (generate din WooCommerce → Setări → Avansat → REST API). Salvarea acestora (rută `PUT /tenants/{id}/woocommerce/config`, disponibilă doar pentru rolul de admin firmă) verifică doar formatul URL-ului, nu conexiunea reală — un URL fără schema `http(s)` sau fără punct în domeniu e respins, dar un URL valid ca formă, chiar dacă e greșit sau magazinul e nefuncțional, e acceptat fără avertisment. Odată configurat, apare și un buton **„Sincronizează acum"**, care declanșează manual, oricând, aceeași funcție folosită și de rularea automată zilnică (07:30). Eroarea reală de conectare (chei greșite, magazin indisponibil) se vede abia atunci, sub forma unui mesaj de eroare la sincronizare, nu la salvarea configurării.

[iConta.eu](/)
