---
title: Cum se împrumută firma de la asociat în 2026: contabilitate și restricții noi
description: Împrumutul de la asociat se înregistrează în contul 4551, iar din 18 decembrie 2025 Legea 31/1990 interzice firmelor care distribuie dividende trimestrial să acorde împrumuturi asociaților până la regularizare și interzice restituirea împrumuturilor când activul net scade sub jumătate din capitalul social.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează contabil un împrumut de la asociat și ce s-a schimbat din 2026?

Un asociat care aduce bani în firmă, fără să treacă prin majorarea capitalului social, îi împrumută firmei — nu îi „donează" și nu îi „aportează". Contabil, suma trece prin contul 4551, iar din 18 decembrie 2025 legea a adăugat două interdicții noi care nu existau înainte și care pot bloca exact operațiunile pe care multe firme mici le fac de rutină: acordarea de împrumuturi când sunt datorate regularizări de dividende, și restituirea împrumuturilor când firma e subcapitalizată.

## Temeiul legal

::: ghid-temei
**Legea 31/1990, art. 67 alin. (2^3)** — adăugat de Legea 239/2025, în vigoare din 18.12.2025: „Societățile care distribuie trimestrial dividende, potrivit legii, nu pot acorda acționarilor sau asociaților, după caz, sau altor persoane afiliate [...] împrumuturi, până la regularizarea diferențelor rezultate din distribuirea dividendelor în cursul anului."

**Legea 31/1990, art. 67 alin. (2^4)** — adăugat de Legea 239/2025: „Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților [...] împrumuturile luate de la aceștia."

**Legea 31/1990, art. 67 alin. (2^5)-(2^6)** — adăugat de Legea 239/2025: răspundere solidară a societății și a asociatului beneficiar, respectiv contravenție cu amendă de 10.000-200.000 lei pentru nerespectarea interdicțiilor de mai sus.

**Codul fiscal (Legea 227/2015), art. 97 alin. (2)** — impozitarea dobânzii: „Veniturile sub formă de dobânzi [...], contractele civile încheiate se impun cu o cotă de 10% din suma acestora, impozitul fiind final [...] În situația sumelor primite sub formă de dobândă pentru împrumuturile acordate pe baza contractelor civile, calculul impozitului datorat de către plătitorii de venit se efectuează la momentul plății dobânzii."
:::

## Contabilitatea împrumutului

**La primirea banilor de la asociat:**

- `5121 = 4551` — cu suma primită în contul bancar al firmei (contravaloarea contractului de împrumut)

**La restituire**, dacă împrumutul are dobândă:

- `4551 = 5121` — restituirea principalului
- `666 = 4551` — cheltuiala cu dobânda datorată asociatului
- `4551 = 446` — impozitul reținut pe dobândă, 10%, final
- `4551 = 5121` — plata dobânzii nete către asociat

Dacă împrumutul e fără dobândă (frecvent între asociat și firma proprie), rămân doar liniile de principal.

## Ce s-a schimbat din 18 decembrie 2025

Cele două interdicții noi lovesc direct în tiparul obișnuit al firmelor mici cu asociat unic sau puțini asociați:

- **Dacă firma distribuie deja dividende trimestrial** și nu a făcut încă regularizarea anuală, **nu poate acorda împrumuturi** asociaților — nici chiar dacă are lichidități disponibile.
- **Dacă activul net al firmei a scăzut sub jumătate din capitalul social subscris**, firma **nu poate restitui** asociaților împrumuturile pe care le-a primit de la ei, chiar dacă scadența contractuală a venit.

Ambele interdicții sunt însoțite de răspundere solidară a firmei și a asociatului beneficiar, plus o contravenție cu amendă între 10.000 și 200.000 lei. Practic, înainte de a acorda sau de a restitui un împrumut către/de la asociat, trebuie verificate două lucruri: dacă firma a distribuit dividende trimestrial nereglementate încă, și care e valoarea curentă a activului net față de capitalul social subscris.

## Ce se greșește în practică

- **Se tratează suma adusă de asociat ca aport la capital, fără majorare de capital social efectivă.** Fără o hotărâre AGA și o înregistrare la Registrul Comerțului care să majoreze capitalul, banii rămân datorie a firmei față de asociat (4551), nu capital propriu.
- **Se ignoră interdicția de la alin. (2^4) la restituire.** O firmă care vrea să restituie un împrumut vechi de la asociat, dar are activul net sub jumătate din capitalul social, riscă răspundere solidară și amendă dacă face plata oricum.
- **Se calculează dobânda fără să se rețină impozitul de 10%.** Dobânda plătită asociatului persoană fizică e venit impozabil final la sursă — impozitul se reține și se virează de firmă, nu se lasă în sarcina asociatului.

## Ce face iConta.eu

Pentru împrumutul primit de la asociat, aplicația înregistrează automat primirea (`5121 = 4551`) și restituirea, inclusiv dobânda calculată și impozitul reținut de 10% pe dobânda plătită (`4551 = 5121`, `666 = 4551`, `4551 = 446`, `4551 = 5121`).

Verificarea celor două interdicții noi din 2025 — dacă firma poate acorda sau restitui împrumuturi în funcție de regularizarea dividendelor sau de nivelul activului net — nu este automatizată în acest moment. Recomandăm verificarea manuală a acestor condiții înainte de a acorda sau restitui un împrumut către/de la asociat.

[iConta.eu](/)
