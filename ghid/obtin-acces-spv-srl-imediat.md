---
title: "Cum obțin acces SPV pentru un SRL imediat după înființare?"
description: "Firmele au obligația de a comunica cu organul fiscal prin mijloace electronice, prin înrolare în sistemul de comunicare electronică (SPV) — o obligație activă, nu una opțională, chiar de la înființare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum obțin acces SPV pentru un SRL imediat după înființare?

Un SRL proaspăt înființat nu poate amâna la nesfârșit conectarea la Spațiul Privat Virtual — legea tratează comunicarea electronică cu ANAF ca pe o obligație, nu ca pe o comoditate opțională.

## Temeiul legal

::: ghid-temei
„Prin excepție de la alin. (1), contribuabilii/plătitorii persoane juridice, asocieri și alte entități fără personalitate juridică, precum și persoane fizice care desfășoară o profesie liberală sau exercită o activitate economică în mod independent în una dintre formele prevăzute de Ordonanța de urgență a Guvernului nr. 44/2008 [...] sunt obligați să transmită organului fiscal central documente de natura celor prevăzute la alin. (1) prin mijloace electronice de transmitere la distanță în condițiile prezentului articol, respectiv prin înrolarea în sistemul de comunicare electronică dezvoltat de Ministerul Finanțelor/A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 79 alin. (1^1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce presupune obligația pentru un SRL nou:

- Firma trebuie să se **înroleze** în sistemul de comunicare electronică al ANAF (Spațiul Privat Virtual) pentru a putea transmite și primi documente de la organul fiscal — nu e o opțiune rezervată firmelor mari sau celor cu volum mare de declarații.
- Accesul se face pe baza unui certificat digital calificat sau, pentru administrator, prin credențiale proprii de identificare electronică, urmate de asocierea firmei nou-înființate la contul respectiv.
- Practic, pentru un SRL nou, pasul urmează firesc după obținerea CUI-ului: fără înrolare în SPV, firma nu poate depune declarații electronic, nu poate primi notificări sau somații electronice și riscă să rateze termene, aflând despre ele abia din corespondența clasică.

## Ce se greșește în practică

- Se amână înrolarea în SPV până la primul termen de declarare, deși obligația de comunicare electronică e activă din momentul înregistrării fiscale, nu doar de la primul document de transmis.
- Se confundă certificatul digital al administratorului cu accesul SPV al firmei — asocierea CUI-ului firmei la cont este un pas separat, care trebuie făcut explicit după obținerea certificatului.
- Se presupune că un cabinet contabil poate accesa automat SPV-ul unei firme noi fără o autorizare explicită din partea acesteia — accesul trece printr-un proces de asociere/împuternicire distinct.

## Ce face iConta.eu

Conectorul OAuth SPV/ANAF este funcționalitate live în iConta.eu (F176): permite cabinetului să se conecteze o singură dată cu certificatul propriu, prin fluxul oficial OAuth ANAF (logincert.anaf.ro), iar de acolo aplicația poate trimite facturi electronice (e-Factura) și notificări e-Transport pentru firmele pe care cabinetul le gestionează, cu reîmprospătare automată a tokenului la fiecare 90 de zile. Ce nu face aplicația: nu înlocuiește înrolarea inițială în SPV a firmei la ANAF (obținerea certificatului, asocierea CUI-ului la cont) și nu depune direct declarații fiscale prin API — la data acestui ghid nu există un API oficial de transmitere a declarațiilor, acestea rămânând de încărcat manual în SPV după generarea și validarea lor în aplicație.

[iConta.eu](/)
