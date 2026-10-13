---
title: "Cum contabilizez încasarea unei facturi în valută?"
description: "Explică ce curs BNR se aplică unei facturi emise în valută și cum îl gestionează automat iConta.eu, inclusiv la stornare."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum contabilizez încasarea unei facturi în valută?

Ca și la o factură de plătit în valută, punctul de plecare e cursul BNR corect atașat facturii — încasarea ulterioară nu îl modifică.

O factură emisă în valută se înregistrează în lei la cursul BNR valabil la data operațiunii (data exigibilității taxei, care în general coincide cu data facturii). Încasarea ulterioară, la un curs diferit, nu modifică baza de TVA a facturii — generează, separat, o diferență de curs valutar la decontare.

## Ce se greșește în practică

Greșeala tipică e „ajustarea" retroactivă a facturii la cursul zilei încasării, în loc să se lase factura la cursul ei de emitere și să se trateze diferența de curs ca element financiar separat. O altă greșeală e lăsarea facturii fără curs valutar atașat, ceea ce blochează raportarea corectă în declarații.

## Ce face iConta.eu

La emiterea facturii în valută, iConta.eu determină automat cursul BNR valabil la data facturii și îl salvează pe factură; acest curs alimentează apoi toate conversiile din declarații (D300, D390, D394, D406) și din contare, printr-o singură sursă de conversie — o factură fără curs valutar atașat e exclusă din declarații, nu tratată tacit cu curs 1. La stornare, cursul folosit rămâne cel al facturii originale, nu cursul zilei de stornare. Contabilul poate introduce manual un curs alternativ, cu data comunicării lui (nu poate fi ulterioară datei facturii) și autorul modificării, iar sursa cursului (BNR sau manual) e afișată explicit pe factură.

Un aspect de reținut: pe factura electronică trimisă prin e-Factura (XML UBL transmis la ANAF), suma și moneda apar în valuta facturii — XML-ul generat nu include un total de TVA convertit în lei sau cursul folosit; cursul BNR e vizibil pe PDF-ul local al facturii, nu în fișierul transmis către SPV.

[iConta.eu](/)
