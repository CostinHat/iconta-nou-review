# C-3. CABINETELE / ASISTENȚII / CLIENȚII — cine administrează firmele (VALIDAT Costin 05.08.2026, cu completări)

**Scop:** cine administrează cele 12 firme din C-2, cu roluri + drepturi DISTINCTE, fiecare rol = cont cu **email +
parolă CUNOSCUTE** (pentru verificarea vizuală de la etapa 2). Setul de conturi acoperă toate combinațiile de rol/drept
pe care aplicația le distinge.

## Modelul de acces (din cod — `core/auth_api.schema_tenant`, `core/asistenti_api`, `core/capacitate_api`)
- **`public.users`**: `rol ∈ {superadmin, admin_firma, angajat, client}`, flags `poate_pregati` / `poate_valida` /
  `poate_depune`, `accounting_firm_id`.
- **`public.accounting_firms`** (cabinetul): `id, nume, cui, patru_ochi_activ, activ`.
- **`public.tenants`** (firmele C-2): `accounting_firm_id` → cabinetul care le ține.
- **`public.user_tenants`** (many-to-many): atribuirea `angajat`↔firmă ȘI accesul de portal al `client`-ului.
- **Regula de acces (`schema_tenant`):** `superadmin` → doar firme FĂRĂ cabinet (conturi gratuite, GDPR); `admin_firma`
  → toate firmele cabinetului lui (prin rol); `angajat`/`client` → DOAR prin `user_tenants`. Aici se testează izolarea.
- **Patru ochi** (`accounting_firms.patru_ochi_activ`): cine PREGĂTEȘTE ≠ cine VALIDEAZĂ (RBAC pe `poate_valida`).

---

## A. CABINETELE (două — al 2-lea pentru izolare cross-cabinet)

### Cabinet 1 — PRISMA (portofoliul principal)
| câmp | valoare |
|---|---|
| nume | **Cabinet Contabil Prisma SRL** (fictiv) |
| CUI | **RO96756476** (fictiv, din lotul verificat ANAF v9 05.08 — `gasit=False`) |
| patru_ochi_activ | **true** (ca să se exercite rolul `poate_valida` = a doua pereche de ochi) |
| firme administrate | **toate cele 12 firme din C-2** (M1, M2, P1, P2, N1, S1, S2, S3, NR1, T1, T2, S4) → `tenants.accounting_firm_id = Prisma.id` |

Un singur cabinet ține toate cele 12 firme → rețeaua de coerență R3 (facturi A↔B, control încrucișat D394) trăiește într-un
singur portofoliu.

### Cabinet 2 — NEXUS (minimal, DOAR pentru izolare cross-cabinet) — completare Costin 05.08
| câmp | valoare |
|---|---|
| nume | **Cabinet Contabil Nexus SRL** (fictiv) |
| CUI | **RO96939899** (fictiv, verificat ANAF v9 05.08 — `gasit=False`) |
| patru_ochi_activ | false (minimal) |
| firme administrate | **1 firmă — „X1"** (tenant separat, NU în rețeaua R3): micro plătitor TVA, 1 salariat, CAEN 4711, CUI **RO97092660** (verificat ANAF v9 05.08). `tenants.accounting_firm_id = Nexus.id` |

Nexus există EXCLUSIV ca să se testeze că un patron dintr-un cabinet **NU** vede firmele altui cabinet (breșa cea mai
gravă). Nu participă la coerența R3. Superadmin-ul existent (cont id=1, costin.hateganu@gmail.com,
`accounting_firm_id=NULL`) rămâne observațional — NU se creează în C-3; intră în matricea de izolare (secțiunea E) și în
verificarea din C-4.

---

## B. CONTURILE — 6 profiluri de rol/drept distincte (email + parolă cunoscute)

Parole = schemă reproductibilă (R2), **credențiale de TEST pe platforma de test golită, niciodată reale/producție**.
Convenție: `<Cabinet>!<rol>2026`. **Emailuri pe TLD-uri rezervate `.test` (RFC 2606) — NU rutează, niciun email de test
nu ajunge într-o cutie reală** (fără gmail/yahoo). Nume = fictive, fără rezonanță cu persoane reale.

