# ICONTA_STATUS — build nou (iconta_v2, port 8010)

Ultima actualizare: 01.07.2026 (seara)
Server: costin@178.105.201.56 · prompt costin@iconta-prod
Cod versionat in git (init 01.07.2026, commit initial cbf24ce). Backup-urile .bak nu se mai folosesc — git e istoricul.

---

## STARE CURENTA

Build nou = ~/iconta_nou, baza iconta_v2, complet separat de productia veche (/opt/iconta, port 8000/8001, baza iconta).

### Cardul FACTURI — COMPLET (01.07.2026)
- Istoric facturi
- Emitere cu VALUTA: selector moneda, curs BNR (core/curs_bnr.py, cache public.curs_bnr_zilnic), cascada bnr->manual->409 CURS_INDISPONIBIL, TVA in lei art. 319
- Detalii factura: defalcare pe cote, bloc conversie in lei
- Model factura: logo (base64)/font/culoare + preview live (firma_profil.font_factura, culoare_factura)
- PDF (core/factura_pdf.py, reportlab): antet+logo, tabel, totaluri pe cote, bloc valuta
- Email (Brevo cu atasament PDF, prin observare.trimite_email_html care primeste attachments)
- Storno (buton doar pe emise ne-storno, confirmare)
- Adresa beneficiar din ANAF (valideaza_cui aduce si adresa; facturi.tert_adresa; pe PDF)

### DIACRITICE PDF — REZOLVAT DEFINITIV
- core/pdf_fonturi.py = sursa UNICA fonturi (DejaVu Sans/Serif/Mono, au diacritice romanesti complete)
- factura_pdf.py foloseste modulul comun; _ascii scos complet (cod curat)

### Facturi in cabinet
- Cabinetul = utilizator ca oricare: intra pe firma (Firme -> click firma -> meniu actiuni) si lucreaza
- Cardul Facturi reutilizabil cu tenantId = firma deschisa; izolare pe schema (GDPR)

### GDPR superadmin
- Superadmin vede DOAR conturi gratuite (accounting_firm_id IS NULL); firmele cabinetelor invizibile

### Navigare ("blestemul sagetilor") — rezolvat
- Sageata doar cand exista inapoi real; X sus-dreapta inchide tot; nav.setInapoi(fn) pt pasi interni

---

## REGULI PERMANENTE (nu incalca)

1. NU construi/deploy pana Costin nu spune "DA". Propune/confirma intai.
2. Valorile fiscale se verifica la sursa oficiala ANAF/lege INAINTE de cod (TVA 21% din 01.08.2025; CAS 25%/CASS 10%/impozit 10%/CAM 2.25% 2026; salariu minim 4050 sem1/4325 sem2).
3. Calea grea dar sigura (refacere din surse oficiale) > validare cod existent.
4. PDF-uri: MEREU `from core.pdf_fonturi import init_fonturi, FONTURI`. NICIODATA Helvetica/Times/Courier (nu au diacritice -> patrate). Text UTF-8 direct, fara transliterare.
5. DIACRITICE: textul AFISAT (UI, PDF acum cu DejaVu, email) are diacritice corecte; cod/comentarii/markeri FARA diacritice.
6. Cand descoperim ceva in neregula, ne OPRIM, remediem, apoi continuam (fara datorii tehnice).
7. ALEGERE MODEL: "gandim pe Opus, executam pe Sonnet". Opus = arhitectura/logica fiscala/debug greu; Sonnet 5 = executie mecanica dupa tipar. Claude anunta, Costin comuta din UI.

## WORKFLOW PATCH
- Claude creeaza .py in outputs -> present_files -> Costin descarca in iCONTA_2026 -> scp din PowerShell la /tmp/ -> ruleaza pe server cu /opt/iconta/venv/bin/python3 (NU sudo)
- DDL: sudo -u postgres psql -d iconta_v2
- JS/CSS -> hard reload. Python (rute) -> restart uvicorn:
  pkill -f "uvicorn main:app.*8010"; cd ~/iconta_nou && set -a && source ~/.iconta/db.env && source ~/.iconta/api_keys.env && set +a && nohup /opt/iconta/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8010 > ~/uvicorn.log 2>&1 &
