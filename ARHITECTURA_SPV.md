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
