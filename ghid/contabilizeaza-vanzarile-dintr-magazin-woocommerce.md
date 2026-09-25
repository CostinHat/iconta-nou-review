---
title: "Cum se contabilizează vânzările dintr-un magazin WooCommerce?"
description: "Principiul de recunoaștere a veniturilor din vânzarea de bunuri se aplică identic vânzărilor online — ce anume automatizează iConta.eu din acest flux și unde se oprește automatizarea."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează vânzările dintr-un magazin WooCommerce?

O vânzare printr-un magazin online nu are un regim contabil separat față de o vânzare „clasică" — principiul de recunoaștere a venitului e același. Ce diferă e doar canalul prin care ajunge comanda la contabilitate, iar aici intervine automatizarea.

## Temeiul legal

::: ghid-temei
„Venituri din vânzări de bunuri [...] În contabilitate, veniturile din vânzări de bunuri se înregistrează în momentul predării bunurilor către cumpărători, al livrării lor pe baza facturii sau în alte condiții prevăzute în contract, care atestă transferul dreptului de proprietate asupra bunurilor respective, către clienți."
— OMFP 1802/2014, Reglementări contabile, pct. 440 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Venitul se recunoaște atunci când bunul e predat/livrat cumpărătorului, pe baza facturii sau a altor condiții contractuale care atestă transferul dreptului de proprietate — nu la momentul plasării comenzii și nu la momentul încasării banilor.
- Regula e generală: se aplică oricărei vânzări de bunuri, indiferent dacă a fost inițiată într-un magazin fizic, telefonic sau online (WooCommerce).
- Pentru vânzarea online, „livrarea pe baza facturii" înseamnă, practic, emiterea facturii corespunzătoare comenzii finalizate (status `completed`/`processing` în WooCommerce) — momentul din care venitul intră în evidența contabilă.

## Ce se greșește în practică

- Se caută un tratament contabil „special" pentru vânzările online, deși principiul de recunoaștere a venitului e identic cu al oricărei alte vânzări de bunuri.
- Se interpretează statusul „de preluat" al unei facturi generate automat ca fiind o proformă sau un document neterminat — de fapt e o factură emisă, valabilă fiscal, care doar așteaptă pasul de preluare în contabilitate (recunoașterea ei explicită de către contabil).
- Se presupune că o comandă cu numele unei firme completat la datele de facturare va fi înregistrată ca vânzare către acea firmă, cu CUI propriu — nu e cazul, vezi mai jos.

## Ce face iConta.eu

Comenzile WooCommerce finalizate sunt transformate automat în facturi emise, prin aceeași funcție de emitere folosită și pentru facturarea manuală din aplicație — nu există un flux contabil separat, dedicat vânzărilor online. Factura rezultată are statusul implicit **„de preluat"**: e o factură emisă, declarabilă, dar care semnalează contabilului că mai are de făcut un pas (recunoașterea/preluarea ei în contabilitatea curentă), nu că ar fi incompletă. Contul de venit se stabilește automat pe baza cuvintelor-cheie din descrierea produsului (potrivit nomenclatorului OMFP 1802/2014) sau, dacă nu se găsește o potrivire, prin recunoaștere automată — mecanism comun tuturor facturilor emise din aplicație, nu unul specific WooCommerce. O limită importantă de reținut: **orice comandă WooCommerce e facturată mereu ca vânzare către o persoană fizică**, indiferent dacă la datele de facturare din comandă apare un nume de firmă — iConta.eu nu are azi un mecanism de a factura automat o comandă WooCommerce către o firmă cu CUI propriu.

[iConta.eu](/)
