# LANSARE — Registru de pregătire pentru pilot și producție

*Ce trebuie avut în vedere înainte de pilot și de lansarea publică. Fără propuneri de soluții — doar enumerare. Statut: **DESCHIS** (neatins/lipsă) · **ÎN LUCRU** (parțial) · **REZOLVAT** (confirmat la sursă) · **DECIS** (decizie luată; implementarea poate fi separată) · **AMÂNAT**. Referințele (DECIZII:n, ISTORIC:n, main.py:n) = verificate la sursă 25.07.2026; „lipsă/nu există" = gol confirmat la sursă.*

## 1. Juridic

| De rezolvat | Statut | Notă |
|---|---|---|
| Termeni și condiții publici | DESCHIS | Nu există pagină/rută T&C în cod sau `static/` (grep gol; login.js n-are link). |
| Politică de confidențialitate (GDPR) | DESCHIS | Nu există document public. |
| Consimțământ la înregistrare | DESCHIS | `RegisterIn`/`RegisterGratuitIn` (main.py:733,1012) nu cer accept T&C/GDPR. |
| Contract de împuternicire / DPA cabinet↔iConta | DESCHIS | iConta = procesator pt datele clienților cabinetului (DECIZII:46). Contract lipsă. |
| Disclaimer „instrument, nu prestare" (zid CECCAR) | DESCHIS | Poziționare în MARKETING, nereflectată juridic (de pus în T&C). |
| **Export date cabinet (art. 20)** | REZOLVAT | **F199** (commit `821184d`): `GET /gdpr/export-cabinet` (admin_firma/superadmin) → ZIP cu public + toate schemele tenant + fișiere disc + MANIFEST. |
| **Ștergere completă cabinet (art. 17)** | REZOLVAT | **F200** (commit `e3d5892`): 2 pași + confirmare typed-back + jurnal `gdpr_stergeri` fără date personale. Backup Storage Box NU se șterge (dump integral, expiră 30z). |
| **Retenție audit_log (art. 5)** | REZOLVAT | **F201** (commit `894b182`): cron zilnic, șterge audit_log > 12 luni. |
| **Alertă acces anormal (art. 33 pregătire)** | REZOLVAT | **F202** (commit `b819f75`): cron 15 min pe audit_log, dedup persistent, alertă Brevo. |
| Retenție cont inactiv (1 an) | DECIS, NEIMPLEMENTAT | Decis 18.07 (DECIZII:447), NECONSTRUIT (fără cron; ALTA decât retenția audit_log F201). **De IMPLEMENTAT sau de SCOS din DECIZII înainte ca avocatul să scrie T&C — nu poate rămâne promisiune nerespectată.** |
| Drepturi GDPR — UI/procedură pentru export & ștergere | DESCHIS | F199/F200 există DOAR ca API superadmin, fără UI. Dacă T&C promite drepturile → trebuie buton SAU procedură declarată (cerere pe email + termen de răspuns). |
| Praguri alertă acces anormal — calibrare | DESCHIS | F202 cu valori GHICITE (8 tenanți / 300 acțiuni / 10 min). De calibrat pe trafic real în pilot. |
| Plan notificare breach (GDPR 72h) | DESCHIS | Detectare = F202 (art.33 pregătire, REZOLVAT); procedura completă de notificare 72h (ANSPDCP + persoane vizate) rămâne DESCHIS. |

## 2. Comercial

| De rezolvat | Statut | Notă |
|---|---|---|
| Ofertă Program Cabinet Fondator | DECIS | 5-7 cabinete, 12 luni gratuit, 3 firme/cabinet (MARKETING.md). |
| Model de preț post-fondator | DESCHIS | Nedefinit ce urmează după 12 luni / peste 3 firme. |
| Trecere beta → acces public | ÎN LUCRU | Azi: poartă beta activă (`BETA_COD_ACCES` setat în proces). Public = F168: email conturi beta + șterge codul din env [PLANIFICAT, DE_FACUT:348]. |
| Mesaj diferențiator | DECIS | „control fiscal automat"; a NU revendica „depune cu un click" (FALS/INTERZIS). |
| Testimoniale/referințe pilot | DESCHIS | Depind de pilot; nimic încă. |
| Google Search Console + sitemap | REZOLVAT | 27.07.2026: proprietate `sc-domain:iconta.eu` verificată prin TXT DNS; `https://iconta.eu/sitemap.xml` trimis (6 URL-uri: landing, /ghid, 3 pagini de ghid, /public/termeni). Indexarea durează zile. |