| # | rol funcțional | nume persoană (fictiv) | email | parolă | `rol` DB | poate_pregati | poate_valida | poate_depune | firme atribuite | ce testează DISTINCT |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Patron cabinet 1 (Prisma)** | Elena Dobrescu | patron@prisma-cont.test | Prisma!patron2026 | admin_firma | (n/a — prin rol) | (n/a) | (n/a) | **toate 12** (prin rol) | vede TOT portofoliul Prisma; nu depinde de `user_tenants` |
| 2 | **Asistent cu poate_valida** | Radu Anghel | validator@prisma-cont.test | Prisma!validator2026 | angajat | ✔ | **✔** | ✔ | **toate 12** (prin user_tenants) | a doua pereche de ochi — VALIDEAZĂ ce pregătesc alții (patru ochi); poate și pregăti/depune |
| 3 | **Asistent fără poate_valida** | Ioana Vintilă | preparator@prisma-cont.test | Prisma!preparator2026 | angajat | ✔ | **✘** | ✘ | **6 firme** (M1,M2,P1,P2,N1,S3) | pregătește DAR nu poate valida/depune → blocaj „rol insuficient" la validare/depunere |
| 4 | **Asistent cu firme atribuite PARȚIAL** | Mihai Șerban | partial@prisma-cont.test | Prisma!partial2026 | angajat | ✔ | ✔ | ✘ | **3 firme** (S4, M2, T1) | izolare per-firmă: accesul la o firmă NEatribuită (ex. P1) → 404 (schema_tenant pe user_tenants) |
| 5 | **Client de portal** | Andrei Grigorescu | client@profit-import.test | Prisma!client2026 | client | — | — | — | **1 firmă** (P1), prin user_tenants | vedere de portal DOAR pe firma lui; nu vede alte firme; fără acțiuni de contabilitate |
| 6 | **Patron cabinet 2 (Nexus)** | Carmen Dumitrache | patron@nexus-cont.test | Nexus!patron2026 | admin_firma | (n/a — prin rol) | (n/a) | (n/a) | **1 firmă (X1)** (prin rol, cabinet Nexus) | IZOLARE CROSS-CABINET: cere resurse ale Prisma → **403/404, niciodată 200** |

Note:
- **#2 vs #3** izolează efectul lui `poate_valida` (același rol `angajat`, drepturi diferite) → testează calea patru-ochi
  și blocajul de validare.
- **#4** e cheia pentru izolarea per-firmă în interiorul cabinetului: are `poate_valida` DAR doar pe 3 firme; pe restul
  de 9 trebuie să primească 404, nu „acces refuzat generic" — `schema_tenant` întoarce None (tratat 404).
- **#5 clientul** e legat de P1 (cont de portal la firma pe care o vede); `_tenant_client` citește `user_tenants LIMIT 1`.
  Testează bara de client + `tenant_are_cabinet=true`.
- **#6 patronul Nexus** e admin_firma pe ALT cabinet → prin `schema_tenant`, o cerere a lui pe o firmă a Prisma trebuie să
  întoarcă None → 403/404. Reciproca: orice cont Prisma (#1–#5) pe firma X1 a Nexus → 403/404. Vezi matricea E.

---

## C. MATRICEA DE ATRIBUIRE user↔firmă (`public.user_tenants`)

| firmă \ user | patron (admin_firma) | validator | preparator | partial | client |
|---|---|---|---|---|---|
| M1 | (rol) | ✔ | ✔ | — | — |
| M2 | (rol) | ✔ | ✔ | ✔ | — |
| P1 | (rol) | ✔ | ✔ | — | ✔ (portal) |
| P2 | (rol) | ✔ | ✔ | — | — |
| N1 | (rol) | ✔ | ✔ | — | — |
| S1 | (rol) | ✔ | — | — | — |
| S2 | (rol) | ✔ | — | — | — |
| S3 | (rol) | ✔ | ✔ | — | — |
| NR1 | (rol) | ✔ | — | — | — |
| T1 | (rol) | ✔ | — | ✔ | — |
| T2 | (rol) | ✔ | — | — | — |
| S4 | (rol) | ✔ | — | ✔ | — |

„(rol)" = admin_firma vede prin rol, NU are rând în user_tenants (atribuirea per-firmă e irelevantă pentru el —
`asistenti_api:248`). Validatorul are toate 12 (poate valida orice). Preparatorul 6, partial 3 (cu suprapunere parțială
M2/T1 ca să existe și firme văzute de amândoi, și firme văzute de unul singur).

---

## D. CĂILE DE INTRARE (R4) — ecran vs seed

| element | cale | mecanism |
|---|---|---|
| Cabinetul Prisma + patronul (admin_firma) | **ECRAN** (funnel înregistrare cabinet) | `auth_api.inregistreaza_cabinet` — se testează calea reală de onboarding |
| Cele 12 firme (tenants) | **ECRAN cel puțin 1, restul SEED** | provizionare din template (46 tabele); prima firmă prin ecranul de adăugare firmă, restul prin seed reproductibil |
| Asistenții (validator/preparator/partial) | **ECRAN** (cardul Asistenți) | `asistenti_api` — creare actor + setare `poate_pregati/valida/depune` prin UI |
| Atribuirea firmelor la asistenți | **ECRAN** | UI de atribuire → scrie `user_tenants` |
| Clientul de portal | **ECRAN** (invitație/creare client) | leagă `user_tenants` la P1, rol `client` |

Fiecare cale distinctă exersată prin ecran cel puțin o dată; volumul (dacă ar fi mulți clienți) ar intra prin seed.

---

## E. GARDURI + IZOLARE care se REACTIVEAZĂ la popularea firmelor

