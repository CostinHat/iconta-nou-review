---
title: Cum se depune D205 electronic?
description: Declarația se generează ca fișier XML validat pe structura oficială, apoi se transmite electronic către ANAF, cu semnătură electronică calificată, prin mijloacele puse la dispoziție de fisc. Aplicația validează conținutul înainte de generare, printr-o reconciliere independentă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se depune D205 electronic?

D205 se depune electronic, ca orice altă declarație fiscală de acest tip, sub forma unui fișier XML conform structurii oficiale, semnat electronic și transmis prin mijloacele de comunicare la distanță puse la dispoziție de ANAF.

## Temeiul legal

::: ghid-temei
**Termenul de depunere**, din instrucțiunile oficiale D205 (OPANAF 179/2022): „5. Termenul de depunere a declarației [...] a) până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat."
:::

## Pașii, la nivel de principiu

**1. Generarea fișierului XML**, conform structurii oficiale D205 (temei OPANAF 179/2022, cu modificările OPANAF 102/2025 și OPANAF 303/2026) — cu datele fiecărui beneficiar: CNP, sumă distribuită, sumă plătită, bază de impozitare, impozit reținut.

**2. Validarea** fișierului față de regulile oficiale ale formularului, înainte de transmitere.

**3. Transmiterea** propriu-zisă, cu semnătură electronică calificată, prin mijloacele electronice de transmitere la distanță acceptate de ANAF.

## Ce se greșește în practică

Se generează declarația fără o verificare prealabilă a datelor sursă (CNP-uri valide, sume corect calculate pe contul 457) — o eroare de date descoperită abia după transmitere e mai costisitoare de corectat decât una prinsă înainte de depunere.

## Ce face iConta.eu

Aplicația generează automat fișierul XML din datele existente (asociați cu cotă de participare, note contabile validate pe contul 457), aplicând validările oficiale ale formularului: cifră de control pe CUI și CNP, respingerea beneficiarilor fără CNP românesc valid, blocarea unui CNP duplicat pe aceeași cheie. Suplimentar, aplicația rulează o reconciliere independentă — recalculează separat, cu o interogare proprie, baza și impozitul per beneficiar și compară rezultatul cu ce a produs generatorul, blocând generarea la orice divergență. Transmiterea efectivă către ANAF a fișierului validat se face prin mijloacele electronice puse la dispoziție de fisc.

[iConta.eu](/)
