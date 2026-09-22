---
title: Cum înregistrezi contabil un împrumut acordat firmei de un asociat
description: Împrumutul de la asociat intră în contul 4551 la primire (5121 = 4551) și se restituie cu dobândă și impozit de 10% reținut la sursă, dacă părțile au stabilit dobândă prin contract.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează contabil un împrumut acordat firmei de asociat?

Când un asociat pune bani la dispoziția firmei, în afara capitalului social, operațiunea e un împrumut, iar contabil se ține separat de conturile de capital — în contul de decontări cu asociații, 4551. Corectitudinea înregistrării contează atât pentru firmă (ca să nu fie confundată cu un venit impozabil nejustificat), cât și pentru asociat (ca să își poată recupera banii fără complicații fiscale).

## Temeiul legal

::: ghid-temei
**Codul fiscal (Legea 227/2015), art. 97 alin. (2)** — impozitarea dobânzii, dacă există: „Veniturile sub formă de dobânzi [...], contractele civile încheiate se impun cu o cotă de 10% din suma acestora, impozitul fiind final [...] În situația sumelor primite sub formă de dobândă pentru împrumuturile acordate pe baza contractelor civile, calculul impozitului datorat de către plătitorii de venit se efectuează la momentul plății dobânzii."

**Legea 31/1990, art. 67 alin. (2^4)** — adăugat de Legea 239/2025, în vigoare din 18.12.2025: „Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților [...] împrumuturile luate de la aceștia."

**Legea 31/1990, art. 67 alin. (2^5)-(2^6)** — răspundere solidară a societății și a asociatului beneficiar, respectiv contravenție cu amendă de 10.000-200.000 lei, pentru nerespectarea interdicțiilor privind împrumuturile de/către asociați.
:::

## Înregistrarea, pas cu pas

**La primirea sumei:**

- `5121 = 4551` — cu suma încasată de firmă în contul bancar

**La restituire**, dacă împrumutul are dobândă stabilită prin contract:

- `4551 = 5121` — restituirea sumei împrumutate (principal)
- `666 = 4551` — cheltuiala cu dobânda datorată
- `4551 = 446` — impozitul de 10% reținut pe dobândă
- `4551 = 5121` — plata dobânzii nete către asociat

Dacă împrumutul e fără dobândă, la restituire rămâne doar linia de principal, `4551 = 5121`.

## Ce trebuie să existe la bază

Un simplu transfer bancar de la asociat către firmă, fără document, e greu de justificat ca împrumut în fața unui control — poate fi reîncadrat ca venit nejustificat sau ca aport informal la capital. E nevoie de un contract de împrumut (sau, la minimum, o decizie a asociatului/hotărâre AGA) care să precizeze suma, termenul de restituire și dacă există sau nu dobândă. Documentul e cel care leagă suma din extrasul bancar de operațiunea din contul 4551.

Înainte de a restitui un împrumut mai vechi, verifică și activul net al firmei față de capitalul social subscris: din 18 decembrie 2025, dacă activul net e sub jumătate din capitalul social, restituirea către asociat e interzisă prin lege, cu răspundere solidară și amendă pentru nerespectare.

## Ce se greșește în practică

- **Se înregistrează suma direct ca venit sau ca aport la capital, fără contract de împrumut.** Fără document care să ateste natura de împrumut, suma poate fi reîncadrată fiscal.
- **Se plătește dobândă fără reținere de impozit.** Dobânda către asociat persoană fizică e impozitată final cu 10% la sursă — firma reține și virează impozitul, nu asociatul îl declară separat.
- **Se restituie împrumutul fără să se verifice activul net al firmei.** Interdicția de la art. 67 alin. (2^4) se aplică indiferent de vechimea contractului de împrumut sau de buna-credință a părților.

## Ce face iConta.eu

Aplicația înregistrează automat primirea împrumutului (`5121 = 4551`) și restituirea, inclusiv calculul dobânzii și reținerea impozitului de 10% (`4551 = 5121`, `666 = 4551`, `4551 = 446`, `4551 = 5121`), pe baza datelor introduse de contabil.

Verificarea condiției legale de la restituire — dacă activul net al firmei e sub jumătate din capitalul social subscris — nu este automatizată în acest moment; recomandăm o verificare manuală a bilanțului curent înainte de a înregistra restituirea unui împrumut către asociat.

[iConta.eu](/)
