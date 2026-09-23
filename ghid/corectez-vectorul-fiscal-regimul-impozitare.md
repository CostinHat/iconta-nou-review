---
title: Cum corectez vectorul fiscal dacă regimul de impozitare este greșit?
description: Corectarea se face din ecranul Date firmă, cu validări stricte pe firmele în partidă simplă — și cu blocaj automat dacă există perioade fiscale deja închise.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez vectorul fiscal dacă regimul de impozitare este greșit?

Ghidul practic, pas cu pas, pentru corectarea regimului de impozitare din Vector fiscal, inclusiv validările pe care aplicația le aplică automat.

## Temeiul legal

::: ghid-temei
Nu există un temei legal unic pentru câmpul „regim fiscal" din vectorul F100 — valoarea corectă se stabilește pe baza condițiilor din art. 47 și art. 52 din Codul fiscal (eligibilitate/ieșire micro). Regula tehnică de salvare (blocajul peste perioade închise, validările de rol și de tip de firmă) e o **regulă de produs**, nu o cerință legală, menită să protejeze integritatea declarațiilor deja depuse.
:::

Corectarea se face din ecranul „Date firmă", secțiunea „Vector fiscal" — endpoint `POST /tenants/{id}/vector`, accesibil doar utilizatorilor cu rol `admin_firma`. Regimul fiscal e obligatoriu la firmele în partidă dublă (SRL, SA etc.) și trebuie să fie exact „micro" sau „profit" — orice altă valoare e respinsă. La firmele în partidă simplă (PFA, II, PFL), câmpul nu se completează deloc — nu au regim micro/profit, iar o încercare de a-l seta e refuzată explicit.

Dacă intervalul afectat de corecție conține perioade fiscale deja închise, salvarea e blocată direct, cu mesajul care indică prima lună blocată. Calea de urmat: redeschide perioada din „Perioade blocate" (cu motiv consemnat), corectează regimul, apoi închide perioada la loc.

Validarea din formular colectează toate erorile deodată, nu se oprește la prima greșeală — util când se corectează simultan mai multe câmpuri ale vectorului (de exemplu regim + periodicitate TVA).

## Ce se greșește în practică

- Se încearcă setarea unui regim fiscal (micro/profit) la o firmă în partidă simplă (PFA/II) — operațiunea e respinsă explicit de aplicație, pentru că PFA-urile nu au acest tip de regim.
- Se ignoră mesajul de eroare la salvare peste o perioadă închisă, presupunând o eroare tehnică generică, nu o protecție intenționată împotriva rescrierii declarațiilor deja depuse.
- Se corectează regimul fiscal fără rol de `admin_firma`, deși endpoint-ul cere explicit acest rol.

## Ce face iConta.eu

Endpoint-ul `POST /tenants/{id}/vector` (`main.py`) aplică validări stricte înainte de salvare: `platitor_tva`/`operatiuni_ic` obligatorii fără valoare implicită tacită, `regim_fiscal` restricționat la valorile valide pentru tipul de firmă, și blocajul peste perioade fiscale închise. Fiecare eroare are un cod distinct (`REGIM_INVALID`, `REGIM_LA_PARTIDA_SIMPLA`, `PESTE_PERIOADA_INCHISA` etc.), afișat contabilului împreună cu explicația.

[iConta.eu](/)
