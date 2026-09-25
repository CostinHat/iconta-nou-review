---
title: "Am plătit impozit pe profit în plus: cum îl recuperez"
description: "Mecanismul legal de compensare și restituire a impozitului pe profit plătit în plus, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am plătit impozit pe profit în plus: cum îl recuperez

O sumă plătită în plus la impozitul pe profit nu se pierde — se restituie, la cerere, dar nu neapărat direct în contul firmei: dacă societatea are alte obligații fiscale restante, suma se folosește mai întâi pentru compensarea acestora, iar doar diferența rămasă se restituie efectiv.

## Temeiul legal

::: ghid-temei
„(1) Se restituie, la cerere, contribuabilului/plătitorului orice sumă plătită sau încasată fără a fi datorată.
[...]
(8) În cazul în care contribuabilul/plătitorul înregistrează obligații restante, restituirea/rambursarea se efectuează numai după efectuarea compensării potrivit prezentului cod.
(9) În cazul în care suma de rambursat sau de restituit este mai mică decât obligațiile restante ale contribuabilului/plătitorului, se efectuează compensarea până la concurența sumei de rambursat sau de restituit.
(10) În cazul în care suma de rambursat sau de restituit este mai mare decât suma reprezentând obligații restante ale contribuabilului/plătitorului, compensarea se efectuează până la concurența obligațiilor restante, diferența rezultată restituindu-se contribuabilului/plătitorului."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 168 alin. (1), (8), (9), (10) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pașii pentru recuperarea unei sume plătite în plus:

1. **Identifici suma plătită în plus** — de exemplu, o plată anticipată de impozit pe profit mai mare decât impozitul anual efectiv datorat, rezultat din regularizarea anuală, sau o eroare de plată.
2. **Depui cererea de restituire** la organul fiscal competent — art. 168 alin. (1) condiționează restituirea de o cerere a contribuabilului, cu excepția câtorva situații de restituire din oficiu enumerate la alin. (4) (care nu includ, în general, impozitul pe profit plătit în plus din proprie inițiativă).
3. **Organul fiscal verifică obligațiile restante** ale firmei, la orice buget — dacă există datorii neachitate, suma de restituit se compensează mai întâi cu acestea (alin. (8)-(9)).
4. **Diferența, dacă rămâne una**, se restituie efectiv contribuabilului, în cazul în care suma de restituit depășește obligațiile restante (alin. (10)).
5. **Compensarea** propriu-zisă, ca mecanism alternativ/prealabil restituirii, este reglementată la art. 167 — creanțele reciproce (statul îți datorează, tu datorezi statului) se sting până la concurența celei mai mici sume, iar organul fiscal comunică decizia de compensare în termen de 7 zile de la efectuarea operațiunii (art. 167 alin. (8)).

## Ce se greșește în practică

- Se așteaptă o restituire automată, din oficiu, a sumei plătite în plus la impozitul pe profit, fără depunerea unei cereri de restituire — restituirea din oficiu este excepția, nu regula (art. 168 alin. (4)).
- Se solicită restituirea integrală, ignorând obligația legală de compensare prealabilă cu orice altă datorie fiscală restantă a firmei, indiferent de buget (art. 168 alin. (8)).
- Se confundă suma plătită în plus la impozitul pe profit cu diferența rezultată din regularizarea anuală a plăților anticipate — aceasta din urmă are un moment de referință distinct pentru calculul exigibilității (data depunerii declarației anuale, potrivit art. 167 alin. (5) lit. h) pct. 2).

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează impozitul pe profit datorat prin modulul D101 (`core/d101.py`, `core/d101_reconciliere.py`), pe baza rezultatului fiscal introdus/calculat din datele contabile, și poate semnala o diferență între plățile anticipate efectuate și impozitul anual datorat. Aplicația nu depune însă cereri de restituire sau de compensare către ANAF și nu urmărește execuția efectivă a compensării cu alte obligații fiscale ale firmei — identificarea sumei plătite în plus și demersul de recuperare la organul fiscal rămân un pas realizat manual de contabil.

[iConta.eu](/)
