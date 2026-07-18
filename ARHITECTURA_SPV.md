# ARHITECTURA SPV / ANAF — decizii si temeiuri
Stabilit 17.07.2026. Verificat la sursa oficiala. Fisier normativ: se suprascrie, nu se acumuleaza copii datate.

## DECIZIA 1 — modelul certificatului (17.07.2026)
iConta = APLICATIE inrolata la ANAF, cu UN SINGUR Client ID + Client Secret.
Fiecare cabinet autorizeaza cu certificatul LUI. iConta NU e imputernicit, NU detine certificat.
Temei: procedura oficiala ANAF - dezvoltatorul e identificat printr-un client app id;
utilizatorii sunt identificati prin serialul certificatului digital calificat.
Token-urile sunt generate pentru certificat si identifica utilizatorul, nu aplicatia.
Coerent cu produsul: iConta e platforma de cabinet; contabilul depune, iConta e unealta.

## LINIA DE DESPARTIRE (temei tehnic, nu preferinta)
| Serviciu                          | OAuth | Server-side |
|-----------------------------------|-------|-------------|
| e-Factura, e-Transport            | DA    | DA          |
| Mesaje SPV, rapoarte, declaratii  | NU    | NU          |
OAuth exista tocmai ca aplicatiile web sa NU aiba nevoie de certificat pe server:
contabilul autorizeaza O DATA in browserul lui, cu stickul introdus; serverul primeste
refresh token 365 zile si lucreaza fara certificat.

## BLOCANTUL CERTIFICATULUI (de ce SPVWS2 nu se poate server-side)
SPVWS2 (webserviced.anaf.ro) se autentifica prin mTLS cu certificat calificat LOCAL:
- token USB -> PKCS#11, driver local (clientul oficial MfpAnaf/ClientSPV, Sign.java:
  KeyStore.Builder.newInstance("PKCS11", ...))
- cloud (certSIGN Paperless) -> cere aplicatia vToken pe Windows/macOS
Sub eIDAS cheia privata NU paraseste dispozitivul calificat. Nu ajunge pe serverul Linux.
Nu e limitare ANAF, e arhitectura QSCD. Nu exista portita.
LIMITA DECLARATA: verificat certSIGN (1 din 4 furnizori). DigiSign/Trans Sped/AlfaTrust
sunt sub aceeasi arhitectura QSCD, dar documentatia lor nu a fost citita.

## PARAMETRI OAUTH (verificati la sursa 17.07.2026)
Sursa: static.anaf.ro/static/10/Anaf/Informatii_R/API/Oauth_procedura_inregistrare_aplicatii_portal_ANAF.pdf
- Authorize: https://logincert.anaf.ro/anaf-oauth2/v1/authorize
- Token:     https://logincert.anaf.ro/anaf-oauth2/v1/token
- Grant type: authorization_code | Client auth: Basic Auth header
- token_content_type=jwt : pe QUERY la authorize SI in BODY la token
- ACCESS TOKEN: 90 zile (129600 min) | REFRESH TOKEN: 365 zile (525600 min)
- Fereastra de obtinere token: 60 secunde, apoi se reseteaza conexiunea
- Limita: 1000 apeluri/minut -> 429 Too Many Requests | 403 = request neautorizat
- Nomenclator servicii la inrolare: DOAR e-Factura si e-Transport (+ TestOauth)
- Certificatul cabinetului trebuie sa aiba drept SPV PJ
  (reprezentant legal / reprezentant desemnat / imputernicit)
- Test: https://api.anaf.ro/TestOauth/jaxrs/hello?name=X (orice token valid il poate apela)

## DE DECIS INAINTE DE INROLARE (nu la implementare)
- CALLBACK URL: propus https://iconta.eu/anaf/oauth/callback — unul singur, ambele servicii.
  Se declara la inrolare, greu de schimbat ulterior.
- Client Secret -> ~/.iconta/api_keys.env (NU in git)
- Un certificat acoperă MAI MULTE firme. Modelul NU e token-per-firma:
  spv_token per accounting_firm_id + lista de CUI-uri acoperite, DESCOPERITA nu presupusa.
- Refresh la 90 zile = cron obligatoriu. Fara el, cabinetul reface autorizarea cu stickul.
  Cu refresh 365 zile, cabinetul care nu intra un an pierde accesul oricum.

