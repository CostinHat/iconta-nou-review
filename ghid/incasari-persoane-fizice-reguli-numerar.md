---
title: "Încasări de la persoane fizice: reguli de numerar 2026"
description: "Plafonul zilnic de 10.000 lei pentru încasările în numerar de la o persoană fizică, valabil neschimbat în 2026, conform Legii 70/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Încasări de la persoane fizice: reguli de numerar 2026

Firmele care încasează în numerar de la persoane fizice — cesiuni de creanțe, împrumuturi primite, contravaloarea unor livrări sau prestări — au un plafon distinct de cel aplicat între firme. Pentru 2026, plafonul rămâne cel din forma consolidată a legii, fără modificări recente identificate în textul actului.

## Temeiul legal

::: ghid-temei
„(1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană. (2) Sunt interzise încasările fragmentate de la o persoană, pentru operațiunile de încasări în numerar prevăzute la alin. (1), cu o valoare mai mare de 10.000 lei."
— Legea 70/2015, art. 4 alin. (1)-(2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Reguli aplicabile în 2026:

- **Plafonul rămâne 10.000 lei pe zi, de la aceeași persoană fizică** — verificat pe textul consolidat al Legii 70/2015, care nu conține nicio modificare a acestui plafon pentru 2026.
- Se aplică unei liste largi de operațiuni: **cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, contravaloarea unor livrări de bunuri sau prestări de servicii** — nu doar vânzărilor obișnuite.
- **Fragmentarea e interzisă expres** — nu se pot împărți încasări mai mari de 10.000 lei de la aceeași persoană în tranșe succesive, în zile diferite, pentru a rămâne sub plafon.
- Excepție: operațiunile cu plata în rate, pe baza unui contract de vânzare-cumpărare cu plata eșalonată, nu intră sub incidența acestor alineate (art. 4 alin. (3)).

## Ce se greșește în practică

- Se aplică plafonul de 5.000 lei (cel dintre firme, art. 3) la încasările de la persoane fizice — plafonul corect e cel de 10.000 lei, de la art. 4.
- Se presupune că regula s-a schimbat pentru 2026, fără verificare la sursă — textul consolidat al Legii 70/2015, verificat direct, nu arată nicio modificare a plafoanelor de numerar aplicabilă din 2026.
- Se ignoră excepția pentru contractele cu plata în rate, tratând orice încasare eșalonată de la o persoană fizică drept fragmentare interzisă — legea le tratează diferit, exact pentru a nu bloca vânzările în rate legitime.

## Ce face iConta.eu

La data acestui ghid, `core/casa.py` are constanta `PLAFON_PF = Decimal("10000")`, aplicată în `verifica_plafon()` pentru orice încasare sau plată cumulată cu o persoană fizică, într-o zi. Aplicația nu are un flux separat pentru excepția contractelor cu plata în rate — orice încasare eșalonată de la o persoană fizică e evaluată prin aceeași regulă de cumul zilnic, iar excluderea ei, unde se aplică, rămâne o decizie a contabilului.

[iConta.eu](/)
