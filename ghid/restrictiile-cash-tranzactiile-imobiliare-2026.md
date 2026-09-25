---
title: "Restricțiile de cash la tranzacțiile imobiliare 2026"
description: "Legea 70/2015 nu prevede un regim special pentru vânzarea-cumpărarea de imobile — se aplică plafonul general de numerar pentru operațiuni cu persoane fizice și cu persoane juridice."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Restricțiile de cash la tranzacțiile imobiliare 2026

Legea limitării utilizării numerarului nu conține un regim special, mai strict, pentru tranzacțiile cu bunuri imobile — se aplică regulile generale: plafonul de 10.000 lei/zi/persoană pentru operațiuni cu persoane fizice (vânzarea unui imobil între o firmă și o persoană fizică) sau de 5.000 lei/10.000 lei pentru operațiuni cu persoane juridice/PFA, cu interdicția expresă de fragmentare a plății pentru a evita plafonul.

## Temeiul legal

::: ghid-temei
„(1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană.
(2) Sunt interzise încasările fragmentate de la o persoană, pentru operațiunile de încasări în numerar prevăzute la alin. (1), cu o valoare mai mare de 10.000 lei, precum și fragmentarea tranzacțiilor reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, respectiv fragmentarea unei livrări de bunuri sau a unei prestări de servicii, cu valoare mai mare de 10.000 lei.
(3) Prevederile alin. (1) și (2) nu se aplică în cazul livrărilor de bunuri și prestărilor de servicii care se efectuează cu plata în rate, în condițiile în care între persoanele prevăzute la art. 1 alin. (1) și persoanele fizice sunt încheiate contracte de vânzare-cumpărare cu plata în rate, conform legii."
— Legea nr. 70/2015, art. 4 alin. (1), (2), (3) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce înseamnă concret pentru o tranzacție imobiliară:

- Un imobil este un „bun" în sensul legii, iar vânzarea lui (livrarea) de către o firmă/PFA către o persoană fizică se supune plafonului general de 10.000 lei/zi de la o persoană (art. 4 alin. (1)) — nu unui plafon special, mai restrictiv.
- Fragmentarea plății/încasării unei sume mai mari de 10.000 lei, în numerar, pentru aceeași tranzacție imobiliară, în mai multe tranșe, este expres interzisă (art. 4 alin. (2)).
- Excepția notabilă: dacă vânzarea imobilului se face **cu plata în rate**, printr-un contract de vânzare-cumpărare cu plata eșalonată încheiat conform legii, plafonul de 10.000 lei și interdicția de fragmentare de la alin. (1)-(2) nu se aplică (alin. (3)) — fiecare rată își are propriul regim, distinct de „fragmentarea" interzisă a unei plăți unice.
- Când tranzacția are loc între două persoane juridice/PFA (de exemplu, o firmă care vinde un imobil altei firme), se aplică plafonul general de 5.000 lei/zi (art. 3), nu cel de 10.000 lei de la art. 4, specific operațiunilor cu persoane fizice.

## Ce se greșește în practică

- Se presupune că tranzacțiile imobiliare au un plafon de numerar special, mai mic sau mai mare decât regula generală — corpusul de legislație verificat pentru acest ghid nu conține o astfel de dispoziție distinctă; se aplică regimul general al art. 3 sau al art. 4, după cum părțile sunt persoane juridice sau persoane fizice.
- Se încearcă plata prețului unui imobil integral în numerar, în mai multe tranșe eșalonate pe zile diferite, fără un contract de vânzare cu plata în rate propriu-zis — aceasta este exact fragmentarea interzisă de art. 4 alin. (2), nu o „plată în rate" în sensul excepției de la alin. (3).
- Se confundă excepția „plății în rate" (care necesită un contract de vânzare-cumpărare cu plata în rate, conform legii) cu simpla înțelegere informală de a plăti prețul în mai multe tranșe, fără un asemenea contract.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o funcționalitate specifică tranzacțiilor imobiliare. Modulul general de casierie (`core/casa.py`, funcția `verifica_plafon`) semnalează totuși, ca avertisment, orice încasare sau plată în numerar care depășește plafonul legal de 10.000 lei/zi/persoană (pentru persoane fizice) sau 5.000 lei/zi/persoană (pentru persoane juridice), indiferent de natura bunului tranzacționat — deci și pentru o eventuală plată în numerar aferentă unui imobil, dacă operațiunea e introdusă ca atare în aplicație.

[iConta.eu](/)