## 3. Operațional

| De rezolvat | Statut | Notă |
|---|---|---|
| Onboarding cabinet nou | ÎN LUCRU | Register self-service (F108) + email bun-venit (main.py:1062). Fără ghid de pași. |
| Canal de suport + SLA | DESCHIS | Triaj AI sesizări (F152) + escaladare există; canal/SLA formal nedefinit. |
| Testare pilot P1-P5 | ÎN LUCRU | Parțial: [C] rulate 14.07; rămân [D] Daniela (validare fiscală) + [T] telefon (DE_FACUT:8,48). |
| Migrare date la intrare | ÎN LUCRU | Import din programe de contabilitate + CSV există; din programe de facturare = gol. |
| Conectare SPV per cabinet | ÎN LUCRU | OAuth e-Factura/e-Transport LIVE (validat 18.07); necesită certificatul cabinetului cu drept SPV PJ. |

## 4. Tehnic

| De rezolvat | Statut | Notă |
|---|---|---|
| HTTPS/certificate | REZOLVAT | Let's Encrypt pe iconta.eu + www. Reînnoire automată (certbot.timer). Certificatul `nou.iconta.eu` șters 27.07 — subdomeniul nu mai e folosit. |
| Rate-limiting brute-force | REZOLVAT | nginx `limit_req` pe /auth/login (ambele domenii) + fail2ban. |
| Un singur deployment activ | REZOLVAT | iconta.eu comutat pe 8010 (25.07); vechiul (8000) oprit+dezactivat. |
| Izolare multi-tenant | REZOLVAT | schema-per-tenant + gardă acces (fixuri securitate C-2/H-1). |
| Validare declarații (DUK) | REZOLVAT | jar-uri oficiale ANAF (core/duk.py). |
| Rotire secrete | ÎN LUCRU | Parola DB rotită 25.07; Fernet/JWT/ANAF/Brevo neroatate. |
| Depunere la ANAF din app | AMÂNAT | F127 fără API (mTLS/certificat local); manual din SPV (DECIZII 25.07). |

## 5. Continuitate

| De rezolvat | Statut | Notă |
|---|---|---|
| Backup local | REZOLVAT | systemd timer 03:00, retenție 7z; restaurare locală confirmată (DECIZII:675). |
| Backup off-site | REZOLVAT | Hetzner Storage Box, rsync, 30z, fail-safe, alertă email la 2 eșecuri (DECIZII:711). |
| Test restaurare off-site cap-coadă | REZOLVAT | Restaurare DIN off-site testată cap-coadă 18.07 (DECIZII:738; ISTORIC:1372). |
| Istoric cod off-site | REZOLVAT | GitHub privat CostinHat/iconta-v2, push 25.07 (SPOF rezolvat). |
| Runbook recuperare (server pierdut) | DESCHIS | Piesele există; pașii end-to-end de reprovizionare+restore neconsemnați ca procedură. |
| Cron-uri critice | REZOLVAT | systemd timers active (spv-refresh 03:30, backup 03:00, spv-poll/receive). |

## 6. Reputațional

| De rezolvat | Statut | Notă |
|---|---|---|
| Onestitatea afirmațiilor publice | DECIS | Listă PERMISE/INTERZISE (MARKETING); fără overclaim. |
| e-Factura round-trip pe CIF real | DESCHIS | Cod complet, dar round-trip pe firmă reală cu drept SPV NEPROBAT (DECIZII:1315). |
| Date reale de clienți în materiale | DECIS | Niciodată publicate (GDPR/secret fiscal); exemple fictive în SEO (MARKETING). |
| Semafor fiscal — fals-pozitive | DECIS | Gardieni zgomotoși respinși; verdict doar pe ce s-a putut verifica (DECIZII). |
| Consecvență brand (iConta.eu) | REZOLVAT | Landing corectat 25.07 (10 ocurențe). |

---

