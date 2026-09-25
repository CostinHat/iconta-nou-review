---
title: "Ce se întâmplă cu comenzile WooCommerce plătite ramburs?"
description: "Încasarea ramburs de la o persoană fizică intră sub plafonul legal de numerar de 10.000 lei pe zi per persoană — un aspect pe care conectorul WooCommerce al iConta.eu nu-l tratează diferit de orice altă comandă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă cu comenzile WooCommerce plătite ramburs?

Plata ramburs (colectarea contravalorii comenzii de către curier, la livrare, de regulă în numerar) e o metodă de plată frecventă în comerțul online din România. Din punct de vedere fiscal, o astfel de încasare rămâne o încasare în numerar, supusă acelorași reguli ca oricare alta.

## Temeiul legal

::: ghid-temei
„Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană."
— Legea 70/2015 privind întărirea disciplinei financiare, art. 4 alin. (1) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Contravaloarea unor livrări de bunuri încasată în numerar de la o persoană fizică e plafonată la 10.000 lei pe zi, de la aceeași persoană — regula se aplică indiferent de canalul de vânzare (magazin fizic, online, ramburs prin curier).
- Fragmentarea încasării (împărțirea unei sume mai mari în mai multe tranșe, pentru a evita plafonul) e explicit interzisă de aceeași lege.
- Deoarece orice comandă WooCommerce e, în practica firmei, facturată către persoana fizică ce a plasat-o, plafonul relevant e cel pentru încasări de la persoane fizice (art. 4), nu cel, diferit, pentru încasări între firme (art. 2).

## Ce se greșește în practică

- Se ignoră plafonul de 10.000 lei pe zi per persoană la comenzi ramburs de valoare mare, sau la mai multe comenzi ramburs plasate de același client în aceeași zi, care s-ar putea cumula peste plafon.
- Se presupune că „ramburs" înseamnă automat plată în numerar la curier — unele firme de curierat colectează ramburs și prin card la livrare, caz în care regulile privind numerarul nu se mai aplică în același fel.
- Se așteaptă ca factura sau evidența contabilă să marcheze diferit, automat, o comandă plătită ramburs față de una plătită online în avans.

## Ce face iConta.eu

Conectorul WooCommerce al iConta.eu **nu citește metoda de plată a comenzii** — nu există în cod niciun cod care să acceseze `payment_method` sau denumirea metodei de plată. O comandă plătită ramburs e tratată identic cu oricare alta: intră în import dacă statusul ei în WooCommerce e `completed` sau `processing`, indiferent cum a fost sau va fi încasată contravaloarea. Nu există, așadar, un tratament contabil special pentru comenzile ramburs — respectarea plafonului legal de încasări în numerar rămâne, ca și până acum, responsabilitatea firmei, urmărită separat de acest import automat.

[iConta.eu](/)