## SPVWS2 — ce ofera (blocat de certificat, consemnat pentru cand/daca se deschide)
Client oficial: github.com/MfpAnaf/ClientSPV (MIT). Ultimul jurnal de modificari: 06.11.2018.
- /SPVWS2/rest/listaMesaje?zile=N[&cif=X]  -> id, detalii, cif, data_creare, tip (ex. RECIPISA)
  Raspunsul contine si lista de CUI-uri acoperite de certificat + serialul.
- /SPVWS2/rest/descarcare?id=N            -> PDF-ul mesajului
- /SPVWS2/rest/cerere?tip=...&cui=...     -> VECTOR FISCAL, Situatie Sintetica (debite),
  Obligatii de plata, Istoric declaratii, NeconcordanteD112CNP (D112 vs REVISAL),
  NeconcordanteD394, Duplicat Recipisa, Fisa Rol, Bilant anual/semestrial etc.
VALOARE PIERDUTA ODATA CU F128: astea erau materia prima pentru verificatoare incrucisate
cu sursa de adevar la ANAF (nu doar in baza proprie). Se redeschid impreuna cu F128.
Contact tehnic ANAF: spv.webservice@mfinante.ro
INTREBARE TRIMISA 17.07.2026 catre spv.webservice@mfinante.ro, doua puncte:
  (1) exista/se planifica transmitere declaratii prin WS?  -> deblocheaza F127
  (2) se planifica OAuth pentru SPVWS2?                    -> deblocheaza F128 + rapoartele 'cerere'
Fara raspuns pana la 17.08.2026: F127/F128 raman AMANAT. Raspunsul se consemneaza AICI.

## STARE FUNCTIONALITATI (17.07.2026)
- F126, F160, F121 : temei tehnic confirmat prin OAuth. Se pot construi server-side.
- F127 (transmitere declaratii): AMANAT. Nu exista API. README oficial il listeaza
  la "pentru viitor". De confirmat la spv.webservice@mfinante.ro inainte de RESPINS.
- F128 (monitorizare mesaje SPV): AMANAT. Blocant structural (certificat local).
  Singura cale = agent desktop la cabinet = ALT PRODUS. Se redeschide daca ANAF
  adauga OAuth la SPVWS2.

## ORDINEA DE CONSTRUCTIE
Conectorul SPV se construieste O DATA (OAuth + stocare token + refresh + retry/coada),
apoi F126, F160, F121 sunt apeluri peste el. Cinci pozitii, un singur auth.

# ============================================================
# LECTII DIN CONCURENTA (verificat la sursa 17.07.2026)
# ============================================================
Surse: ajutor.smartbill.ro/article/982, smartbill.ro/e-factura, smartbill.ro/totul-despre-efactura,
certsign.ro (interviu Mircea Capatana). Limita: verificat SmartBill; Oblio/FGO/EasyBill
au acelasi flux dupa documentatia lor publica, dar nu au fost citite in detaliu.

## CONFIRMARE: nu exista cale ascunsa
SmartBill face IDENTIC ce face iConta: aplicatie inrolata o data, utilizatorul autorizeaza
cu certificatul lui, 90 de zile, reinnoire automata care uneori esueaza -> email + reautorizare
manuala. Aceleasi constrangeri ANAF pentru toata lumea.
"SmartBill va putea accesa doar sectiunea e-Factura, nu si alte informatii ale companiei
tale care se regasesc in SPV" -> NICI SMARTBILL NU ARE MESAJE SPV. F128 nu e o gaura
in produsul iConta, e limita platformei ANAF pentru toti jucatorii cloud.

## AVANTAJ STRUCTURAL iCONTA (decurge din decizia model (1))
SmartBill autorizeaza PER FIRMA: fiecare client, cont propriu, autorizare proprie, 90 zile.
Cabinet cu 40 de firme in SmartBill = 40 de autorizari, fiecare la 90 de zile.
iConta autorizeaza PER CABINET: contabilul autorizeaza O DATA, tokenul acopera toate
firmele pe care certificatul lui are drept. UNA, la 90 de zile, si aia automata.
Nu e detaliu tehnic - e argument de vanzare. Vine direct din "platforma de cabinet",
nu "platforma de firma".

