---
title: "Se poate corecta D406 înainte de un control ANAF?"
description: "Mecanismul declarației rectificative pentru D406 (SAF-T) și ce trebuie să cuprindă, potrivit instrucțiunilor ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se poate corecta D406 înainte de un control ANAF?

Da — D406 (Fișierul standard de control fiscal, SAF-T) poate fi corectat oricând, inclusiv înainte de un control, prin redepunere pentru aceeași perioadă. Legea nu leagă dreptul de corectare de existența sau iminența unui control; declarația rectificativă este mecanismul standard prevăzut chiar de instrucțiunile de completare.

## Temeiul legal

::: ghid-temei
„18. Prima Declarație informativă D406 validată, depusă pentru o lună sau un trimestru de către un contribuabil/plătitor este considerată declarație inițială. Declarațiile ulterioare depuse pentru aceeași perioadă (lună/trimestru) sunt automat considerate declarații rectificative. [...] 21. Declarațiile rectificative care se depun pentru corectarea unei erori materiale, omisiuni etc. trebuie să cuprindă toate informațiile din declarația inițială, plus cele asupra cărora s-au efectuat corecții."
— OPANAF nr. 1.783/2021, Instrucțiuni de completare a Declarației informative D406, pct. 18 și pct. 21 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Mecanismul practic, conform sursei:

- Nu există o procedură separată de „declarație rectificativă" cu un buton distinct — orice **redepunere validă pentru aceeași perioadă** (lună sau trimestru) este calificată automat de sistem drept rectificativă.
- Declarația rectificativă trebuie să conțină **integral** informațiile din declarația inițială, nu doar diferențele — un fișier SAF-T „parțial", cu doar corecțiile, nu respectă norma.
- Corectarea se poate face oricând până la reguli generale de prescripție fiscală; sursele disponibile nu prevăd o limitare specifică legată de existența unui control în derulare pentru D406 (spre deosebire de alte declarații, unde rectificarea în timpul unei inspecții poate avea reguli speciale — verificați situația concretă separat).

## Ce se greșește în practică

- Se încearcă transmiterea unui fișier SAF-T care conține doar liniile corectate, crezând că sistemul le va „adăuga" la declarația inițială — norma cere fișierul complet, cu tot conținutul.
- Se așteaptă declanșarea unui control pentru a corecta erorile deja identificate în D406, deși corectarea poate (și ar trebui) făcută imediat ce eroarea e descoperită.
- Se ignoră mesajele de eroare/avertizare primite la încărcare (disponibile în fișierul „Validator" și, pentru contribuabilii înrolați, în secțiunea „Mesaje" din SPV), lăsând erori nesemnalate să rămână necorectate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează Declarația D406 din datele contabile ale perioadei (conturi, clienți, furnizori, jurnal), pe baza motorului intern de construire SAF-T. Aplicația **nu marchează sau nu transmite** automat fișierul ca „rectificativă" către ANAF — regenerarea fișierului pentru o perioadă deja raportată produce un nou XML complet, pe care utilizatorul trebuie să îl încarce manual în portalul ANAF, unde sistemul îl va califica automat drept declarație rectificativă.

[iConta.eu](/)
