---
title: D394: ce operațiuni declari și de ce apar neconcordanțe
description: Ce intră în declarația informativă D394, cum se grupează operațiunile pe parteneri și cote, cum se leagă de decontul de TVA și de ce ANAF trimite notificări de neconcordanță.
published: 2026-08-12
modified: 2026-08-12
---

# Ce declari în D394 și de ce primești notificări de neconcordanță?

D394 e declarația prin care ANAF verifică dacă doi parteneri de afaceri spun același lucru. Fiecare tranzacție internă între plătitori de TVA apare de două ori în sistem: o dată la tine ca livrare, o dată la celălalt ca achiziție. Când cele două nu se potrivesc — un cod fiscal greșit, o cotă diferită, o factură scăpată — sistemul o vede singur și trimite notificare. Cele mai multe notificări nu vin din fraudă, ci din nepotriviri mărunte care puteau fi prinse înainte de depunere.

## Temeiul legal

::: ghid-temei
**D394 — „Declarație informativă privind livrările/prestările și achizițiile efectuate pe teritoriul național de persoane înregistrate în scopuri de TVA".**

Ordinul de bază: **OPANAF 3769/2015**. Structura curentă a tipurilor de operațiune provine din **OPANAF 77/2022** (Monitorul Oficial nr. 95 din 31 ianuarie 2022). Formularul a fost actualizat prin **OPANAF 2194/2025**, care a adăugat cotele de **21%** și **11%**, aplicabile de la 1 august 2025.

Declarația se depune pe **aceeași perioadă fiscală ca decontul de TVA** — lunar, trimestrial, semestrial sau anual, după cum e încadrată firma — până la data de 25 a lunii următoare încheierii perioadei.
:::

## Regula concretă

**Ce intră.** Livrările, prestările și achizițiile efectuate **pe teritoriul național**, între persoane înregistrate în scopuri de TVA. Operațiunile intracomunitare nu intră aici — ele merg în [D390](/ghid/control-incrucisat-d390).

**Cum se clasifică fiecare factură.** Pe două axe:

- **Direcția și regimul** — o factură emisă către un plătitor de TVA din România e livrare; dacă are taxare inversă, e livrare cu regim special. O achiziție de la un plătitor român e achiziție, cu sau fără taxare inversă. O achiziție de la un neplătitor sau de la o persoană fizică se raportează separat.
- **Tipul partenerului** — plătitor de TVA în România, neplătitor, persoană din alt stat membru neînregistrată în România, sau persoană din afara Uniunii Europene. Statutul contează, nu naționalitatea.

**Cum se grupează.** Fiecare factură apare individual, cu codul fiscal al partenerului. Peste ele, declarația construiește două niveluri de totaluri: unul pe combinația **tip de partener și cotă**, altul pe **cotă**, la nivel de firmă.

**Legătura cu decontul.** Totalurile pe cotă din D394 trebuie să fie coerente cu rândurile din decontul de TVA al aceleiași perioade. Relația e de **incluziune, nu de egalitate**: D394 conține doar operațiunile interne raportabile, în timp ce decontul cuprinde tot TVA-ul firmei — inclusiv achiziții intracomunitare, importuri, operațiuni scutite. O diferență nu e automat o eroare; o diferență **neexplicată** e.

**Taxarea inversă** are un tratament propriu: operațiunea se raportează cu un cod de produs din nomenclatorul oficial — cereale, deșeuri, masă lemnoasă, telefoane, laptopuri, gaze naturale și celelalte categorii din art. 331.

## Un exemplu

::: ghid-exemplu
**SC Exemplu SRL**, plătitoare de TVA cu regim lunar, luna iulie 2026, cota standard 21%. Două achiziții interne, de la doi furnizori plătitori de TVA din România:

- **Furnizor A SRL:** bază **50.000 lei**, TVA **10.500 lei**
- **Furnizor B SRL:** bază **30.000 lei**, TVA **6.300 lei**

În declarație apar **două linii distincte**, fiecare cu codul fiscal al furnizorului ei — pentru că ANAF trebuie să le poată confrunta separat cu ce declară fiecare furnizor.

La nivel de totaluri, cele două se contopesc: pe combinația „partener plătitor de TVA, cota 21%" rezultă **2 facturi**, bază **80.000 lei**, TVA **16.800 lei**.

Acest total trebuie să se regăsească în TVA-ul deductibil din decontul lunii iulie. Dacă decontul arată **mai puțin**, ai o factură declarată în D394 dar necontabilizată. Dacă arată **mai mult**, restul vine din operațiuni care nu intră în D394 — de exemplu o achiziție intracomunitară. Prima situație e problemă; a doua e normală, dar trebuie să știi din ce.
:::

## Ce se greșește în practică

- **Cod fiscal greșit la partener.** O cifră tastată greșit rupe legătura: la tine factura există, la partener apare cu alt cod. Confruntarea automată scoate diferența, chiar dacă TVA-ul tău e corect.
- **Statut de partener greșit.** Un partener trecut ca plătitor de TVA când de fapt e neplătitor — sau invers — mută operațiunea în altă categorie. Statutul contează la **data operațiunii**, nu cel de azi: un furnizor care s-a înregistrat între timp nu schimbă retroactiv facturile vechi.
- **Cotă greșită pe linie.** O factură rămasă pe 19% după 1 august 2025 migrează în alt total, iar suma nu mai corespunde decontului.
- **Factură scăpată.** Lipsa unei facturi din D394 nu trece neobservată: partenerul o declară, la tine lipsește.

## Ce face iConta.eu

D394 se generează direct din facturile emise și primite ale perioadei. Fiecare factură e clasificată pe tipul de partener — folosind statutul TVA **înghețat pe factură**, cel de la momentul operațiunii, nu cel curent — și pe tipul de operațiune. Totalurile se calculează pe ambele niveluri, codurile de produs se atribuie la taxarea inversă, iar fișierul XML se scrie pe structura oficială și se validează pe validatorul ANAF (DUKIntegrator).

Peste generator rulează o **a doua cale de calcul**: totalurile pe cotă sunt recalculate independent, din liniile brute ale facturilor, printr-un cod care nu folosește nimic din generator. Dacă cele două căi diferă, generarea se **oprește** și îți sunt numite ambele valori și câmpul divergent. Instrumentul nu alege singur care e corectă — îți semnalează că trebuie să te uiți.

Depunerea o faci din SPV, cu fișierul deja verificat.

Vezi și: [cotele de TVA în vigoare](/ghid/cote-tva-2025) și [taxarea inversă internă](/ghid/taxare-inversa-interna), care schimbă modul de raportare.

[iConta.eu](/)