## DE APLICAT IN ECRANUL DE CONECTARE (cand se stabileste cu DS - Regula 0)
1. AVERTISMENT 24 DE ORE: dupa inrolarea certificatului in SPV trebuie asteptate 24h
   pana functioneaza (sursa: certSIGN/SmartBill). Fara mesaj explicit, cabinetul incearca
   imediat, primeste eroare si crede ca e vina iConta. Text in ecran, nu in FAQ.
2. LINK DE AUTORIZARE TRIMISIBIL: SmartBill genereaza un link pe care il trimiti celui
   care are certificatul. La iConta contabilul E utilizatorul, deci nu e necesar la baza -
   DAR tiparul e util invers: cabinetul trimite linkul unui client care are certificat propriu.
   De evaluat cand se face ecranul.
3. CERTIFICAT CLOUD = OK pentru autorizare, daca e instalat local prin vToken
   ("versiunea digitala a certificatului, daca este instalata pe calculator, este echivalenta
   cu un certificat pe token"). Deci contabilul cu certificat cloud POATE autoriza iConta.
   Nu confunda cu blocantul SPVWS2 (acolo problema e serverul, nu clientul).

## PENTRU TERMENI SI CONDITII (nu tehnic, dar decurge din arhitectura)
Formularea SmartBill, de folosit ca model: "Trimiterea e-Facturii e obligatia intocmitorului
si nu are nicio legatura cu procesul de autorizare in SPV a contului SmartBill."
Aplicat la iConta: contabilul depune cu certificatul lui, pe firmele lui; iConta e unealta.
Raspunderea pe depunere NU trece la iConta. Modelul (2) ar fi mutat-o.
Firma (SRL) = vehicul comercial (contracte, facturi, GDPR-procesator), NU intra in lantul ANAF.
Contul de dezvoltator OAuth e pe persoana fizica (CNP), nu pe CUI.

# ============================================================
# CONECTORUL SPV — arhitectura (17.07.2026, inainte de cod)
# ============================================================

## DOMENIU
FACE: autorizare OAuth, stocare token, refresh automat, functia unica apel_anaf().
NU FACE: e-Factura, e-Transport. Alea sunt F126/F160/F121, construite PESTE conector.
Daca intra logica de facturi in conector, scopul e ratat.

## SCHEMA (in public, NU per tenant — tokenul apartine cabinetului, nu firmei)
CREATE TABLE spv_token (
  id                 SERIAL PRIMARY KEY,
  accounting_firm_id INT NOT NULL,
  serial_certificat  TEXT NOT NULL,        -- din JWT decodat
  access_token       TEXT NOT NULL,        -- CRIPTAT (Fernet)
  refresh_token      TEXT NOT NULL,        -- CRIPTAT (Fernet)
  access_expira      TIMESTAMPTZ NOT NULL,
  refresh_expira     TIMESTAMPTZ NOT NULL,
  creat_la           TIMESTAMPTZ DEFAULT now(),
  reimprospatat_la   TIMESTAMPTZ,
  activ              BOOLEAN DEFAULT true,
  UNIQUE (accounting_firm_id, serial_certificat)
);
CREATE TABLE spv_cui_acoperit (
  token_id      INT REFERENCES spv_token(id) ON DELETE CASCADE,
  cui           TEXT NOT NULL,
  verificat_la  TIMESTAMPTZ,
  are_drept     BOOLEAN,
  UNIQUE (token_id, cui)
);
CRIPTARE: obligatorie. Procedura ANAF pune explicit responsabilitatea pastrarii
securizate a token-urilor in seama dezvoltatorului. Cheia Fernet in ~/.iconta/api_keys.env
(NU in git, NU in DB). Dump de DB fara env = inutilizabil.

## CAPCANA CRITICA — ROTATIA REFRESH TOKEN-ULUI
La refresh se obtin valori NOI si pentru access_token, SI pentru refresh_token.
AMANDOUA trebuie salvate (temei: procedura oficiala ANAF, sectiunea Refresh Token JWT:
"In Body se gasesc valorile noi pentru access_token si in refresh_token. Acestea
trebuiesc salvate pentru a putea fi folosite in continuare").
Daca salvezi doar access-ul nou -> urmatorul refresh esueaza -> cabinetul reautorizeaza
cu stickul. Comentariu explicit in cod, altfel se pierde la prima refactorizare.

## FLUXUL DE AUTORIZARE
1. Contabil apasa "Conecteaza SPV"
2. Backend: genereaza state (CSRF), legat de accounting_firm_id, expira in 10 min
3. Redirect -> https://logincert.anaf.ro/anaf-oauth2/v1/authorize
     ?response_type=code&client_id=..&redirect_uri=..&token_content_type=jwt&state=..
   (scope gol; token_content_type=jwt pe QUERY aici)
4. Contabil: alege certificatul de pe stick + PIN
5. ANAF -> GET https://iconta.eu/anaf/oauth/callback?code=..&state=..
6. Backend verifica state, apoi POST https://logincert.anaf.ro/anaf-oauth2/v1/token
     Basic Auth (client_id:client_secret)
     x-www-form-urlencoded: grant_type=authorization_code, code, redirect_uri,
     token_content_type=jwt        <- in BODY aici, nu pe query
   FEREASTRA 60 SECUNDE (procedura ANAF) - pasul 6 nu se amana.
7. Decodeaza JWT -> serial_certificat, exp
8. Salveaza criptat.

## CRON REFRESH  (IMPLEMENTAT 18.07 = F177, core/spv_refresh.py + spv-refresh.timer)
Zilnic 03:30 (dupa backup 03:00), systemd timer (NU crontab) -> TOATE token-urile active
cu access_expira < now() + MARJA (SPV_REFRESH_MARJA_ZILE, implicit 15 zile).
Reutilizeaza reimprospateaza_token: POST /token grant_type=refresh_token, salveaza AMBELE
valori noi criptate (vezi CAPCANA CRITICA).
FAIL-SAFE: fiecare token in tranzactie separata; un esec NU opreste restul. La esec,
tranzactia face ROLLBACK -> tokenul RAMANE activ si se reincearca a doua zi (15z marja =
~15 incercari inainte de expirare). NU se dezactiveaza la prima eroare - o eroare ANAF
tranzitorie (5xx/timeout) nu trebuie sa forteze reconectarea cand exista marja. Orice esec
-> email Brevo (core.observare), nu tacit.
Marja 15 zile > avertismentul UI de 7 zile (MARJA_REFRESH_ZILE): cronul actioneaza INAINTE
ca ecranul sa alarmeze. Cabinet inactiv un an pierde accesul oricum (refresh 365z) - regula
ANAF, nu bug; cronul continua sa alerteze.
LIMITA: reimprospateaza_token trateaza orice non-200 la fel (nu distinge invalid_grant
permanent de 5xx tranzitoriu). Rafinarea (deactivare doar pe invalid_grant) cere schimbare
in _post_token - amanata pana la primul cabinet real; marja de 15z acopera tranzitoriile.

## FUNCTIA UNICA DE APEL
def apel_anaf(accounting_firm_id, metoda, url, **kw):
  1. ia token activ; lipsa/inactiv -> EroareSpvNeconectat
  2. access expirat -> refresh sincron, apoi continua
  3. request cu Bearer
  4. 401 -> refresh o data, retry o data, apoi eroare
  5. 429 -> backoff exponential (limita ANAF: 1000 apeluri/minut)
  6. 403 -> EroareSpvFaraDrept (certificatul n-are drept pe CIF)
REGULA: TOATE apelurile catre ANAF trec prin ea. Zero requests.get direct spre
api.anaf.ro in restul codului. De pus regula in verificator_conformitate.py.

## FINDING 18.07.2026 (primul apel real per-CIF pe listaMesajeFactura) — "fara drept" = 200, NU 403
DOVEDIT pe SPV real: ANAF e-Factura semnaleaza lipsa dreptului pe un CIF cu
  HTTP 200 + body {"eroare": "Nu aveti drept in SPV pentru CIF=<cui>"}
NU cu 403. Deci presupunerea "403 -> are_drept=false" din arhitectura era INCOMPLETA:
un status 200 poate ascunde un refuz de drept in campul "eroare". apel_anaf ramane corect
(403 tot ridica EroareSpvFaraDrept), dar decizia are_drept se ia din TEXT, la nivelul
apelantului care parseaza raspunsul, nu doar din status. 403 apare pentru alte refuzuri
(serviciu/aplicatie); "fara drept pe acest CIF" vine ca 200+eroare.
Endpoint verificat la sursa (build vechi /opt/iconta/main.py):
  https://api.anaf.ro/prod/FCTEL/rest/listaMesajeFactura?zile=N&cif=X[&filtru=P]
  raspuns: {"mesaje":[...]} = are drept (chiar si gol/"fara mesaje" = drept OK);
           {"eroare":"...drept..."} = fara drept.

## NECUNOSCUTA — ce CUI-uri acopera token-ul  (REZOLVATA 18.07.2026, pe token real)
CONFIRMAT prin decodarea unui JWT real (certificat admin, 18.07): JWT-ul OAuth NU contine
NICIO lista de CUI-uri. Payload-ul are doar: rolurile de SERVICIU la care are drept tokenul
(roles = HELLO@EFACTURA@ETRANSPORT@SRV_EFACTURA@SRV_ETRANSPORT), serialul certificatului,
issuer-ul certificatului (ex. DigiSign), clientappid-ul aplicatiei, exp/iat/nbf. Formatul:
alg RS512, kid anaf_2023_2024; claim-uri utile: scope_data[] + campuri plate (efactura,
etransport, roles, serial, sub).
CONSECINTA (nu mai e optionala, e OBLIGATORIE): spv_cui_acoperit NU se poate popula din token.
Se populeaza EMPIRIC - apel de test per CIF la listaMesajeFactura; verdictul are_drept se ia
din TEXTUL raspunsului, nu din status HTTP (vezi FINDING 18.07 de mai sus: "fara drept" = 200+eroare,
nu 403). Lista de mesaje (chiar goala) = are drept; {"eroare":"...drept..."} = fara drept.
Certificatul poate emite e-Factura pe firmele pe care are drept SPV PJ, dar CARE sunt acele firme
se afla doar intreband ANAF per CIF, nu din token.
Serialul certificatului = claim `serial` (si `sub` = acelasi fara ':'). extrage_serial il prinde.

## CONTEXT — certificatul de dezvoltare (18.07.2026)
Certificatul folosit la validarea conectorului e al ADMINISTRATORULUI platformei (Costin), NU al
unui cabinet. Costin nu e cabinet: nu depune prin SPV, nu are drept SPV pe firme si nici nu trebuie.
Verdictul "Nu aveti drept in SPV pentru CIF=<iConta>" e ASTEPTAT si CORECT, nu un bug. Rolul tokenului
admin e strict sa testeze MECANISMUL (apel_anaf, criptare, refresh, sondaj per-CIF) pe SPV real -
si mecanismul e VALIDAT cap-coada 18.07. Conexiunile de productie se fac PER CABINET din UI
(Setari -> Conectare SPV), fiecare cabinet cu certificatul LUI, pe firmele LUI unde are drept SPV PJ;
accounting_firm_id = cabinetul logat, niciodata hardcodat.

## FISIERE
spv_conector.py       auth, token, refresh, apel_anaf
spv_rute.py           GET /spv/autorizare, GET /anaf/oauth/callback
spv_refresh.py        cron
test_spv_conector.py  teste
Migrare: cele 2 tabele in public. In tenant_template: NIMIC (nu e per tenant).

## ORDINEA DE EXECUTIE
1. Migrare schema
2. spv_conector.py + teste pe refresh/rotatie (mock, nu ANAF real)
3. Rute + callback
4. STOP -> se citeste DESIGN_SYSTEM.md, se stabileste ecranul de conectare (Regula 0)
5. TEST REAL cu stickul: autorizare -> https://api.anaf.ro/TestOauth/jaxrs/hello?name=X
   -> decodare JWT -> aflam ce contine (rezolva NECUNOSCUTA de mai sus)
   Acesta e testul functional real (regula 0c). TestOauth exista exact pentru asta.
6. Cron
7. Abia apoi F126.

## INTREBARE TRIMISA LA ANAF (17.07.2026)
Contact tehnic ANAF: spv.webservice@mfinante.ro
INTREBARE TRIMISA 17.07.2026 catre spv.webservice@mfinante.ro, doua puncte:
  (1) exista/se planifica transmitere declaratii prin WS?  -> deblocheaza F127
  (2) se planifica OAuth pentru SPVWS2?                    -> deblocheaza F128 + rapoartele 'cerere'
Fara raspuns pana la 17.08.2026: F127/F128 raman AMANAT. Raspunsul se consemneaza AICI.
