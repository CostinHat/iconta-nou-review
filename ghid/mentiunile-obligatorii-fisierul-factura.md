---
title: "Mențiunile obligatorii în fișierul e-Factura"
description: "Lista elementelor principale pe care structura oficială a facturii electronice RO e-Factura le cere, conform OUG 120/2021."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Mențiunile obligatorii în fișierul e-Factura

Structura facturii electronice din sistemul RO e-Factura nu e la liberă alegere a emitentului — OUG 120/2021 enumeră explicit elementele principale pe care trebuie să le conțină fișierul, ca urmare a respectării standardului european SR EN 16931-1 și a specificațiilor naționale RO_CIUS.

## Temeiul legal

::: ghid-temei
„(2) Elemente principale ale facturii electronice sunt:
a) identificatorii de proces și de factură;
b) data facturii;
c) informații privind identificarea operatorului economic care a livrat bunurile/produsele, a prestat serviciile sau a executat lucrările;
d) informații privind destinatarul facturii electronice;
e) informații privind beneficiarul plății;
f) informații privind reprezentantul fiscal al emitentului;
g) identificarea tipului de bunuri/produse livrate, servicii prestate sau lucrări executate;
h) referirea la contractul de achiziții publice/sectoriale, de concesiune de lucrări și servicii, precum și, după caz, la contractul de achiziții publice în domeniile apărării și securității;
i) detalii privind executarea lucrărilor, livrarea bunurilor/produselor sau prestarea serviciilor;
j) instrucțiuni de plată;
k) informații privind creditări sau debitări;
l) informații privind pozițiile de pe factură;
m) defalcarea TVA;
n) totalul facturii."
— OUG 120/2021, art. 4 alin. (2) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce trebuie reținut din această listă pentru o firmă mică:

- Nu toate cele 14 elemente sunt relevante pentru orice tranzacție — cele legate de contracte de achiziții publice/sectoriale (lit. h) sau de reprezentantul fiscal (lit. f) se aplică doar situațiilor specifice, dar identificatorii de proces/factură, datele părților, poziițiile facturii, defalcarea TVA și totalul (lit. a, b, c, d, g, l, m, n) sunt esențiale pentru orice factură emisă prin sistem.
- Structura trebuie să respecte simultan standardul european SR EN 16931-1 **și** specificațiile naționale RO_CIUS — nu ajunge ca fișierul XML să fie tehnic valid conform standardului european dacă nu respectă și regulile operaționale specifice aplicabile în România.
- O factură care nu respectă structura prevăzută la art. 4 alin. (1) e respinsă de sistem, iar emitentul primește mesaj cu erorile identificate — abia după corectare, factura poate fi retransmisă în același sistem.

## Ce se greșește în practică

- Se completează doar câmpurile „vizibile" pe o factură tradițională (părți, sumă, TVA), ignorând identificatorii de proces/factură ceruți explicit de structura RO_CIUS.
- Se presupune că o factură validă tehnic conform standardului european SR EN 16931-1 e automat acceptată — regulile operaționale specifice RO_CIUS pot impune cerințe suplimentare, naționale.
- Se ignoră mesajele de eroare primite de la sistem la o factură respinsă, retrimițând fișierul nemodificat, în loc să se corecteze elementele semnalate.

## Ce face iConta.eu

iConta.eu generează factura electronică direct din datele deja existente în evidența firmei (parteneri, linii de factură, profil fiscal), construind structura XML UBL 2.1/CIUS-RO cu identificatorii, datele părților, liniile de factură, defalcarea TVA și totalul cerute de art. 4 alin. (2), și o transmite prin conectorul propriu la sistemul RO e-Factura. O limită cunoscută, în lucru: pentru cumpărător, aplicația reține în prezent doar nume/CUI/adresă liberă, în timp ce structura RO_CIUS cere orașul ca element separat (BT-52) — până la completarea acestui câmp dedicat în formularul de factură, informația trebuie introdusă corect direct în câmpul de adresă.

[iConta.eu](/)
