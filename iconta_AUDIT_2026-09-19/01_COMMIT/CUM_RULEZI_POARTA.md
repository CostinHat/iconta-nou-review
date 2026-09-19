# CUM RULEZI POARTA COMPLETĂ, DE LA ZERO

*Scris ca să poți verifica singur, nu ca să ne crezi pe cuvânt. Durata e **măsurată**, nu estimată.*

---

## 1. CE TREBUIE INSTALAT

| | versiunea pe care rulează azi | de ce e necesar |
|---|---|---|
| **Python** | 3.12.3 | aplicația și suita |
| **PostgreSQL** | 16.15 | schema-per-firmă; suita cere o bază **proprie**, v. §3 |
| **Java (JRE)** | OpenJDK 17.0.20 | `DUKIntegrator` — validatorul oficial ANAF |
| **DUKIntegrator** | pachetul oficial ANAF, în `~/duk/dist/` | probele fiscale îl cheamă ca arbitru |
| dependențe Python | 60 de pachete, `pip freeze` în `DEPENDENTE.txt` | — |

**DUKIntegrator NU e în depozit** (e software ANAF, redistribuit separat). Fără el, probele care
cer validatorul **se sar** și spun de ce (`stare='gri'`) — nu trec tăcut. *Asta e o limită reală a
reproducerii: fără DUK, ai o poartă verde care n-a întrebat arbitrul.*

## 2. CLONAREA

```
git clone <oglinda publică, v. OGLINDA_PUBLICA.md>
cd iconta-nou-review
git checkout <COMMIT din COMMIT.txt>
python3.12 -m venv venv
./venv/bin/pip install -r DEPENDENTE.txt
```

## 3. BAZA DE DATE — și de ce suita REFUZĂ să pornească fără ea

Suita **nu pornește** dacă nu poate dovedi că baza nu e cea de producție. Mesajul ei, verbatim:

```
suita NU porneste: nu se poate dovedi ca mediul e de test.
  - baza e chiar cea de PRODUCTIE (iconta_v2)
  - utilizatorul e chiar cel de PRODUCTIE (iconta_user)
```

*Frontiera adevărată e la PostgreSQL — rolul de test n-are `CONNECT` pe baza de producție —, iar
mesajul e doar prima încuietoare.* Pentru un audit, creează o bază proprie și un rol propriu, apoi:

```
export ICONTA_MEDIU=test
export DATABASE_URL='postgresql://<rol_test>:<parola>@localhost/<baza_test>'
./venv/bin/python -c "import core.db as d; d.init_pool()"      # verifică legătura
```

Schema unei firme se creează din `tenant_template.sql` (e în depozit).

## 4. POARTA COMPLETĂ

Exact ce rulează hook-ul de `pre-commit`, în ordinea lui:

```
./venv/bin/python -m ruff check core/ scripts/ main.py        # secunde
./venv/bin/python -m pytest -q                                # v. durata măsurată
./venv/bin/python verificator_conformitate.py                 # secunde
```

### DURATA, MĂSURATĂ — nu estimată

| ce | durată |
|---|---|
| suita completă, 11 rulări consecutive pe 16–17.09.2026 | **2099–2145 s** (34:59 – 35:45) |
| mediană | ≈ **2109 s** (35:09) |
| `ruff` + verificator | secunde |

*Se scrie ca INTERVAL, nu ca cifră unică: mașina e partajată, iar o singură cronometrare ar deveni
încă un fapt fals.* Istoric, pe 01–07.09 aceeași suită dura 1223–1593 s; a crescut odată cu numărul
de probe.

**Cifra pe care o aștepți la capăt**, pe commitul din pachet:

```
6247 passed, 7 skipped, 10 xfailed
verificator: TOTAL 0 candidate
```

`skipped` și `xfailed` **nu sunt zgomot** — sunt declarate: `04_NEVERIFICAT/` le numește pe fiecare,
cu motivul.

## 5. CE **NU** ACOPERĂ POARTA — citește înainte de a-i da greutate

1. **`frontend_test/` nu e cules de pytest.** Cele 35 de probe de lanț — singurele care apasă
   aplicația cap-coadă, prin HTTP, pe o instanță vie — **nu rulează la poartă**. Se rulează de mână.
2. **Nicio probă de browser.** Nu există Playwright în poartă. Uneltele vizuale (`axe_scan`,
   `mobil_scan`, `interactiune_scan`) cer browser și se rulează separat; poarta verifică doar că
   **artefactul** lor nu e stătut.
3. **Nicio depunere reală la ANAF.** Validatorul rulează local; recipisa nu se exercită (R40).
4. **Baza de test e o copie a producției**, nu date sintetice. Un defect care depinde de o anumită
   formă de date reale poate să nu apară.
5. **Poarta rulează arborele de lucru, nu indexul.** Un fișier nestagiat influențează rezultatul.
   *Măsurat pe 16.09: lucrul în curs la o lucrare a înroșit commitul alteia.*

## 6. CUM RECALCULEZI CIFRELE DIN PACHET

```
./venv/bin/python audit/deriva_cifrele.py          # clichetele, recalculate și comparate
./venv/bin/python audit/deriva_neverificatul.py    # ce NU e verificat
./venv/bin/python scripts/raport_b.py              # starea derivată din CONFORMITATE.md
```

Primul tipărește, pentru fiecare clichet, **valoarea scrisă în cod** și **valoarea recalculată
acum**, cu verdict. Dacă vreuna diverge, e un defect — al codului sau al pachetului — și merită
raportat.
