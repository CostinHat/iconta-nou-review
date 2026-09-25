---
title: "Cum mă înscriu în SPV pentru prima dată"
description: "Cum se identifică un contribuabil în relația electronică cu ANAF, conform Codului de procedură fiscală, pentru a putea folosi Spațiul Privat Virtual."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum mă înscriu în SPV pentru prima dată

Spațiul Privat Virtual (SPV) este canalul prin care contribuabilii comunică electronic cu ANAF — depun declarații, primesc notificări, verifică situația fiscală. Legea nu descrie SPV ca „aplicație", ci ca unul dintre mijloacele prin care se realizează identificarea contribuabilului în mediul electronic, iar modul de identificare diferă fundamental între firme și persoane fizice.

## Temeiul legal

```
::: ghid-temei
„(1) Contribuabilul/Plătitorul care depune cereri, înscrisuri sau documente la organul fiscal, prin mijloace electronice de transmitere la distanță, se identifică în relația cu organul fiscal astfel:
a) persoanele juridice, asocierile și alte entități fără personalitate juridică, precum și persoanele fizice care desfășoară activități economice în mod independent ori exercită profesii libere se identifică numai cu certificate calificate;
b) persoanele fizice, altele decât cele prevăzute la lit. a), se identifică prin intermediul furnizorilor de servicii publice de autentificare electronică autorizați potrivit legii sau prin diverse dispozitive, cum ar fi certificat calificat, credențiale de tip utilizator/parolă însoțite de liste de coduri de autentificare de unică folosință, telefon mobil, digipass ori alte dispozitive stabilite prin ordin al președintelui A.N.A.F."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 80 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::
```

Ce rezultă practic din text pentru înscrierea în SPV:

- **Firmele (SRL, SA), PFA-urile și profesiile libere se identifică exclusiv cu certificat digital calificat** — nu există, pentru ele, o variantă „simplă" cu user/parolă. Acest lucru înseamnă achiziția unui certificat de la un furnizor acreditat, înainte de a putea accesa SPV.
- **Persoanele fizice** (care nu desfășoară activitate economică) au mai multe variante de identificare acceptate: certificat calificat, dar și credențiale utilizator/parolă cu coduri de unică folosință, autentificare prin telefon mobil sau alte metode stabilite prin ordin al președintelui ANAF (inclusiv, în practică, videoidentificarea).
- Pentru firmele, asocierile și entitățile fără personalitate juridică, precum și pentru PFA/II/IF, comunicarea electronică cu organul fiscal **nu e opțională**: legea le obligă să transmită documentele prin mijloace electronice, prin înrolarea în sistemul de comunicare electronică al ANAF — documentele depuse pe hârtie, în locul canalului electronic, nu sunt luate în considerare.

## Ce se greșește în practică

- Se încearcă înscrierea unei firme în SPV cu metodele „ușoare" disponibile persoanelor fizice (user/parolă, cod OTP) — pentru persoane juridice și PFA, legea impune certificat calificat, fără excepție.
- Se confundă certificatul digital calificat cu semnătura electronică simplă folosită ocazional pentru alte platforme — certificatul necesar SPV trebuie emis de un furnizor acreditat și e distinct de alte instrumente de semnare.
- Se amână înscrierea firmei în SPV, considerând-o opțională — legea o tratează ca obligație, iar documentele depuse pe hârtie de o firmă obligată la comunicare electronică nu sunt luate în considerare de organul fiscal.

## Ce face iConta.eu

La data acestui ghid, `core/spv_conector.py` implementează conectorul OAuth2 dintre iConta.eu și ANAF pentru accesul la SPV, cu stocare criptată a token-urilor de acces și reîmprospătare automată a acestora — confirmat direct din cod. Acest conector presupune însă că firma (sau cabinetul contabil) are deja un cont SPV funcțional, autorizat cu certificatul digital calificat descris mai sus: iConta.eu preia și folosește accesul deja acordat de ANAF, dar **nu înlocuiește** pasul inițial de obținere a certificatului și de înregistrare a contribuabilului în SPV, care rămâne o procedură realizată direct pe portalul ANAF.

[iConta.eu](/)
