# iConta — Inventar functionalitati + Plan de testare
Actualizat: 05.07.2026

## A. INVENTAR FUNCTIONALITATI

### 1. Cont & acces
- Landing + inregistrare cabinet (CUI verificat ANAF, provisioning tenant automat)
- Login (cabinet/client/superadmin), magic-link client
- Suspendare cabinet (blocare instant per-request)
- Chei API publice per cabinet (Setari cont)

### 2. Portal client
- Acasa: semafor ANAF colapsabil
- Facturi (istoric, emitere, detalii, storno, model)
- Declaratii depuse, Documente (balanta PDF + declaratii)
- Solicitari (chat bidirectional + email), Povestea lunii, Recomanda
- Pozeaza bon (multi-imagine, camera pe mobil)
- Cifrele firmei: KPI YTD + Previziune bani 8 saptamani
- PWA: manifest + service worker (test pe HTTPS)

### 3. Facturare
- Emitere inteligenta (CUI ANAF, cote AI pe linii, numerotare auto)
- Proforme + avize (contoare separate, transformare in factura)
- Facturi recurente (sabloane, cron 07:00, UI lista/adaugare/toggle)
- Storno, contare automata (ciorna), TVA la incasare
- Regim marja art. 312 / turism art. 311
- WooCommerce: import comenzi -> facturi (config per firma, cron 07:30, idempotent)

### 4. Contabilitate
- Registru jurnal: ciorna/validata, editor linii, validare
- Reconciliere bancara: import extras (XLS/CSV), matching exact/combo/FIFO,
  ignora/readu, contare, AI sugestie invatata + semafor incredere
- AI learning: ai_corectii per tenant (validari + corectii contabil)
- Casa, Stocuri GV+CV, Retetar HoReCa, Raport Z, Amortizare MF
- Period locking (perioade blocate, 423 la scriere)
- Balanta de verificare (cabinet + portal), fallback denumiri OMFP
- Operatiuni speciale (28): curs valutar, leasing, credite, avansuri,
  necorporale, reevaluare, provizioane, productie, obiecte inventar,
  decontari asociati, sponsorizari, subventii, comodat/chirii, deconturi,
  bacsis, SGR, perisabilitati, zilieri, inventariere, lichidare, ONG etc.
- Partida simpla PFA/II/IF: rip_operatiuni, import banca/casa, Fisa D212,
  Registru-inventar

### 5. Salarizare
- Salariati CRUD, stat de plata, fluturasi PDF
- Concedii medicale (Ordinul 506/1030/2026)
- D112 cu CM (validat DUKIntegrator)

### 6. Declaratii & raportari
- D100, D101, D112, D205, D300, D301, D390, D394, D406 (dispatch core)
- Bilant anual S1005/S1003 (XML validat)
- e-Transport v1 (XML pentru upload manual)
- Verificatoare: echilibru, trezorerie, TVA, coerenta stocuri
- Control fiscal (semafor cross-portofoliu), Termene

### 7. Cabinet
- Firme (fisa cu ~18 module), De validat, Asistenti (competente, 4 ochi)
- Sinteza zilei, Activitate, Capacitate, Pachete lunare
- Consolidare portofoliu (KPI toate firmele + total)
- Setari cont (profil, parola, cabinet, competente, chei API)

### 8. API public (/api/v1, X-Api-Key)
- GET firme / facturi / kpi / balanta

### 9. Admin iConta (superadmin)
- Raportari, Activitate cabinete (+suspendare), Sanatate server
  (metrici 5 min, grafice SVG, alerte email Brevo)

### 10. Migrare (7 straturi, testate)
Firme, solduri initiale, solduri parteneri, salariati, asociati, MF, istoric declaratii

## B. PLAN DE TESTARE

Legenda: [C]=Costin singur, [D]=cu Daniela (validare fiscala), [T]=telefon

### P1 — Fluxuri critice de business (inainte de orice pilot)
1. [C] Creeaza cont nou end-to-end: inregistrare -> login -> firma noua ->
   prima factura -> contare -> validare -> balanta
2. [D] Flux lunar complet pe KAI: import e-Factura + extras banca ->
   reconciliere -> validari jurnal -> balanta -> D300 -> validare ANAF
3. [D] Salarizare: salariat nou -> stat plata -> fluturas -> D112 validat
4. [C] Recurente: sablon -> asteapta cron (sau ruleaza manual) -> factura emisa
5. [C] WooCommerce: comanda noua in demo shop -> sincronizare -> factura + contare

### P2 — Module noi (sesiunile 04-05.07)
6. [D] TVA la incasare: factura + incasare partiala -> 4428->4427 proportional
7. [D] Operatiuni speciale — esantion 5: leasing, avansuri, sponsorizare,
   dividende, provizioane (Daniela valideaza notele)
8. [D] Partida simpla: import banca -> validare -> Fisa D212 (verificat cu calcul manual)
9. [C] KPI + forecast: cifrele din portal vs balanta (manual)
10. [C] Consolidare: total = suma firmelor
11. [C] AI learning: valideaza 3 note aceeasi descriere -> import extras ->
    sugestie cu semafor "sigur"
12. [C] API public: cheie noua -> curl firme/kpi -> revocare -> 401

### P3 — Securitate & margini
13. [C] Suspendare cabinet in timp ce userul e logat -> blocat instant
14. [C] Period locking: nota in luna blocata -> 423
15. [C] Patru ochi: acelasi user creeaza+aproba -> respins
16. [C] Client nu vede rutele cabinet (403), cabinet A nu vede firmele cabinet B
17. [C] Cheie API revocata / gresita -> 401; cheie cabinet A pe firma cabinet B -> 404

### P4 — Mobil & UX [T] (dupa nou.iconta.eu + HTTPS)
18. PWA: Adauga pe ecran principal (Android+iOS), pornire standalone
19. Pozeaza bon: camera direct, multi-imagine, flux complet pana la nota
20. Portal responsive: toate cardurile pe <400px
21. Landing responsive <900px si <560px

### P5 — Operational
22. [C] Alerte sanatate: test-alerta + prag real (stress scurt)
23. [C] Cron-uri: recurente 07:00, WooCommerce 07:30, sinteza — log-uri a doua zi
24. [C] Backup/restore: pg_dump iconta_v2 -> restore pe DB temporar -> login OK

### Reguli
- Orice bug gasit: fix imediat daca <30 min, altfel in PENDING cu prioritate
- Testele [D] planificate in sesiuni de 2h cu Daniela, incepand cu P1.2
- P1 complet inainte de a invita orice cabinet real