- Verificare: sleep 2 && curl -s -o /dev/null -w "%{http_code}\n" localhost:8010/  (200=ok)

## CONTURI TEST (parola Test1234!)
- superadmin: costin.hateganu@gmail.com (uid=1)
- admin_firma: costin.hateganu+nistor@gmail.com (uid=2, cabinet NISTOR si Asociatii, accounting_firm_id=2)
- angajat: asistent@gmail.com (uid=3) · client: costin.hateganu+client@gmail.com (uid=5)
- Firme (accounting_firm_id=2): Test srl (id=1, tenant_001), KAI PERFORMANCE (id=2, tenant_002)
- Login: /auth/login. /tenants intoarce firma cu .id (NU .tenant_id)

---

## RAMASE DE FACUT

### Marunt (din sesiunea facturi)
- Verificat campurile PDF reg_com/iban/banca cu diacritice cand firma are date complete (erau goale la firmele de test)
- Facturi de test (KAI-148...155 tenant_002, nr 1-2 tenant_001) = date de test, se pot sterge

### Firul principal (build nou, ecrane ramase — intrerupt de facturi)
- Ecran CLIENT PORTAL (scoping inceput inainte de facturi)
- Master list ecrane Management echipa C-G: C.Capacitate+norma+responsabil · D.Activitate cabinet (centralizator+jurnal) · E.Notificari (clopotel+sumar login+email zilnic) · F.Self-view asistent · G.Educatie AI pe tipare (A gata, B card echipa partial)

### Povestea lunii + Povestea anului (design agreat 01.07.2026)

**Povestea LUNII** (backend gata in pachete_api.py: rezumat_luna, genereaza_poveste AI, get/salveaza_poveste, trimite Brevo). Flux: cabinet genereaza -> aproba -> trimite email. LIPSESTE: afisare in PORTAL client.
- DE FACUT (Pas 1, urmatorul): ruta GET /portal/poveste (guard cere_client) care intoarce ultima poveste APROBATA a firmei clientului (NU ciorne). Cardul "Povestea lunii" din portal.js (acum placeholder ecranInLucru) o afiseaza read-only.

**Povestea ANULUI** (Pas 2, dupa portal luna). Nu e 12x povestea lunii - e naratiune diferita: tendinte (cifra afaceri creste/scade), TVA colectat vs dedus pe an, evolutie salarii, declaratii la termen, profit/pierdere+impozit, COMPARATIE cu anul anterior (aurul, daca exista istoric 2 ani).
- Declansare: NOTIFICARE pe CLOPOTEL (nu buton mereu-prezent), aparuta cand DECEMBRIE e efectiv depus (nu data fixa 1 ian) -> datele-s complete. UNA per firma. Doar firme cu istoric pe tot anul (prag 12/12 luni sau >=10, de decis la build). Se degradeaza elegant: fara istoric an-anterior -> poveste doar despre anul curent, fara comparatie.
- Flux: notificare -> cabinet genereaza (AI, prompt ANUAL nou cu agregari+comparatii, diferit de _prompt_poveste lunar) -> aproba -> email + portal. Dupa generare, notificarea se marcheaza rezolvata.
- Cost AI: mai mare (mai multe date), dar rar (o data/an/firma) -> acceptabil. Se leaga de migrarea istoricului (justifica incarcarea: "da-mi 2 ani de date, iti arat povestea completa").
- Backend nou necesar: rezumat_perioada(an, luna_start, luna_end) agregare multi-luni + _prompt_perioada + tip nou de notificare (clopotel) declansata la depunerea lui decembrie.

### Backlog mare (build nou)
- Migrare straturile 3-7: Salariati, Asociati, Mijloace fixe, Istoric declaratii (layer 1 Firme + layer 2 Solduri initiale = gata)
- Portare module declaratii din legacy in build nou (D100/D101/D112/D205/D300/D301/D390/D394/D406 exista in legacy + refacute in iCONTA_2026, de integrat in iconta_v2)

