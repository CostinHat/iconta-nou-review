Marca de referință: 569a52f. Citește CLAUDE.md §2.2 (structura raportului) și §2.3 (lanț, siguranță, limbă) și ARHITECT.md „FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, înainte de a începe. Stare: audit vizual tenant_003 (Comert Micro TVA SRL, cabinet 1968 Prisma) — tură de PARCURGERE (fără reparații). Am ajuns până la generarea D300 (Declarații pasul 2/3). Restul traseului NEparcurs (mai jos, cu ecranul exact). Regula 14: captură privită.

# PREDARE LANT — audit vizual tenant_003 (parcurgere, în curs)

## FOUR-WAY (ultima execuție, 16.08.2026)
HEAD = origin/main = backup/lant-2026-08-16 = RUNNING = 569a52f (doar PREDARE, cod neatins — tură de parcurgere).

## CUM SE PARCURGE tenant_003 (auth cross-cabinet, reutilizabil)
- tenant_003 e sub cabinetul 1968 (Prisma), NU sub FE (4163). Token mintuit fără parolă:
  `auth_api.emite_token(<user patron@prisma-cont.test>)` + inject sessionStorage. Scripturi gata în
  frontend_test/: w_auth.py (helper comun), w_salariati/w_operare/w_straturi/w_date_vector/w_declaratii/w_decl_gen3.py.
- Rulare: `set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=~/iconta_nou:~/iconta_nou/frontend_test ./venv/bin/python frontend_test/<script>.py`. Serviciul = 127.0.0.1:8010.
- MUTAȚIE DE DATE făcută (parte din „salvarea reală"): am importat 2 salariați în tenant_003 (Popescu Ana existentă + Ionescu Radu nou, CNP 1850715410012, brut 6000). Stat de plată îi arată.

## PARCURS ȘI VĂZUT (captură privită) — harta de până acum
- **Cardurile firmei (26)**: facturi, produse, declaratii, control, salariati, bonuri, jurnal, raportz, stocuri,
  balanta, bilant, casa, etransport, operatiuni, mijloace, banca, magazin, verificari, solicitari, acces, import,
  datefirma, rapoarte, registratura, contracte, centrecost.
- **Salariați (migrare)**: import valid → preview „toate 2 CNP corecte" → SALVARE reală → wizard cabinet, badge „✓ gata, 2 importați". Intro corectată e live (fără „vor fi sărite").
- **Stat de plată (#fa-salariati)**: cei 2 salariați apar cu brut/CAS/CASS/impozit/net corect.
- **Facturi (#fa-facturi)**: hub cu 6 acțiuni (Istoric, Scadențar, Emite, Model, Facturi primite SPV, Recurente).
- **Casă (#fa-casa)**: sold 12.000, semnalează plafonul (Legea 70/2015 art.3) cu temei — bine.
- **Control fiscal (#fa-control)**: RESTANȚE (10: D112 dec-iun + D100 T4/T1/T2), NU POT VERIFICA (D300/D394/D406
  → completează platitor_tva_anaf_inceput în vector; D205 lipsă note 2025), D301 nu se datorează, D300↔4427/4426
  coincid, D112 blocat pontaj (HG 1045/2018). Bine mesajat.
- **Straturi Import date**: toate file-upload cu intro care descrie coloanele; Plan de conturi = căutare/adăugare
  manuală (nu upload). „Descarcă model" doar la Solduri.
- **Date firmă (#fa-datefirma)**: exemplar — casetă „Profil incomplet — Nr. registrul comerțului blochează Bilanț
  S1005", asteriscuri pe obligatorii, câmp-ajutor preventiv, vector integrat (Regim micro, TVA Da, Periodicitate,
  vf-tva_data_inceput gol).
- **Declarații (#fa-declaratii)**: wizard 3 pași; tip din dropdown; generare D300 → ecran „Rânduri manuale D300".

## CONSTATĂRI (defecte văzute, NEatinse — numerotare continuă C1..C8)
- **C1** [Stat de plată] Pontaj neconfirmat afișat INCONSISTENT: Popescu Ana „⚠ pontaj neconfirmat", Ionescu Radu
  (la fel de nou, fără pontaj) NU. Ambii ar trebui marcați la fel.
- **C2** [Salariați, după salvare] Confirmarea = doar badge „✓ gata"; navighează la wizardul CABINET (toate 13
  firmele), nu la firma curentă; fără mesaj explicit de succes (arataMesaj „ok").
- **C3** [Import date, per firmă] Fără badge de stare per strat — nu se vede ce e importat (Q8, reconfirmat).
- **C4** [Straturi] „Descarcă model (CSV)" lipsește pe parteneri/asociați/mijloace/istoric/articole/rețete (doar
  Solduri îl are). Contabilul deduce formatul doar din intro.
- **C5** [Date firmă] Acord greșit: „**1 câmpuri** obligatorii lipsesc" (corect: „1 câmp obligatoriu lipsește").
- **C6** [Declarații, dropdown tip] D301 și D390 marcate „**nu se aplică (partidă simplă)**" pe un SRL (partidă
  DUBLĂ) — motiv GREȘIT (D301: firma e plătitoare TVA; D390: fără operațiuni IC). Mapare greșită a motivului.
- **C7** [Declarații, generare D300 T3] Eroare roșie „**luna invalidă: None (aștept 1-12)**" — expune „None"
  (valoare internă) utilizatorului, nu spune unde se corectează/ce consecință; D300 e TRIMESTRIAL (n-are lună).
  POSIBIL BLOCANT pentru generarea D300 → n-am ajuns la XML/DUK.
- **C8** [Casă] Placeholder dată „mm/dd/yyyy" (format american) pe aplicație RO (așteptat zz/ll/aaaa).

## RĂMAS DE PARCURS (traseul, cu ecranul EXACT)
1. **Declarații pasul 3 (XML + DUK)** — blocat pe C7 la D300 (T3). De reluat: alege trimestru explicit
   (#dec-trim) sau altă declarație; ajunge la „Descarcă XML" + „Validează DUK".
2. **Celelalte declarații**: D100 (trim), D112 (lunar — blocat pontaj neconfirmat), D205, D394, D406 → XML → DUK.
3. **Bancă (#fa-banca)** — capturată (t003_op_banca.png), NEprivită în detaliu.
4. **Salvarea reală + ecranul-unde-apar** pe straturile: Solduri, Parteneri, Asociați, Mijloace fixe, Istoric,
   Plan de conturi, Articole, Rețete (până acum doar ecranul de import văzut, nu salvarea).
5. Vector fiscal ca ecran separat (din Import date) + provocarea unui submit cu câmp obligatoriu gol pe Date firmă.

## LECȚII METODĂ (16.08)
- Selectorul de text prinde dashboard-ul din spatele modalului → citește din DOM-ul modalului sau privește captura.
- `#dec-trim` NU are valoarea „T2"; selectează prin index/label sau lasă default.
- Auth cross-cabinet: `auth_api.emite_token` (JWT_SECRET în api_keys.env).
