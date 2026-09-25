---
title: "Cum se semnează electronic declarația D112?"
description: "Ce cere legea pentru depunerea electronică a declarației 112 și de ce semnarea și transmiterea efectivă la ANAF rămân, azi, un pas făcut în afara aplicației."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se semnează electronic declarația D112?

Declarația 112 nu se poate depune pe suport hârtie — legea impune transmiterea ei exclusiv prin mijloace electronice. Asta înseamnă, în practică, generarea unui fișier XML valid, semnarea lui electronică și încărcarea prin portalul ANAF (SPV), cu certificatul digital al depunătorului.

## Temeiul legal

::: ghid-temei
„Persoanele fizice şi juridice care au calitatea de angajatori sau sunt asimilate acestora, instituţiile şi persoanele fizice prevăzute la art. 68^1 alin. (2), art. 72 alin. (2), art. 84 alin. (8), art. 125 alin. (8) şi (9), art. 147 alin. (1), (1^1), (1^2) şi (1^3), art. 151 alin. (8), art. 169 alin. (1) şi (1^1), art. 174 alin. (5), art. 174^1 alin. (5), art. 220 alin. (1) şi (2) şi art. 220^7 din Legea nr. 227/2015 [...], au obligaţia depunerii declaraţiei prevăzute la art. 1 prin mijloace electronice de transmitere la distanţă."
— Ordinul comun ANAF/CNPP/CNAS/ANOFM nr. 605/95/928/2314/2026, art. 3 (sursă: anaf_surse/opanaf_605_2026_d112.txt)
:::

- Obligația e clară în privința canalului (electronic, nu hârtie), dar textul nu descrie el însuși mecanica tehnică a semnării — aceasta ține de procedura generală ANAF de depunere prin Spațiul Privat Virtual (SPV), unde documentul transmis e asociat identității depunătorului prin certificat digital calificat sau prin autentificarea contului SPV, potrivit procedurii aplicabile la data depunerii.
- Depunerea electronică presupune, de regulă, fie un certificat digital calificat al reprezentantului legal/împuternicitului, fie transmiterea prin contul propriu de SPV al firmei, autentificat corespunzător.
- Validarea tehnică a fișierului (structura XML corectă) e un pas separat de semnare — un XML valid, dar nesemnat/netransmis, nu are nicio valoare declarativă față de ANAF.

## Ce se greșește în practică

- Se presupune că, odată ce o aplicație de contabilitate generează și „validează" fișierul D112, declarația a și fost depusă — validarea tehnică (conformitatea cu schema XML) și depunerea efectivă la ANAF sunt două lucruri diferite.
- Se caută în interiorul unei aplicații de contabilitate o funcție de „semnare electronică" a declarațiilor, deși semnarea ține de certificatul digital al depunătorului, gestionat de acesta, nu de softul de contabilitate.
- Se amână depunerea până aproape de termen, presupunând că procesul de semnare + încărcare pe SPV durează câteva secunde — în practică certificatele expirate, reînnoirile sau problemele de disponibilitate a portalului ANAF pot întârzia depunerea.

## Ce face iConta.eu

iConta generează local fișierul XML al declarației 112, din datele de salarizare introduse, și îl validează cu DUKIntegrator — validatorul oficial ANAF, rulat local, nu simulat. Mesajul afișat utilizatorului după validare este explicit: fișierul e „validat [...], fără erori", dar **„nu a fost depusă la ANAF"**.

Aplicația **nu semnează electronic și nu depune** nicio declarație — o verificare directă în cod (căutare exhaustivă pe termeni precum „semnătură", „certificat digital/calificat", „PKCS") nu găsește nicio funcție legată de semnare sau transmitere a declarațiilor. Fluxul real, azi, e: contabilul generează și validează D112 în iConta, descarcă XML-ul rezultat, apoi îl semnează și îl depune el însuși, prin SPV sau portalul ANAF, cu propriul certificat digital — un pas care se întâmplă integral în afara aplicației.

[iConta.eu](/)
