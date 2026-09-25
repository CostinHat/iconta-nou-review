---
title: "Cum se înregistrează consumul personalului într-un restaurant?"
description: "Tratamentul de TVA al mâncării și băuturii consumate de angajați într-un restaurant, potrivit Codului fiscal, ca livrare de bunuri asimilată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează consumul personalului într-un restaurant?

Când un restaurant acordă gratuit personalului propriu masa din stocul destinat vânzării, operațiunea nu este „invizibilă" din punct de vedere fiscal — chiar dacă nu există o factură către un client, TVA-ul dedus la achiziția ingredientelor trebuie „întors", pentru că bunurile respective nu mai ajung să fie vândute, ci sunt folosite în afara circuitului economic normal al firmei.

## Temeiul legal

::: ghid-temei
„Sunt asimilate livrărilor de bunuri efectuate cu plată următoarele operațiuni: a) preluarea de către o persoană impozabilă a bunurilor mobile achiziționate sau produse de către aceasta pentru a fi utilizate în scopuri care nu au legătură cu activitatea economică desfășurată, dacă taxa aferentă bunurilor respective sau părților lor componente a fost dedusă total sau parțial;"
— Codul fiscal (Legea 227/2015), art. 270 alin. (4) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Legea nu tratează diferit „masa personalului" de orice altă preluare de bunuri din stoc pentru un scop fără legătură cu activitatea economică: dacă TVA-ul aferent ingredientelor consumate a fost dedus la achiziție, preluarea acestora pentru consumul angajaților este asimilată unei livrări de bunuri cu plată, deci generează obligația de a colecta TVA.
- Baza de calcul a TVA colectată pentru o astfel de operațiune este, de regulă, costul de achiziție/producție al bunurilor preluate (nu prețul de vânzare din meniu către clienți), pentru că nu are loc o vânzare propriu-zisă.
- Aceeași logică se aplică oricărei preluări de bunuri din stoc pentru scopuri fără legătură cu activitatea — spre deosebire de litera b) a aceluiași alineat, care vizează bunurile puse gratuit la dispoziția altor persoane (nu a personalului propriu în cadrul relației de muncă).

## Ce se greșește în practică

- Se consideră masa oferită angajaților ca fiind „în afara" oricărei evidențe fiscale, doar pentru că nu există o factură emisă — de fapt, dacă TVA-ul de la achiziție a fost dedus, operațiunea rămâne asimilată unei livrări impozabile.
- Se confundă tratamentul TVA al consumului de personal cu cel al mesei calde oferite ca beneficiu de natură salarială (tichete de masă, indemnizație de hrană etc.), care are un regim distinct la impozitul pe venit/contribuții sociale — art. 270 alin. (4) privește exclusiv obligația de TVA a preluării bunurilor din stoc.
- Se omite ajustarea de TVA atunci când bunurile preluate pentru consum propriu provin dintr-un lot la care taxa a fost dedusă doar parțial (de exemplu la achiziții mixte), caz în care asimilarea se aplică proporțional cu taxa dedusă.

## Ce face iConta.eu

La verificarea codului, iConta.eu are un modul de rețetar pentru HoReCa (`retete.py`), care calculează consumul de ingrediente la cost mediu ponderat (CMP) pe baza vânzărilor efective (numărul de porții vândute) și food cost-ul aferent. Aplicația nu are însă, în prezent, o funcție dedicată consumului de personal (mese oferite gratuit angajaților) ca operațiune distinctă de vânzarea către clienți — tratamentul de TVA descris mai sus, asimilarea la livrare de bunuri conform art. 270 alin. (4) lit. a), rămâne o înregistrare manuală a contabilului.

[iConta.eu](/)
