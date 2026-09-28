---
title: D107 la anul fiscal modificat sau la lichidare: ce perioadă de raportare completez?
description: Când raportarea nu acoperă anul calendaristic, în D107 se completează rubrica „Perioada": anul fiscal modificat, pentru contribuabilii de la art. 16 alin. (5), (5^1) și (5^2) Cod fiscal, sau perioada de la prima zi a anului fiscal următor deschiderii lichidării până la închiderea ei, conform art. 16 alin. (6) (OPANAF 355/2024, anexa 2 pct. 7-8).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# D107 la anul fiscal modificat sau la lichidare: ce perioadă de raportare completez?

D107 se completează, ca regulă, pe anul calendaristic. În două situații perioada de raportare este alta și se completează rubrica „Perioada": când firma are an fiscal modificat și când firma e în lichidare, pentru perioada care se încheie cu închiderea lichidării. Perioada din D107 trebuie să fie aceeași cu perioada declarației anuale de impozit pe profit.

### Ce spun instrucțiunile

OPANAF 355/2024, anexa 2:

- **pct. 7**: la rubrica „Anul" se înscrie anul calendaristic pentru care se completează declarația;
- **pct. 8**: rubrica „Perioada" se completează când raportarea se face pentru alte perioade decât anul calendaristic, de exemplu:
  - anul fiscal modificat, pentru contribuabilii de la Codul fiscal art. 16 alin. (5), (5^1) și (5^2);
  - perioada dintre prima zi a anului fiscal următor celui în care s-a deschis procedura lichidării și data închiderii procedurii, pentru contribuabilii de la art. 16 alin. (6).

### Anul fiscal modificat

Codul fiscal art. 16 alin. (5): contribuabilii care au optat pentru un exercițiu financiar diferit de anul calendaristic pot opta ca anul fiscal să corespundă exercițiului financiar. Primul an fiscal modificat include și perioada de la 1 ianuarie până în ziua anterioară primei zile a anului fiscal modificat. Alin. (5^1) reglementează schimbarea sau revenirea la anul calendaristic.

Structura XML a D107 publicată de ANAF urmează aceleași cazuri. Are câmpuri pentru data de început a anului modificat și bife pentru „primul an fiscal modificat" și „ultimul an fiscal modificat". La primul an, perioada începe la 1 ianuarie. La ultimul, se încheie la 31 decembrie.

Termenul D107 este cel al declarației anuale de impozit pe profit (anexa 2 pct. 4). Pentru anul fiscal modificat, acesta este data de 25 a celei de-a șasea luni de la închiderea anului fiscal modificat (Codul fiscal art. 42 alin. (2)).

**Exemplu.** O firmă are an fiscal modificat 1 octombrie 2026 – 30 septembrie 2027. D107 cuprinde sponsorizările din această perioadă, iar la „Perioada" se trec datele de început și de sfârșit ale anului fiscal modificat. Termenul este 25 martie 2028, a șasea lună de la închiderea anului fiscal modificat, în forma art. 42 alin. (2) dată de OUG 8/2026, aplicabilă de la anul fiscal modificat care începe în 2026.

### Lichidarea

Codul fiscal art. 16 alin. (6): pentru contribuabilii care se dizolvă cu lichidare, perioada dintre prima zi a anului fiscal următor celui în care s-a deschis lichidarea și data închiderii lichidării se consideră un singur an fiscal.

Codul fiscal art. 41 alin. (16): persoanele juridice care se dizolvă cu lichidare depun declarația anuală de impozit pe profit pentru această perioadă și plătesc impozitul până la data depunerii situațiilor financiare la organul fiscal competent. D107 urmează același termen.

**Exemplu.** Lichidarea unei societăți se deschide la 10 aprilie 2025 și se închide la 20 august 2026.

- Pentru 2025 se depune D107 obișnuită, pe anul calendaristic 2025.
- Pentru perioada 1 ianuarie – 20 august 2026 se depune D107 cu „Perioada" completată, până la data depunerii situațiilor financiare de lichidare.

Structura XML a D107 are un câmp pentru data dizolvării cu lichidare, care devine data de sfârșit a perioadei.

### Greșeli frecvente

- La an fiscal modificat se raportează pe anul calendaristic, iar sponsorizările se împart greșit între două declarații.
- La lichidare, anul deschiderii lichidării se tratează ca fiind deja perioada de lichidare, deși art. 16 alin. (6) începe perioada unică cu anul fiscal următor.
- Perioada din D107 diferă de cea din declarația anuală de impozit pe profit.

### De reținut
- Rubrica „Perioada" se completează doar când raportarea nu e pe anul calendaristic (OPANAF 355/2024, anexa 2 pct. 8).
- Anul fiscal modificat urmează Codul fiscal art. 16 alin. (5)-(5^2).
- În lichidare, perioada unică începe la 1 ianuarie a anului următor deschiderii lichidării (art. 16 alin. (6)).
- Termenul D107 este termenul declarației anuale de impozit pe profit pentru aceeași perioadă.
