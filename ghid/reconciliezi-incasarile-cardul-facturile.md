---
title: Cum reconciliezi încasările cu cardul cu facturile
description: O încasare cu cardul se reconciliază automat dacă ajunge în extrasul bancar ca linie individuală, cu CUI-ul clientului identificabil. O decontare agregată de la un procesator sau POS nu se potrivește automat — rămâne alocare manuală.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum reconciliezi încasările cu cardul cu facturile

Depinde cum ajunge încasarea în extrasul bancar. Dacă banca înregistrează plata cu cardul ca linie separată, cu suma egală cu factura și cu datele clientului identificabile în descriere, reconcilierea bancară din iConta.eu o tratează exact ca pe o încasare obișnuită prin transfer. Dacă în schimb banca înregistrează o **decontare agregată** — o singură linie care adună mai multe plăți cu cardul ale unor clienți diferiți, cum fac de regulă procesatorii de plăți (POS, Stripe și similare) — automatul nu are cum să o potrivească pe facturi individuale.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

::: ghid-temei
„Factura este document justificativ care stă la baza înregistrării în contabilitate a operațiunilor economice. Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: [...] extras de cont bancar, notă de contabilitate etc."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 25
:::

Legea nu distinge tehnic de plată (transfer, card, numerar depus) — cere doar ca operațiunea să fie susținută de un document justificativ, iar extrasul bancar confirmat de bancă este un astfel de document, indiferent cum a ajuns suma în cont.

## De ce încasările cu cardul nu se potrivesc mereu automat

Motorul de reconciliere caută, pe fiecare linie de extras, un CUI de partener identificabil în descrierea liniei. Dacă îl găsește, caută apoi o potrivire de sumă (exactă, pe combinație de facturi sau FIFO parțial) pe facturile deschise ale acelui partener — exact ca la orice altă plată.

Problema apare când suma din extras nu mai corespunde individual unui singur client:

- **Decontare cumulată** — un procesator de plăți sau un terminal POS depune, de regulă zilnic, o singură sumă care acoperă încasările de la mai mulți clienți. Linia din extras nu poartă CUI-ul niciunui client anume, deci motorul o clasifică automat drept nepotrivită („fără CUI în descriere"), oricâte facturi individuale ar acoperi în realitate suma.
- **Decontare netă de comision** — dacă procesatorul virează suma minus comisionul reținut, suma din extras nu mai coincide exact cu totalul facturii/facturilor acoperite, așa că nici măcar o potrivire pe CUI individual nu iese exact — linia rămâne pe alocare parțială sau nepotrivită.

Pentru aceste cazuri, în iConta.eu nu există azi un modul dedicat care să despartă automat o decontare agregată în facturile individuale acoperite și să separe comisionul reținut de procesator. Alocarea se face manual, factură cu factură, din picker-ul „Alege facturile", pe baza raportului de tranzacții pus la dispoziție de procesator/bancă.

## Ce se greșește în practică

- Se așteaptă ca o decontare agregată de la un procesator de card să se potrivească automat, la fel ca o plată directă cu CUI vizibil — și se pierde timp căutând de ce linia a căzut pe roșu.
- Se contabilizează suma netă din extras direct pe o singură factură, fără să se separe comisionul reținut de procesator ca cheltuială distinctă.
- Se ignoră raportul de tranzacții al procesatorului/POS-ului ca sursă de verificare, deși e singurul document care arată ce facturi individuale acoperă suma decontată.

## Ce face iConta.eu

Pentru o încasare cu cardul care ajunge în extras ca linie individuală cu CUI vizibil, motorul de matching (`core/reconciliere.py`) o tratează identic cu orice altă încasare bancară — potrivire exactă, pe combinație sau FIFO. Pentru decontările agregate de la procesatori de plăți sau terminale POS, iConta.eu nu are azi un parser sau un mecanism automat de despărțire pe facturi individuale și de netare a comisionului — funcționalitatea corespunzătoare din registrul intern de funcționalități este amânată, nu construită. Alocarea rămâne manuală, din picker-ul „Alege facturile", pe baza raportului de tranzacții al procesatorului.

[iConta.eu](/)
