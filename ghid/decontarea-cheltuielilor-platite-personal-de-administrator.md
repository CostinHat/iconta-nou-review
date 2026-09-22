---
title: Cum se decontează cheltuielile plătite personal de administrator
description: Dacă administratorul plătește din bani proprii o cheltuială a firmei, suma devine o datorie a firmei față de el și se restituie prin contul 4551, dacă administratorul e și asociat, pe baza documentelor justificative ale cheltuielii.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se decontează cheltuielile plătite personal de administrator?

Se întâmplă des ca administratorul unei firme mici să plătească din buzunarul propriu o cheltuială urgentă — un abonament, o factură, o taxă — pentru care firma nu avea încă lichiditate disponibilă sau card la îndemână. Din acel moment, firma îi datorează banii înapoi. Contabil, tratamentul depinde de un singur lucru: administratorul e sau nu și asociat al firmei.

## Temeiul legal

::: ghid-temei
**Codul fiscal (Legea 227/2015), art. 97 alin. (2)** — dacă suma avansată de administratorul-asociat e tratată formal ca împrumut cu dobândă: „Veniturile sub formă de dobânzi [...], contractele civile încheiate se impun cu o cotă de 10% din suma acestora, impozitul fiind final [...] calculul impozitului datorat de către plătitorii de venit se efectuează la momentul plății dobânzii."

**Legea 31/1990, art. 67 alin. (2^4)** — adăugat de Legea 239/2025, în vigoare din 18.12.2025: „Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților [...] împrumuturile luate de la aceștia" — relevant dacă suma avansată e privită ca împrumut de la asociat.
:::

## Administrator-asociat: cont 4551

Când administratorul care a plătit din bani proprii e și asociat, cea mai curată tratare e ca o sumă temporar avansată firmei — practic un mic împrumut fără dobândă, care se stinge la restituire:

- `4551` se creditează cu suma cheltuielii înregistrate pe firmă, în contrapartidă cu contul de cheltuială/furnizor justificat de document (de exemplu `628 = 4551`, pentru un abonament plătit direct)
- La restituirea banilor administratorului: `4551 = 5121` (sau `5311`, dacă restituirea se face din casierie)

Dacă suma e purtătoare de dobândă (rar, dar posibil dacă se stabilește explicit), se aplică aceeași logică de dobândă și impozit de 10% ca la orice împrumut de la asociat.

## Ce document stă la bază

Fiecare sumă decontată are nevoie de documentul justificativ al cheltuielii pe numele firmei (factură, bon fiscal cu CUI-ul firmei, chitanță), plus o dovadă că administratorul a plătit-o din bani proprii (extras de cont personal, sau bon cu semnătura acestuia). Fără document justificativ pe firmă, suma nu poate fi înregistrată drept cheltuială a firmei.

## Ce se greșește în practică

- **Se decontează sume fără documente justificative pe numele firmei.** Un bon fiscal fără CUI-ul firmei sau o factură pe numele administratorului ca persoană fizică nu justifică o cheltuială a firmei.
- **Se confundă decontarea cu un avans de trezorerie clasic**, deși administratorul nu a primit bani în avans — a plătit deja din proprii bani, deci operațiunea e o datorie a firmei, nu o justificare de avans primit.
- **Se restituie sume mari administratorului-asociat fără să se verifice activul net al firmei**, deși interdicția de la art. 67 alin. (2^4) se aplică oricărei restituiri către asociat, indiferent de motivul inițial al sumei.

## Ce face iConta.eu

Pentru sumele avansate de administratorul-asociat și restituite ulterior de firmă, aplicația folosește logica de decontări cu asociații (contul 4551), inclusiv calculul dobânzii și al impozitului de 10%, dacă operațiunea e introdusă cu dobândă.

Verificarea documentelor justificative ale cheltuielii inițiale rămâne responsabilitatea contabilului la introducerea operațiunii. Verificarea activului net al firmei față de capitalul social, cerută de art. 67 alin. (2^4) înainte de restituire, nu este automatizată în acest moment.

[iConta.eu](/)