- **`test_toti_tenantii_au_cnp_ingrijit`** (core/test_migrare_cnp_ingrijit.py) — a fost SKIP pe DB gol; la crearea celor
  12 tenants REDEVINE ACTIV. E gard de SCHEMĂ: fiecare `tenant_[0-9]+` trebuie să aibă coloana
  `concedii_medicale.cnp_ingrijit`. **Verificare obligatorie:** template-ul de provizionare TREBUIE să includă migrarea
  `core.migrare_cnp_ingrijit` (altfel gardul pică la primul tenant). Se rulează `python3 -m core.migrare_cnp_ingrijit`
  după provizionare dacă template-ul n-o are. (S4 chiar folosește cnp_ingrijit — CM cod 09/91/92/17.)
- **Patru ochi:** cu `patru_ochi_activ=true`, o declarație pregătită de #3 (preparator, fără poate_valida) nu se poate
  depune fără validarea lui #2 (validator) → calea de validare devine testabilă.

### Matricea de IZOLARE (probele efective intră la C-5; actorii se fixează AICI)
Fiecare celulă „✋" = cererea TREBUIE respinsă (403/404 / schema_tenant→None), **niciodată 200**.

| cont \ resursă | firmele Prisma atribuite lui | firme Prisma NEatribuite | firma X1 (Nexus) | acțiune peste drept |
|---|---|---|---|---|
| #1 patron Prisma | 200 (toate 12, prin rol) | — (are toate) | **✋ 403/404** | 200 |
| #2 validator | 200 (12) | — | **✋ 403/404** | 200 (poate valida) |
| #3 preparator | 200 (6) | **✋ 404** (celelalte 6) | **✋ 403/404** | **✋** validare/depunere (fără poate_valida/depune) |
| #4 partial | 200 (3: S4,M2,T1) | **✋ 404** (celelalte 9) | **✋ 403/404** | 200 pe cele 3 (are poate_valida) |
| #5 client (P1) | 200 doar portal P1 | **✋ 404** | **✋ 403/404** | **✋** orice acțiune de contabilitate |
| #6 patron Nexus | **✋ 403/404** (TOATE firmele Prisma) | **✋ 403/404** | 200 (X1, prin rol) | 200 pe X1 |
| **superadmin (id=1)** | **✋** (schema_tenant: superadmin vede DOAR firme cu `accounting_firm_id IS NULL`; toate ale noastre au cabinet) | **✋** | **✋** | **✋** — observațional, NU vede date de tenant |

- **Cross-cabinet (completare Costin):** #6 patron Nexus pe orice firmă Prisma → 403/404. Reciproc: #1–#5 pe X1 → 403/404.
  Cea mai gravă breșă posibilă (un patron care vede firmele altui cabinet) — testată explicit.
- **Superadmin (notă Costin pt C-4):** contul id=1 e pur observațional. `schema_tenant` îl lasă DOAR pe firme fără cabinet
  (conturi gratuite, GDPR). Toate cele 13 firme (12 Prisma + X1 Nexus) au cabinet ⇒ superadmin **nu trebuie să vadă date
  de tenant** pe niciuna. E rolul cu cel mai mare risc de scurgere; se verifică în C-4/C-5, dar intră AICI în matrice.

---

## F. DECIZII (VALIDATE 05.08.2026) + LIMITE

**Decizii Costin — VALIDATE:**
1. **Al 2-lea cabinet minimal (Nexus, 1 firmă X1, CUI RO96939899)** — DA, adăugat, cu propriul patron (#6, email+parolă
   cunoscute). În matricea de izolare: patron Nexus cere resurse Prisma → 403/404, niciodată 200.
2. **Distribuția atribuirilor** (preparator 6, partial 3) — validat.
3. **Convenția de parole** `<Cabinet>!<rol>2026` — validat. (Emailuri pe `.test`, nu rutează.)
4. **Numele persoanelor** — fixate acum în C-3 (secțiunea B): fictive, fără rezonanță cu persoane reale; emailuri pe
   domenii `.test` (RFC 2606) care nu există/nu trimit → niciun email de test către cutii reale.

**CUI-uri folosite în C-3** (toate verificate ANAF v9 05.08, `gasit=False`): cabinet Prisma RO96756476, cabinet Nexus
RO96939899, firma X1 RO97092660. Rezervă rămasă din lotul verificat: 97341990, 97363599, … (din cele 45). Re-verificare
la seed (ca la C-2).

**Limite declarate:**
- CNP-urile persoanelor (patron/asistenți/salariați) = C-4, cu caveatul de non-verificabilitate (nu există registru
  public de CNP). Conturile din C-3 au email+parolă + nume; CNP-ul persoanei fizice (dacă e cerut pe `users`) se pune în C-4.
- Probele efective de izolare/blocare (403/404, rol insuficient, perioadă închisă) = C-5; C-3 fixează ACTORII + matricea
  de izolare (inclusiv superadmin id=1, de verificat în C-4/C-5 că NU vede date de tenant).

**C-3 VALIDAT (2 cabinete, 6 conturi + superadmin în matrice). Următorul: C-4 (datele corecte).**
