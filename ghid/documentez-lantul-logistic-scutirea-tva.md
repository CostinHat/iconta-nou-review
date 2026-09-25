---
title: "Cum documentez lanțul logistic pentru scutirea de TVA intra-UE"
description: "Condiția legală de bază pentru scutirea de TVA la livrările intracomunitare, conform Codului fiscal, și limita informației disponibile despre dovezile de transport."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum documentez lanțul logistic pentru scutirea de TVA intra-UE

Scutirea de TVA la o livrare intracomunitară nu e automată — depinde de îndeplinirea unei condiții legale precise, verificabile, și de dovada efectivă a transportului bunurilor în alt stat membru. Fără documentație, scutirea poate fi contestată la control, chiar dacă operațiunea a fost reală.

## Temeiul legal

::: ghid-temei
„(2) Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru [...]"
— Codul fiscal (Legea 227/2015), art. 294 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condiția de bază, din text:

- **Codul valabil de TVA al cumpărătorului**, comunicat furnizorului și atribuit de autoritățile fiscale din alt stat membru — condiție explicită, prima verificată la un control. În practică, se confirmă prin sistemul VIES.
- Legea exclude de la scutire, explicit: livrările efectuate de o întreprindere mică (regim de scutire, nu de TVA la cotă zero), livrările de mijloace de transport noi fără cod TVA valid comunicat, și livrările supuse regimului special pentru bunuri second-hand.

**Limitare onestă privind „lanțul logistic" și dovada transportului:** condiția codului de TVA valid e confirmată explicit de Codul fiscal, dar cerințele detaliate de **dovadă a transportului efectiv** al bunurilor în alt stat membru (documente de transport, CMR, confirmare de primire, extrase din sistemul de urmărire al transportatorului) sunt reglementate la nivel de Uniune Europeană prin **Regulamentul de punere în aplicare (UE) 2018/1912**, direct aplicabil în România, dar care nu se regăsește într-o formă citabilă verbatim în sursele consultate aici (anaf_surse). Orice listă de documente „acceptate" pentru dovada transportului (CMR, poliță de asigurare a transportului, confirmare scrisă a cumpărătorului etc.) trebuie verificată direct la textul acelui regulament, nu presupusă.

## Ce se greșește în practică

- Se aplică scutirea de TVA doar pe baza facturii, fără verificarea codului de TVA al cumpărătorului în VIES la momentul livrării.
- Se presupune că orice document de transport (chiar informal) e suficient, fără să se verifice cerințele minime din Regulamentul UE 2018/1912 privind seturile de dovezi acceptate.
- Se ignoră faptul că scutirea nu se aplică livrărilor către o întreprindere mică din alt stat membru sau când cumpărătorul nu comunică un cod valabil — cazuri excluse explicit de lege.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **verifică validitatea codului de TVA al partenerului intracomunitar prin interogarea directă a serviciului VIES** (modulul `core/intracomunitar.py`), pe baza Codului fiscal art. 294 alin. (2) lit. a) — condiția centrală a scutirii. Aplicația **nu gestionează însă documentele de transport** (CMR, confirmări de livrare) care completează dosarul de dovadă cerut de Regulamentul UE 2018/1912 — acestea rămân în responsabilitatea contabilului/firmei, în afara fluxului aplicației.

[iConta.eu](/)
