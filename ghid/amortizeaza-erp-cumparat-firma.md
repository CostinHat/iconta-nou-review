---
title: "Cum se amortizează un ERP cumpărat de firmă?"
description: "Perioada de amortizare fiscală pentru programele informatice, potrivit Codului fiscal — și diferența față de amortizarea calculatoarelor fizice."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se amortizează un ERP cumpărat de firmă?

Un sistem ERP cumpărat sau produs pentru firmă e o imobilizare necorporală (licență/program informatic), nu un mijloc fix corporal — iar Codul fiscal îi stabilește o perioadă fixă de amortizare, diferită de duratele din catalogul mijloacelor fixe.

## Temeiul legal

::: ghid-temei
„Cheltuielile aferente achiziționării de brevete, drepturi de autor, licențe, mărci de comerț sau fabrică, drepturi de explorare a resurselor naturale și alte imobilizări necorporale recunoscute din punct de vedere contabil [...] se recuperează prin intermediul deducerilor de amortizare liniară pe perioada contractului sau pe durata de utilizare, după caz. Cheltuielile aferente achiziționării sau producerii programelor informatice se recuperează prin intermediul deducerilor de amortizare liniară sau degresivă pe o perioadă de 3 ani."
— Legea nr. 227/2015, art. 28 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă concret pentru un ERP:

- **Programele informatice** (categorie în care se încadrează un ERP achiziționat ca licență sau produs pe comandă) au o regulă specială și clară: amortizare fiscală pe **3 ani**, prin metodă liniară sau degresivă — contribuabilul poate alege între cele două metode.
- Regula e diferită de cea generală pentru celelalte imobilizări necorporale (brevete, mărci, licențe de altă natură), care se amortizează „pe perioada contractului sau pe durata de utilizare" — pentru programele informatice, legea nu lasă loc de negociere a duratei, fixând-o direct la 3 ani.
- Diferența față de hardware: calculatoarele electronice și echipamentele periferice (partea fizică, dacă firma cumpără și servere/stații pentru ERP) se amortizează separat, ca mijloace fixe corporale, conform Catalogului privind clasificarea și duratele normale de funcționare (clasa 2.2.9, 2-4 ani) — licența ERP și hardware-ul pe care rulează sunt active distincte, cu reguli de amortizare distincte.
- Dacă achiziția ERP e finanțată printr-un contract de leasing financiar și e pusă în funcțiune, ea poate intra și sub incidența scutirii pentru profitul reinvestit (art. 22), care menționează explicit „programe informatice, precum și [...] dreptul de utilizare a programelor informatice".

## Ce se greșește în practică

- Se amortizează ERP-ul pe durata contractului de licențiere (de exemplu 5 sau 10 ani), tratându-l ca „licență generică" în loc de „program informatic" — regula specifică de 3 ani din art. 28 alin. (9) se aplică indiferent de durata comercială a contractului.
- Se amestecă în aceeași fișă de amortizare costul licenței ERP (3 ani) cu costul hardware-ului pe care rulează (2-4 ani, conform catalogului mijloacelor fixe) — sunt active diferite, amortizate diferit.
- Se omite posibilitatea metodei degresive pentru programele informatice, presupunând că doar metoda liniară e permisă — legea permite explicit ambele metode.

## Ce face iConta.eu

Modulul de amortizare a mijloacelor fixe din iConta.eu (`core/d406_active.py`) recunoaște categoria de activ prin contul de imobilizare asociat și aplică regulile de amortizare corespunzătoare, inclusiv metodele liniară și degresivă. Încadrarea unei achiziții ERP ca „program informatic" (cu durata fixă de 3 ani, conform art. 28 alin. (9)) versus mijloc fix corporal separat pentru hardware rămâne o decizie a contabilului la introducerea activului, pe baza facturii și a naturii reale a achiziției.

[iConta.eu](/)
