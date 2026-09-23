---
title: Greșeala de a nu împărți corect bacșișul între angajați
description: Legea 376/2022 cere distribuire integrală, nominală, pe bază de regulament intern — nu o sumă globală lăsată „la liber" sau păstrată de firmă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeala de a nu împărți corect bacșișul între angajați

Bacșișul încasat de un restaurant sau bar nu e al firmei, ca să decidă ea cum și dacă îl împarte — legea obligă la distribuire integrală, pe baza unei evidențe nominale a angajaților și a unei proceduri stabilite printr-un regulament intern. Orice abatere de la aceste două condiții e o greșeală de conformare, nu o simplă alegere de management.

## Temeiul legal

::: ghid-temei
„Sumele provenite din încasarea bacșișului se înregistrează în contabilitatea operatorilor economici pe seama conturilor de datorii folosind un analitic distinct și se distribuie integral salariaților, pe baza unei evidențe nominale a acestora. Operatorii economici stabilesc, printr-un regulament intern, procedura și modalitatea de distribuire..."

*(Legea nr. 376/2022 pentru modificarea și completarea OUG nr. 28/1999, art. 2^3 alin. (8))*
:::

## Ce cere legea, punct cu punct

- **Distribuire integrală** — nu parțială, nu „ce rămâne după cheltuieli". Tot bacșișul încasat, mai puțin impozitul de 10% reținut la sursă, ajunge la salariați.
- **Evidență nominală** — pe fiecare salariat, nu o sumă globală „pentru echipă".
- **Regulament intern aprobat** — procedura și modalitatea de împărțire (egală, pe ore lucrate, pe funcție etc.) trebuie stabilite explicit de operator, nu improvizate lunar.

## Ce se greșește în practică

- **Bacșișul e împărțit fără evidență nominală** — o sumă globală trecută în plic sau distribuită verbal, fără să se poată reconstitui cine a primit cât.
- **Nu există regulament intern** care să stabilească procedura de distribuire — fără el, orice metodă de împărțire e greu de apărat la un control.
- **Distribuirea nu e integrală** — firma reține o parte „pentru cheltuieli operaționale" sau „rezervă", deși alin. (8) și (9) exclud explicit orice altă destinație a bacșișului în afara salariaților.
- **Impozitul de 10% nu e reținut corect la fiecare distribuire individuală**, ci calculat global pe suma totală și dedus aproximativ.

## Ce face iConta.eu

Funcția `nota_distribuire(bacsis_brut, sursa)` din modulul F010 (`core/bacsis.py`) calculează, pentru fiecare distribuire introdusă, impozitul de 10% (`COTA_IMPOZIT`) reținut din brut, cu rotunjire aritmetică la 2 zecimale, și generează nota `462=446` (impozitul) + `462=5121/5311` (netul plătit). Exemplu verificat: un bacșiș brut de 100 lei generează impozit 10,00 lei și net 90,00 lei. Aplicația nu impune însă existența unui regulament intern sau a unei evidențe nominale pe salariat înainte de a introduce distribuirea — acestea rămân responsabilitatea operatorului, stabilite separat de flux.

[iConta.eu](/)
