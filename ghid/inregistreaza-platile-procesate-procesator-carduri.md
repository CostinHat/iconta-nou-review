---
title: Cum se înregistrează plățile procesate de un procesator de carduri
description: Sumele încasate cu cardul prin procesatorii de plăți nu ajung imediat în extrasul de cont — până la decontarea efectivă, se înregistrează distinct în contul 5125 „Sume în curs de decontare".
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează plățile procesate de un procesator de carduri

Când un client plătește cu cardul printr-un procesator (POS, gateway de plăți online etc.), banii nu apar instant în contul bancar al firmei — există un decalaj de decontare, tipic de 1-3 zile lucrătoare. Contabilitatea trebuie să reflecte exact acest decalaj.

### Temeiul: contul 5125 „Sume în curs de decontare"

Reglementările contabile aprobate prin OMFP nr. 1802/2014 tratează explicit această situație, la punctul 302 alin. (2):

> „(2) Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)."

Practic, între momentul în care clientul plătește cu cardul (și firma emite documentul justificativ — bon fiscal, factură) și momentul în care suma apare efectiv în extrasul de cont bancar, valoarea tranzacției stă în contul 5125, nu direct în contul de disponibilități bancare (512).

### Mecanismul contabil, pas cu pas

1. **La momentul vânzării** — se înregistrează venitul (contul de venituri corespunzător) și TVA colectată, pe baza bonului fiscal emis de aparatul de marcat electronic sau a facturii, indiferent de modalitatea de plată.
2. **La momentul încasării prin card** — suma încasată de procesator intră în contul 5125, ca sumă în curs de decontare, nu direct în 512.
3. **La momentul decontării efective** — când banii apar în extrasul de cont bancar (de regulă minus comisionul reținut de procesator), se stinge contul 5125 și se înregistrează suma netă în contul 512.
4. **Comisionul procesatorului** — se înregistrează distinct, ca o cheltuială cu serviciile bancare, nu se scade „pe ascuns" din venit.

### De ce contează distincția, nu doar formal

Dacă tratezi încasarea cu cardul ca și cum ar fi intrat direct în bancă la data vânzării, soldul contului de disponibilități bancare nu se va reconcilia cu extrasul real — diferența „lipsă" e exact suma aflată în tranzit la procesator. Contul 5125 există specific pentru a evita această discrepanță și pentru a permite reconcilierea corectă la finalul fiecărei luni.

### Ce documente stau la bază

- Bonul fiscal sau factura emisă către client, la momentul vânzării.
- Raportul de decontare (settlement report) primit de la procesatorul de carduri, cu sumele brute, comisioanele reținute și sumele nete virate.
- Extrasul de cont bancar, pentru confirmarea sumei nete efectiv încasate.

### Practic, la închiderea lunii

- Reconciliază soldul contului 5125 cu rapoartele de decontare primite de la procesator — un sold rămas necontat la finalul lunii trebuie explicat (tranzacții din ultimele zile, încă nedecontate).
- Nu amâna înregistrarea comisionului procesatorului — el trebuie recunoscut ca cheltuială în perioada la care se referă, nu doar scăzut din suma netă primită.
