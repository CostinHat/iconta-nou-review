---
title: "Se plătește CAM pentru concediul medical?"
description: "De ce indemnizația de concediu medical nu intră în baza de calcul a contribuției asiguratorii pentru muncă, potrivit art. 220^5 din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se plătește CAM pentru concediul medical?

Nu. Indemnizația de concediu medical e o prestație de asigurări sociale de sănătate, nu un venit salarial plătit din buzunarul angajatorului — și tocmai de aceea legea o scoate explicit din baza de calcul a contribuției asiguratorii pentru muncă.

## Temeiul legal

::: ghid-temei
„Contribuția asiguratorie pentru muncă nu se datorează pentru prestațiile suportate din bugetul asigurărilor sociale de stat, bugetul asigurărilor pentru șomaj, precum și din Fondul național unic de asigurări sociale de sănătate."
— Legea nr. 227/2015, art. 220^5 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă practic pentru o lună cu concediu medical:

- Indemnizația de concediu medical se suportă, integral sau parțial, din **Fondul național unic de asigurări sociale de sănătate** (FNUASS) — deci se încadrează direct în excepția de la art. 220^5.
- CAM se calculează **doar** pe partea din salariu efectiv realizată de angajat în zilele lucrate din lună — baza CAM exclude zilele acoperite de indemnizația de concediu medical.
- Această regulă e distinctă de CAS și CASS, care au propriile reguli de bază minimă pentru lunile cu concediu medical — CAM nu urmează același mecanism de „prag minim", ci pur și simplu exclude complet suma respectivă din bază.

## Ce se greșește în practică

- Se calculează CAM pe salariul brut „normal" al lunii, fără a scădea partea acoperită de concediul medical, ceea ce supraevaluează contribuția datorată.
- Se aplică aceeași logică de bază minimă folosită la CAS/CASS și pentru CAM, deși art. 220^5 exclude complet prestațiile din FNUASS din calculul CAM, nu doar le tratează diferit.
- Se presupune că excepția se aplică doar la concediul medical propriu-zis, ignorând că art. 220^5 acoperă în aceeași frază și prestațiile din bugetul asigurărilor sociale de stat și din bugetul asigurărilor pentru șomaj.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează baza CAM pentru fiecare salariat folosind doar salariul efectiv realizat, excluzând explicit indemnizația de concediu medical din bază — comportament documentat intern ca aplicare directă a art. 220^5 din Codul fiscal. Rezultatul e reflectat corect în **D112**, fără a genera obligație de CAM pe zilele de concediu medical.

[iConta.eu](/)
