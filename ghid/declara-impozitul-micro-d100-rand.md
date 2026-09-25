---
title: Cum se declară impozitul micro în D100, rând cu rând?
description: Impozitul micro se declară în D100, secțiunea B, tabelul I „Impozite și taxe care se plătesc în contul unic”, la poziția 5 din nomenclator, completând rândul 1 „Suma datorată” și rândul 2 „Suma de plată”, conform instrucțiunilor din anexa nr. 4 la OPANAF 587/2016.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară impozitul micro în D100, rând cu rând?

Impozitul pe veniturile microîntreprinderilor se declară în formularul 100 „Declarație privind obligațiile de plată la bugetul de stat”. Completezi perioada de raportare (ultima lună a trimestrului), iar în secțiunea B, tabelul I, treci impozitul la rândul 1 „Suma datorată” și aceeași sumă la rândul 2 „Suma de plată”. Instrucțiunile sunt în anexa nr. 4 la OPANAF 587/2016, iar modelul formularului a fost înlocuit prin OPANAF 57/2026.

### Temeiul obligației

Codul fiscal art. 56 alin. (1) cere calculul și plata trimestrială a impozitului, „până la data de 25 inclusiv a lunii următoare trimestrului pentru care se calculează impozitul”. Art. 56 alin. (2) adaugă obligația de a depune declarația până la același termen. Cota este de 1%, potrivit Codului fiscal art. 51 alin. (1), în forma modificată de OUG 89/2025.

### Pasul 1: perioada de raportare

Instrucțiunile din OPANAF 587/2016, anexa nr. 4, cap. II pct. 1, cer ca la rubrica „Luna” să treci numărul ultimei luni a perioadei, „3 pentru trimestrul I”. Pentru trimestrul II treci 6, pentru trimestrul III treci 9, iar pentru trimestrul IV treci 12. Anul se scrie cu patru cifre.

### Pasul 2: secțiunea A

Treci codul de identificare fiscală, aliniat la dreapta. Dacă firma e înregistrată în scopuri de TVA, prima căsuță primește prefixul RO. Adresa trecută e cea a domiciliului fiscal.

### Pasul 3: secțiunea B, tabelul I

Potrivit pct. 3.1 din aceleași instrucțiuni, impozitul micro (poziția 5 din nomenclator) se declară în tabelul I „Impozite și taxe care se plătesc în contul unic”:

- **Rândul 1 „Suma datorată”**: impozitul datorat pentru trimestru.
- **Rândul 1.1 „Reducere impozit conform OUG nr. 153/2020”**: îl completează numai plătitorii de impozit micro. Reducerea se aplică însă doar în perioada 2021–2025 (OUG 153/2020, art. VI). Pentru trimestrele din 2026 rândul rămâne gol.
- **Rândul 2 „Suma de plată”**: suma de la rândul 1, sau diferența dintre rândul 1 și rândul 1.1.

Structura XML publicată de ANAF cere în plus, pentru acest impozit, câmpul de cotă cu valoarea 1. Altfel validatorul respinge declarația cu eroare de cotă micro invalidă. Câmpurile pentru sponsorizări și pentru costul aparatelor de marcat nu se mai folosesc: Codul fiscal art. 56 alin. (2^5) stabilește că ultimul an în care aceste sume se mai scădeau din impozitul micro a fost 2023.

### Exemplu

Veniturile impozabile din trimestrul IV 2026 sunt de 184.300 lei. Impozitul este 1% × 184.300 = 1.843 lei. În D100 treci luna 12 și anul 2026. La rândul 1 treci 1.843, rândul 1.1 rămâne gol, iar la rândul 2 treci tot 1.843. Termenul este 25 ianuarie 2027, conform art. 56 alin. (1). Derogarea din OUG 153/2020 care muta trimestrul IV la 25 iunie s-a aplicat doar pentru perioada 2021–2025.

### Trimestru fără impozit

Dacă din trimestru nu rezultă sumă datorată pentru un impozit din vectorul fiscal, instrucțiunile cer să treci „cifra 0 (zero)” la „Suma datorată/de plată”. Atenție, dacă pentru o obligație declarativă nu completezi deloc tabelul, instrucțiunile spun că asta „echivalează cu nedeclararea obligației respective”.

### După depunere

D100 se completează cu programul de asistență și se transmite electronic (anexa nr. 4, cap. I pct. 3). Potrivit formularului aprobat prin OPANAF 57/2026, declarația depusă este titlu de creanță și produce efectele juridice ale înștiințării de plată de la data depunerii. Erorile nu se corectează printr-o nouă D100, ci prin formularul 710.

### De reținut

- Perioada de raportare se trece ca ultima lună a trimestrului: 3, 6, 9 sau 12.
- Impozitul se trece la rândul 1 și, de regulă, aceeași sumă la rândul 2.
- Rândul 1.1 (reducerea din OUG 153/2020) nu se mai folosește pentru perioadele din 2026.
- Tabelul lăsat necompletat pentru o obligație din vector înseamnă nedeclarare. În lipsa unei sume, treci 0.
- Greșelile se corectează cu formularul 710.
