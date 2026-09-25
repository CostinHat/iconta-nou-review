---
title: "Cum se facturează ambalajele cu garanție în e-Factura?"
description: "Legea SGR cere afișarea distinctă a garanției pe documentul fiscal, dar iConta.eu nu are încă o modalitate dedicată de a reprezenta acest lucru pe o factură e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se facturează ambalajele cu garanție în e-Factura?

De la intrarea în funcțiune a sistemului garanție-returnare (SGR), fiecare produs vândut într-un ambalaj SGR are asociată o garanție de 0,50 lei, care trebuie arătată separat de prețul produsului — inclusiv pe factură, nu doar la raft. Întrebarea firească pentru comercianții care emit facturi (nu doar bonuri fiscale) e cum se reflectă corect acest lucru într-o factură electronică transmisă prin RO e-Factura.

## Temeiul legal

::: ghid-temei
„Comercianții sunt obligați: [...] b) să indice distinct valoarea garanției la raft și pe documentele fiscale aferente produsului în ambalaj SGR;"
— HG nr. 1074/2021 privind stabilirea sistemului de garanție-returnare pentru ambalaje primare nereutilizabile, art. 6 alin. (1) lit. b) (sursă: anaf_surse/hg_1074_2021_stabilirea_sistemului_garantie_returnare_ambalaje.txt)
:::

- Obligația legală e clară: garanția SGR trebuie evidențiată **distinct** pe orice document fiscal aferent produsului ambalat — bon fiscal sau factură deopotrivă —, nu inclusă tacit în prețul unitar al produsului.
- Garanția, conform art. 12 alin. (1) din același act, „reprezintă suma plătită de către consumatorul sau utilizatorul final la momentul achiziționării unui produs în ambalaj SGR, **separată de preț**" — deci pe o factură trebuie să apară ca linie/valoare distinctă, nu amestecată în baza de calcul a produsului.
- Regimul de TVA al garanției (în afara sferei de TVA, spre deosebire de prețul produsului) nu are, verificat, un temei explicit în HG 1074/2021 — vine din interpretări ale Codului fiscal și precizări ale Ministerului Finanțelor, separate de acest act.

## Ce se greșește în practică

- Se include valoarea garanției SGR în prețul unitar al produsului pe factură, în loc s-o afișeze ca linie distinctă.
- Se aplică aceeași cotă de TVA garanției ca și produsului, deși garanția e, prin natura ei, în afara sferei de TVA.
- Se ignoră complet obligația de afișare distinctă pe facturi (spre deosebire de bonurile fiscale, unde practica e mai răspândită), mai ales la vânzările B2B.

## Ce face iConta.eu

Verificat exhaustiv în cod: modulul care generează notele contabile SGR (`core/sgr.py`, ruta `POST /tenants/{tenant_id}/nota-sgr`) **nu are nicio legătură** cu modulele de facturare sau e-Factura ale aplicației (`core/facturi_api.py`, `core/efactura_send.py`, `core/efactura_trimitere.py`, `core/efactura_import.py` — căutare pe termenii „sgr"/„garant" în toate: zero rezultate). SGR, în iConta.eu, produce exclusiv note contabile de jurnal (achiziție, vânzare, restituire, autofactură, virare), nu facturi.

Onest: iConta.eu **nu automatizează** facturarea (nici pe hârtie, nici prin e-Factura) a garanției SGR. Mai mult, structura actuală a liniilor de factură din modulul de facturare nu are un concept distinct de „în afara sferei de TVA" pentru o linie — deci reprezentarea corectă a garanției SGR pe o factură emisă din iConta.eu, la data acestui ghid, trebuie gestionată manual, în afara aplicației.

[iConta.eu](/)
