---
title: "Cum tratez dividendele neridicate de asociați la lichidare?"
description: "În sursele verificate, „neridicat” înseamnă aprobat dar neîncasat (cont 457); un eventual regim distinct de prescripție a dividendelor neridicate nu e documentat și nu trebuie inventat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez dividendele neridicate de asociați la lichidare?

„Neridicat” poate însemna două lucruri diferite: un dividend aprobat, dar pe care asociatul nu l-a încasat încă, sau un dividend rămas nerevendicat mult timp, cu o eventuală problemă de prescripție. E important să nu le confundăm.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend." — Legea 31/1990, art. 67 alin. (1)
:::

Pentru sensul „aprobat, dar neîncasat”, tratamentul e cel obișnuit: dividendul e o datorie a firmei din momentul aprobării (1171=457, cu impozitul reținut 457=446), care nu dispare la lichidare și trebuie plătită, ca orice altă datorie, în cadrul etapei de stingere a datoriilor care precede partajul final.

Pentru sensul „nerevendicat de mult timp de asociat” — o eventuală prescripție a dreptului asociatului de a mai încasa sau o reclasificare a sumei ca venit al firmei — legea Legea 31/1990 tratează explicit doar prescripția dreptului societății la acțiunea de **restituire** a dividendelor plătite nelegal, în 3 ani de la distribuire (art. 67 alin. 5). Nu am găsit, în sursele legale verificate pentru această funcționalitate, un regim distinct pentru dividende neridicate de asociat pe termen lung; orice afirmație despre un asemenea regim trebuie verificată separat, direct în sursă, înainte de a fi folosită.

## Ce se greșește în practică

Greșeala cea mai des întâlnită e tratarea unui dividend „neridicat” ca și cum s-ar prescrie automat sau ar deveni venit al firmei după o anumită perioadă, prin analogie greșită cu art. 67 alin. (5) — care vorbește despre restituirea dividendelor plătite nelegal, nu despre neridicare.

## Ce face iConta.eu

Funcționalitatea de decontări cu asociații (F039) înregistrează dividendul aprobat, cu sau fără plată efectivă (parametrul „cu_plata”), pe contul 457. Nu are o categorie separată pentru „dividend neridicat de mult timp” — orice sold rămas pe 457 e tratat identic, indiferent de vechime. Funcționalitatea de lichidare (partajul capitalului și rezervelor) nu preia automat acest sold în calculul ei; el trebuie clarificat separat — plătit către asociat sau tratat conform unei decizii documentate — înainte de finalizarea lichidării.

[iConta.eu](/)
