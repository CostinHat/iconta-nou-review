---
title: Cum înregistrezi banii aduși de un asociat în casieria firmei
description: Banii depuși de asociat direct în casierie, ca împrumut, se înregistrează 5311 = 4551, cu aceeași logică folosită și pentru sumele intrate prin contul bancar, iar plafoanele pentru operațiuni în numerar rămân de verificat separat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum înregistrez banii aduși de un asociat în casieria firmei?

Când un asociat aduce bani direct în numerar, în casieria firmei, nu în contul bancar, operațiunea rămâne aceeași din punct de vedere contabil — un împrumut către firmă — doar contrapartida se schimbă: casieria (531), nu banca (512).

## Temeiul legal

::: ghid-temei
**Codul fiscal (Legea 227/2015), art. 97 alin. (2)** — dacă suma poartă dobândă: „Veniturile sub formă de dobânzi [...], contractele civile încheiate se impun cu o cotă de 10% din suma acestora, impozitul fiind final [...] calculul impozitului datorat de către plătitorii de venit se efectuează la momentul plății dobânzii."

**Legea 31/1990, art. 67 alin. (2^4)** — adăugat de Legea 239/2025, în vigoare din 18.12.2025: „Societățile care, pe baza situațiilor financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social subscris nu pot restitui acționarilor sau asociaților [...] împrumuturile luate de la aceștia."
:::

## Înregistrarea contabilă

**La depunerea banilor în casierie:**

- `5311 = 4551` — cu suma depusă de asociat în numerar

**La restituire**, tot prin casierie sau prin bancă, după caz:

- `4551 = 5311` (sau `4551 = 5121`, dacă restituirea se face din contul bancar) — principalul
- `666 = 4551`, `4551 = 446`, `4551 = 5311`/`5121` — dacă există dobândă convenită, cu impozitul de 10% reținut la sursă

## Atenție la plafoanele pentru numerar

Chiar dacă suma trece prin casierie și nu prin bancă, rămân aplicabile regulile generale privind operațiunile cu numerar (plafoane de încasări/plăți în numerar, obligația de a nu depăși soldul maxim de casă la sfârșitul zilei) — reguli care nu țin de natura sumei ca împrumut, ci de disciplina financiară generală aplicabilă oricărei operațiuni de casă.

## Ce se greșește în practică

- **Se înregistrează suma direct ca venit al firmei**, fără să se lege de contul 4551. Fără această legătură, suma poate fi interpretată ca venit nejustificat.
- **Se ignoră plafoanele legale pentru operațiuni cu numerar**, tratând depunerea în casierie ca pe o simplă mișcare internă fără nicio limită.
- **Se restituie suma din casierie fără să se verifice, în prealabil, activul net al firmei** — interdicția de la art. 67 alin. (2^4) se aplică indiferent de canalul prin care se face restituirea (casierie sau bancă).

## Ce face iConta.eu

Pentru împrumuturile de la asociat prin contul bancar, aplicația înregistrează automat primirea și restituirea, cu dobânda și impozitul de 10% calculate automat, dacă operațiunea e introdusă ca împrumut. Pentru sumele depuse direct în casierie, contabilul introduce operațiunea cu contrapartida 5311, urmând aceeași logică de cont 4551.

Verificarea plafoanelor legale pentru operațiuni cu numerar și a interdicției de restituire la activ net scăzut, de la art. 67 alin. (2^4), nu este automatizată în acest moment.

[iConta.eu](/)
