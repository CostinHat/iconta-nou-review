---
title: Cum ies din TVA la încasare dacă depășesc plafonul
description: Depășirea plafonului nu e o opțiune de părăsire a sistemului, ci o obligație — firma trebuie să notifice ANAF până la data de 20 a lunii următoare celei în care a depășit plafonul, altfel riscă radierea din oficiu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum ies din TVA la încasare dacă depășesc plafonul

Ieșirea din TVA la încasare arată complet diferit după cum firma alege să iasă din proprie inițiativă sau e obligată să iasă pentru că a depășit plafonul. A doua situație are un termen strict și o consecință dură dacă e ratat.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**, modificat prin art. 6 pct. 38 OUG 8/2026 (MO 147/25.02.2026): *„...Plafonul pentru aplicarea sistemului TVA la încasare este de: a) 5.000.000 lei, în perioada 1 martie-31 decembrie 2026; b) 5.500.000 lei, începând cu data de 1 ianuarie 2027."*

**Art. 282 alin. (4) lit. c) CF** (rezumat din dosar): nu sunt eligibile persoanele impozabile care în anul precedent au depășit plafonul aplicabil pentru anul respectiv.

**Art. 282 alin. (5) CF** (rezumat din dosar): firma rămâne obligată în sistem cel puțin până la sfârșitul anului calendaristic al opțiunii, cu excepția depășirii plafonului; ieșirea voluntară se face prin notificare depusă între 1 și 20 ale lunii (nu în primul an de aplicare).

**Art. 324 alin. (14) CF** (rezumat din dosar): la depășirea plafonului în cursul anului, notificarea se depune până la data de 20 a lunii următoare celei în care s-a depășit plafonul; nedepunerea duce la radiere din oficiu.
:::

## Ce înseamnă practic

Depășirea plafonului nu îți lasă de ales — nu mai poți rămâne în sistem din anul următor (art. 282 alin. (4) lit. c)), spre deosebire de o ieșire voluntară, care e opțională și supusă regulii „minim până la sfârșitul anului calendaristic" de la alin. (5).

Termenul concret e cel de la art. 324 alin. (14): ai la dispoziție până la data de 20 a lunii **următoare** celei în care ai depășit plafonul, ca să depui notificarea la ANAF. Dacă nu o depui, legea prevede radierea din oficiu — deci evitarea notificării nu te ține în sistem, ci doar expune firma unei radieri impuse, nu alese.

Plafonul de raportat depinde de anul: 5.000.000 lei pentru perioada 1 martie-31 decembrie 2026, respectiv 5.500.000 lei începând cu 1 ianuarie 2027.

## Ce se greșește în practică

- **Se crede că depășirea plafonului e doar un motiv de ieșire opțională**, tratată la fel ca o ieșire voluntară (fereastra 1-20 ale lunii de la alin. (5)). Depășirea plafonului are propriul termen, de la art. 324 alin. (14).
- **Se ratează termenul de notificare** (20 a lunii următoare depășirii), ceea ce duce la radiere din oficiu, nu la rămânerea tacită în sistem.
- **Se compară cifra de afaceri cu un plafon fix**, ignorând că plafonul aplicabil diferă între 2026 (5.000.000 lei, din 1 martie) și 2027 (5.500.000 lei).

## Ce face iConta.eu

Funcția `plafon_la(data)` din `core/common.py` întoarce plafonul corect valabil la orice dată, pe baza istoricului din tabelul `COTE["plafon_tva_incasare"]`. Depistarea automată a momentului exact în care firma depășește plafonul în cursul anului, cu alertă pentru depunerea notificării la ANAF, nu e confirmată în acest dosar ca funcționalitate implementată — calculul plafonului aplicabil e automat, dar depunerea notificării rămâne, conform cercetării de față, un pas manual al contabilului.

[iConta.eu](/)
