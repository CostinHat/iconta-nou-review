---
title: "Cum se predă numerarul la firma de transport valori 2026"
description: "De ce predarea fizică a numerarului către o firmă de transport de valori ține de legislația privind paza și protecția, nu de Codul fiscal, și ce urmărește totuși legea plafoanelor de numerar în acest context."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se predă numerarul la firma de transport valori 2026

Predarea fizică a numerarului către o firmă de transport de valori (servicii de tip „cash-in-transit") este o procedură de securitate, reglementată de legislația privind paza obiectivelor, bunurilor și valorilor, nu de Codul fiscal sau de legislația contabilă. Ce rămâne, totuși, în sfera fiscală este depunerea numerarului rezultat în conturile bancare ale firmei — operațiune pe care legea plafoanelor de numerar o exceptează explicit de la orice limită valorică.

## Temeiul legal

::: ghid-temei
„Plafoanele-limită prevăzute de prezentul capitol nu se aplică de către persoanele prevăzute la art. 1 alin. (1), pentru următoarele operațiuni: a) depunerea de numerar în conturile deschise la instituțiile de credit sau la instituțiile care prestează servicii de plată și care sunt autorizate de Banca Națională a României, inclusiv în automatele de încasări în numerar [...]."
— Legea nr. 70/2015, art. 5 lit. a) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce rezultă practic de aici pentru firmele care apelează la transport de valori:

- **Depunerea numerarului în cont bancar**, indiferent de sumă, **nu e supusă niciunui plafon** din Legea 70/2015 — deci nu există, din perspectivă fiscală, o limită la suma pe care o firmă o poate depune printr-o singură operațiune de transport de valori.
- **Procedura fizică de predare** a numerarului către operatorul de transport valori (verificarea sigiliilor, semnarea proceselor-verbale de predare-primire, custodia pe traseu) ține de contractul comercial cu firma de pază/transport și de legislația specifică pazei obiectivelor, complet în afara Codului fiscal.
- Ce rămâne, totuși, relevant fiscal, este că plafonul zilnic de 5.000 lei/10.000 lei (după caz) privește **încasările și plățile în numerar**, nu depunerea excedentului de casă la bancă — o firmă care predă către transport valori un sold mare de casă, acumulat legal din încasări sub plafon, nu încalcă legea prin depunerea integrală a sumei.

## Ce se greșește în practică

- Se crede că suma predată către o firmă de transport valori trebuie fragmentată sub un plafon legal, confundând regula privind încasările/plățile în numerar (care au plafoane) cu depunerea de numerar în cont, care e neplafonată.
- Se tratează contractul cu firma de transport valori ca pe o obligație fiscală, cu temei în Codul fiscal, deși el aparține exclusiv relației comerciale și legislației de pază, în afara materiei fiscale.
- Se omite păstrarea documentelor de predare-primire (proces-verbal, sigilii) ca document justificativ contabil pentru mișcarea de numerar din registrul de casă, deși acestea rămân utile pentru reconcilierea soldului de casă cu extrasul bancar ulterior.

## Ce face iConta.eu

La data acestui ghid, iConta.eu ține registrul de casă și verifică plafonul de sold de casă introdus în profilul firmei (`core/casa.py`, funcția `verifica_plafon`), dar **nu are o funcționalitate dedicată** predării numerarului către o firmă de transport de valori — operațiunea se înregistrează, ca orice altă ieșire din casă, sub forma unei note de depunere în bancă, pe baza documentelor de predare-primire păstrate în afara aplicației.

[iConta.eu](/)
