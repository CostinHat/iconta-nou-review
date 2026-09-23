---
title: Cum se aplică TVA la vânzarea apartamentelor în 2026?
description: De la 01.08.2025 nu mai există o cotă redusă generală pentru locuințe — vânzarea unui apartament obișnuit intră, ca regulă, la cota standard de 21%. Regimul tranzitoriu de 9% avea condiții stricte, iar fereastra lui de livrare s-a închis la 31.07.2026.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se aplică TVA la vânzarea apartamentelor în 2026?

Spre deosebire de perioada anterioară lui august 2025, când locuințele beneficiau de o cotă redusă generală, de la 1 august 2025 această cotă a fost abrogată. Vânzarea unui apartament obișnuit, în 2026, intră ca regulă generală la cota standard de 21%, nu la o cotă redusă.

## Temeiul legal

::: ghid-temei
Alineatul (3) al art. 291 din Codul fiscal — cel care prevedea cota redusă generală pentru locuințe — a fost **abrogat** de la 1 august 2025, prin art. II pct. 43 din Legea nr. 141/2025 (MO nr. 699/25.07.2025).
:::

## Regula pentru 2026

Fosta cotă redusă (5%, valabilă până la 31.07.2025) pentru locuințele cu suprafață și valoare sub anumite praguri a fost eliminată integral odată cu abrogarea alin. (3). Lista actuală a cotei reduse (art. 291 alin. (2)) păstrează la 11% doar o categorie mult mai restrânsă — „locuința ca parte a politicii sociale", definită explicit ca: clădiri destinate a fi utilizate drept cămine de bătrâni/pensionari, respectiv case de copii și centre de recuperare pentru minori cu handicap. **Apartamentele obișnuite, vândute către persoane fizice pentru locuit, nu se încadrează în această categorie.**

## Excepția tranzitorie de 9% — și de ce nu se mai aplică unei vânzări noi

Legea 141/2025 (art. III) a păstrat, tranzitoriu, o cotă de 9% pentru persoane fizice, dar condiționat cumulativ de:

- o singură locuință achiziționată cu cotă redusă, cu suprafață utilă de maximum 120 mp (exclusiv anexe) și valoare (inclusiv teren) de cel mult 600.000 lei fără TVA;
- livrarea efectivă a locuinței **până la 31 iulie 2026 inclusiv**;
- un act juridic cu plată în avans, încheiat **până la 1 august 2025**;
- nicio altă achiziție cu cotă redusă din 2023 încoace, verificată în Registrul achizițiilor de locuințe cu cotă redusă.

Această fereastră s-a închis la 31 iulie 2026. Pentru o vânzare de apartament încheiată sau livrată după această dată, regimul tranzitoriu nu se mai poate aplica — concluzia corectă, pentru 2026, e cota standard de 21%.

## Ce se greșește în practică

- Se aplică din obișnuință fosta cotă de 5% pentru apartamente, ignorând abrogarea alineatului (3) de la 01.08.2025.
- Se invocă regimul tranzitoriu de 9% pentru o vânzare nouă, deși fereastra de livrare (până la 31.07.2026) e deja depășită.
- Se confundă „locuință ca parte a politicii sociale" (cămine de bătrâni, case de copii, la 11%) cu un apartament obișnuit vândut unei persoane fizice — categoriile nu se suprapun.

## Ce face iConta.eu

`core/cote_tva.py` modelează explicit doar categoria restrânsă `locuinte_sociale` (cămine de bătrâni, case de copii) la cota de 11%. Nu există o categorie automată pentru „apartament obișnuit" sau pentru regimul tranzitoriu de 9%, care presupune verificări specifice (suprafață, plafon valoric, Registrul achizițiilor de locuințe) ce nu țin de motorul de potrivire produs-cotă — la vânzarea unui apartament, aplicația nu aplică implicit nicio reducere, iar cota corectă (de regulă 21%) se declară explicit de către utilizator.

[iConta.eu](/)
