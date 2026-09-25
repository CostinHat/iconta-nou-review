---
title: "Modificarea obiectului de activitate și efectul asupra impozitării"
description: "Cum poate schimbarea obiectului de activitate al firmei să scoată societatea din regimul de impozitare pe veniturile microîntreprinderilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Modificarea obiectului de activitate și efectul asupra impozitării

Nu orice modificare a obiectului de activitate are impact fiscal — dar unele au, și pot avea efect imediat asupra regimului de impozitare al firmei. Legea exclude explicit anumite domenii de activitate de la impozitul pe veniturile microîntreprinderilor, indiferent de cifra de afaceri sau de celelalte condiții îndeplinite. Dacă firma își extinde sau își schimbă obiectul de activitate către unul dintre aceste domenii, trece automat la impozit pe profit.

## Temeiul legal

::: ghid-temei
„(3) Nu intră sub incidența prezentului titlu următoarele persoane juridice române: [...] f) persoana juridică română care desfășoară activități în domeniul bancar; [...] persoana juridică română care desfășoară activități în domeniul asigurărilor și reasigurărilor, al pieței de capital, precum și persoana juridică română care desfășoară activități de intermediere/distribuție în aceste domenii, cu excepția intermediarilor secundari de asigurări și/sau reasigurări, definiți potrivit legii, care au realizat venituri din activitatea de distribuție de asigurări/reasigurări în proporție de până la 15% inclusiv din veniturile totale; [...] persoana juridică română care desfășoară activități în domeniul jocurilor de noroc."
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (3) lit. f) și literele următoare, Titlul III „Impozitul pe veniturile microîntreprinderilor" (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă pentru o firmă care își modifică obiectul de activitate:

- Dacă noul obiect de activitate include activități bancare, de asigurări/reasigurări, de piață de capital sau de jocuri de noroc, societatea **iese automat din sfera impozitului pe veniturile microîntreprinderilor**, indiferent de veniturile realizate sau de celelalte condiții din art. 47 alin. (1).
- Excepția pentru intermediarii secundari de asigurări/reasigurări (venituri din distribuție ≤ 15% din total) arată că testul nu e mereu binar — uneori contează ponderea veniturilor din activitatea „sensibilă", nu simpla existență a codului CAEN respectiv.
- Verificarea acestor condiții se face, potrivit legii, pe baza unei proceduri aprobate prin ordin al președintelui ANAF — deci nu depinde doar de autoevaluarea contribuabilului.

## Ce se greșește în practică

- Se modifică obiectul de activitate (adaugă un cod CAEN secundar) fără a verifica dacă noul domeniu se regăsește printre excluderile de la art. 47 alin. (3), presupunând că doar activitatea principală contează.
- Se crede că trecerea la impozit pe profit are loc abia la începutul anului fiscal următor — de fapt, condițiile de excludere legate de domeniul de activitate se pot aplica din momentul în care activitatea respectivă este efectiv desfășurată.
- Se ignoră excepția intermediarilor secundari de asigurări cu venituri de distribuție sub 15%, tratând orice legătură cu domeniul asigurărilor ca excludere automată.

## Ce face iConta.eu

Pentru acest subiect nu am găsit în cod o funcție care să verifice automat obiectul/codul CAEN al firmei față de lista de excluderi din art. 47 alin. (3) a Codului fiscal (activități bancare, de asigurări, jocuri de noroc). Aplicația validează codul CAEN al firmei doar în raport cu nomenclatorul folosit la generarea unor declarații (de exemplu D112), nu în raport cu eligibilitatea pentru regimul de microîntreprindere — încadrarea corectă la schimbarea obiectului de activitate rămâne, la acest moment, o verificare manuală.

[iConta.eu](/)
