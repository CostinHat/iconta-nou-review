---
title: 'Overdraft vs linie de credit 2026: ce aleg'
description: În limbajul bancar curent, overdraft-ul este forma cea mai comună de linie de credit (descoperire de cont) — contabil, cele două se tratează identic, fără notă de primire a sumei, doar dobânda direct pe cheltuială; alegerea între ofertele concrete ale băncilor e o decizie financiară, nu una contabilă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Overdraft vs linie de credit 2026: ce aleg

Din perspectivă contabilă, întrebarea „overdraft sau linie de credit” nu are, de regulă, un răspuns diferit — sunt, în esență, aceeași facilitate bancară: dreptul de a retrage din contul curent mai mult decât soldul disponibil, până la un plafon aprobat, fără ca banca să vireze o sumă distinctă. Diferența reală dintre ofertele de pe piață e una financiară (cost, plafon, condiții de reînnoire), nu contabilă — pentru asta comparați ofertele băncilor, nu ecranele aplicației de contabilitate.

## Temeiul legal

::: ghid-temei
„360. - (1) O datorie trebuie clasificată ca datorie pe termen scurt, denumită și datorie curentă, atunci când: a) se așteaptă să fie decontată în cursul normal al ciclului de exploatare al entității; sau b) este exigibilă în termen de 12 luni de la data bilanțului. (2) Toate celelalte datorii trebuie clasificate ca datorii pe termen lung.”

— *OMFP 1802/2014, pct. 360.*

„În creditul contului 519 [Credite bancare pe termen scurt] ... se înregistrează: – creditele bancare pe termen scurt, acordate de bancă pentru nevoi temporare, prin conturi bancare distincte, inclusiv dobânzile datorate (512, 666). În debitul contului 519 ... se înregistrează: – creditele bancare pe termen scurt restituite, inclusiv dobânzile plătite (512). Soldul contului reprezintă creditele bancare pe termen scurt nerestituite.”

— *OMFP 1802/2014, Capitolul 16, funcțiunea contului 519.*
:::

## Ce înseamnă „overdraft” din punct de vedere contabil

Overdraft-ul (descoperirea de cont) și linia de credit pe termen scurt sunt, practic, același mecanism: banca aprobă un plafon până la care firma poate avea sold negativ pe contul curent, fără să existe o „primire” de bani distinctă, ca la un credit clasic. Consecința contabilă directă:

- **Nu se înregistrează o notă de primire a sumei** (nu există echivalentul `5121 = 5191` de la un credit obișnuit pe termen scurt) — plafonul e pur și simplu disponibil pe contul curent, fără o mișcare separată.
- **Se înregistrează doar dobânda**, calculată la soldul negativ folosit efectiv, direct pe cheltuială: `666 = 5121`.
- **Soldul „creditului” se vede din extrasul contului bancar** (5121, cu sold eventual negativ), nu dintr-un cont distinct de credit populat separat de aplicație.

Dacă banca oferă, în schimb, o linie de credit pe un cont separat de contul curent (situație mai apropiată de un credit clasic pe termen scurt, cu tragere/rambursare explicită), atunci tratamentul standard `5121=5191` (primire), `666=5198` (dobândă angajată), `5191=5121` (rată) se aplică normal — diferența nu e de „denumire” a produsului bancar, ci de mecanismul contractual concret: dacă banca virează efectiv o sumă distinctă pe un subcont, e o primire propriu-zisă; dacă doar permite sold negativ pe contul curent, e overdraft.

## Ce se greșește în practică

- Se înregistrează „primirea” unei linii de credit/overdraft ca la un credit clasic (`5121 = 5191`), deși banii nu au intrat separat în cont — plafonul era deja disponibil.
- Se așteaptă un ecran/produs contabil separat pentru „linie de credit” — nu există o astfel de distincție în formularele de contabilitate, doar tipul „termen scurt” vs „termen lung”.
- Se confundă alegerea financiară (ce ofertă bancară e mai avantajoasă) cu o decizie de contabilitate — costul, plafonul și condițiile de reînnoire ale unui overdraft sau ale unei linii de credit sunt negociate cu banca, nu configurate în aplicația de contabilitate.

## Ce face iConta.eu

Formularul „Credite bancare” (`static/js/ecrane/operatiuni_ecran.js`, cheia `"credit"`) oferă doar distincția `tip: scurt (519) | lung (162)` — nu există o a treia opțiune „overdraft” sau „linie de credit” separată. Tratamentul pentru overdraft e descris explicit doar în comentariul de sursă al motorului, `core/credite.py`: „OVERDRAFT (descoperire de cont): nu se înregistrează primirea, doar 666=5121”. Practic, pentru un overdraft/linie de credit fără tragere separată, folosiți doar operația „dobândă” din ecranul „Credite bancare”, fără „primire”; pentru o linie de credit cu tragere efectivă pe un subcont dedicat, folosiți fluxul standard de credit pe termen scurt.

Alegerea concretă dintre ofertele bancare de overdraft și de linie de credit rămâne o decizie financiară a firmei — aplicația nu compară costuri sau condiții de creditare, doar înregistrează corect operațiunile odată decise.

[iConta.eu](/)
