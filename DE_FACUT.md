# iConta — DE FĂCUT

**Doar viitorul: ce e deschis. Când termini, ștergi rândul. Trecutul e în ISTORIC.md + git log.**
Ultima actualizare: 11.07.2026 (noapte)

---

## 1. Testare pentru pilot (din planul P1-P5, orientat business)

### Prin SSH — deja acoperit tehnic (NU relua): zonele 8,9,11,12,13,14,15

### Cere Daniela [D] — validare fiscală, sesiuni 2h
- P1.2 Flux lunar complet pe KAI: e-Factura + extras → reconciliere → jurnal → balanță → D300 → validare ANAF
- P1.3 Salarizare: salariat nou → stat plată → **fluturaș → D112 validat** (acum și cu Concediu Medical nou!)
- P2.6 TVA la încasare: factură + încasare parțială → 4428→4427 proporțional
- P2.7 Operațiuni speciale (5 eșantion): leasing, avansuri, sponsorizare, dividende, provizioane
- P2.8 Partidă simplă: import bancă → Fișă D212 (vs calcul manual)

### Cere Costin singur [C]
- P1.1 Creează cont nou end-to-end: înregistrare → firmă → factură → contare → validare → balanță
- P1.4 Recurente: șablon → cron → factură emisă
- P1.5 WooCommerce: comandă demo → sincronizare → factură + contare
- P2.9 KPI+forecast portal vs balanță; P2.10 Consolidare = suma firmelor; P2.11 AI learning
- P5.24 Backup/restore: pg_dump → restore pe DB temp → login OK

### Cere telefon [T] — după HTTPS (nou.iconta.eu e sus)
- P4.18 PWA: adaugă pe ecran (Android+iOS), pornire standalone
- P4.19 Pozează bon: cameră, multi-imagine, flux până la notă
- P4.20/21 Responsive portal <400px, landing <900px/<560px

## 2. Blocate — DUK / desktop ANAF
- **D394** pe DUKIntegrator (validare desktop)

## 3. Sesiune desktop (Word, nu SSH)
- **Design System docx**: adaugă 7 reguli noi (dataRo, .camp-ajutor, .oblig, bordură buton #b9c2cf, fără wrapper alb, esc canonic, fără native dialogs). Detalii: caută "REGULI DESIGN SYSTEM noi" în ISTORIC.md.

## 4. Infra
- **Reboot kernel** — "System restart required". Fereastră liniștită (downtime clienți, Daniela pilot).

## 5. Iterații viitoare (nu urgente)
- Cod 10 CM (reducere timp muncă) — exclus din dropdown; `calcul_cm_cod10` neintegrat în flux.
- raporteaza.js — verifică vizual data "cu_ora" în feed (migrat azi).
- Verifică date CM de test invalide în alte tenant-uri (CCMAD corupt deja șters din tenant_002).
