---
title: "Cum semnez și trimit D212 prin SPV?"
description: "Ce înseamnă din punct de vedere legal semnarea și transmiterea electronică a Declarației unice (D212) prin Spațiul Privat Virtual."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum semnez și trimit D212 prin SPV?

Din punct de vedere legal, „semnarea" D212 nu înseamnă neapărat o semnătură olografă scanată, ci identificarea contribuabilului în Spațiul Privat Virtual cu mijlocul electronic corespunzător categoriei sale, urmată de transmiterea declarației prin sistemul de tranzacționare al ANAF. Pentru o persoană cu activitate economică independentă, obligația de semnare a declarației fiscale se consideră îndeplinită prin însuși actul transmiterii prin sistemul electronic, cu identificare pe bază de certificat calificat.

## Temeiul legal

::: ghid-temei
„(3) Contribuabilul/Plătitorul are obligația de a completa declarația fiscală înscriind corect, complet și cu bună-credință informațiile prevăzute de formular, corespunzătoare situației sale fiscale. Declarația fiscală se semnează de către contribuabil/plătitor sau, după caz, reprezentantul legal ori împuternicitul acestuia.
(4) Obligația de semnare a declarației fiscale se consideră a fi îndeplinită și în următoarele situații: a) în cazul transmiterii declarației fiscale prin sistemul electronic de plăți; b) în cazul transmiterii declarației fiscale prin sisteme electronice de transmitere la distanță în condițiile art. 103 alin. (1)."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 102 alin. (3), (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pașii, așa cum rezultă din corelarea art. 79, 80, 102 și 103 din Codul de procedură fiscală:

1. **Identificarea în SPV**: pentru persoanele fizice cu activitate economică independentă, identificarea în relația cu organul fiscal se face **numai** cu certificat digital calificat (art. 80 alin. (1) lit. a)) — nu prin username/parolă, cum se întâmplă la alte categorii de persoane fizice.
2. **Completarea și încărcarea declarației**: formularul (sau fișierul XML generat cu un program de asistență) se încarcă în contul SPV al contribuabilului.
3. **Transmiterea**: prin depunerea în sistem, obligația de semnare se consideră îndeplinită automat, potrivit art. 102 alin. (4) lit. b), fără a fi necesară o semnătură separată aplicată pe document, dincolo de autentificarea cu certificatul calificat folosit la accesarea SPV.
4. **Confirmarea**: art. 103 alin. (3)-(4) prevede că data depunerii declarației transmise electronic este data înregistrării pe portal, „astfel cum rezultă din mesajul electronic de confirmare transmis ca urmare a primirii declarației" — cu condiția ca declarația să fi fost validată.

## Ce se greșește în practică

- Se așteaptă un pas suplimentar de „semnare olografă/scanare" după încărcarea în SPV — nu este necesar; transmiterea electronică autentificată cu certificatul calificat ține loc de semnătură, potrivit art. 102 alin. (4) lit. b).
- Se consideră declarația depusă în momentul încărcării fișierului, fără a mai verifica mesajul electronic de confirmare — dacă declarația nu e validată (conține erori), data depunerii rămâne data validării ulterioare, nu data încărcării inițiale (art. 103 alin. (4)-(5)).
- Se încearcă transmiterea cu alt tip de identificare decât certificatul calificat, valabil doar pentru persoanele fizice fără activitate independentă (art. 80 alin. (1) lit. b)).

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează fișierul XML al Declarației unice (D212), validat structural după schema oficială a validatorului ANAF (`core/d212.py`), pe baza datelor introduse manual de contabil. Aplicația nu efectuează ea însăși autentificarea cu certificat calificat și nu transmite declarația către SPV — încărcarea, semnarea (prin autentificare) și transmiterea efectivă în Spațiul Privat Virtual rămân un pas manual, realizat de contribuabil sau de contabil direct pe portalul ANAF.

[iConta.eu](/)