*27.07.2026 — REGULA DE VERIFICARE: un rând marcat REZOLVAT în acest registru trebuie să aibă
o dovadă reproductibilă (test în suită sau comandă care se poate rula), nu doar o notă. Motivul:
„Un singur deployment activ | REZOLVAT (25.07)" era fals — pe 27.07 `/opt/iconta` era viu, cu
venv-ul din care rula aplicația. Nimeni nu mințise; nimic nu verifica afirmația. Datoria
verificabilă mecanic trăiește acum în `core/test_datorie.py`.*

---

## Rămas din DE_FACUT.md (închis 27.07.2026)

`LANSARE.md` a fost șters. Tot ce era **reparabil din cod** s-a reparat pe 27.07; ce a rămas
nu e cod. Datoria verificabilă mecanic trăiește în `core/test_datorie.py` (rulează la fiecare
commit, acum gol). Gardurile și limitele lor declarate sunt în `GARZI.md`.

### Blochează pilotul
| Ce | Stare |
|---|---|
| Briefing juridic pentru avocat | REDACTAT, NETRIMIS. **Nu e pe server** — doar pe Desktop, deci nici în git, nici în backup. |

### Decizii de produs, deschise
| Ce | Context |
|---|---|
| ~~Bypass owner pe patru-ochi~~ | **NU E O DECIZIE DESCHISĂ** (verificat 27.07). `coada_api.aproba` cere DOUĂ condiții cumulate: patronul să fi activat regula (`patru_ochi_activ`, implicit oprită) ȘI să fie posibilă (`patru_ochi_posibil`: minim 2 utilizatori activi, cu pregătitor și validator distincți). Într-un cabinet cu un singur om nu se declanșează niciodată. Nota era rămasă în urmă. |
| ~~`tip_firma` needitabil~~ | **NU E O DECIZIE DESCHISĂ, e restricție corectă** (verificat 27.07). PFA ține partidă simplă, SRL partidă dublă; schimbarea tipului pe o firmă cu date ar lăsa înregistrări într-un regim care nu le recunoaște (11 module depind de `tip_firma`, prin `straturi_pentru`/`regim_efectiv`). 27.07: adăugat avertisment la creare — „tipul nu se mai poate schimba după creare". **Rămâne real**: nu există ștergere de firmă, deci o firmă creată cu tipul greșit rămâne așa. De decis dacă se adaugă ștergere (firmă fără date). |
| Ecran de introducere D301 | Generatorul și tabelul există; nu există UI de completare. |
| e-Transport `/trimite` pentru rol client | Azi cabinet-only; de decis dacă clientul trimite singur. |
| D230 / D307 | Respinse ca scop pe 20.07. De reconfirmat. |

### Blocate extern (nu depind de noi)
| Ce | Blocaj |
|---|---|
| F127/F128 — depunere prin SPV | SPVWS2 e read-only, fără API de submisie. Re-verificat 19.07. Review 17.08. |
| Round-trip e-Factura / e-Transport | Cere patron cu certificat digital pe firmă reală. |
| Import Ciel | Fără specificație de format. |
| Art. 317 (cod special TVA) | ANAF nu-l expune în API-ul public. |
| XSD e-Transport v2 | Schema oficială nepublicată; validare offline imposibilă. |

### Datorie acceptată explicit (decis, nu uitat)
| Ce | Decizie |
|---|---|
| ~136 style-uri inline | Decis 23.07: se lasă. Verificatorul le tolerează deliberat. |
| Audit vizual ~20 ecrane | Verificatorul prinde semnătura textuală, nu randarea. Limită în `GARZI.md`. |
| 20 module fără test propriu | Măsurat 27.07. Acoperite indirect prin teste de integrare. |
| 19 ecrane fără mesaj de succes | Măsurat 27.07. Tipar real; reparația e globală, nu ecran cu ecran. |
| `og:image` = logo, nu 1200×630 | Preview social arată logo întins. Cosmetic. |
| `nou.iconta.eu` | ÎNCHIS 27.07: certificat șters din certbot, config nginx scos. Rămâne doar înregistrarea DNS (inofensivă — nu mai are ce servi). |
| T&C: 4 clauze completate provizoriu | Plafon = sume 12 luni; păstrare 90 zile; preaviz 30 zile; DPA la cerere. Avocatul confirmă sau schimbă. |
