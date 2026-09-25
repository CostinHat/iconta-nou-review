---
title: "Ce diferențe între SAF-T și balanță pot declanșa verificări?"
description: "Cum folosește ANAF analiza de risc pentru a selecta firmele la inspecție fiscală și ce tip de neconcordanțe SAF-T vs. balanță atrag atenția."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce diferențe între SAF-T și balanță pot declanșa verificări?

Selectarea firmelor pentru inspecție fiscală nu se mai face „la întâmplare" — legea impune ca regulă generală selecția pe bază de analiză de risc, iar SAF-T (D406) oferă ANAF exact datele granulare (note contabile, rulaje per cont) necesare pentru a compara automat ce a raportat firma cu ce ar rezulta din propriile ei înregistrări. O neconcordanță între fișierul SAF-T depus și balanța de verificare reală a firmei e un semnal tipic de risc.

## Temeiul legal

::: ghid-temei
„(1) În cazul creanțelor fiscale administrate de organul fiscal local, selectarea contribuabililor/plătitorilor ce urmează a fi supuși inspecției fiscale este efectuată de către organul de inspecție fiscală competent, în funcție de nivelul riscului. Nivelul riscului se stabilește pe baza analizei de risc. În cazul creanțelor fiscale administrate de organul fiscal central, selectarea contribuabililor/plătitorilor pentru efectuarea acțiunii de inspecție fiscală se efectuează la nivelul aparatului central al ANAF, în funcție de nivelul riscului stabilit pe baza analizei de risc."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 121 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Legea definește explicit „analiza de risc" ca fiind „activitatea efectuată de organul fiscal în scopul identificării riscurilor de neconformare în ceea ce privește îndeplinirea de către contribuabil/plătitor a obligațiilor prevăzute de legislația fiscală" (art. 7 pct. 3). Tipurile de neconcordanțe SAF-T vs. balanță care alimentează tipic o astfel de analiză:

- **Rulaj total per cont diferit** între `GeneralLedgerEntries` din SAF-T și rulajul din balanța de verificare lunară a firmei — semn că fișierul depus nu reflectă integral notele contabile reale.
- **Dezechilibru debit/credit** pe o notă din SAF-T (Σdebit ≠ Σcredit) — indică o notă incompletă la generare, care distorsionează inclusiv soldurile finale raportate.
- **Solduri de deschidere/închidere incompatibile** de la o lună la alta în secțiunile de stocuri sau conturi — un sold de închidere al lunii N care nu devine soldul de deschidere al lunii N+1 e ușor de detectat automat.

Când riscul e identificat, contribuabilul primește întâi o **notificare de conformare** (art. 121¹), cu 30 de zile la dispoziție să corecteze declarațiile înainte de a fi supus obligatoriu inspecției sau verificării documentare, dacă riscul rămâne neremediat.

## Ce se greșește în practică

- Se tratează SAF-T ca pe o formalitate separată de contabilitatea curentă, generată o singură dată „ca să fie depusă", fără reconciliere ulterioară cu balanța — orice eroare de mapare rămâne nedescoperită până la o eventuală notificare ANAF.
- Se ignoră notificarea de conformare primită de la ANAF, presupunând că „nu are legătură cu inspecția" — de fapt, netratarea ei în cele 30 de zile duce direct la inspecție obligatorie, conform art. 121¹ alin. (4).
- Se corectează manual balanța după depunerea SAF-T, fără a redepune și declarația rectificativă corespunzătoare — rămân astfel neconcordanțe vizibile pentru orice comparație automată ANAF vs. contabilitate.

## Ce face iConta.eu

iConta.eu nu are acces la sistemul intern de analiză de risc al ANAF și nu poate simula sau prezice o selecție pentru inspecție. Ce oferă concret: o verificare internă, independentă, a coerenței propriului SAF-T înainte de depunere — `core/d406_reconciliere.py` reconstruiește balanța de rulaje per cont direct din notele contabile validate ale firmei și o compară cu rulajele din fișierul SAF-T generat, blocând depunerea dacă apare o divergență pe un cont sau un dezechilibru debit/credit pe o notă. Scopul e să elimine, înainte de depunere, exact tipul de neconcordanțe (rulaj greșit, notă dezechilibrată) care ar putea atrage atenția unei analize de risc ANAF — nu să evalueze riscul propriu-zis, funcție care nu există în aplicație.

[iConta.eu](/)
