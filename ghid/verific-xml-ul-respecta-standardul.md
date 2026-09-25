---
title: "Cum verific dacă XML-ul respectă standardul RO_CIUS?"
description: "Ce este standardul RO_CIUS pentru factura electronică și cum se verifică structural o factură XML contra validatorului oficial ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific dacă XML-ul respectă standardul RO_CIUS?

O factură electronică nu e „validă" doar pentru că fișierul XML se deschide fără erori — trebuie să respecte specificațiile tehnice naționale RO_CIUS, care detaliază, peste standardul european, exact ce elemente sunt obligatorii și cum trebuie completate pentru factura românească.

## Temeiul legal

::: ghid-temei
„k) specificaţiile naţionale de utilizare a facturii electronice - RO_CIUS - specificaţii tehnice de utilizare a elementelor de bază ale facturii electronice aşa cum sunt prevăzute în standardul european SR EN 16931-1, aplicabile la nivel naţional."
— OUG 120/2021, art. 2 lit. k) (sursă: anaf_surse/oug_120_2021.txt)
:::

RO_CIUS nu e un standard nou și paralel, ci o **implementare națională** a standardului european SR EN 16931-1 — stabilește, concret, ce câmpuri sunt obligatorii, opționale sau interzise pentru o factură emisă în România prin sistemul RO e-Factura, peste regulile generale europene.

Verificarea efectivă a conformității unui XML cu RO_CIUS se face contra **validatorului de structură oficial al ANAF** (schematron CIUS-RO), disponibil public, fără necesitatea unui token de autentificare — orice XML poate fi verificat structural înainte de a fi trimis efectiv la ANAF pentru încărcare.

## Ce se greșește în practică

- Se consideră un XML „valid" doar pentru că a fost generat corect sintactic (XML bine format), fără a-l trece prin validatorul de structură ANAF, care verifică regulile specifice RO_CIUS (de exemplu câmpuri obligatorii precum localitatea vânzătorului/cumpărătorului).
- Se confundă validarea de structură (publică, fără drept de acces pe CIF, doar verifică formatul) cu încărcarea efectivă a facturii în sistemul RO e-Factura (care necesită autentificare OAuth și drept pe CIF) — sunt doi pași diferiți, cu URL-uri diferite la ANAF.
- Se ignoră faptul că standardul RO_CIUS poate evolua (noi reguli, noi coduri de eroare); o factură validă acum câteva luni poate necesita ajustări dacă schematronul a fost actualizat între timp.

## Ce face iConta.eu

iConta.eu generează facturile electronice în format XML UBL 2.1 / CIUS-RO și trimite structura rezultată către **validatorul oficial de structură al ANAF** (endpoint public de validare, fără token), pentru a confirma conformitatea cu RO_CIUS înainte de emitere. La data acestui ghid, această validare este cea folosită efectiv de aplicație pentru facturile emise prin RO e-Factura.

[iConta.eu](/)
