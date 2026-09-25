---
title: "Ce taxe plătește un asociat angajat în propriul SRL?"
description: "Regimul fiscal aplicabil unui asociat care este și salariat al propriei firme, conform Codului fiscal — aceleași reguli ca pentru orice salariat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce taxe plătește un asociat angajat în propriul SRL?

Un asociat poate fi, în același timp, și salariatul propriei firme, cu contract individual de muncă. Din perspectiva Codului fiscal, calitatea de asociat nu schimbă cu nimic regimul fiscal aplicabil salariului obținut — nu există o categorie fiscală separată „asociat-salariat".

## Temeiul legal

::: ghid-temei
„Sunt considerate venituri din salarii toate veniturile în bani și/sau în natură obținute de o persoană fizică rezidentă ori nerezidentă ce desfășoară o activitate în baza unui contract individual de muncă, a unui raport de serviciu, act de detașare sau a unui statut special prevăzut de lege, indiferent de perioada la care se referă, de denumirea veniturilor ori de forma sub care ele se acordă [...]."
— Legea 227/2015 (Codul fiscal), art. 76 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Am căutat explicit un regim fiscal distinct pentru „asociatul angajat în propria firmă" și nu am găsit unul — Codul fiscal definește veniturile din salarii exclusiv prin raportare la existența unui contract individual de muncă, indiferent de calitatea de asociat a persoanei:

- Un asociat cu contract individual de muncă la propria firmă **plătește exact aceleași taxe ca orice alt salariat**: impozit pe venit 10%, contribuție de asigurări sociale (CAS) 25%, contribuție de asigurări sociale de sănătate (CASS) 10% — calculate pe venitul brut din salariu.
- Situația e diferită de cea a **administratorului neangajat**, care poate primi indemnizație de administrare — un venit asimilat salariilor conform art. 76 alin. (2) lit. d), supus altui regim de contribuții, sau de cea a **dividendelor**, impozitate separat, ca venit din capital.
- Nu există un plafon minim sau maxim special pentru salariul unui asociat-angajat, dincolo de regulile generale (de exemplu, baza minimă de calcul CAS/CASS raportată la salariul minim pe economie, aplicabilă oricărui salariat cu normă întreagă, conform art. 146 alin. (5^6)).
- Cumulul calității de asociat cu cea de salariat este permis fără restricții fiscale speciale — problema care apare frecvent în practică nu e taxarea, ci corecta separare contabilă între salariu, dividende și eventuale sume ridicate fără document justificativ.

## Ce se greșește în practică

- Se presupune, greșit, că un asociat-salariat ar plăti taxe reduse sau ar fi scutit de anumite contribuții pentru că „e patronul firmei" — regimul fiscal e identic cu al oricărui alt angajat.
- Se confundă salariul asociatului cu indemnizația de administrator sau cu retragerile din profit (dividende), tratându-le fiscal la fel, deși au regimuri complet diferite (impozit pe salarii vs. impozit pe dividende).
- Se omite plata efectivă a salariului stabilit prin contract, tratând sumele ca „retrageri" fără bază legală — situație care expune firma la riscul recalificării fiscale a acestor sume.

## Ce face iConta.eu

Am verificat în `core/salarizare.py`: modulul de calcul al salariilor **nu face nicio distincție între un salariat obișnuit și un asociat cu contract individual de muncă** — regulile de calcul (CAS, CASS, impozit, deducere personală) se aplică identic, exact conform art. 76 din Codul fiscal. Separarea corectă între salariu, indemnizație de administrator și dividende rămâne, ca înregistrare distinctă, în sarcina contabilului.

[iConta.eu](/)
