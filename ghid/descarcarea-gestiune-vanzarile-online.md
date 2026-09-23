---
title: "Descărcarea de gestiune la vânzările online"
description: La o firmă cu gestiune cantitativ-valorică, fiecare vânzare online facturată prin integrare descarcă gestiunea individual, legat de factura respectivă — nu există o descărcare unică, pe lot, pentru mai multe vânzări deodată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Descărcarea de gestiune la vânzările online

Mecanismul care descarcă gestiunea la o vânzare online este identic, ca logică, cu cel de la o factură emisă manual din ecran: la emiterea unei facturi cu cel puțin o linie legată de un articol de stoc, se stabilește explicit dacă marfa pleacă odată cu factura. Diferența, la o vânzare online (facturare automată prin integrare), e că această decizie se transmite ca un câmp separat în cererea de emitere, nu printr-o fereastră de confirmare pe ecran.

## Temeiul legal

::: ghid-temei
"440. - În contabilitate, veniturile din vânzări de bunuri se înregistrează în momentul predării bunurilor către cumpărători, al livrării lor pe baza facturii sau în alte condiţii prevăzute în contract, care atestă transferul dreptului de proprietate asupra bunurilor respective, către clienţi."
— OMFP 1802/2014, pct. 440
:::

Momentul contabil relevant e predarea/livrarea mărfii, care în comerțul online poate coincide cu emiterea facturii (comandă onorată imediat, din stoc) sau poate fi ulterioară (comandă în așteptare, precomandă). De aceea fiecare vânzare online tratată prin acest mecanism trebuie să declare individual acest moment, la factura respectivă — nu se aplică o regulă unică, valabilă pentru toate vânzările zilei.

## Ce se greșește în practică

- Se așteaptă ca gestiunea să se descarce "automat, la sfârșitul zilei", pentru toate vânzările online — nu există un asemenea job; fiecare factură emisă prin integrare descarcă (sau nu) gestiunea individual, în momentul emiterii ei.
- Se emit facturi din integrare fără să se seteze răspunsul poartă la nivel de sistem al integratorului — dacă factura are linii de stoc și câmpul lipsește, cererea de emitere e respinsă, nu emisă implicit într-un fel sau altul.
- Se presupune că o vânzare online cu marfă din stoc trece automat printr-o "punte" chiar și atunci când factura e emisă ca proformă sau ca aviz — mecanismul de descărcare automată se activează doar pentru tipul "factura", nu și pentru celelalte tipuri de document.

## Ce face iConta.eu

Pentru firmele cu gestiune cantitativ-valorică, fiecare factură emisă prin API-ul de integrare (folosit tipic de un magazin online) care conține linii legate de articole de stoc cere explicit un răspuns: marfa pleacă odată cu factura sau nu. Dacă răspunsul e afirmativ, gestiunea se descarcă în aceeași operațiune cu emiterea facturii, iar mișcarea de stoc rezultată rămâne legată de factura respectivă — util ulterior, printre altele, pentru calculul profitului pe produs.

Menționăm onest limitele acestui mecanism: se aplică doar firmelor cu gestiune cantitativ-valorică (nu celor pe metoda global-valorică, unde descărcarea rămâne lunară) și doar facturilor propriu-zise (nu proformelor sau avizelor emise prin aceeași integrare). Nu există, la acest moment, o agregare automată care să descarce gestiunea o singură dată pentru toate vânzările online ale unei zile — fiecare factură se tratează individual.

[iConta.eu](/)
