---
title: "Ce fac dacă o comandă WooCommerce nu apare în iConta?"
description: "O comandă poate lipsi din iConta din mai multe motive verificabile — configurare, statusul comenzii, conținut gol sau idempotență — iar termenul legal de emitere a facturii curge indiferent de sincronizare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă o comandă WooCommerce nu apare în iConta?

Când o comandă din magazinul online nu se transformă în factură în iConta, cauza e aproape întotdeauna una din câteva situații concrete, verificabile — nu un „bug" generic. Important de reținut: indiferent de cauza tehnică, factura tot trebuie emisă în termenul legal, așa că o comandă „rătăcită" nu scutește de obligația de facturare la timp.

## Temeiul legal

::: ghid-temei
„Pentru alte operațiuni decât cele prevăzute la alin. (15), persoana impozabilă are obligația de a emite o factură cel târziu până în cea de-a 15-a zi a lunii următoare celei în care ia naștere faptul generator al taxei, cu excepția cazului în care factura a fost deja emisă."
— Codul fiscal (Legea nr. 227/2015), art. 319 alin. (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Termenul de emitere a facturii nu depinde de faptul că firma folosește sau nu un conector automat pentru magazinul online — el curge de la faptul generator (livrarea/prestarea), indiferent de canalul de vânzare.
- Dacă o comandă nu ajunge automat ca factură, obligația legală rămâne: factura trebuie emisă manual până la termenul de mai sus, ca pentru orice altă vânzare.
- „Comanda a fost onorată" (livrare/prestare efectivă) e faptul generator relevant, nu momentul plasării comenzii în magazinul online.

## Ce se greșește în practică

- Se presupune că orice comandă vizibilă în magazinul online trebuie neapărat să devină factură automat, indiferent de statusul ei — de fapt conectorul citește doar comenzile aflate în anumite statusuri.
- Se caută eroarea în magazinul online, deși cauza e frecvent lipsa configurării conectorului (chei sau URL neintroduse ori golite) în aplicația de contabilitate.
- Se retrimite manual aceeași comandă, presupunând că „nu s-a procesat", când de fapt a fost deja importată și pur și simplu nu mai apare ca „nouă".
- Se ignoră comenzile fără conținut (fără produse/linii) — acestea sunt sărite intenționat, nu sunt o eroare de sincronizare.

## Ce face iConta.eu

Conectorul WooCommerce (ecranul „Magazin online", cu config URL + chei API și butonul „Sincronizează acum") citește comenzile prin API-ul magazinului și le transformă în facturi, cu patru verificări reale, confirmate direct în cod (`core/woocommerce.py`):

- **Configurare lipsă sau incompletă.** Dacă URL-ul sau cheile API nu sunt completate (ori au fost golite între timp), sincronizarea se oprește cu mesajul „WooCommerce neconfigurat" — nicio comandă nu poate fi citită.
- **Statusul comenzii.** Conectorul citește implicit doar comenzile aflate în stare `completed` sau `processing`. O comandă `pending`, `on-hold`, `cancelled` sau `refunded` nu e citită niciodată de sincronizare, oricât de multe ori se apasă butonul.
- **Comandă fără conținut.** O comandă fără linii de produs e sărită tăcut, contorizată separat la „sărite", nu la „importate" — nu apare ca eroare vizibilă.
- **Idempotența.** O comandă deja transformată în factură nu mai e reimportată la o sincronizare ulterioară — comportament voit, ca să nu apară facturi duplicate.

O limitare identificată la verificarea codului, nedocumentată încă în textul de ajutor al aplicației: reperul de la care sincronizarea citește comenzi noi avansează pe **data curentă**, nu pe data comenzii celei mai vechi rămase neprocesate. Dacă acest reper filtrează comenzile după data lor de creare (comportament tipic al API-ului WooCommerce, neconfirmat însă printr-un test direct pe un magazin real), o comandă creată într-o zi și care ajunge abia câteva zile mai târziu în starea `completed` riscă să rămână definitiv în afara ferestrei citite de sincronizările ulterioare. Dacă suspectați acest caz, verificați manual, direct în magazinul online, comenzile mai vechi care au trecut târziu în `completed`/`processing` și, dacă lipsesc din iConta, introduceți factura manual.

[iConta.eu](/)
