---
title: "Cum se declară în D112 concediul medical?"
description: "Regulile de bază pentru raportarea concediului medical în D112: cine plătește primele zile, ce venit se declară și de unde vine baza legală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară în D112 concediul medical?

Concediul medical se declară în D112 diferit față de o lună lucrată integral, pentru că indemnizația nu e „salariu" în sensul obișnuit, iar primele zile de incapacitate sunt suportate de angajator, nu de bugetul asigurărilor sociale de sănătate.

## Temeiul legal

::: ghid-temei
„Indemnizațiile pentru incapacitate temporară de muncă se suportă după cum urmează: A. de către angajator, din prima zi până în a 5-a zi de incapacitate temporară de muncă, cu excepția indemnizațiilor aferente certificatelor de concediu medical acordate persoanelor asigurate pentru care a fost instituită măsura izolării, potrivit Legii nr. 136/2020."
— OUG 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate, art. 12 lit. A) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Efectul practic pentru declarație:

- Pentru primele 5 zile de incapacitate temporară de muncă, indemnizația e suportată din fondul de salarii al angajatorului, nu din FNUASS — ceea ce se reflectă distinct față de zilele următoare, suportate din bugetul asigurărilor de sănătate.
- Salariul lunii cu concediu medical nu se calculează la brutul contractual, ci la zilele efectiv lucrate plus indemnizația de concediu medical, calculată separat pe baza certificatului medical.
- Certificatul de concediu medical (cu codul de boală, numărul de zile, tipul de indemnizație) e documentul justificativ pe baza căruia se completează secțiunea de concedii din D112 — fără el, nu există bază pentru declararea corectă.

## Ce se greșește în practică

- Se declară toată luna ca fiind plătită integral din fondurile FNUASS, ignorând regula primelor 5 zile suportate de angajator.
- Se calculează venitul lunii ca brutul contractual nediminuat, în loc de zilele lucrate plus indemnizația calculată separat.
- Se omit câmpurile obligatorii ale certificatului de concediu medical (cod, serie, tip) la introducerea în sistem, ceea ce blochează validarea declarației.

## Ce face iConta.eu

Modulul D112 din iConta.eu tratează explicit concediul medical: salariul lunii cu concediu medical se calculează pe zilele efectiv lucrate (nu pe brutul contractual), certificatul de concediu medical se introduce cu câmpurile lui obligatorii, iar aplicația validează prezența acestora înainte de generarea declarației, semnalând clar când un certificat are date incomplete sau un cod de boală care necesită informații suplimentare.

[iConta.eu](/)
