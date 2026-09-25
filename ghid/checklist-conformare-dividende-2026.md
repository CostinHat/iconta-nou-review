---
title: "Checklist de conformare pentru dividende 2026"
description: "Ce trebuie verificat înainte de a distribui și impozita dividende în 2026: cota de impozit, termenele de regularizare și restricția nouă privind împrumuturile către asociați."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Checklist de conformare pentru dividende 2026

Distribuirea dividendelor — anuală sau trimestrială, interimară — e presărată cu termene și reguli care se schimbă frecvent: cota de impozit s-a modificat de trei ori din 2022 încoace, iar din decembrie 2025 a apărut o restricție nouă privind împrumuturile către asociați. Iată ce trebuie verificat înainte de a aproba și plăti un dividend în 2026.

## Temeiul legal

::: ghid-temei
„Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat, opțional trimestrial pe baza situațiilor financiare interimare și anual, după regularizarea efectuată prin situațiile financiare anuale [...] Plata diferențelor rezultate din regularizare se face în termen de 60 de zile de la data aprobării situațiilor financiare anuale [...]. În caz contrar, societatea datorează [...] dobândă penalizatoare calculată conform art. 3 din Ordonanța Guvernului nr. 13/2011 [...]."
— Legea 31/1990, art. 67 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Checklist-ul de conformare, punct cu punct:

- **Cota de impozit pe dividende** — 16% de la 1.01.2026 (Legea 141/2025, care modifică art. 43 alin. (2) Cod fiscal), față de 10% în 2025. Pentru dividendele interimare distribuite în 2025 dar regularizate/plătite în 2026, verifică pe ce dată se aplică cota — nu presupune automat 16%.
- **Regularizarea dividendelor interimare** — dacă firma a distribuit trimestrial în cursul anului, diferența față de dividendul anual aprobat prin situațiile financiare se regularizează, iar plata diferenței (sau restituirea excedentului de la asociat) se face în **60 de zile** de la aprobarea situațiilor financiare anuale (Legea 31/1990 art. 67 alin. (2^2)).
- **Restricție nouă, în vigoare din 18.12.2025** (Legea 31/1990 art. 67 alin. (2^3), introdus de Legea 239/2025): o firmă care distribuie dividende trimestrial **nu poate acorda împrumuturi asociaților** până la regularizarea diferențelor rezultate din distribuirea din cursul anului. Verifică această condiție înainte de a aproba un împrumut către asociat, dacă firma are dividende interimare nereglementate.
- **Dobânda la împrumutul asociat, dacă există** — impozitul reținut la sursă pe dobânda plătită asociatului persoană fizică e de 10% (Cod fiscal art. 64 alin. (1) lit. d) + art. 91 lit. b) — venituri din investiții), nu de 10% în baza art. 97^1 CF, care privește exclusiv dobânzi din obligațiuni pe piețe externe.
- **Prescripția acțiunii de restituire** a dividendelor plătite nelegal (de ex. dacă societatea nu avea profit distribuibil) — 3 ani de la data distribuirii (Legea 31/1990 art. 67 alin. (5)).

## Ce se greșește în practică

- Se aplică aceeași cotă de impozit (16%) tuturor dividendelor din 2026, fără să se verifice dacă unele sunt regularizări ale unor sume distribuite interimar în 2025, la cotă diferită.
- Se aprobă un împrumut către un asociat fără să se verifice dacă firma are dividende trimestriale distribuite și neregularizate încă — situație în care legea, din 18.12.2025, interzice explicit acordarea împrumutului.
- Se calculează termenul de 60 de zile de la data distribuirii, nu de la data **aprobării situațiilor financiare anuale** — cele două date pot fi la distanță de luni.
- Se confundă restituirea excedentului de dividend interimar (când suma plătită trimestrial depășește dividendul anual aprobat) cu o simplă corecție contabilă, fără să se respecte termenul legal de 60 de zile pentru restituire.

## Ce face iConta.eu

Modulul de **Decontări asociați** (Operațiuni speciale > Finanțare) generează notele contabile pentru dividende (anuale și interimare, cu regularizare) și pentru împrumuturi de la/către asociați: `1171=457` + `457=446` la aprobarea dividendului anual, `463=456` + `456=446` la dividendul interimar, `1171=457` + `457=463` la regularizare (cu restituire pe `5121=456` dacă interimarul depășește anualul aprobat), respectiv `5121=4551`/`4551=5121` pentru împrumuturi, cu dobânda pe `666=4551` și impozitul reținut pe `4551=446`. Cota de impozit pe dividende e citită dintr-un registru intern sensibil la dată (10% pentru operațiuni din 2025, 16% pentru cele din 2026), nu e hardcodată.

Aplicația **nu verifică automat** restricția nouă din art. 67 alin. (2^3) — dacă firma are dividende trimestriale neregularizate, nimic din ecranul de „Decontări asociați" nu blochează sau avertizează la introducerea unui împrumut către asociat; verificarea rămâne responsabilitatea contabilului. De asemenea, aplicația nu tratează regimul fiscal special al dividendelor plătite unor asociați nerezidenți (convenții de evitare a dublei impuneri, D207) — calculează nota contabilă cu cota standard, indiferent de rezidența asociatului. Declararea fiscală a dividendelor (D205) e o funcționalitate separată, care se alimentează din notele generate aici.

[iConta.eu](/)
