---
title: "Termene pentru firmele cu TVA la încasare"
description: "Termenele-cheie pentru intrarea, rămânerea și ieșirea din sistemul TVA la încasare, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Termene pentru firmele cu TVA la încasare

Sistemul TVA la încasare are propriile termene de notificare, distincte de termenele obișnuite de depunere a decontului. Ratarea lor are consecințe directe — inclusiv radierea din oficiu.

## Temeiul legal

::: ghid-temei
Art. 324 alin. (16) Cod fiscal: „A.N.A.F. organizează Registrul persoanelor impozabile care aplică sistemul TVA la încasare... Registrul este public și se afișează pe site-ul A.N.A.F." — verificat în `cod_fiscal_227_2015_consolidat.txt`.
:::

Termenele confirmate în Codul fiscal (art. 324) și în regulile de plafon (art. 282 alin. 3, modificat prin OUG 8/2026):

- **Notificare de intrare**: până la data de 20 inclusiv a lunii anterioare începerii perioadei fiscale din care se va aplica sistemul (art. 324 alin. 12).
- **Opțiune tacită**: dacă în anul precedent firma a aplicat deja sistemul și cifra de afaceri nu a depășit plafonul, nu mai e nevoie de o notificare nouă — continuarea e automată (tot art. 324 alin. 12).
- **Depășirea plafonului în cursul anului**: notificare până la data de 20 a lunii următoare celei în care s-a depășit plafonul (art. 324 alin. 14). Nedepunerea duce la radiere din oficiu.
- **Rămânerea minimă în sistem**: cel puțin până la sfârșitul anului calendaristic al opțiunii (art. 282 alin. 5), cu excepția depășirii plafonului.
- **Ieșire voluntară**: prin notificare depusă între 1 și 20 ale lunii, dar nu în primul an de aplicare a sistemului (art. 282 alin. 5).

Plafonul relevant pentru eligibilitate, cu valabilitatea în timp (confirmată la sursă în `core/common.py`, tabelul `COTE["plafon_tva_incasare"]`):

| Valabil de la | Plafon | Temei |
|---|---|---|
| 2027-01-01 | 5.500.000 lei | OUG 8/2026, art. 282 alin. (3) lit. b |
| 2026-03-01 | 5.000.000 lei | OUG 8/2026, art. 282 alin. (3) lit. a |
| 2021-01-01 | 4.500.000 lei | Legea 296/2020 |

O notă tranzitorie din art. 9 OUG 8/2026: firmele care au depășit 4.500.000 lei dar nu 5.000.000 lei în ianuarie 2026 nu au fost radiate; cele aflate în aceeași situație în februarie 2026 n-au avut obligația de notificare.

## Ce se greșește în practică

Cea mai costisitoare greșeală e ratarea termenului de 20 a lunii următoare depășirii plafonului (art. 324 alin. 14) — firma nu iese „automat" din sistem la depășire, ci trebuie să notifice; altfel urmează radierea din oficiu. A doua greșeală e încercarea de ieșire voluntară în primul an de aplicare, când legea nu o permite.

## Ce face iConta.eu

Funcția `plafon_la(data)` din `core/common.py` e period-aware — întoarce automat plafonul corect (4.500.000 / 5.000.000 / 5.500.000 lei) pentru orice dată, folosită direct de motorul F097. Aplicația nu depune însă notificările către ANAF (art. 324) și nu urmărește automat termenele de 20 ale lunii pentru intrare, depășire sau ieșire — acestea rămân responsabilitatea contabilului.

[iConta.eu](/)
