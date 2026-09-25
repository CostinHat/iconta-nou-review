---
title: "Retururi și refulări online 2026: impact pe casierie"
description: "Cât poate restitui în numerar un magazin online atunci când un client returnează marfa, și când restituirea trebuie făcută obligatoriu prin bancă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Retururi și refulări online 2026: impact pe casierie

Un magazin online care vinde către persoane fizice și primește retururi nu poate restitui oricât în numerar la curier sau la ramburs. Legea 70/2015 privind disciplina financiară pune un plafon separat pentru restituiri, diferit de plafonul de încasare, iar depășirea lui e o problemă de casierie, nu doar de contabilitate.

## Temeiul legal

::: ghid-temei
„(2) În cazul returnării de bunuri de către persoanele fizice și, respectiv, neprestării de servicii către persoanele fizice, restituirea sumelor aferente poate fi efectuată în numerar în limita a 10.000 lei, sumele care depășesc acest plafon putând fi restituite numai prin instrumente de plată fără numerar. Prin excepție, în cazul în care, la data restituirii, persoanele fizice declară pe propria răspundere că nu mai dețin cont bancar, restituirea se poate face integral în numerar, indiferent de nivelul sumei care trebuie restituită."
— Legea 70/2015, art. 9 alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Concret, pentru un retur online plătit inițial ramburs sau cash la livrare:

- Restituirea se poate face în numerar **doar până la 10.000 lei** pentru o singură restituire către aceeași persoană fizică.
- Peste acest plafon, diferența se restituie **numai prin instrument de plată fără numerar** (transfer bancar, card) — nu se poate „rotunji" restul în cash.
- Excepția: clientul declară pe propria răspundere că nu are cont bancar — atunci restituirea integrală se poate face în numerar, indiferent de sumă.
- Plafonul e distinct de cel de la încasare (art. 3) și de cel pentru facturi stornate către alte firme (art. 9 alin. (1), 5.000 lei, respectiv 10.000 lei la cash and carry) — nu se confundă cele două situații.

## Ce se greșește în practică

- Se aplică din reflex plafonul de încasare de la persoane juridice (5.000 lei) și la restituiri către persoane fizice, deși legea prevede un plafon separat, de 10.000 lei.
- Se restituie integral în numerar o sumă mare doar pentru că „așa a cerut clientul", fără declarația scrisă pe propria răspundere că nu deține cont bancar — declarație care e condiția excepției, nu o formalitate opțională.
- Se tratează refuzul la livrare (marfa nu ajunge la client, deci nu există „retur" efectiv) la fel ca returul propriu-zis, deși contabil pot cere tratamente diferite pe factura stornată.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul dedicat de gestiune a rambursurilor de comerț electronic** care să verifice automat plafonul din art. 9 alin. (2) la momentul restituirii. Aplicația oferă evidența generală de casierie (`core/casa.py`), cu plafoanele de încasare/plată în numerar prevăzute de Legea 70/2015 și verificarea lor pe operațiunile introduse (`core/casa_api.py`, `verifica_plafon`), dar restituirea specifică unui retur din vânzare online rămâne o operațiune pe care contabilul o introduce și încadrează manual, urmărind el însuși plafonul de 10.000 lei.

[iConta.eu](/)
