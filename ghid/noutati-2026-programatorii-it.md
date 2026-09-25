---
title: "Noutăți 2026 pentru programatorii IT"
description: "De ce nu mai există, în 2026, o scutire de impozit pe venit pentru angajații din creare de programe pentru calculator — și de la ce dată a dispărut."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Noutăți 2026 pentru programatorii IT

Pentru mulți angajatori din IT, „noutatea" pe care o caută de fapt este dacă mai există, în vreo formă, vechea scutire de impozit pe venit pentru salariații din activitatea de creare de programe pentru calculator. Răspunsul scurt: nu — facilitatea a fost eliminată din Codul fiscal începând cu 1 ianuarie 2025 și rămâne eliminată și în 2026. Nu există, la acest moment, niciun semnal legislativ de reintroducere.

## Temeiul legal

::: ghid-temei
„2. Abrogat.
(la 01-01-2025, Punctul 2., Articolul 60, Capitolul I, Titlul IV a fost abrogat de Punctul 7., Articolul LXIV din ORDONANȚA DE URGENȚĂ nr. 156 din 30 decembrie 2024, publicată în MONITORUL OFICIAL nr. 1334 din 31 decembrie 2024)"
— Codul fiscal (Legea 227/2015), art. 60 pct. 2, formă consolidată (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Art. 60 din Codul fiscal enumera categoriile de venituri scutite integral de impozitul pe venit; punctul 2 era temeiul scutirii pentru salariile obținute din activitatea de creare de programe pentru calculator (condiții stabilite anterior prin ordin comun MFP/MMSS/MCID).
- Acest punct a fost abrogat expres, cu efect de la 1 ianuarie 2025, prin OUG 156/2024 — nu printr-o reformulare care să restrângă facilitatea, ci prin eliminarea ei completă din text.
- Aceeași ordonanță a abrogat, de la aceeași dată, și punctele 5 și 7 ale art. 60 (alte scutiri sectoriale de venit salarial din Codul fiscal), semn al aceleiași direcții de politică fiscală: reducerea numărului de facilități sectoriale de impozit pe venit.

## Ce se greșește în practică

- Se presupune, din obișnuință, că scutirea IT există în continuare cu un plafon lunar (așa cum funcționa înainte de abrogare) — de fapt nu mai există deloc, indiferent de nivelul salariului.
- Se caută o „noutate 2026" specifică programatorilor, când modificarea reală s-a produs deja cu un an înainte (01.01.2025); pentru 2026 nu s-a identificat nicio schimbare suplimentară a regimului fiscal al angajaților IT.
- Se calculează salariul net al unui angajat IT ca înainte de 2025 (fără impozit pe venit), ceea ce produce o subdeclarare a impozitului reținut la sursă.

## Ce face iConta.eu

Această temă face parte din **F060 — Monitorul fiscal**, mecanismul intern (`core/monitor_fiscal.py`) care citește săptămânal noutățile legislative de la ANAF/Ministerul Finanțelor, le filtrează cu ajutorul AI după relevanță (TVA, salarii, plafoane, declarații, dividende) și trimite un rezumat prin email către administratorul platformei. F060 **nu** e un modul orientat spre utilizatorul contabil și nu generează automat articole afișate în aplicație — e un cron intern, fără ecran dedicat. Ghidurile de acest tip, inclusiv cel de față, sunt sinteze editoriale redactate manual, pe bază de text de lege verificat direct la sursă, nu un produs al monitorului însuși. Calculul efectiv al salariului (inclusiv impozitul pe venit reținut la sursă, fără nicio scutire specifică IT) se face în modulul de salarizare al aplicației, conform regulilor generale în vigoare.

[iConta.eu](/)
