---
title: "Cum recuperez TVA plătită în vamă la import"
description: Deducerea TVA plătită la vamă se face pe baza declarației vamale de import și a dovezii plății — nu automat, ci prin condițiile exprese de la art. 299 alin. (1) lit. c).
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum recuperez TVA plătită în vamă la import

Când o firmă plătitoare de TVA nu are certificat de amânare de la plată, TVA-ul aferent unui import se plătește direct la vamă. Recuperarea acestei sume nu e automată — legea condiționează dreptul de deducere de existența unor documente specifice.

## Temeiul legal

::: ghid-temei
„c) pentru taxa achitată pentru importul de bunuri, altele decât cele prevăzute la lit. d), să dețină declarația vamală de import sau actul constatator emis de organele vamale, care să menționeze persoana impozabilă ca importator al bunurilor din punctul de vedere al taxei, precum și documente care să ateste plata taxei de către importator [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 299 alin. (1) lit. c)
:::

Condiția e dublă: firma trebuie să dețină **declarația vamală de import (DVI)** sau actul constatator emis de organele vamale, care s-o menționeze explicit ca importator din punctul de vedere al taxei, **și** documente care să dovedească faptul că taxa a fost efectiv plătită. Fără oricare din cele două, deducerea nu are acoperire documentară.

::: ghid-temei
„(3) Taxa pentru importuri de bunuri, cu excepția importurilor scutite de taxă, se plătește la organul vamal în conformitate cu reglementările în vigoare privind plata drepturilor de import."

— Codul fiscal (Legea 227/2015 consolidat), art. 326 alin. (3)
:::

Acest traseu — plată la vamă, apoi deducere pe baza DVI — este regula generală pentru firmele fără certificat de amânare. Alternativa, disponibilă doar unei categorii restrânse de firme (cu certificat de amânare de la plată, condiționat de un plafon de minimum 50 milioane lei importuri din țări terțe în ultimele 6 luni și alte condiții cumulative de la art. 326 alin. 4^1), evită plata efectivă la vamă și reflectă totul direct în decontul de TVA.

## Ce se greșește în practică

- Se așteaptă deducerea automată a TVA-ului plătit la vamă doar pe baza plății, fără să se păstreze declarația vamală de import (DVI) sau actul constatator care să menționeze firma drept importator din punct de vedere al taxei.
- Se confundă condițiile de deducere la import cu cele de la o achiziție internă obișnuită (unde e suficientă factura), ignorând că la import legea cere specific DVI/actul constatator plus dovada plății.
- Se presupune că certificatul de amânare de la plată e disponibil oricărei firme plătitoare de TVA, ca alternativă la plata la vamă, fără verificarea plafonului de 50 milioane lei și a celorlalte condiții de la art. 326 alin. (4^1).

## Ce face iConta.eu

Pentru firmele plătitoare de TVA fără certificat de amânare, aplicația calculează baza de TVA și taxa aferentă importului (pe baza valorii vamale, taxelor, accizelor, accesoriilor și cotei declarate explicit) și generează automat nota contabilă corespunzătoare modului „vamă": 4426 = 446, reflectând TVA-ul plătit la vamă și dedus pe baza declarației vamale de import, conform art. 299 alin. (1) lit. c). Documentele efective (DVI, dovada plății) rămân în sarcina contabilului — aplicația calculează suma și generează nota contabilă, dar nu verifică existența fizică a documentelor justificative.

De precizat o limitare curentă: la data acestei cercetări, aplicația nu populează automat rândul de TVA la import (rd.21) în D300 pentru operațiunile cu parteneri din afara UE — acestea rămân clasificate generic pe rd.26, indiferent de modul de tratare calculat la import. Contabilul trebuie să verifice manual reflectarea corectă a deducerii în decontul depus.

[iConta.eu](/)
