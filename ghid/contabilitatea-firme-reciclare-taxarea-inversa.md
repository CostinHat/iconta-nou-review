---
title: "Contabilitatea unei firme de reciclare: taxarea inversă la deșeuri"
description: "O firmă de reciclare care livrează deșeuri și materiale reciclabile unui alt plătitor de TVA aplică taxare inversă potrivit art. 331 CF, cu formula contabilă 4426=4427 la beneficiar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unei firme de reciclare: taxarea inversă la deșeuri

Pentru o firmă de reciclare, livrarea de deșeuri feroase, neferoase sau alte materiale reciclabile
către un alt plătitor de TVA din România este cazul clasic de taxare inversă internă. Iată cum
arată corect contabilizarea, atât la furnizor, cât și la beneficiar.

## Temeiul legal

::: ghid-temei
„(2) Operațiunile pentru care se aplică taxarea inversă sunt: a) livrarea următoarelor categorii de
bunuri: 1. deșeuri feroase și neferoase [...]; 2. reziduuri și alte materiale reciclabile [...];
3. deșeuri de materiale reciclabile [...] hârtie, carton, material textil, cabluri, cauciuc,
plastic, cioburi de sticlă și sticlă; 4. materialele prevăzute la pct. 1-3 după
prelucrare/transformare [...]"

— art. 331 alin. (2) lit. a) Cod fiscal (Legea 227/2015)

„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa
este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427."

— pct. 109 alin. (1) din normele metodologice (HG 1/2016)
:::

Mecanismul, pas cu pas:

1. **Condiția de bază** — ambele părți trebuie să fie înregistrate în scopuri de TVA conform
   art. 316 CF (art. 331 alin. (1)).
2. **La furnizor (firma de reciclare)** — factura se emite fără TVA colectat, cu mențiunea
   obligatorie „taxare inversă" (pct. 109 alin. (1) din norme). Nu se contabilizează TVA colectat
   pe 4427 pentru operațiunea respectivă.
3. **La beneficiar** — se calculează TVA aferentă și se înregistrează simultan ca taxă colectată și
   deductibilă, prin formula 4426=4427 — impact net zero asupra TVA de plată, dar suma rămâne
   vizibilă în totalurile decontului.
4. Categoria „deșeuri" (lit. a) nu are termen de expirare și nu are prag valoric minim — spre
   deosebire de alte categorii de la art. 331 alin. (2), afectate de termenul din 2026 sau de
   pragul de 22.500 lei.

## Ce se greșește în practică

Greșeli frecvente la firmele de reciclare: omiterea mențiunii „taxare inversă" pe factură (ceea ce,
dacă beneficiarul deduce TVA dintr-o factură greșit emisă cu TVA, poate duce la pierderea dreptului
de deducere al beneficiarului, conform pct. 109 alin. (4) din norme); și introducerea manuală a
sumei în decont, în paralel cu preluarea ei automată din factură, ceea ce dublează suma raportată.

## Ce face iConta.eu

Pentru achizițiile pe categoria „deșeuri" (când firma e beneficiar), ecranul dedicat „Taxare
inversă internă (art. 331)" din iConta validează automat că ambele părți sunt plătitoare de TVA,
generează mențiunea de factură („taxare inversa - art. 331 alin. (2) lit. a) Cod fiscal", text
exact din sursă, fără diacritice) și calculează TVA-ul aferent cu rotunjire aritmetică standard.
Pentru livrările proprii (firma e furnizor, vinde deșeuri), aplicația nu are un ecran dedicat
echivalent — factura se emite prin fluxul obișnuit de facturare, fără TVA, iar mențiunea „taxare
inversă" se adaugă manual de contabil. Indiferent de sursă, suma este preluată automat în
declarația D300 — rd. 13 la emiterea facturii (latura furnizorului) și rd. 12/rd. 25 la primirea ei
(latura beneficiarului, colectat + deductibil, net zero) — și în D394, cu tip de operațiune „V" la
livrare și „C" la achiziție. Pentru D300, dacă
aceeași sumă e introdusă și automat din factură, și manual în rândurile dedicate (rd. 12/13/25),
aplicația blochează calculul decontului cu un mesaj de dublă numărare; la D394 nu există aceeași
verificare dedicată — sumele automate și cele manuale se însumează pe aceeași cheie.

[iConta.eu](/)
