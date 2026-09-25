---
title: "Numerar de la asociați 2026: restricții noi"
description: "Restricția nouă din 2026 privind împrumuturile către asociați în timpul distribuirii trimestriale de dividende, și cum se leagă de decontările cu asociații."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Numerar de la asociați 2026: restricții noi

De la 18 decembrie 2025, Legea societăților are o restricție nouă, care leagă direct dividendele plătite trimestrial de posibilitatea firmei de a mai acorda împrumuturi asociaților. E important de precizat sensul exact: regula nu limitează cât numerar poate aduce un asociat în firmă (asta rămâne sub plafoanele generale de încasări în numerar), ci interzice firmei să dea bani cu titlu de împrumut asociatului, cât timp nu a regularizat dividendele distribuite în cursul anului.

## Temeiul legal

::: ghid-temei
„Societățile care distribuie trimestrial dividende, potrivit legii, nu pot acorda acționarilor sau asociaților [...] împrumuturi, până la regularizarea diferențelor rezultate din distribuirea dividendelor în cursul anului."
— Legea 31/1990, art. 67 alin. (2^3), introdus de Legea 239/2025, în vigoare de la 18.12.2025 (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Restricția se aplică **doar firmelor care distribuie dividende trimestrial** (deci care optează pentru dividend interimar) și **doar cât timp** diferențele din distribuirea în cursul anului nu au fost regularizate prin situațiile financiare anuale.
- Ea vizează **împrumuturile acordate DE firmă asociaților/acționarilor**, nu sumele pe care asociații le depun în firmă (acelea rămân un împrumut primit de firmă, un subiect distinct).
- Pentru operațiunile de numerar propriu-zise, plafonul general rămâne cel din Legea 70/2015, art. 4 alin. (1): încasările în numerar de la o persoană fizică (deci și de la un asociat, dacă acesta dă bani cu titlu de împrumut firmei) reprezentând „cesiuni de creanțe, primiri de împrumuturi sau alte finanțări [...] se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană" — regulă mai veche, nu introdusă în 2026.

## Ce se greșește în practică

- Se confundă restricția nouă (firma nu poate da împrumut asociatului cât dividendele trimestriale nu sunt regularizate) cu un plafon pe sumele primite de firmă de la asociat — sunt două lucruri diferite, cu temei legal diferit.
- Se continuă acordarea de avansuri/împrumuturi către asociați în paralel cu distribuirea de dividende interimare, fără verificarea prealabilă dacă regularizarea anuală a fost deja făcută.
- Se ignoră complet noul alin. (2^3), pentru că a intrat în vigoare recent (18.12.2025) și nu apare încă în multe rezumate sau ghiduri mai vechi ale art. 67.

## Ce face iConta.eu

Din verificarea codului (`core/decontari_asociati.py`), funcția care generează nota de împrumut către/de la asociat, `nota_imprumut_asociat()`, **nu verifică nicio condiție legată de dividendele interimare nerregularizate** înainte de a genera operațiunea. Aplicația calculează corect liniile contabile ale împrumutului (primire, restituire, dobândă, impozit reținut), dar nu blochează și nu avertizează dacă firma a distribuit dividende trimestrial și nu a făcut încă regularizarea anuală — verificarea restricției din art. 67 alin. (2^3) rămâne, la acest moment, o obligație de conformitate pe care contabilul trebuie s-o urmărească manual, nu o validare automată în iConta.eu.

[iConta.eu](/)
