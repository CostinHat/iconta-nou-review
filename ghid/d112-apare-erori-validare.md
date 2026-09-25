---
title: "Ce faci dacă D112 apare cu erori la validare"
description: "Ce drept ai de corectare când Declarația 112 nu trece validarea și ce pași urmezi pentru a o retransmite corect."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă D112 apare cu erori la validare

D112 e declarația care centralizează, lunar, obligațiile privind contribuțiile sociale, impozitul pe venit și evidența nominală a asiguraților. Când validatorul ANAF o respinge, ea nu e considerată depusă — trebuie corectată și retransmisă, iar dreptul de a face asta e reglementat expres, indiferent de motivul tehnic al erorii.

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Codul de procedură fiscală nu descrie erorile tehnice de validare XML ale D112 — acelea țin de structura formularului stabilită de ANAF, nu de lege. Ce transează legea e dreptul contribuabilului de a corecta oricând, în termenul de prescripție.

- **O respingere la validare nu e o depunere reușită** — declarația nu produce efecte până nu trece integral validarea și e înregistrată.
- **Corectarea se face prin declarație rectificativă**, care înlocuiește complet varianta anterioară pentru perioada respectivă, nu doar câmpurile greșite.
- **Termenul de corectare e cel de prescripție** a dreptului organului fiscal de a stabili creanțe fiscale — practic ani de zile, nu doar câteva luni de la scadență.

## Ce se greșește în practică

- Se ignoră eroarea de validare și se lasă declarația "în așteptare", ceea ce echivalează cu nedepunere și poate atrage sancțiuni pentru întârziere.
- Se corectează doar simptomul semnalat de validator (de exemplu o sumă), fără să se verifice dacă eroarea structurală provine dintr-o secțiune anterioară a declarației care afectează parsarea întregului fișier.
- Se retransmite aceeași declarație nemodificată, presupunând că a fost o eroare temporară a sistemului ANAF, fără să se verifice mesajul exact al erorii.

## Ce face iConta.eu

Modulul de generare D112 din iConta.eu construiește declarația din datele de salarizare introduse (contract, stat de plată, concedii) și produce fișierul XML pe structura publicată de ANAF. Aplicația nu are acces la validatorul oficial ANAF în timp real din interfața contabilului — validarea finală se face la depunere, pe portalul SPV sau prin serviciul ANAF, iar mesajul de eroare primit de acolo trebuie interpretat manual pentru identificarea câmpului sau secțiunii afectate, înainte de regenerarea și retransmiterea declarației.

[iConta.eu](/)
