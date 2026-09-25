---
title: "Statistici de numerar pentru management 2026"
description: "Ce evidență a numerarului cere legea (Registrul de casă) și diferența față de o statistică de management, care nu este o obligație legală distinctă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Statistici de numerar pentru management 2026

Legea nu cere firmelor o „statistică de numerar pentru management" ca document distinct — obligația legală acoperită este ținerea Registrului de casă, care înregistrează zilnic încasările, plățile și soldul de numerar. Orice raportare suplimentară, agregată la nivel de lună/an sau pe categorii, pentru uzul intern al managementului, este o decizie de gestiune a firmei, nu o cerință a legislației contabile sau fiscale.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP nr. 2.634/2015, Anexa 2 – Norme specifice de întocmire și utilizare a formularelor, Registrul de casă (cod 14-4-7/a) (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce rezultă din text pentru evidența numerarului:

- Registrul de casă este documentul legal obligatoriu, cu trei funcții: evidență operativă zilnică, stabilire a soldului de casă la finalul fiecărei zile și bază pentru înregistrarea contabilă a operațiunilor de casă.
- El se completează **zilnic**, pe baza documentelor justificative (chitanțe, dispoziții de încasare/plată, bonuri fiscale) — nu retroactiv sau agregat pe perioade mai lungi.
- Dincolo de acest registru, legea nu impune un format standard de „statistici" sau „rapoarte de management" privind numerarul (de exemplu, evoluția lunară a soldului de casă, structura încasărilor pe categorii de clienți) — acestea sunt instrumente interne de gestiune, utile firmei, dar nu ținute în baza unei obligații legale distincte.

## Ce se greșește în practică

- Se confundă obligația legală (Registrul de casă, zilnic) cu o presupusă obligație de raportare periodică agregată către un organ de control — nu există o asemenea cerință generică în legislația verificată.
- Se renunță la completarea zilnică a Registrului de casă, considerându-se suficientă o „statistică" lunară realizată ulterior — aceasta nu înlocuiește obligația legală de înregistrare operativă zilnică.
- Se așteaptă ca un instrument de „statistici de management" să aibă valoare probatorie în fața organului fiscal, similar cu Registrul de casă — documentul cu valoare legală rămâne registrul, nu rapoartele interne derivate din el.

## Ce face iConta.eu

La data acestui ghid, iConta.eu ține un registru de casă cu sold rulant, calculat operațiune cu operațiune (`core/casa.py`, funcția `registru_casa`), care poate fi folosit ca bază atât pentru evidența legală, cât și pentru o privire de ansamblu asupra fluxului de numerar. Aplicația nu are însă un modul dedicat de „statistici de numerar pentru management" (grafice, tendințe, comparații pe perioade) — dincolo de registrul de casă și de verificarea plafoanelor legale (`verifica_plafon`), orice analiză suplimentară a numerarului rămâne de făcut manual, pe baza datelor exportate din aplicație.

[iConta.eu](/)
