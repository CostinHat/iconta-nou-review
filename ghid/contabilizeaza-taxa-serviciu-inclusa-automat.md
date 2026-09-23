---
title: Cum se contabilizează taxa de serviciu inclusă automat pe nota de plată a unui restaurant?
description: O taxă de serviciu adăugată automat pe notă nu e bacșiș din punct de vedere legal — regimul de la Legea 376/2022 se aplică doar sumei alese voluntar de client.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează taxa de serviciu inclusă automat pe nota de plată a unui restaurant?

Înainte de contabilizare, trebuie lămurită o distincție care schimbă complet tratamentul: legea bacșișului din HoReCa (Legea 376/2022) se aplică doar sumei pe care clientul o alege voluntar, pe o rubrică dedicată din nota de plată. O „taxă de serviciu" adăugată automat, ca procent fix, indiferent de voința clientului, nu se încadrează în definiția legală a bacșișului.

## Temeiul legal

::: ghid-temei
„Prin bacșiș se înțelege orice sumă de bani oferită în mod voluntar de client, în plus față de contravaloarea bunurilor livrate sau a serviciilor prestate de către operatorii economici care desfășoară activități corespunzătoare codurilor CAEN: 5610 - «Restaurante», 5630 - «Baruri și alte activități de servire a băuturilor». Bacșișul nu poate fi asimilat, din punctul de vedere al TVA, unei livrări de bunuri sau unei prestări de servicii."

*(Legea nr. 376/2022 pentru modificarea și completarea OUG nr. 28/1999, art. 2^3 alin. (1))*
:::

## De ce contează diferența

Legea condiționează explicit tot regimul special (fără TVA, fără impozit pe profit/venit la firmă, impozit 10% la salariat, fără CAS/CASS) de caracterul **voluntar** al sumei. O taxă de serviciu inclusă automat, pe care clientul n-o poate refuza sau ajusta, nu îndeplinește această condiție — e, din punct de vedere legal, parte din prețul serviciului prestat, nu bacșiș.

În plus, legea interzice explicit condiționarea livrării/prestării de acordarea bacșișului (alin. (4)) — o taxă „obligatorie" adăugată automat riscă exact acest tip de problemă, chiar dacă e numită „bacșiș" pe bon.

## Ce se greșește în practică

- **Se tratează orice sumă suplimentară de pe notă ca „bacșiș"**, indiferent dacă a fost aleasă voluntar de client sau adăugată automat de restaurant.
- **O taxă de serviciu obligatorie e trecută prin conturile de datorii ale F010** (461/462), ca și cum ar fi bacșiș, deși nu îndeplinește condiția de voluntariat de la alin. (1) — ceea ce ar scoate nejustificat suma din baza de TVA și de venituri a firmei.
- **Nu se verifică modul de prezentare pe nota de plată** — rubricile de 0-15% + sumă fixă, cerute la alin. (3), presupun o alegere reală a clientului, nu un procent fix inserat automat.

## Ce face iConta.eu

Motorul F010 din iConta.eu (`core/bacsis.py`) implementează exact traseul bacșișului voluntar definit de Legea 376/2022 — încasare pe bon + distribuire la salariați cu impozit 10%. O taxă de serviciu obligatorie, care nu e bacșiș în sensul legii, nu are un tratament dedicat identificat în acest modul; ea urmează regimul normal al prețului serviciului prestat (parte din baza de TVA și din venitul firmei), nu regimul special F010. Dacă operatorul aplică efectiv o astfel de taxă obligatorie, tratamentul ei corect ține de o verificare separată, nu de acest modul.

[iConta.eu](/)
