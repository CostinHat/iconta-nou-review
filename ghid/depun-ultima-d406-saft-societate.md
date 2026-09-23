---
title: Când depun ultima D406 SAF-T pentru o societate radiată?
description: Verificarea în sursele legale disponibile nu a identificat un text explicit despre ultima declarație D406 la radiere — explicăm ce este confirmat și ce rămâne neclar.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când depun ultima D406 SAF-T pentru o societate radiată?

Această întrebare nu are, la acest moment, un răspuns confirmat printr-un text legal identificat explicit. Spunem asta direct, la început, pentru că e important să știți ce este verificat și ce nu.

## Temeiul legal

::: ghid-temei
„Am căutat explicit (grep pe `anaf_surse/` și pe tot codul) termenii radiat/radiere/încetare/dizolvare/lichidare în corelație cu D406/SAF-T — nicio potrivire." — Dosar de cercetare F035, secțiunea Discrepanțe, pct. 4.
:::

Ce știm sigur, din sursele legale verificate local (OPANAF 1783/2021 și OPANAF 407/2025):

- Legea reglementează explicit o singură situație de întrerupere a obligației: **activitatea suspendată temporar**, prin trimitere la Codul de procedură fiscală, art. 101 alin. (41) și (42) (OPANAF 407/2025, pct. 4, lit. o)-p)). Radierea/încetarea activității **nu** apare ca situație distinctă, tratată explicit, în textele citite pentru acest dosar.
- Regulile de periodicitate (OPANAF 1783/2021, Anexa 4, pct. 1-3) stabilesc termenul obișnuit de depunere — ultima zi calendaristică a lunii următoare perioadei de raportare — dar nu spun nimic special despre firmele radiate.
- Motorul de lichidare/radiere din iConta.eu (bazat pe OMFP 897/2015 și Legea 31/1990, art. 227 și următoarele) **nu conține nicio referință la D406/SAF-T** — verificat direct în cod.

Cu alte cuvinte: nu am găsit, în sursele ANAF disponibile local, un text care să spună fie că obligația de depunere D406 încetează automat la data radierii, fie că ultima declarație trebuie depusă cu un termen special legat de radiere. Orice afirmație în acest sens ar fi o interpretare, nu un citat legal — și interpretările nu au ce căuta într-un ghid fiscal.

## Ce se greșește în practică

Cea mai frecventă greșeală este să se presupună, din analogie cu alte declarații (D100, D101, D300 etc.), că "ultima D406 se depune odată cu bilanțul de lichidare" sau că "obligația încetează automat la radiere" — fără să existe un temei citabil pentru D406 în mod specific. O altă greșeală este ignorarea completă a subiectului, pe motiv că firma oricum nu mai există — dar obligațiile de raportare pentru perioadele în care firma a fost activă și înregistrată rămân, indiferent de radierea ulterioară.

## Ce face iConta.eu

iConta.eu generează D406 pentru orice perioadă în care firma a fost activă și obligată, indiferent de stadiul ulterior al societății (inclusiv radiată) — generatorul (`core/d406.py`) nu are o regulă specială legată de radiere, pentru că, așa cum am arătat mai sus, o astfel de regulă nu a fost identificată nici în legislația verificată.

Pentru situația concretă a unei societăți în curs de radiere sau deja radiate, recomandăm verificarea directă cu un consultant fiscal sau cu organul fiscal competent, înainte de a stabili dacă mai este necesară o declarație D406 și pentru ce perioadă — acest ghid nu poate oferi un răspuns definitiv pe un subiect fără temei legal confirmat local.

[iConta.eu](/)
