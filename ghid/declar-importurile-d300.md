---
title: "Cum declar importurile în D300?"
description: "TVA la import se plătește de regulă în vamă, în afara decontului; doar importatorii cu certificat de amânare autolichidează taxa prin decont. iConta.eu nu modelează azi acest calcul automat în D300 — bunurile importate din afara UE rămân, incorect, pe rândul de operațiuni scutite."
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum declar importurile în D300?

Regimul depinde de statutul importatorului: majoritatea plătesc TVA-ul la import direct organului vamal, în afara decontului de TVA. Doar cei cu certificat de amânare de la plată autolichidează taxa prin decontul D300, ca taxă colectată și dedusă simultan.

## Temeiul legal

::: ghid-temei
„(3) Taxa pentru importuri de bunuri, cu excepția importurilor scutite de taxă, se plătește la organul vamal în conformitate cu reglementările în vigoare privind plata drepturilor de import. [...] (4) Prin excepție de la prevederile alin. (3), nu se face plata efectivă la organele vamale pentru: a) importurile efectuate de persoanele impozabile înregistrate în scopuri de TVA conform art. 316, care îndeplinesc cumulativ condițiile prevăzute la alin. (4^1) și care au obținut certificat de amânare de la plată, conform procedurii stabilite prin ordin al ministrului finanțelor publice; [...]"
— Cod fiscal (Legea 227/2015), art. 326 alin. (3)-(4) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Din text rezultă practic două trasee:

- **Fără certificat de amânare** (cazul obișnuit): TVA-ul de import se achită direct în vamă, la organul vamal, odată cu declarația vamală. Nu apare ca linie deductibilă în D300 pe baza autolichidării — el a fost deja plătit, iar dreptul de deducere se exercită separat, pe baza documentului vamal.
- **Cu certificat de amânare** (condiții cumulative la art. 326 alin. (4^1), inclusiv lipsa obligațiilor fiscale restante): TVA-ul de import nu se mai plătește efectiv la vamă — se autolichidează prin decontul de TVA, la fel ca taxarea inversă: taxă colectată și taxă dedusă simultan, cu efect net zero când deducerea e integrală.

## Ce se greșește în practică

- Se caută un rând „TVA import" în D300 valabil pentru toți importatorii — de fapt majoritatea importurilor nu ating deloc decontul de TVA, fiindcă taxa se plătește direct în vamă.
- Se presupune că orice import din afara UE intră automat pe rândurile de taxare inversă/autolichidare din D300 — doar importatorii cu certificat de amânare de la plată (sau alte excepții de la art. 326 alin. (4)) au acest regim.
- Se declară TVA-ul plătit în vamă ca „achiziție scutită" pentru că nu se știe unde altundeva să fie pus — regimul corect e deducerea taxei plătite la import, nu o scutire.

## Ce face iConta.eu

Pentru bunurile importate din afara UE în regimul obișnuit (fără taxare inversă, cu TVA plătit în vamă), iConta.eu lasă azi operațiunea, la întocmirea D300, pe rândul de achiziții scutite/neimpozabile (rândul 29), **nu pe rândurile de TVA aferentă importului** (în formularul 2026: rândul 24 sau 25, pentru TVA plătită în vamă; rândurile 7 și 22, pentru importul cu certificat de amânare, art. 326 alin. (4) și (5)) — aplicația nu tratează încă acest caz. E o limită cunoscută a aplicației, a cărei reparare depinde de o clarificare separată privind structura oficială a rândului corespunzător.

Servicii primite de la parteneri non-UE, pentru care beneficiarul din România e obligat la plata taxei, se autolichidează corect, automat, ca taxare inversă (rândul 7 colectat + rândul 22 dedus, oglindă). Limitarea de mai sus privește strict **bunurile** importate, nu serviciile.

Practic, dacă firma ta importă bunuri din afara UE, verifică manual regimul aplicabil (plată în vamă sau autolichidare cu certificat de amânare) și, dacă e cazul, introdu rândul corect prin panoul de rânduri manuale D300 — aplicația nu-l derivă azi corect automat din factura de import.

[iConta.eu](/)
