---
title: "Dispoziția de încasare/plată 2026: modele"
description: "Ce este dispoziția de plată/încasare către casierie, cine o reglementează și de ce rămâne un document justificativ curent al registrului de casă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Dispoziția de încasare/plată 2026: modele

Dispoziția de plată/încasare către casierie este unul dintre documentele financiar-contabile de bază, folosit pentru a consemna operațiunile de casă care nu au alt document justificativ direct (de exemplu, ridicări de numerar pentru cheltuieli neprevăzute sau încasări care nu provin dintr-o factură). Modelul și codificarea sa sunt stabilite prin ordinul care reglementează documentele financiar-contabile, aplicabil și în 2026.

## Temeiul legal

::: ghid-temei
„13. | Dispoziţie de plată/încasare către casierie | 14-4-4"
— OMFP nr. 2634/2015 privind documentele financiar-contabile, Nomenclatorul documentelor financiar-contabile (sursă: anaf_surse/omfp_2634_2015.txt)
:::

- Dispoziția de plată/încasare către casierie poartă codul de formular **14-4-4** în nomenclatorul documentelor financiar-contabile stabilit prin OMFP 2634/2015.
- Documentul face parte din categoria documentelor justificative care „stau la baza înregistrărilor în contabilitate", alături de chitanță, avizul de însoțire a mărfii sau extrasul de cont.
- Potrivit normelor generale ale aceluiași ordin, documentele justificative trebuie să cuprindă elemente minime obligatorii: denumirea documentului, datele emitentului, numărul și data întocmirii, părțile implicate, conținutul operațiunii și, unde e cazul, temeiul legal, precum și datele cantitative/valorice și semnăturile persoanelor responsabile.
- Entitățile — persoanele prevăzute la art. 1 alin. (1)-(4) din Legea contabilității nr. 82/1991 — au obligația de a consemna operațiunile economico-financiare „în momentul efectuării lor", ceea ce înseamnă că dispoziția de plată/încasare trebuie întocmită concomitent cu operațiunea de casă, nu ulterior, la reconstituire.

## Ce se greșește în practică

- Se folosește dispoziția de plată/încasare ca înlocuitor general pentru documente specifice (chitanță, factură, ordin de plată), deși fiecare tip de operațiune are, de regulă, documentul său propriu.
- Se completează documentul ulterior operațiunii de casă, „din memorie", încălcând principiul consemnării operațiunilor „în momentul efectuării lor".
- Se omit elementele obligatorii minime (semnăturile persoanelor responsabile, temeiul operațiunii), ceea ce poate afecta valoarea probatorie a documentului la un control.
- Se ignoră corelarea dispoziției de plată/încasare cu plafoanele legale pentru operațiunile de casă (plăți/încasări în numerar), tratate distinct de legislația privind disciplina financiară.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu are un modul de **registru de casă** (`core/casa.py` — motorul de plafoane — și `core/casa_api.py` — API-ul de operațiuni), care generează automat notele contabile pentru operațiuni tipice de casă (încasare de la client, plată către furnizor, ridicare/depunere la bancă, avans spre decontare), fiecare operațiune producând o notă contabilă ciornă pe care contabilul o validează. Modulul este orientat spre înregistrarea contabilă a operațiunilor de casă, nu spre tipărirea formularului 14-4-4 ca atare — generarea propriu-zisă a formularului fizic de dispoziție de plată/încasare, cu toate elementele cerute de OMFP 2634/2015, rămâne, în prezent, în afara acestui modul.

[iConta.eu](/)
