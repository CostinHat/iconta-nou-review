---
title: "Ce este proiectul raportului de inspecție fiscală?"
description: "Dreptul contribuabilului de a fi informat înainte de finalizarea inspecției fiscale, conform Codului de procedură fiscală, și termenele pentru exprimarea punctului de vedere."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce este proiectul raportului de inspecție fiscală?

Înainte ca inspecția fiscală să se încheie oficial, legea obligă organul de control să prezinte contribuabilului o variantă preliminară a constatărilor — proiectul raportului de inspecție fiscală — și să-i dea posibilitatea reală de a răspunde înainte ca actul final să fie emis.

## Temeiul legal

::: ghid-temei
„(2) Organul de inspecție fiscal comunică contribuabilului/plătitorului proiectul de raport de inspecție fiscală, în format electronic sau pe suport hârtie, acordându-i acestuia posibilitatea de a-și exprima punctul de vedere. În acest scop, odată cu comunicarea proiectului de raport, organul de inspecție fiscală comunică și data, ora și locul la care va avea loc discuția finală, însă nu mai devreme de 3 zile lucrătoare de la data comunicării proiectului de raport de inspecție fiscală, respectiv 5 zile lucrătoare în cazul marilor contribuabili."
— Legea 207/2015 (Codul de procedură fiscală), art. 130 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă concret, pentru un contribuabil aflat sub inspecție:

- proiectul de raport nu e actul final — e o **versiune de lucru** a constatărilor, comunicată tocmai pentru ca firma să poată reacționa înainte de emiterea deciziei de impunere;
- odată cu proiectul, organul de inspecție trebuie să comunice și **data, ora și locul discuției finale**, cu un termen minim de așteptare: 3 zile lucrătoare pentru contribuabilii obișnuiți, 5 zile lucrătoare pentru marii contribuabili;
- contribuabilul are dreptul să-și prezinte **în scris** punctul de vedere față de constatări, în termen de cel mult 5 zile lucrătoare de la încheierea inspecției fiscale (7 zile lucrătoare pentru marii contribuabili — art. 130 alin. 5), termen ce poate fi prelungit motivat, cu acordul conducătorului organului de inspecție;
- dacă punctul de vedere e exprimat, **raportul final de inspecție fiscală** trebuie să cuprindă și opinia motivată a organului de inspecție cu privire la el (art. 131 alin. 2) — nu poate fi ignorat tacit;
- contribuabilul poate renunța expres la discuția finală, notificând acest fapt — caz în care data încheierii inspecției devine data notificării renunțării (art. 130 alin. 3-4).

## Ce se greșește în practică

- Se ignoră proiectul de raport, considerându-l „provizoriu și fără importanță" — de fapt e ultima fereastră reală de a influența constatările înainte ca ele să devină decizie de impunere executorie.
- Se depășește termenul de 5 zile lucrătoare pentru exprimarea punctului de vedere fără a cere prelungire motivată — după acest termen, poziția contribuabilului riscă să nu mai fie luată în calcul în raportul final.
- Se confundă discuția finală cu o simplă formalitate — participarea la ea (sau renunțarea expresă la ea) marchează chiar data juridică a încheierii inspecției fiscale, cu efecte asupra calculului termenelor ulterioare.

## Ce face iConta.eu

iConta.eu nu are niciun modul legat de gestionarea unei inspecții fiscale ANAF — aplicația nu generează, nu urmărește și nu răspunde la proiecte de raport de inspecție fiscală. Modulul `core/control_fiscal_api.py` din aplicație vizează exclusiv conformarea declarativă proprie a firmei (ce declarații sunt datorate și dacă au fost depuse), nu procedura de inspecție fiscală derulată de organele ANAF.

[iConta.eu](/)
