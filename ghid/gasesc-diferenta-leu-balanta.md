---
title: "Cum găsesc diferența de un leu din balanță?"
description: "Metoda sistematică de identificare a unei diferențe mici dintr-o balanță de verificare care nu se închide, pornind de la obligația legală de întocmire lunară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum găsesc diferența de un leu din balanță?

O balanță care nu se închide cu o diferență de câțiva lei e una dintre cele mai frustrante situații din contabilitatea curentă — suma e prea mică pentru a fi „văzută" ușor cu ochiul liber, dar suficientă cât să oprească verificarea corectitudinii înregistrărilor cerută de lege.

## Temeiul legal

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare."
— Legea 82/1991 (legea contabilității), art. 22 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Rolul balanței de verificare, așa cum reiese din text, este tocmai verificarea corectitudinii înregistrărilor — adică ea trebuie să confirme, prin egalitatea totalurilor de rulaje și solduri debitoare/creditoare, că fiecare operațiune a fost înregistrată corect, o singură dată, cu dublă înregistrare. O diferență, oricât de mică, înseamnă că această egalitate nu e respectată undeva în lanțul de note contabile.

Pași sistematici de căutare, când diferența e mică (1 leu, câțiva lei):

1. **Verifică rotunjirile**: diferențele de 1-2 lei apar frecvent din rotunjiri necorelate — o notă contabilă rotunjită „la sursă" (de exemplu într-un modul de salarizare sau TVA) care nu corespunde exact cu rotunjirea aplicată la altă notă legată de aceeași operațiune.
2. **Compară rulajele cu soldurile inițiale**: o balanță „aproape" corectă, cu diferență mică, sugerează adesea o eroare de transcriere a soldului inițial al unui cont (o cifră transpusă greșit), nu o eroare de înregistrare curentă.
3. **Caută o notă contabilă cu o singură linie**: o eroare tehnică (import de date, corecție manuală) poate lăsa în jurnal o singură înregistrare debit sau credit, fără contrapartidă — aceasta produce exact o diferență reziduală mică, nu o discrepanță masivă.
4. **Filtrează după perioadă**: dacă balanța pe lună curentă e corectă dar cumulat de la începutul anului nu e, problema e într-o lună anterioară, nu în cea curentă — reduce căutarea la intervalul unde apare prima dată diferența.

## Ce se greșește în practică

- Se recalculează întreaga balanță de la zero, notă cu notă, în loc să se izoleze mai întâi luna sau perioada în care a apărut diferența, prin comparație cumulat vs. lunar.
- Se ignoră rotunjirile ca sursă posibilă, presupunând că o diferență „prea mică pentru a conta" trebuie să vină dintr-o eroare majoră de înregistrare.
- Se corectează diferența printr-o notă contabilă artificială „de ajustare" direct în cont de diferențe, fără să se identifice cauza reală — practică ce maschează eroarea în loc s-o rezolve și poate distorsiona alte solduri.

## Ce face iConta.eu

iConta.eu generează balanța de verificare direct din notele contabile înregistrate în aplicație, pe baza rulajelor și soldurilor conturilor, respectând obligația de întocmire lunară prevăzută de lege. Pentru că notele contabile din aplicație sunt generate cu dublă înregistrare automată (debit = credit pe fiecare notă), o diferență reziduală în balanță indică, de regulă, o corecție manuală sau un import extern de date introdus incomplet — contabilul poate urmări jurnalul de operațiuni din aplicație, filtrat cronologic, pentru a izola nota care a produs dezechilibrul.

[iConta.eu](/)
