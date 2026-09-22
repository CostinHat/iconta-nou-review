---
title: Cum se raportează furnizorii din UE în D406?
description: Furnizorii din UE se raportează cu codul de identificare "01" urmat de codul de țară ISO și CUI-ul de TVA (format VIES), cu excepția Greciei, unde prefixul de țară folosit este "EL", nu "GR".
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se raportează furnizorii din UE în D406?

Fișierul SAF-T identifică fiecare partener (client sau furnizor) printr-un cod de înregistrare structurat, standardizat de ANAF, nu prin CUI-ul brut din factură. Pentru furnizorii din alte state membre UE, formatul acestui cod diferă de cel folosit pentru partenerii români, iar o greșeală de mapare aici e una dintre cele mai frecvente cauze de respingere la validare.

## Temeiul legal

::: ghid-temei
**Notă onestă privind temeiul**: formatul exact al codurilor de identificare a furnizorilor străini (`01`+țară+cod pentru UE, cu excepția Greciei unde se folosește prefixul VIES `EL`, nu ISO-ul `GR`; `02`+țară+cod pentru furnizorii din afara UE) nu a fost găsit ca citat verbatim în actele normative citite integral pentru acest dosar (OPANAF 1783/2021, OPANAF 407/2025). Formatul provine din schema tehnică oficială ANAF (foaia "5. Structures" a fișierului `d406_schema_anaf.xlsx`), verificată direct în codul aplicației — nu dintr-un text de lege redat ca atare în sursele parcurse aici. Detaliile tehnice sunt descrise mai jos, în secțiunea explicativă.
:::

## Cum se construiește codul pentru un furnizor din UE

Regula sintactică S.C.1 din schema oficială ANAF cere ca un partener din UE, altul decât România, să fie identificat astfel: prefixul `01`, urmat de codul ISO al țării, urmat de CUI-ul de TVA înregistrat în VIES — fără spații sau caractere de separare.

::: ghid-exemplu
Un furnizor german cu codul de TVA intracomunitar `DE123456789` este raportat ca `01DE123456789`.

Excepția: un furnizor din Grecia cu codul de TVA `EL123456789` NU se raportează ca `01GR123456789` (codul ISO oficial al Greciei este `GR`), ci ca `01EL123456789` — pentru că nomenclatorul VIES folosește prefixul `EL`, nu ISO-ul de țară. Schema ANAF exemplifică literal acest caz.
:::

Pentru furnizorii din afara UE (ex. Marea Britanie, SUA, Elveția), prefixul folosit este `02`, nu `01` — codul de țară plus identificatorul fiscal local al furnizorului.

## Ce se greșește în practică

- Se folosește codul ISO al țării (`GR`) pentru Grecia în loc de prefixul VIES (`EL`), ceea ce duce la respingere la validarea oficială.
- Se raportează furnizorii din afara UE cu prefixul `01` (rezervat UE) în loc de `02`.
- Se omite prefixul de țară și se transmite doar CUI-ul brut, fără codul `01`/`02` din față.
- Se pune prefixul `RO` pe furnizorii români (regula S.C.1 cere doar `00`+CUI, fără litere "RO" în față).
- Nu se verifică dacă furnizorul are un cod de TVA valid înregistrat în VIES la data facturii, ci se preia orice cod introdus manual.

## Ce face iConta.eu

Construcția codului de partener este automată, prin funcția `_partener_registration_number` din motorul D406: pentru un partener român se generează `00`+CUI, pentru un partener din UE (altul decât România) se generează `01`+prefixul de țară+CUI, iar pentru un partener din afara UE, `02`+țară+CUI. Maparea codului ISO de țară la prefixul VIES este cablată explicit pentru cazul Greciei (`_ISO_TO_VAT = {"GR": "EL"}`), astfel încât un furnizor grecesc introdus cu țara `GR` primește automat codul corect `01EL...`, fără intervenție manuală.

[iConta.eu](/)
