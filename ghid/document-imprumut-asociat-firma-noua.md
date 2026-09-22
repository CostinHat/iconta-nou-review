---
title: Ce documente sunt necesare pentru împrumutul acordat de asociat unei firme noi
description: O firmă nou-înființată care primește bani de la asociat sub formă de împrumut are nevoie de un contract de împrumut sau de o decizie a asociatului, nu de o majorare de capital social, iar suma se înregistrează în contul 4551.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce documente sunt necesare pentru împrumutul acordat de un asociat firmei nou-înființate?

O firmă la început de drum are nevoie de capital de lucru înainte să genereze venituri, iar cea mai simplă soluție e ca asociatul să pună bani la dispoziția firmei sub formă de împrumut. Diferența față de aportul la capital social e esențială: împrumutul nu trece prin Registrul Comerțului, dar are nevoie de un document propriu care să ateste natura sumei — altfel riscă să fie interpretată ca venit nejustificat al firmei.

## Temeiul legal

::: ghid-temei
**Codul fiscal (Legea 227/2015), art. 97 alin. (2)** — dacă părțile stabilesc dobândă: „Veniturile sub formă de dobânzi [...], contractele civile încheiate se impun cu o cotă de 10% din suma acestora, impozitul fiind final [...] calculul impozitului datorat de către plătitorii de venit se efectuează la momentul plății dobânzii."

**Legea 31/1990, art. 67 alin. (2^4)** — adăugat de Legea 239/2025, în vigoare din 18.12.2025: „Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților [...] împrumuturile luate de la aceștia" — relevant pentru firma nouă în momentul în care va trebui să restituie suma.
:::

## Ce document stă la baza înregistrării

Nu există o formă unică obligatorie prin lege pentru contractul dintre asociat și firma proprie, dar practica și organele de control cer, la minimum:

- un **contract de împrumut** (sau o decizie scrisă a asociatului unic / o hotărâre a asociaților, dacă sunt mai mulți), care să precizeze suma, data acordării, termenul de restituire și dacă există dobândă;
- **dovada transferului efectiv** — extrasul de cont sau chitanța de casă, cu suma și data care se potrivesc exact cu ce apare în contract.

Fără acest document, o sumă intrată în contul firmei de la asociat, fără explicație, poate fi tratată la un control ca venit nejustificat, impozabil separat de natura reală a operațiunii.

Concret, art. 67 alin. (2⁴) înseamnă că firma nu va putea restitui asociatului împrumutul dacă, la data restituirii, activul net (din ultimele situații financiare anuale aprobate) e sub jumătate din capitalul social subscris — o situație plauzibilă tocmai la o firmă nou-înființată, cu activitate încă redusă.

## Înregistrarea contabilă

**La primirea sumei:**

- `5121 = 4551` — cu suma încasată de firmă

**La restituire**, dacă există dobândă:

- `4551 = 5121` — principalul
- `666 = 4551` — dobânda cheltuială
- `4551 = 446` — impozitul de 10% reținut pe dobândă
- `4551 = 5121` — dobânda netă plătită asociatului

## Ce se greșește în practică

- **Se aduc bani în firmă fără niciun document scris**, doar printr-un transfer bancar de la contul personal al asociatului. Fără contract, suma nu are o justificare formală ca împrumut.
- **Se confundă împrumutul cu aportul la capital.** Doar majorarea de capital social, înregistrată la Registrul Comerțului, transformă suma în capital propriu; altfel, rămâne datorie a firmei către asociat.
- **Se stabilește dobândă prin contract, dar nu se reține impozitul de 10% la plata ei.** Impozitul pe dobânda plătită asociatului persoană fizică e final și se reține de firmă, nu se lasă în sarcina asociatului.

## Ce face iConta.eu

Aplicația înregistrează automat, pe baza datelor introduse, primirea împrumutului (`5121 = 4551`) și restituirea acestuia, inclusiv calculul dobânzii și reținerea impozitului de 10% pe dobânda plătită asociatului.

Verificarea documentației de bază (existența contractului, corespondența cu extrasul de cont) rămâne responsabilitatea contabilului — aplicația nu validează automat existența sau conținutul contractului de împrumut.

[iConta.eu](/)
