---
title: "Cum pregătesc datele pentru primul SAF-T"
description: Ce date merită verificate înainte de prima generare a fișierului SAF-T — identificarea partenerilor, planul de conturi, unitățile de măsură și liniile facturilor.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum pregătesc datele pentru primul SAF-T

Prima generare a unui fișier SAF-T scoate de obicei la iveală lipsuri pe care evidența curentă nu le semnala — parteneri fără cod de identificare complet, conturi fără corespondent în nomenclator, produse fără unitate de măsură. Le poți repara dinainte, dacă știi ce verifică fișierul.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

## Ce date verifică, de fapt, fiecare subsecțiune

Fiecare subsecțiune din MasterFiles cere date complete pe tipul ei de nomenclator:

- **Customers/Suppliers** — fiecare partener trebuie identificat corect: cod 00+CUI pentru o firmă românească, 01/02+cod fiscal pentru un operator străin din UE, respectiv din afara UE, 03+CNP pentru o persoană fizică. Un partener fără niciunul dintre aceste identificatoare complete e o sursă tipică de eroare la prima generare.
- **GeneralLedgerAccounts** — planul de conturi trebuie să corespundă nomenclatorului tehnic al conturilor acceptate pe normă (publicat de ANAF alături de schema XSD), nu doar planului intern de conturi al firmei.
- **UOMTable** — produsele trebuie să aibă o unitate de măsură validă asociată; lipsa ei blochează raportarea corectă a liniilor de factură din SourceDocuments.
- **SourceDocuments** — facturile deja emise sau primite trebuie să aibă liniile complete (produs, cantitate, preț, cotă) și totalurile reconciliate cu antetul, nu doar suma finală.

Nu toată pregătirea privește raportarea periodică. Dacă firma are active de amortizat, secțiunea Active (anuală) cere metoda reală de amortizare pe fiecare activ (liniară, degresivă, accelerată sau superaccelerată); dacă ANAF cere Stocuri, e o declarație separată, generată la cerere.

## Ce se greșește în practică

- Se lasă parteneri vechi din evidență cu date incomplete (fără CUI, fără CNP), presupunând că „merge oricum" — fișierul poate fi respins sau generat cu identificatori incorecți.
- Se presupune că planul de conturi intern, oricât de bine organizat, corespunde automat nomenclatorului tehnic ANAF — corespondența trebuie verificată explicit.
- Se pregătesc doar datele pentru raportarea periodică, ignorând că secțiunea Active are reguli proprii de amortizare, dacă firma are active de raportat.

## Ce face iConta.eu

La generarea fișierului, iConta.eu produce Header, MasterFiles și GeneralLedgerEntries complet din structura XSD, cu identitatea partenerilor determinată automat din datele lor (CUI, CNP sau lipsa lor) și liniile de factură reconciliate obligatoriu cu antetul. Modulul de reconciliere verifică independent GeneralLedgerEntries înainte de validare. Rămân, la stadiul curent, două limite de pregătit separat: secțiunea Payments nu e emisă (lipsă sursă de mapare a plăților), iar Movement of Goods și Asset Transactions nu sunt acoperite.

[iConta.eu](/)
