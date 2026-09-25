---
title: "Poate ANAF recalcula TVA pentru perioade deja controlate?"
description: "Când poate ANAF să reia o perioadă deja inspectată — condițiile cumulative ale reverificării — și cât timp rămâne expus contribuabilul, conform Codului de procedură fiscală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate ANAF recalcula TVA pentru perioade deja controlate?

Regula generală e că o inspecție fiscală încheiată „închide" perioada verificată — ANAF nu poate reveni oricând asupra ei. Există însă o excepție strict reglementată, **reverificarea**, care permite reluarea unei perioade deja controlate dacă apar, ulterior, informații noi pe care organul fiscal nu le cunoștea la data inspecției. În plus, chiar și fără reverificare, dreptul ANAF de a stabili obligații fiscale e limitat de termenul general de prescripție.

## Temeiul legal

::: ghid-temei
„(1) Prin excepție de la prevederile art. 118 alin. (3), conducătorul organului de inspecție fiscală poate decide reverificarea unor tipuri de obligații fiscale pentru o anumită perioadă impozabilă, la propunerea organului de inspecție fiscală desemnat cu efectuarea inspecției sau la cererea contribuabilului, dacă sunt îndeplinite următoarele condiții cumulative:
a) după încheierea inspecției fiscale apar date suplimentare care erau necunoscute organului de inspecție fiscală sau, după caz, contribuabilului, la data efectuării inspecției fiscale;
b) datele suplimentare influențează rezultatele inspecției fiscale încheiate.
(2) Prin date suplimentare se înțelege orice fapt sau mijloc de probă de care se ia cunoștință ulterior inspecției, de natură să modifice rezultatele inspecției anterioare."
— Legea 207/2015 (Codul de procedură fiscală), art. 128 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Reverificarea nu e la liberul discreționar al inspectorului — cere **ambele** condiții cumulate: date noi, necunoscute la data inspecției, care influențează efectiv rezultatele acesteia. O simplă reinterpretare a acelorași fapte, deja cunoscute, nu justifică reverificarea.
- Poate fi declanșată fie din inițiativa organului de inspecție, fie **la cererea contribuabilului însuși** — inclusiv atunci când acesta nu mai poate corecta singur o declarație de impunere.
- Decizia de reverificare trebuie comunicată contribuabilului și poate fi contestată; pentru reverificare nu se mai emite aviz de inspecție fiscală separat.
- Independent de reverificare, dreptul organului fiscal de a stabili creanțe fiscale se prescrie: „Dreptul organului fiscal de a stabili creanțe fiscale se prescrie în termen de 5 ani, cu excepția cazului în care legea dispune altfel" (art. 110 alin. (1) din același cod) — termen extins la 10 ani dacă obligațiile rezultă dintr-o faptă penală.

## Ce se greșește în practică

- Se presupune că o perioadă „închisă" de o inspecție anterioară e definitiv intangibilă — de fapt rămâne expusă reverificării, oricând apar date noi relevante, fără limită de timp în afara prescripției generale.
- Se confundă reverificarea (reluarea unei inspecții deja încheiate, condiționată de date noi) cu refacerea inspecției fiscale (reluare impusă în urma admiterii unei contestații) — sunt proceduri diferite, cu temeiuri și condiții diferite.
- Se ignoră faptul că un contribuabil poate cere el însuși reverificarea, atunci când vrea să corecteze o eroare descoperită ulterior și nu mai poate face acest lucru printr-o simplă declarație rectificativă.

## Ce face iConta.eu

Subiectul acestui ghid este pur procedural-legal, guvernat de Codul de procedură fiscală, și nu are legătură cu **F118 — Blocare perioade**, mecanismul intern al aplicației care protejează integritatea evidenței contabile a firmei (blochează scrierea de note noi într-o lună închisă, per tenant). Verificat direct în cod: motorul SAF-T (`core/d406.py`) și modulul de control fiscal nu verifică deloc tabela `perioade_blocate`, iar reverificarea fiscală de care vorbește art. 128 e o procedură desfășurată exclusiv de ANAF, asupra propriei sale decizii de impunere anterioare — nu ceva ce o aplicație de contabilitate ar putea automatiza sau preveni. Ceea ce oferă iConta.eu în zona adiacentă este blocarea perioadelor contabile proprii ale firmei (F118) și, separat, controlul încrucișat intern D300 vs. evidența contabilă, util pentru a reduce riscul ca ANAF să găsească motive de reverificare — dar niciuna dintre aceste funcționalități nu „răspunde" pentru firmă la o reverificare deja declanșată de organul fiscal.

[iConta.eu](/)
