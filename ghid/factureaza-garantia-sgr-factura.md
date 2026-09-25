---
title: "Cum se facturează garanția SGR în e-Factura?"
description: "iConta.eu contabilizează operațiunile SGR, dar nu produce facturi sau e-Factura pentru garanția aferentă ambalajelor — cele două fluxuri sunt complet separate în cod."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se facturează garanția SGR în e-Factura?

Comercianții care vând produse în ambalaje SGR trebuie să încaseze de la clienți garanția de 0,50 lei/ambalaj și, dacă emit factură (nu doar bon fiscal), s-o arate distinct pe document. Titlul acestui ghid întreabă specific despre reprezentarea garanției SGR pe o factură electronică transmisă prin sistemul RO e-Factura — un flux tehnic distinct de simpla obligație de afișare de pe bonul fiscal.

## Temeiul legal

::: ghid-temei
„Garanția reprezintă suma plătită de către consumatorul sau utilizatorul final la momentul achiziționării unui produs în ambalaj SGR, separată de prețul produsului, gestionată în cadrul sistemului de garanție-returnare prin intermediul administratorului SGR și care este restituită integral consumatorului sau utilizatorului final la momentul returnării ambalajului SGR în cadrul unui punct de returnare."
— HG nr. 1074/2021 privind stabilirea sistemului de garanție-returnare pentru ambalaje primare nereutilizabile, art. 12 alin. (1) (sursă: anaf_surse/hg_1074_2021_stabilirea_sistemului_garantie_returnare_ambalaje.txt)
:::

- Definiția legală fixează două lucruri obligatorii pentru orice document fiscal: garanția e **separată de preț** și e gestionată prin administratorul SGR, nu de comerciant direct — comerciantul doar o încasează și o restituie, potrivit obligațiilor din art. 6.
- Aceeași hotărâre (art. 6 alin. (1) lit. b), citat integral în ghidul „Cum se facturează ambalajele cu garanție în e-Factura?") cere explicit indicarea distinctă a garanției „pe documentele fiscale aferente produsului în ambalaj SGR" — deci și pe o factură electronică, nu doar pe bonul fiscal.
- Regimul de TVA al garanției (în afara sferei TVA) rămâne, verificat, un aspect care nu are temei explicit chiar în HG 1074/2021 — actul reglementează mecanismul și obligațiile, nu regimul fiscal al garanției.

## Ce se greșește în practică

- Se presupune că, pentru că aplicația de contabilitate „știe" să înregistreze notele SGR, ea generează automat și factura/e-Factura corespunzătoare — cele două operațiuni sunt, tehnic și legal, complet distincte.
- Se omite separarea garanției de preț pe factură, tratând-o ca parte a valorii produsului.
- Se aplică eronat TVA garanției, deși ea nu intră în sfera taxei.

## Ce face iConta.eu

Verificat direct în cod: `core/sgr.py` (motorul SGR) generează exclusiv note contabile — achiziție (`461=401`), vânzare (`5311/5121=462`), restituire către consumator (`461=5311/5121`), autofactură RetuRO (`5121=461` + tarif de gestionare cu TVA) și virare (`462=401/5121`). Niciuna dintre aceste funcții nu emite o factură sau o linie de e-Factura. Căutare exhaustivă în modulele de facturare (`core/facturi_api.py`) și e-Factura (`core/efactura_send.py`, `core/efactura_trimitere.py`, `core/efactura_import.py`) pentru termenii „sgr"/„garant" → zero rezultate.

Concluzia, onestă: **iConta.eu nu facturează și nu transmite prin e-Factura garanția SGR** — aplicația automatizează doar partea contabilă (notele de jurnal), în ecranul dedicat „SGR - garanție ambalaje". Reprezentarea corectă a garanției pe o factură/e-Factura efectivă rămâne, la data acestui ghid, o operațiune manuală, în afara aplicației.

[iConta.eu](/)
