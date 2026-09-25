---
title: "Cum se repartizează discountul unei comenzi între produsele returnate și cele păstrate?"
description: "Principiul contabil din OMFP 1802/2014 pentru determinarea sumei veniturilor recunoscute atunci când o tranzacție include reduceri comerciale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se repartizează discountul unei comenzi între produsele returnate și cele păstrate?

Când o comandă cu discount e parțial returnată, întrebarea practică e simplă: discountul se aplică proporțional pe toate produsele, sau doar pe cele care rămân la client? Reglementările contabile dau răspunsul prin principiul de determinare a sumei veniturilor recunoscute.

## Temeiul legal

::: ghid-temei
„433. - Suma veniturilor rezultate dintr-o tranzacție este determinată, de obicei, printr-un acord între vânzătorul și cumpărătorul/utilizatorul activului, ținând cont de suma oricăror reduceri comerciale."
— OMFP 1802/2014, pct. 433 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o comandă parțial returnată cu discount acordat la nivel de comandă (nu per produs individual):

- discountul face parte din **suma tranzacției convenite** între părți, deci se raportează la valoarea totală a comenzii, nu la fiecare produs izolat — de aici rezultă că repartizarea lui pe produse trebuie să fie **proporțională** cu ponderea fiecărui produs în valoarea totală a comenzii (fără discount), nu împărțit egal sau atribuit arbitrar unui singur produs;
- la returnarea parțială, venitul recunoscut pentru produsele **păstrate** trebuie să reflecte prețul lor net de discount, calculat proporțional — venitul aferent produselor **returnate** se stornează integral (preț net de discount, pe aceeași bază proporțională), nu se anulează doar prețul brut;
- această logică rezultă din principiul general de determinare a venitului net de reduceri comerciale (pct. 433), coroborat cu principiul contabilității de angajamente (pct. 53) — reducerea comercială reduce venitul de la momentul recunoașterii lui, nu se tratează ca o cheltuială separată.
- reglementarea nu detaliază explicit o formulă de repartizare produs-cu-produs pentru cazul specific al returului parțial — proporționalitatea descrisă mai sus e o interpretare rezonabilă a principiului general de la pct. 433, aplicabilă în lipsa unei reguli mai specifice în sursele verificate.

## Ce se greșește în practică

- Se calculează retur-ul pe baza prețului de listă, fără discount, iar apoi discountul rămâne aplicat integral doar pe produsele păstrate — clientul ajunge să „piardă" discountul pe partea returnată, deși acesta era negociat la nivelul întregii comenzi.
- Se atribuie tot discountul unui singur produs din comandă „pentru simplitate", distorsionând marja raportată pe fiecare produs în parte — repartizarea proporțională e cea care păstrează coerența prețului net pe fiecare linie.
- Se stornează la retur doar prețul brut al produsului, fără a recalcula partea proporțională de discount aferentă — rezultă o eroare de venit recunoscut, care afectează atât contabilitatea, cât și baza de calcul a TVA aferentă retur-ului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o funcție dedicată repartizării automate a unui discount aplicat la nivel de comandă între produsele returnate și cele păstrate — nu există în cod un modul de facturare care să gestioneze acest calcul proporțional. Retururile parțiale și discounturile se introduc și se verifică manual de utilizator, pe baza documentelor justificative.

[iConta.eu](/)
