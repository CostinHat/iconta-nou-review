---
title: "Sancțiuni pentru facturi emise fără e-Factura în 2026"
description: "Nerespectarea obligației B2B de transmitere în RO e-Factura se sancționează cu amendă egală cu 15% din valoarea totală a facturii, iar întârzierea peste termenul de 5 zile lucrătoare, cu amenzi fixe separate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Sancțiuni pentru facturi emise fără e-Factura în 2026

De la intrarea în vigoare deplină a obligației B2B (1 iulie 2024), o factură emisă în relația dintre doi contribuabili stabiliți în România, dar netrimisă în RO e-Factura, nu mai e doar o abatere administrativă minoră — legea leagă amenda direct de valoarea facturii, nu de o sumă fixă mică. În 2026 aceste sancțiuni rămân aplicabile în forma consolidată descrisă mai jos.

## Temeiul legal

::: ghid-temei
„Constituie contravenții, dacă nu au fost săvârșite în astfel de condiții încât să fie considerate potrivit legii infracțiuni, următoarele fapte: a) nerespectarea de către emitentul facturii — persoană impozabilă stabilită în România [...] a prevederilor art. 10 alin. (1); b) primirea și înregistrarea de către destinatarul — persoană impozabilă stabilită în România [...] a unei facturi emise de operatori economici stabiliți în România, în relația B2B, fără respectarea prevederilor art. 10 alin. (1); c) nerespectarea prevederilor art. 10 alin. (7). [...] (2) Contravențiile prevăzute la alin. (1) lit. a) și b) se sancționează [...] cu o amendă egală cu 15% din valoarea totală a facturii. (3) Contravenția prevăzută la alin. (1) lit. c) se sancționează cu amendă de la 5.000 lei la 10.000 lei, pentru persoanele juridice încadrate în categoria contribuabililor mari [...], cu amendă de la 2.500 lei la 5.000 lei, pentru persoanele juridice încadrate în categoria contribuabililor mijlocii [...], și cu amendă de la 1.000 lei la 2.500 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice."
— OUG 120/2021, art. 13^2 alin. (1)-(3) (text introdus prin OUG 115/2023, art. LXV pct. 9) (sursă: anaf_surse/oug_115_2023_consolidat.txt)
:::

- Legea sancționează **două fapte distincte, în oglindă**: emitentul care nu transmite factura B2B (lit. a) și destinatarul care primește și înregistrează o astfel de factură fără ca ea să fi respectat obligația de transmitere (lit. b). Ambele se pedepsesc cu aceeași amendă de 15% din valoarea totală a facturii — nu o sumă fixă, ci proporțională, ceea ce poate deveni foarte costisitor la facturi mari.
- Nerespectarea separată a termenului de transmitere de 5 zile lucrătoare (art. 10 alin. (7)) e o contravenție diferită, sancționată cu amenzi fixe, eșalonate pe categorii de contribuabili: 5.000-10.000 lei pentru contribuabilii mari, 2.500-5.000 lei pentru cei mijlocii, 1.000-2.500 lei pentru ceilalți (persoane juridice și fizice).
- Constatarea contravențiilor și aplicarea amenzilor revin organelor fiscale competente.

## Ce se greșește în practică

- Se crede că există o singură amendă „forfetară" pentru orice abatere legată de e-Factura, ignorând că legea distinge net între netransmiterea propriu-zisă (15% din valoarea facturii) și simpla întârziere peste 5 zile (amendă fixă).
- Se subestimează impactul amenzii procentuale la facturile de valoare mare, unde 15% din total poate depăși cu mult amenzile fixe prevăzute pentru alte contravenții fiscale.
- Se presupune că doar emitentul poate fi sancționat — de fapt și destinatarul care înregistrează o factură primită necorespunzător (fără respectarea obligației de transmitere B2B) riscă aceeași amendă de 15%.

## Ce face iConta.eu

Singura funcționalitate verificată în cod în acest dosar de cercetare pentru cuvintele-cheie apropiate acestui titlu este F171 — exportul tehnic al facturilor emise către programul SAGA, care nu are nicio legătură cu sistemul RO e-Factura/SPV și, fiind o punte între două softuri de contabilitate, nu are temei legal propriu, deci nici sancțiuni asociate. Aplicația conține, conform dosarului, un modul separat pentru transmiterea efectivă în e-Factura (`core/efactura_send.py`), dar acest dosar nu a verificat dacă și cum semnalează aplicația riscul de sancțiune pentru facturi netransmise sau transmise cu întârziere — nu facem, deci, nicio afirmație neconfirmată despre asta.

[iConta.eu](/)
