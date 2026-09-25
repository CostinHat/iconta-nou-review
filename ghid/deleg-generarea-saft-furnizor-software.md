---
title: "Cum deleg generarea SAF-T către un furnizor de software"
description: "Ce se poate delega tehnic la fișierul standard de control fiscal și ce obligație rămâne, prin lege, doar a contribuabilului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum deleg generarea SAF-T către un furnizor de software

Generarea tehnică a fișierului SAF-T (D406) poate fi făcută de orice software — a firmei sau al unui furnizor extern. Ce nu se poate delega, potrivit legii, e obligația însăși de depunere: aceasta rămâne, prin definiție legală, a contribuabilului sau a plătitorului, indiferent cine a produs efectiv fișierul XML.

## Temeiul legal

::: ghid-temei
„Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fișierul standard de control fiscal."
— Legea 207/2015, art. 59^1 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text pentru relația cu un furnizor de software:

- **Obligația legală e nominală**, atașată contribuabilului/plătitorului, nu unui prestator tehnic — un contract cu un furnizor de software care generează fișierul nu transferă răspunderea depunerii.
- **Corectitudinea conținutului rămâne a firmei**: dacă fișierul generat de un terț conține erori (parteneri clasificați greșit, solduri incorecte), firma răspunde pentru depunerea unei declarații incorecte, nu furnizorul de software.
- **Depunerea în format electronic**, la termenul stabilit prin ordin al președintelui ANAF (art. 59^1 alin. 2), e tot un pas care poate fi tehnic externalizat, dar procedural rămâne în responsabilitatea plătitorului.

## Ce se greșește în practică

- Se presupune că semnarea unui contract cu un furnizor de software transferă și răspunderea fiscală a depunerii, când legea leagă obligația explicit de contribuabil/plătitor (art. 59^1 alin. 1).
- Se acceptă fișierul generat de furnizor fără o verificare internă a corectitudinii lui — mai ales pe secțiunile care cer judecată fiscală (clasificarea partenerilor, tratamentul taxării inverse), nu doar extragere mecanică de date.
- Se ignoră termenul de corecție de 5 zile lucrătoare după respingerea unui fișier invalid (art. 59^1 alin. 3) — o eroare a furnizorului descoperită târziu poate consuma acest termen fără ca firma să-și dea seama.

## Ce face iConta.eu

iConta.eu generează fișierul SAF-T (D406) intern, din propriile evidențe contabile ale firmei (`core/d406.py`), fără să depindă de un furnizor extern de software pentru acest pas. Aplicația nu oferă o funcție de „delegare" sau export către un alt generator SAF-T terț — fluxul e integrat: facturile, amortizarea și stocurile din iConta.eu alimentează direct declarația. Persoanele fizice autorizate, întreprinderile individuale și cele familiale (PFA/II/IF) sunt excluse necondiționat din obligația SAF-T, conform OPANAF 407/2025, Anexa 5 pct. 4 lit. a)-c) — cod care nu le generează declarația pentru că legea nu o cere.

[iConta.eu](/)
