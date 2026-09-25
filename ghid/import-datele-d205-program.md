---
title: "Cum import datele pentru D205 din program"
description: "Declarația D205 nu se completează prin import manual de fișiere, ci se generează direct din registrele contabile ale firmei, conform structurii XML impuse de ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum import datele pentru D205 din program

Pentru D205, întrebarea „cum import datele" are, într-un program de contabilitate bine construit, un răspuns simplu: nu le imporți — programul le generează direct din ce ai deja înregistrat, dacă evidența contabilă și registrul de asociați sunt complete.

## Temeiul legal

::: ghid-temei
„<declaratie205 luna=\"12\" an=\"AAAA\" d_rec=\"0\" cui=\"...\" [...]>
<sect_II tip_venit=\"08\" nrben=\"N\" [...] Tbaza=\"...\" Timp=\"...\">
<benef tip_venit1=\"08\" den1=\"...\" Rezid=\"1\" cifR=\"...\" tip_plata=\"2\" divid_D=\"...\" divid_P=\"...\" baza1=\"...\" imp1=\"...\"/>
</sect_II>
</declaratie205>"
— OPANAF nr. 102/2025, structura declarației 205 (sursă: anaf_surse/d205_struct_anaf.txt) — notație reconstituită pe baza denumirilor exacte de câmpuri din documentul de structură (documentul sursă e un tabel de câmpuri, nu un exemplu XML redat ca atare)
:::

Structura XML impusă de ANAF nu specifică o sursă anume a datelor — cere doar rezultatul final, corect calculat: totaluri pe secțiune (`Tbaza`, `Timp`, `nrben`) și detaliu pe fiecare beneficiar (`baza1`, `imp1`, `divid_D`, `divid_P`). De unde vin aceste cifre — dintr-un import de fișier extern sau direct din contabilitatea deja ținută în program — este o decizie de implementare a fiecărui software, nu o cerință a normei.

- Cifrele de bază și impozit trebuie să corespundă exact mișcărilor contabile reale ale contului de dividende de plată — orice discrepanță între ce a fost efectiv distribuit/plătit și ce apare în declarație este o eroare de fond, indiferent de metoda de completare.
- Rezidența fiecărui beneficiar (`Rezid`) trebuie derivată corect din codul de identificare fiscală (`cifR`) — o eroare aici duce la o declarație respinsă de validatorul oficial ANAF.

## Ce se greșește în practică

- Se caută o funcție de „import fișier D205" pentru date venite din altă sursă (Excel, alt program), deși într-un program integrat datele ar trebui să vină direct din contabilitatea deja ținută acolo, fără pasul intermediar de export-import.
- Se recalculează manual, în afara programului, baza și impozitul pe fiecare beneficiar și se introduc apoi ca valori fixe — crește riscul ca declarația să nu mai corespundă cu mișcările reale ale contului de dividende, mai ales dacă acestea se modifică ulterior.
- Se ignoră faptul că declararea corectă depinde și de datele de asociați (CNP, rezidență) ținute separat în program — o declarație D205 „generată" fără actualizarea prealabilă a acestor date reproduce erorile din registrul de asociați.

## Ce face iConta.eu

iConta.eu **nu are un flux de „import" separat pentru D205** — declarația se generează direct din registrele proprii ale aplicației (`core/d205.py`, `core/repo_d205.py`): mișcările contului 457 pentru fiecare asociat, datele de identificare din modulul de asociați și profilul firmei. Contabilul nu introduce a doua oară sumele de dividende plătite, ele fiind preluate automat din contabilitatea deja înregistrată în aplicație; condiția este ca aceste înregistrări (plăți de dividende, date de asociați) să fie corecte și complete la momentul generării declarației.

[iConta.eu](/)
