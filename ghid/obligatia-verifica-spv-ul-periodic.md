---
title: "Obligația de a verifica SPV-ul periodic"
description: "De ce comunicarea electronică prin Spațiul Privat Virtual are aceleași efecte juridice ca notificarea pe hârtie, potrivit Codului de procedură fiscală — chiar dacă firma nu accesează contul."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Obligația de a verifica SPV-ul periodic

Legea nu obligă explicit contribuabilul să „verifice SPV-ul o dată pe săptămână" ca atare — dar odată înrolat (obligatoriu, pentru firme și PFA) în sistemul de comunicare electronică, actele ANAF se consideră comunicate din momentul publicării lor acolo, indiferent dacă firma le-a citit sau nu.

## Temeiul legal

::: ghid-temei
„Actul administrativ fiscal emis în formă electronică se comunică prin mijloace electronice de transmitere la distanță [...], iar acesta se consideră comunicat la data punerii la dispoziția contribuabilului/plătitorului prin aceste mijloace."
— Legea nr. 207/2015, art. 47 alin. (15) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Comunicarea actelor administrative fiscale prevăzute la art. 46 alin. (6), pentru contribuabilii/plătitorii care au fost înregistrați din oficiu potrivit alin. (16^1) și nu au accesat sistemul de comunicare electronică în termen de 15 zile de la comunicarea datelor referitoare la înregistrare, se realizează doar prin publicitate potrivit alin. (5)-(7)."
— Legea nr. 207/2015, art. 47 alin. (16^2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din aceste texte:

- Un act fiscal transmis electronic (decizie de impunere, notificare, somație) se consideră **comunicat legal din momentul în care e pus la dispoziție** în SPV — nu din momentul în care firma îl deschide sau îl citește efectiv.
- Consecința practică: termenele de contestație, de plată sau de răspuns curg de la data publicării în SPV, nu de la data la care contabilul „a apucat" să verifice contul — de aici rezultă, indirect, necesitatea unei verificări periodice.
- Pentru firmele/persoanele fizice cu activitate independentă (obligate să comunice exclusiv electronic cu ANAF), există un mecanism suplimentar de siguranță pentru ANAF, nu pentru contribuabil: dacă cel înregistrat din oficiu nu accesează sistemul în 15 zile de la înregistrare, comunicarea trece pe publicitate (afișare pe pagina ANAF) — dar acest mecanism nu absolvă contribuabilul de a fi luat deja cunoștință, ci confirmă doar o cale alternativă de comunicare pentru ANAF.
- Legea nu prevede un interval fix („o dată pe săptămână", „zilnic") pentru verificarea SPV — obligația de facto rezultă din faptul că, odată comunicat, actul își produce efectele indiferent de comportamentul contribuabilului.

## Ce se greșește în practică

- Se presupune că un act „necitit" în SPV nu produce efecte juridice — legea spune explicit contrariul: comunicarea se consideră făcută la data punerii la dispoziție, nu la data citirii.
- Se verifică SPV-ul doar quando se așteaptă un răspuns la o cerere depusă, ignorând actele emise din inițiativa ANAF (notificări de conformare, somații, decizii de impunere), care pot ajunge oricând.
- Se lasă verificarea SPV exclusiv în sarcina contabilului extern, fără ca administratorul firmei să fie informat că termenele legale curg indiferent de frecvența cu care biroul contabil accesează contul.

## Ce face iConta.eu

iConta.eu nu are, la data acestui ghid, o integrare care să descarce automat sau să notifice în aplicație actele publicate în Spațiul Privat Virtual al firmei — modulele SPV existente (`core/spv_conector.py`, `core/spv_poll.py`, `core/spv_receive.py`) gestionează exclusiv fluxul de e-Factura (trimitere/primire facturi electronice, autorizare OAuth), nu comunicarea actelor administrativ-fiscale de la art. 47. Verificarea periodică a SPV pentru notificări și decizii ANAF rămâne, deocamdată, o obligație pe care contabilul o îndeplinește direct pe portalul ANAF.

[iConta.eu](/)
