---
title: "Cum se înregistrează o garanție încasată în contul bancar?"
description: "Tratamentul contabil al unei garanții primite de la un client sau partener, cu distincția esențială între angajamentul extrabilanțier și banii încasați efectiv în cont."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o garanție încasată în contul bancar?

O firmă poate primi o garanție de la un client, chiriaș sau partener contractual — de exemplu garanția de bună execuție a unui contract, garanția unei închirieri sau garanția aferentă unui împrumut. Tratamentul contabil diferă radical în funcție de un singur lucru: dacă banii chiar intră fizic în contul bancar al firmei sau dacă garanția e doar un angajament (o promisiune, un gaj) fără nicio mișcare de numerar.

## Temeiul legal

::: ghid-temei
„Contul 802 «Angajamente primite» [...] Cu ajutorul acestui cont se ține evidența angajamentelor primite de către entitate (giruri, cauțiuni, garanții, alte angajamente primite), reflectând eventuala creanță a entității față de terți, generată de angajamentele primite. În debitul contului 802 «Angajamente primite» se înregistrează valoarea angajamentelor în momentul primirii lor de către entitate, iar în credit, valoarea angajamentelor în momentul încetării lor."
— OMFP 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, Clasa 8 „Conturi speciale", Grupa 80 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din text rezultă distincția-cheie:

- Contul 802 (cu subcontul 8021 „Giruri și garanții primite") e un cont **din afara bilanțului**, care funcționează „în partidă simplă" — adică fără o notă contabilă propriu-zisă, cu debit și credit în conturi corespondente. E folosit când garanția primită e un simplu **angajament** (o obligație pe care o are cineva față de firmă, fără să fi mutat bani), nu o încasare efectivă.
- Dacă banii **chiar intră** în contul bancar al firmei — exact situația din titlu, „garanție încasată în contul bancar" — nu mai vorbim de un angajament extrabilanțier, ci de o operațiune de trezorerie reală: firma încasează o sumă pe care o datorează înapoi (integral sau parțial) celui care a depus-o, la un moment ulterior. Aceasta e o operațiune de bilanț, cu o datorie corespunzătoare, nu o simplă evidență extracontabilă.

## Ce se greșește în practică

- Se înregistrează orice garanție primită direct ca venit, ignorând faptul că e o sumă de restituit, nu un câștig al firmei.
- Se confundă cele două cazuri: o garanție-angajament (extrabilanțieră, cont 802/8021) cu o garanție încasată efectiv în bancă (operațiune de trezorerie, cu datorie de restituit).
- Se omite stornarea/închiderea evidenței la momentul în care garanția e restituită sau reținută definitiv (de exemplu, ca despăgubire pentru neexecutarea contractului).

## Ce face iConta.eu

iConta.eu are, în ecranul de operațiuni **Credite bancare** (operațiunea „Garanție"; funcționalitate separată de SGR, verificată în `core/credite.py`), o funcție dedicată de înregistrare a unei garanții primite, care generează nota extracontabilă `8021=891` (valoarea implicită a operațiunii, singura pe care formularul o poate trimite azi). Această funcție acoperă exact cazul „angajament" descris mai sus — o evidență în partidă simplă, fără mișcare de bani.

Important de precizat onest: pentru cazul concret din titlul acestui ghid — o garanție care **chiar intră ca sumă de bani** în contul bancar al firmei — iConta.eu **nu are** o funcție dedicată separată care să genereze automat nota de trezorerie corespunzătoare (încasare + datorie de restituit). Acea operațiune, fiind un caz de bilanț și nu extrabilanțier, trebuie înregistrată manual, printr-o notă contabilă obișnuită de încasare, cu contrapartida potrivită situației concrete.

[iConta.eu](/)
