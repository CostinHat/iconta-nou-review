---
title: "Cum se calculează amortizarea pentru bunurile concesionate"
description: "Cine amortizează mijloacele fixe primite în concesiune și cum se recuperează fiscal investițiile făcute asupra lor, potrivit normelor Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează amortizarea pentru bunurile concesionate

Regula de bază pentru bunurile date în concesiune e simplă, dar deseori aplicată greșit: dreptul de a amortiza rămâne la proprietar, nu trece la concesionar — cel care doar folosește bunul. Ce se schimbă, în schimb, e tratamentul investițiilor pe care concesionarul le face asupra bunului concesionat.

## Temeiul legal

::: ghid-temei
„Amortizarea mijloacelor fixe concesionate, închiriate sau date în locație de gestiune se calculează de către agentul economic care le are în proprietate.
Amortizarea investițiilor efectuate la mijloacele fixe concesionate, închiriate sau luate în locație de gestiune se recuperează de agentul economic care a efectuat investiția, pe perioada contractului."
— Legea nr. 15/1994 privind amortizarea capitalului imobilizat în active corporale și necorporale, art. 11 alin. (2)-(3) (sursă: anaf_surse/legea_15_1994_amortizarea_capitalului_imobilizat_active_corporale.txt)
:::

- **Bunul concesionat în sine** se amortizează de către cel care îl are în proprietate (concedent), nu de concesionar, chiar dacă acesta din urmă îl folosește efectiv în activitate.
- **Investițiile efectuate de concesionar** asupra bunului (modernizări, extinderi, reparații capitalizabile) se recuperează fiscal de cel care le-a făcut, pe durata contractului de concesiune — practic o amortizare separată, distinctă de cea a bunului de bază.
- Aceeași lege confirmă simetric acest regim și pentru imobilizările necorporale: „Imobilizarile necorporale de natura concesiunii, superficiei și a uzufructului se amortizează pe durata contractului" (Legea nr. 15/1994, art. 13 alin. (2)).
- Dacă durata contractului de concesiune depășește durata normală de utilizare a investiției, recuperarea investiției se face, în practică, pe durata normală de utilizare, nu peste aceasta.

## Ce se greșește în practică

- Concesionarul amortizează greșit bunul de bază primit în concesiune, ca și cum ar fi propriul mijloc fix, în loc să amortizeze doar investițiile pe care le-a făcut asupra lui.
- Se confundă durata contractului de concesiune cu durata normală de utilizare a investiției la stabilirea perioadei de amortizare a acesteia din urmă.
- La încetarea contractului înainte de termen, nu se regularizează valoarea rămasă neamortizată a investiției, deși aceasta ar trebui tratată distinct (cedare, recuperare de la concedent sau cheltuială).
- Se omite distincția dintre concesiunea unui bun corporal (mijloc fix) și concesiunea unui drept necorporal (ex. dreptul de a exploata un serviciu public), care are propriul regim de amortizare pe durata contractului.

## Ce face iConta.eu

iConta.eu are un modul dedicat mijloacelor fixe și amortizării (`d406_active.py`), cu funcții care calculează amortizarea lunară/anuală după metodă (liniară, degresivă, accelerată) și încadrează activul pe categorii pentru raportarea în SAF-T secțiunea „Active". Modulul nu are însă, la acest moment, o distincție explicită de tip „bun concesionat vs. investiție proprie asupra unui bun concesionat" — o firmă care are un astfel de caz trebuie să introducă investiția ca mijloc fix separat, cu durata de amortizare corespunzătoare, aplicând manual regula de mai sus.

[iConta.eu](/)
