---
title: "Cum transmit factura către o persoană fizică prin SPV"
description: "Ce prevede legea despre transmiterea facturilor emise către persoane fizice prin sistemul național RO e-Factura și cum diferă de relația B2B."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum transmit factura către o persoană fizică prin SPV

Sistemul RO e-Factura a fost gândit inițial pentru relația dintre operatori economici (B2B) și pentru achizițiile publice (B2G). Facturile emise către persoane fizice — consumatori finali — ridică o întrebare diferită: intră sau nu sub aceeași obligație de transmitere prin sistemul național.

## Temeiul legal

::: ghid-temei
„n) relația comercială dintre doi operatori economici - B2B - tranzacția având ca obiect execuția de lucrări, livrarea de bunuri/produse și/sau prestarea de servicii dintre doi operatori economici."
— OUG nr. 120/2021, art. 2 alin. (1) lit. n) (sursă: anaf_surse/oug_120_2021.txt)
:::

**Limitare declarată:** definiția de mai sus delimitează explicit relația B2B (între doi operatori economici) ca obiect central al reglementării inițiale a sistemului RO e-Factura, alături de relația B2G (către autorități contractante). Sursele verificate **nu conțin un text distinct, explicit, care să reglementeze regimul de transmitere a facturilor emise către persoane fizice (relația B2C)** prin sistemul RO e-Factura — deși obligativitatea facturării electronice B2B a fost extinsă succesiv prin acte ulterioare (Legea nr. 296/2023 și modificările ei), textul exact al clauzei privind opțiunea de transmitere facultativă către persoane fizice nu a fost identificat verbatim în corpusul disponibil. Redirecționăm onest: cadrul cert e obligația de facturare electronică în relația B2B/B2G, definită de OUG 120/2021; pentru facturile către persoane fizice, regimul aplicabil (obligatoriu sau opțional, după caz) trebuie verificat direct în forma consolidată curentă a Legii nr. 296/2023 și în procedura ANAF de utilizare a sistemului, aprobată prin ordin al ministrului finanțelor.

## Ce se greșește în practică

- Se presupune că orice factură emisă de o firmă, indiferent de destinatar, trebuie transmisă automat prin RO e-Factura — regimul obligatoriu a fost construit inițial pentru relația dintre operatori economici, nu pentru consumatori finali.
- Se confundă transmiterea facturii prin SPV (canalul electronic de comunicare cu ANAF, disponibil oricărui contribuabil) cu obligația specifică de facturare electronică B2B/B2G din RO e-Factura — sunt mecanisme diferite, chiar dacă ambele folosesc autentificarea ANAF.
- Se ignoră faptul că, pentru persoana fizică fără cod de identificare fiscală structurat similar unui operator economic, structura tehnică a facturii electronice (identificatori, cod de înregistrare) poate impune adaptări față de o factură B2B standard.

## Ce face iConta.eu

Verificat în cod: `core/efactura_send.py` și `core/efactura_trimitere.py` gestionează trimiterea facturilor prin sistemul RO e-Factura, dar nu conțin o ramificație de tratament separată pentru destinatari persoane fizice (nu am găsit referințe la CNP sau la un flux distinct „persoană fizică" în aceste module). Aplicația tratează transmiterea facturilor conform fluxului standard B2B/B2G; pentru facturile emise către persoane fizice, includerea sau nu în fluxul de transmitere prin SPV rămâne o decizie pe care contabilul o ia în funcție de regimul aplicabil firmei respective.

[iConta.eu](/)
