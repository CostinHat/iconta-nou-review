---
title: "Cum calculez impozitul pe profit pentru o firmă reactivată în cursul anului?"
description: "Firma ieșită din inactivitate temporară aplică sistemul de impozit pe profit trimestrial, calculat pe profitul contabil efectiv, nu pe formula de 1/4 din impozitul anului precedent."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum calculez impozitul pe profit pentru o firmă reactivată în cursul anului?

O firmă care iese dintr-o perioadă de inactivitate temporară înscrisă în registrul comerțului nu poate calcula plățile anticipate ca „1/4 din impozitul anului precedent" — pentru că, de regulă, anul precedent nu are un impozit relevant de la care să pornească un asemenea calcul. Codul fiscal o încadrează explicit în regimul de plată pe profitul trimestrial efectiv.

## Temeiul legal

::: ghid-temei
„(6) Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), aplică sistemul de declarare și plată prevăzut la alin. (1) în anul pentru care se datorează impozit pe profit, dacă în anul precedent se încadrează în una dintre următoarele situații: (...)
c) s-au aflat în inactivitate temporară sau au declarat pe propria răspundere că nu desfășoară activități la sediul social/sediile secundare, situații înscrise, potrivit prevederilor legale, în registrul comerțului sau în registrul ținut de instanțele judecătorești competente, după caz."
— Legea 227/2015, art. 41 alin. (6) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se calculează, concret, impozitul pentru o astfel de firmă:

- Firma care s-a aflat în **inactivitate temporară** în anul precedent aplică, în anul reactivării, sistemul de la **alin. (1)** — declarare și plată **trimestrială, pe profitul contabil efectiv** al perioadei, nu formula de plăți anticipate bazată pe anul precedent (alin. (8)).
- Impozitul se calculează separat pentru **fiecare trimestru**, pe baza rezultatului contabil real din acel trimestru, cu termen de declarare și plată **25 a lunii următoare trimestrului**.
- Aceeași regulă (profit trimestrial efectiv, nu formula 1/4) se aplică și firmelor **nou-înființate** în anul precedent, celor cu **pierdere fiscală** sau fără impozit datorat anul trecut, și celor care în anul precedent au fost **plătitoare de impozit micro** — toate cele patru situații de la alin. (6) sunt tratate identic, din perspectiva mecanismului de calcul.
- Dacă firma se dizolvă cu lichidare, regulile de plăți anticipate nu se aplică pentru perioada dintre prima zi a anului fiscal următor celui în care a fost deschisă procedura lichidării și închiderea procedurii — o excepție separată, relevantă doar dacă reactivarea e urmată ulterior de o dizolvare.

## Ce se greșește în practică

- Se calculează plata anticipată ca 1/4 din impozitul anului precedent, deși firma reactivată intră explicit sub regimul de la alin. (6) lit. c), care cere calculul pe profitul trimestrial **efectiv**, nu pe o proiecție din anul anterior.
- Se ignoră perioada exactă de inactivitate și se presupune că firma revine automat la regula generală (formula 1/4) din primul trimestru complet de activitate — regimul special se aplică pentru întregul an în care firma a fost, în anul precedent, în inactivitate temporară.
- Se confundă reactivarea din inactivitate temporară (înscrisă în registrul comerțului) cu o simplă reluare informală a activității, fără mențiune înscrisă — condiția legală cere ca situația să fie **înscrisă** potrivit prevederilor legale, nu doar declarată intern de firmă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu detectează automat** situația de inactivitate temporară a unei firme și nu comută singură între cele două regimuri de calcul al impozitului pe profit (formula 1/4 din anul precedent versus profitul trimestrial efectiv) — încadrarea corectă, pe baza mențiunilor din registrul comerțului, rămâne o verificare a contabilului. Aplicația generează declarația de impozit pe profit (D101) pe baza datelor contabile efective introduse pentru fiecare trimestru, fapt care susține calculul pe profit efectiv odată ce regimul corect e ales, dar decizia de încadrare în sine nu e automatizată.

[iConta.eu](/)
