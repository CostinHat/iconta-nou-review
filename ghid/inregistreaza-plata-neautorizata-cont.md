---
title: "Cum se înregistrează o plată neautorizată din cont"
description: "De ce o plată neautorizată apărută în extras nu se înregistrează ca o cheltuială obișnuită, ci ca o creanță în litigiu, conform Legii contabilității 82/1991."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o plată neautorizată din cont

O sumă ieșită din contul firmei fără ordin de plată emis de firmă — fraudă cu cardul, eroare a băncii, tranzacție neautorizată — ridică o întrebare de contabilitate distinctă de cea bancară: cum se tratează documentul (sau lipsa lui) până la clarificarea situației cu banca.

## Temeiul legal

::: ghid-temei
„Articolul 6 (1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)-(2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Consecința, pentru o plată neautorizată:

- **Nu se înregistrează ca o cheltuială curentă**, pentru simplul motiv că lipsește exact ce cere art. 6: un document justificativ real al unei operațiuni economico-financiare efectuate de firmă. O plată pe care firma nu a autorizat-o nu e o "operațiune economico-financiară efectuată" în sensul legii — e o ieșire de bani neconsimțită.
- Corect e înregistrarea provizorie într-un **cont de creanțe în litigiu/de clarificat** (461 "Debitori diverși" sau un analitic dedicat), până la soluționarea disputei cu banca — nu direct pe un cont de cheltuială, care ar da o imagine falsă a activității firmei.
- Contestarea propriu-zisă a tranzacției la bancă (recuperarea sumei, termenele de contestare, procedura de chargeback) e reglementată de contractul cu banca și de normele bancare aplicabile, nu de legislația fiscal-contabilă — pe acest palier, ghidul de față nu poate cita un temei din corpusul de legislație fiscală verificat, pentru că subiectul aparține dreptului bancar, nu contabilității sau fiscalității.

## Ce se greșește în practică

- Se lasă suma "neexplicată" în extrasul de cont, fără nicio notă contabilă, până la soluționarea disputei — orice ieșire din cont trebuie reflectată contabil, chiar dacă provizoriu, pe un cont de clarificat.
- Se înregistrează direct ca o cheltuială (ex. "diverse", "comision") pentru a "închide" luna — greșit: fără document justificativ al unei operațiuni reale a firmei, suma nu poate fi cheltuială deductibilă.
- Se șterge înregistrarea provizorie fără notă explicativă, odată recuperată suma de la bancă — istoricul complet (ieșire, clarificare, recuperare) trebuie să rămână trasabil în contabilitate.

## Ce face iConta.eu

La data acestui ghid, `core/banca.py` contabilizează liniile din extrasul bancar prin `contabilizeaza_extras()`, pe baza unor cuvinte-cheie din descriere (comision, dobândă, credit, salarii etc.) — nu are o categorie dedicată „plată neautorizată/de clarificat", care să direcționeze automat o astfel de sumă spre un cont de creanțe în litigiu. O plată neidentificată prin niciun cuvânt-cheie cade, implicit, în categoria generică „furnizor" (plată) — reclasificarea ei corectă, pe un cont de clarificat, rămâne azi o intervenție manuală a contabilului.

[iConta.eu](/)
