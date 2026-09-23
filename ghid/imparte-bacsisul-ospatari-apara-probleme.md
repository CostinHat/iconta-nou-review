---
title: Cum se împarte bacșișul între ospătari fără să apară probleme la control
description: Un regulament intern aprobat și o evidență nominală a distribuirii sunt condițiile care apără firma la un control ANAF — nu metoda de împărțire aleasă în sine.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se împarte bacșișul între ospătari fără să apară probleme la control

Legea 376/2022 nu impune o formulă anume de împărțire a bacșișului între angajați (egal, pe ore lucrate, pe funcție) — lasă alegerea metodei la latitudinea operatorului. Ce impune, în schimb, e ca metoda aleasă să fie documentată printr-un regulament intern și aplicată pe bază de evidență nominală. Acestea două sunt exact ce verifică un control.

## Temeiul legal

::: ghid-temei
„Sumele provenite din încasarea bacșișului se înregistrează în contabilitatea operatorilor economici pe seama conturilor de datorii folosind un analitic distinct și se distribuie integral salariaților, pe baza unei evidențe nominale a acestora. Operatorii economici stabilesc, printr-un regulament intern, procedura și modalitatea de distribuire..."

*(Legea nr. 376/2022 pentru modificarea și completarea OUG nr. 28/1999, art. 2^3 alin. (8))*
:::

## Ce apără firma la un control

- **Regulamentul intern aprobat**, care descrie explicit criteriul de împărțire (egal între toți angajații din tură, proporțional cu orele lucrate, ponderat pe funcție etc.) — indiferent care e criteriul, el trebuie să existe în scris, aprobat de operator, nu improvizat lunar.
- **Evidența nominală** — cine a primit cât, la fiecare distribuire, nu o sumă globală „pentru personal".
- **Impozitul de 10% reținut și plătit corect** pe fiecare distribuire individuală, cu declararea la D100 (până pe 25 a lunii următoare) și raportarea informativă la D205 — categoria proprie „Venituri provenite din încasarea bacșișului de către salariați", distinctă de veniturile din alte surse generice.
- **Bacșișul rămâne exclus din statul de plată** — alin. (10) exclude explicit titlul V din Codul fiscal (contribuții sociale) pentru aceste sume; amestecarea lor cu salariul (CAS/CASS reținute) e ea însăși o abatere, nu o măsură de siguranță.

## Ce se greșește în practică

- Bacșișul e împărțit „din ochi", fără regulament scris și fără evidență pe persoană — la un control, nu există cum să se demonstreze criteriul aplicat.
- Regulamentul există, dar nu e efectiv respectat — angajați diferiți primesc sume care nu corespund criteriului declarat.
- Impozitul e reținut o singură dată, global, pe suma totală distribuită într-o lună, în loc de reținere pe fiecare distribuire nominală.

## Ce face iConta.eu

Funcția `nota_distribuire(bacsis_brut, sursa)` din modulul F010 (`core/bacsis.py`) calculează impozitul de 10% și netul pentru fiecare distribuire introdusă, cu rotunjire aritmetică la 2 zecimale, generând nota `462=446` + `462=5121/5311`. Aplicația nu stochează însă evidența nominală pe salariat (cine a primit exact cât din bacșișul distribuit) și nu generează regulamentul intern — acestea rămân documente și evidențe separate, ținute de operator, pe care controlul le cere alături de notele contabile.

[iConta.eu](/)
