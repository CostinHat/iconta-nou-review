---
title: "Cât este amenda pentru D112 depus cu întârziere"
description: "Sancțiunea contravențională pentru nedepunerea la termen a declarației D112, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cât este amenda pentru D112 depus cu întârziere

D112 — declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate — este o declarație fiscală, iar nedepunerea ei la termenul legal e o contravenție cu amendă stabilită expres de Codul de procedură fiscală, diferențiată în funcție de mărimea contribuabilului.

## Temeiul legal

::: ghid-temei
„ART. 336 Contravenții
(1) Constituie contravenții următoarele fapte, dacă nu au fost săvârșite în astfel de condiții încât să fie considerate, potrivit legii, infracțiuni: (...)
b) neîndeplinirea de către contribuabil/plătitor la termen a obligațiilor de declarare prevăzute de lege, a bunurilor și veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuțiilor și a altor sume, precum și orice informații în legătură cu impozitele, taxele, contribuțiile, bunurile și veniturile impozabile, dacă legea prevede declararea acestora; (...)
(2) Contravențiile prevăzute la alin. (1) se sancționează astfel: (...)
d) cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii și mari și cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice, în cazul săvârșirii faptei prevăzute la alin. (1) lit. a), b) și i) - m)."
— Legea 207/2015, art. 336 alin. (1) lit. b) și alin. (2) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Concret, pentru nedepunerea la termen a D112:

- Contribuabilii **mijlocii și mari**: amendă între **1.000 și 5.000 lei**.
- Celelalte persoane juridice, precum și persoanele fizice: amendă între **500 și 1.000 lei**.
- Sancțiunea se aplică pentru simpla nedepunere la termen, indiferent dacă declarația conținea sau nu sume de plată — obligația de declarare există independent de obligația de plată.
- Dacă din nedepunerea D112 rezultă și nestabilirea la timp a unor obligații fiscale principale (contribuții, impozit pe venit din salarii), organul fiscal poate stabili acele obligații prin decizie de impunere, caz în care se aplică doar penalitatea de nedeclarare, **fără** cumul cu sancțiunea contravențională (art. 181 alin. (9)).

## Ce se greșește în practică

- Se presupune că amenda pentru D112 e fixă, aceeași pentru toți contribuabilii — legea diferențiază explicit între contribuabilii mijlocii/mari și restul persoanelor juridice/fizice.
- Se confundă amenda pentru **nedepunere la termen** cu penalitățile și dobânzile de întârziere la plata contribuțiilor declarate — sunt sancțiuni diferite, cu temeiuri diferite, care se pot aplica simultan sau, în anumite situații, se exclud reciproc.
- Se consideră că o depunere „cu câteva ore întârziere" nu riscă amenda, pentru că fapta e minoră — legea nu prevede o toleranță; nedepunerea la termenul legal constituie contravenție indiferent de durata întârzierii.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează și nu aplică amenzi** — aplicarea sancțiunilor contravenționale e atributul organului fiscal, nu al aplicației. iConta.eu generează D112 pe baza datelor din statele de plată și urmărește scadențarul oficial ANAF (25 a lunii următoare) prin modulul de conformare fiscală (`core/control_fiscal_api.py`), care semnalează, cu semafor, când o declarație datorată nu a fost încă depusă — un mecanism de prevenire a întârzierii, nu de calcul al amenzii.

[iConta.eu](/)
