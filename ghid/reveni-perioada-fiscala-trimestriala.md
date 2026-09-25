---
title: "Când pot reveni la perioada fiscală trimestrială?"
description: "Condițiile legale de revenire la trimestru calendaristic ca perioadă fiscală de TVA, după ce o achiziție intracomunitară a forțat trecerea temporară la lună."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când pot reveni la perioada fiscală trimestrială?

O firmă cu perioadă fiscală trimestrială la TVA trece obligatoriu la lună calendaristică din momentul în care efectuează o achiziție intracomunitară de bunuri taxabilă în România — dar trecerea nu e definitivă. Legea prevede exact condiția și momentul revenirii la trimestru.

## Temeiul legal

::: ghid-temei
„(8) Persoana impozabilă care potrivit alin. (7) este obligată să își schimbe perioada fiscală trebuie să depună o declarație de mențiuni la organul fiscal competent, în termen de maximum 5 zile lucrătoare de la finele lunii în care intervine exigibilitatea achiziției intracomunitare care generează această obligație, și va utiliza ca perioadă fiscală luna calendaristică pentru anul curent și pentru anul următor. Dacă în cursul anului următor nu efectuează nicio achiziție intracomunitară de bunuri, persoana respectivă va reveni conform alin. (1) la trimestrul calendaristic drept perioadă fiscală. În acest sens va trebui să depună declarația de mențiuni prevăzută la alin. (6)."
— Codul fiscal (Legea 227/2015), art. 322 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul, pas cu pas:

- Firma avea trimestru ca perioadă fiscală (cifră de afaceri sub plafonul de 100.000 euro, fără achiziții intracomunitare — art. 322 alin. (2)).
- Face o achiziție intracomunitară de bunuri taxabilă în România → perioada fiscală devine **lună calendaristică**, obligatoriu, atât pentru anul curent, **cât și pentru anul următor** — nu doar pentru luna în care a avut loc achiziția.
- Revenirea la trimestru se produce automat prin lege **doar dacă, în tot anul următor, nu se mai face nicio altă achiziție intracomunitară de bunuri**.
- Revenirea nu e „din oficiu" la nivel administrativ: trebuie depusă o **declarație de mențiuni** (art. 322 alin. (6)), până la 25 ianuarie, care înscrie cifra de afaceri din anul precedent și menționează explicit că nu s-au făcut achiziții intracomunitare în anul respectiv.

## Ce se greșește în practică

- Se revine la trimestru din prima lună în care nu mai apare o achiziție intracomunitară, fără să se respecte perioada obligatorie de „anul curent + anul următor" impusă de alin. (8).
- Se presupune că revenirea e automată, fără depunerea declarației de mențiuni prevăzute la alin. (6) — fără ea, organul fiscal continuă să aștepte deconturi lunare.
- Se confundă achiziția intracomunitară de bunuri (care declanșează schimbarea) cu achiziția de servicii intracomunitare — regula de la alin. (7)-(8) vizează explicit bunurile, nu serviciile.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu automatizează** schimbarea sau revenirea perioadei fiscale TVA în funcție de achizițiile intracomunitare efectuate. Am găsit în cod modulul `core/perioada_fiscala_tva.py`, care oferă doar text explicativ despre diferența dintre periodicitatea declarației D100 (întotdeauna trimestrială din temeiul impozitului pe profit) și cea a TVA (lunară sau trimestrială, în funcție de situația firmei) — nu calculează și nu urmărește automat momentul din care trebuie depusă declarația de mențiuni. Verificarea condiției de revenire la trimestru rămâne responsabilitatea contabilului.

[iConta.eu](/)
