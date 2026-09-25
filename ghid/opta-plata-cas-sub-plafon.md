---
title: "Pot opta pentru plata CAS dacă sunt sub plafon?"
description: "Da — sub pragul de 12 salarii minime brute, CAS nu e obligatorie, dar contribuabilul poate opta pentru plata ei, la un venit ales de minimum 12 salarii minime brute, prin D212."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot opta pentru plata CAS dacă sunt sub plafon?

Da, legea prevede explicit această opțiune — util mai ales pentru cine vrea să-și continue stagiul de cotizare la pensie, chiar dacă veniturile din activități independente nu ating pragul obligatoriu.

## Temeiul legal

::: ghid-temei
„Persoanele fizice prevăzute la alin. (1) care nu se încadrează în plafonul de cel puțin 12 salarii prevăzut la alin. (3) pot opta pentru plata contribuției de asigurări sociale pentru anul de realizare a venitului la un venit ales, care nu poate fi mai mic decât nivelul prevăzut la alin. (2) lit. a). Exercitarea opțiunii se efectuează anual prin depunerea Declarației unice privind impozitul pe venit și contribuțiile sociale datorate de personale fizice prevăzute la art. 122, până la termenul prevăzut la art. 122 alin. (3)."
— Codul fiscal (Legea 227/2015), art. 148 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce presupune concret opțiunea:

- Condiția de bază: venitul cumulat din activități independente și drepturi de proprietate intelectuală trebuie să fie SUB pragul de 12 salarii minime brute (art. 148 alin. (1) și (3)) — dacă îl atinge sau depășește, CAS devine oricum obligatorie, nu mai e o opțiune.
- Venitul ales pentru bază nu poate fi mai mic decât 12 salarii minime brute — chiar dacă venitul real e mult sub această valoare, contribuția opțională se calculează pe minimum acest nivel.
- Opțiunea se exercită anual, exclusiv prin D212, până la termenul legal (25 mai a anului următor celui de realizare a venitului) — nu există un formular sau un canal separat pentru exercitarea ei.
- Contribuția plătită astfel se valorifică la stabilirea stagiului de cotizare și a punctajului pentru pensie (art. 151 alin. (16)), la fel ca CAS obligatorie.

## Ce se greșește în practică

- Se crede că opțiunea poate fi exercitată oricând în timpul anului, separat de D212 — de fapt se exercită exclusiv prin declarație, la termenul ei legal.
- Se optează pentru un venit ales mai mic de 12 salarii minime brute, crezând că baza poate fi proporțională cu venitul real — legea fixează un minim absolut pentru opțiune, identic cu pragul obligatoriu.
- Se confundă opțiunea de plată CAS (art. 148 alin. (4)) cu opțiunea de plată CASS (art. 180) — sunt contribuții și praguri diferite, cu reguli proprii fiecare.

## Ce face iConta.eu

Motorul `core/d212_engine.py` (funcția `calculeaza_cas`) acceptă parametrul `optiune_cas`: dacă venitul net e sub pragul de 12 salarii minime brute, dar contribuabilul optează explicit, funcția calculează CAS pe baza minimă de 12 salarii minime brute, exact cum cere legea. Opțiunea e disponibilă și în fișa de calcul automată (`fisa_d212`, `core/rip_api.py`) pentru contribuabilii la sistem real, pentru veniturile anilor 2025 și 2026.

Aplicația nu decide ea însăși dacă opțiunea e avantajoasă și nici nu completează automat exercitarea opțiunii în declarația D212 — parametrul se activează manual, la cererea contribuabilului.

[iConta.eu](/)
