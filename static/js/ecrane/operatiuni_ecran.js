// [operatiuni] Ecran generic "Operatiuni speciale" - condus de configuratie.
// O operatiune noua = o intrare in REGISTRU (titlu, ruta, campuri), zero cod nou de ecran.
import { api, esc, arataMesaj, semnAjutor } from "../api.js?v=a7f9e80ae0";
// [ajutor_contextual] mapare cheie operatiune -> ID functionalitate (semnul "?" dinamic)
const _OP_AJUTOR = { avans:"F009", bacsis:"F010", leasing:"F056", asociati:"F039",
  credit:"F024", chirie:"F020", decont:"F040", contract_special:"F021", reevaluare:"F074",
  provizion:"F071", sponsorizare:"F086", subventie:"F090", obiect_inv:"F063", inventariere:"F052" };

// tipuri de camp: data | numar | text | select(optiuni) | bool
// conditie: {camp: "tip", val: "rata"} - campul apare doar cand alt camp are valoarea
const C = (nume, eticheta, tip = "numar", extra = {}) => ({ nume, eticheta, tip, ...extra });

const REGISTRU = [
  { cat: "Finanțare", cheie: "leasing", titlu: "Leasing", ruta: "nota-leasing", campuri: [
    C("data", "Data", "data"), 
    C("tip", "Tip operatiune", "select", { optiuni: [["primire","Primire bun (financiar)"],["rata","Rata lunara"],["reziduala","Valoare reziduala"],["operational","Chirie leasing operational"]] }),
    C("valoare_capital", "Valoare capital", "numar", { cond: { camp: "tip", val: "primire" } }),
    C("dobanda_totala", "Dobanda totala", "numar", { cond: { camp: "tip", val: "primire" }, optional: true }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "tip", val: "primire" }, optional: true, sugestie: "2133" }),
    C("capital", "Capital rata", "numar", { cond: { camp: "tip", val: "rata" } }),
    C("dobanda", "Dobanda", "numar", { cond: { camp: "tip", val: "rata" }, optional: true }),
    C("comision", "Comision", "numar", { cond: { camp: "tip", val: "rata" }, optional: true }),
    C("valoare_reziduala", "Valoare reziduala", "numar", { cond: { camp: "tip", val: "reziduala" } }),
    C("chirie", "Chirie lunara", "numar", { cond: { camp: "tip", val: "operational" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "credit", titlu: "Credite bancare", ruta: "nota-credit", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["primire","Primire credit"],["dobanda","Dobanda"],["plata","Plata rata"],["restanta","Restanta"],["garantie","Garantie"]] }),
    C("tip", "Termen", "select", { optiuni: [["scurt","Sub 1 an (519)"],["lung","Peste 1 an (162)"]] }),
    C("suma", "Suma", "numar", { cond: { camp: "operatie", val: "primire" } }),
    C("dobanda", "Dobanda", "numar", { cond: { camp: "operatie", val: "dobanda" } }),
    C("rata", "Rata (capital)", "numar", { cond: { camp: "operatie", val: "plata" }, optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "asociati", titlu: "Decontări asociați (455/457)", ruta: "nota-asociati", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["dividend","Dividend"],["imprumut","Imprumut asociat"],["regularizare","Regularizare interimare"]] }),
    C("brut", "Dividend brut", "numar", { cond: { camp: "operatie", val: "dividend" } }),
    C("suma", "Suma imprumut", "numar", { cond: { camp: "operatie", val: "imprumut" } }),
    C("fel", "Sens", "select", { optiuni: [["primire","Primire de la asociat"],["restituire","Restituire catre asociat"]], cond: { camp: "operatie", val: "imprumut" } }),
    C("total_interimar", "Total dividende interimare", "numar", { cond: { camp: "operatie", val: "regularizare" } }),
    C("dividend_anual", "Dividend anual final", "numar", { cond: { camp: "operatie", val: "regularizare" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "avans", titlu: "Avansuri (409/419)", ruta: "nota-avans", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["avans_platit","Avans platit (409)"],["regularizare_platit","Regularizare 409"],["avans_incasat","Avans incasat (419)"],["regularizare_incasat","Regularizare 419"]] }),
    C("suma", "Suma (fara TVA)"), C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("destinatie", "Destinatie", "select", { optiuni: [["stocuri","Stocuri"],["servicii","Servicii"],["imobilizari","Imobilizari"],["imobilizari_necorporale","Imobilizari necorporale"]], optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "Vânzări speciale", cheie: "agricultor", titlu: "Vânzare către agricultor (regim special)", ruta: "vanzare-agricultor", campuri: [
    C("data", "Data", "data"),
    C("pret", "Preț (fără taxă)", "numar"),
    C("descriere", "Descriere", "text", { optional: true }),
  ] },  /* [0a_rute_v1] backend existent, legat in registru */
  { cat: "Imobilizări și capital", cheie: "necorporala", titlu: "Achiziție necorporală (software/licență/brevet)", ruta: "achizitie-necorporala", campuri: [
    C("data", "Data", "data"),
    C("denumire", "Denumire", "text"),
    C("valoare", "Valoare (fără TVA)", "numar"),
    C("tip", "Tip", "select", { optiuni: [["software","Software (36 luni)"],["licenta","Licență"],["brevet","Brevet"]] }),
    C("dnf_luni", "Durată contract (luni)", "numar", { cond: { camp: "tip", val: "licenta" }, optional: true }),
    C("furnizor_nume", "Furnizor", "text"),
    C("furnizor_cui", "CUI furnizor", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
  ] },  /* [0a_rute_v1] */
  { cat: "Imobilizări și capital", cheie: "reevaluare", titlu: "Reevaluare imobilizări (105)", ruta: "reevaluare-imobilizare", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["reevaluare","Reevaluare MF"],["surplus","Transfer surplus la 1175"]] }),
    C("mijloc_fix_id", "ID mijloc fix", "numar", { cond: { camp: "operatie", val: "reevaluare" } }),
    C("valoare_justa", "Valoare justa", "numar", { cond: { camp: "operatie", val: "reevaluare" } }),
    C("suma", "Suma surplus", "numar", { cond: { camp: "operatie", val: "surplus" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Imobilizări și capital", cheie: "obiect_inv", titlu: "Obiecte de inventar (303)", ruta: "nota-obiect-inventar", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["achizitie","Achizi\u021bie"],["dare_folosinta","Dare in folosinta (603=303)"],["scoatere","Scoatere din folosinta"]] }),
    C("valoare", "Valoare"), C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Imobilizări și capital", cheie: "provizion", titlu: "Provizioane și ajustări", ruta: "nota-provizion", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["creanta","Ajustare creante (491)"],["provizion","Provizion (151)"],["stoc","Ajustare stocuri (39x)"]] }),
    C("actiune", "Actiune", "select", { optiuni: [["constituire","Constituire"],["reluare","Reluare"]] }),
    C("suma", "Suma"),
    C("tip", "Tip provizion", "select", { optiuni: [["litigii","Litigii"],["garantii","Garantii"],["dezafectare","Dezafectare"],["restructurare","Restructurare"],["impozite","Impozite"],["altele","Altele"]], cond: { camp: "fel", val: "provizion" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Imobilizări și capital", cheie: "productie", titlu: "Producție (711/345)", ruta: "nota-productie", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["obtinere","Ob\u021binere produse"],["pic","Produc\u021bie \u00een curs (331)"],["vanzare","V\u00e2nzare + desc\u0103rcare"]] }),
    C("cost_standard", "Cost standard", "numar", { cond: { camp: "operatie", val: "obtinere" } }),
    C("cost_efectiv", "Cost efectiv", "numar", { cond: { camp: "operatie", val: "obtinere" }, optional: true }),
    C("suma", "Suma PIC", "numar", { cond: { camp: "operatie", val: "pic" } }),
    C("moment", "Moment", "select", { optiuni: [["constatare","Constatare"],["reluare","Reluare"]], cond: { camp: "operatie", val: "pic" } }),
    C("pret_vanzare", "Pret vanzare", "numar", { cond: { camp: "operatie", val: "vanzare" } }),
    C("cost_standard_iesit", "Cost standard iesit", "numar", { cond: { camp: "operatie", val: "vanzare" } }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "vanzare" }, optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Imobilizări și capital", cheie: "inventariere", titlu: "Inventariere anuală", ruta: "nota-inventariere", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["plus","Plus stoc"],["plus_mf","Plus mijloc fix"],["minus","Minus"],["casare","Casare"]] }),
    C("valoare", "Valoare"),
    C("cont_stoc", "Cont stoc", "text", { optional: true, sugestie: "371" }),
    C("imputabil", "Imputabil", "select", { optiuni: [["true","Da"],["false","Nu"]], cond: { camp: "operatie", val: "minus" } }),
    C("valoare_imputare", "Valoare imputare", "numar", { cond: { camp: "operatie", val: "minus" }, optional: true }),
    C("denumire", "Denumire mijloc fix", "text", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "operatie", val: "plus_mf" }, optional: true, sugestie: "2131" }),
    C("cont_amortizare", "Cont amortizare", "text", { cond: { camp: "operatie", val: "plus_mf" }, optional: true, sugestie: "2813" }),
    C("dnf_luni", "Durat\u0103 normal\u0103 (luni)", "numar", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("data_pif", "Dat\u0103 punere \u00een func\u021biune", "data", { cond: { camp: "operatie", val: "plus_mf" }, optional: true }),
    C("metoda", "Metod\u0103 amortizare", "select", { cond: { camp: "operatie", val: "plus_mf" }, optiuni: [["liniara","Liniar\u0103"],["degresiva","Degresiv\u0103"],["accelerata","Accelerat\u0103"],["superaccelerata","Superaccelerat\u0103"]] }),
    C("mijloc_fix_id", "ID mijloc fix", "numar", { cond: { camp: "operatie", val: "casare" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "TVA regimuri speciale", cheie: "tva_incasare", titlu: "TVA la încasare (art. 282)", ruta: "nota-tva-incasare", campuri: [
    C("data", "Data", "data"),
    C("sens", "Sens", "select", { optiuni: [["incasare","Incasare de la client (4428=4427)"],["plata","Plata catre furnizor (4426=4428)"]] }),
    C("suma_incasata", "Suma incasata/platita (cu TVA)"),
    C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "marja", titlu: "Vânzare regim marjă (second-hand)", ruta: "vanzare-marja", campuri: [
    C("data", "Data", "data"), C("pret_vanzare", "Pret vanzare"), C("pret_cumparare", "Pret cumparare"),
    C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "marja_turism", titlu: "Marjă agenții de turism", ruta: "vanzare-marja-turism", campuri: [
    C("data", "Data", "data"),
    C("calitate_client", "Client", "select", { optiuni: [["PF","Persoana fizica"],["PJ","Persoana juridica"]] }),
    C("incasat", "Incasat de la client"),
    C("cost_ue", "Cost servicii UE"),
    C("cost_non_ue", "Cost servicii non-UE", "numar", { optional: true }),
    C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "taxare_inversa", titlu: "Taxare inversă internă (art. 331)", ruta: "achizitie-taxare-inversa", campuri: [
    C("data", "Data", "data"),
    C("furnizor_nume", "Furnizor", "text"),
    C("furnizor_cui", "CUI furnizor (RO, plătitor TVA)", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("categorie", "Categorie art. 331", "select", { optiuni: [["deseuri","Deșeuri"],["masa_lemnoasa","Masă lemnoasă"],["cereale","Cereale"],["certificate_emisii","Certificate emisii"],["energie_electrica","Energie electrică"],["certificate_verzi","Certificate verzi"],["cladiri_terenuri","Clădiri/terenuri"],["aur_investitii","Aur de investiții"],["telefoane","Telefoane"],["circuite_integrate","Circuite integrate"],["console_tablete","Console/tablete"],["gaze_naturale","Gaze naturale"]] }),
    C("valoare", "Valoare (fara TVA)"),
    C("cont_destinatie", "Cont destinatie", "text", { sugestie: "371" }),
    C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("furnizor_platitor_tva", "Furnizor platitor TVA", "select", { optiuni: [["true","Da"],["false","Nu"]] }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "neinregistrat", titlu: "Achiziție de la neînregistrat (persoană fizică) — D394 op. N", ruta: "achizitie-neinregistrat", campuri: [
    C("data", "Data", "data"),
    C("furnizor_nume", "Furnizor (persoană fizică)", "text"),
    C("valoare", "Valoare"),
    C("cont_cheltuiala", "Cont cheltuială/stoc", "text", { sugestie: "301" }),
    C("numar", "Nr. document (borderou)", "text", { optional: true }),
    C("categorie", "Categorie bun (art. 331 lit. D)", "select", { optional: true, optiuni: [["cereale","Cereale"],["deseuri","Deșeuri"],["masa_lemnoasa","Masă lemnoasă"],["terenuri","Terenuri"],["constructii","Construcții"],["alte_bunuri","Alte bunuri"],["alte_servicii","Alte servicii"]], ajutor: "Fără categorie, operațiunea N rămâne EXCLUSĂ din D394 cu avertisment (nu se ghicește)." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "agricultor", titlu: "Achiziție de la agricultor (compensare 8%)", ruta: "achizitie-agricultor", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare (fara taxa)"),
    C("cont_cheltuiala", "Cont cheltuiala/stoc", "text", { sugestie: "301" }),
    C("agricultor_in_registru", "Agricultor in registru", "select", { optiuni: [["true","Da"],["false","Nu"]] }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "aur", titlu: "Aur de investiții (art. 313)", ruta: "vanzare-aur-investitii", campuri: [
    C("data", "Data", "data"),
    C("tip", "Tip", "select", { optiuni: [["lingou","Lingou"],["plancheta","Plancheta"],["moneda","Moneda"]] }),
    C("puritate", "Puritate (ex. 995)", "text"),
    C("suma", "Valoare vanzare"),
    C("calitate_client", "Client", "select", { optiuni: [["PF","Persoana fizica"],["PJ","Persoana juridica"]] }),
    C("client_identificare", "Identificare client", "text"),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "Extern", cheie: "reeval_valuta", titlu: "Reevaluare lunară solduri valută", ruta: "reevaluare-valuta", multi: "solduri", campuri: [
    C("data", "Data (ultima zi a lunii)", "data") ], subcampuri: [
    C("cont", "Cont", "text", { sugestie: "4111" }),
    C("valoare_valuta", "Sold in valuta"),
    C("moneda", "Moneda", "text", { sugestie: "EUR" }),
    C("curs_evidenta", "Curs evidenta"),
    C("tip", "Tip", "select", { optiuni: [["creanta","Creanta"],["datorie","Datorie"],["disponibil","Disponibil"]] }) ] },
  { cat: "Extern", cheie: "decont_valuta", titlu: "Decontare în valută (665/765)", ruta: "decontare-valuta", campuri: [
    C("data", "Data", "data"),
    C("tip", "Tip", "select", { optiuni: [["creanta","Incasare creanta"],["datorie","Plata datorie"]] }),
    C("valoare_valuta", "Valoare in valuta"),
    C("moneda", "Moneda (EUR/USD...)", "text", { sugestie: "EUR" }),
    C("curs_evidenta", "Curs de evidenta"),
    C("cont_tert", "Cont tert", "text", { sugestie: "4111" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Extern", cheie: "achizitie_ic", titlu: "Achiziție intracomunitară", ruta: "achizitie-ic", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare (RON)"),
    C("cod_tva_furnizor", "Cod TVA furnizor UE (ex. DE123456789)", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("furnizor_nume", "Furnizor", "text", { optional: true }),
    C("cont_destinatie", "Cont destinatie", "text", { sugestie: "371" }),
    C("tip", "Tip", "select", { optiuni: [["bunuri","Bunuri"],["servicii","Servicii"]] }),
    C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("data_faptului_generator", "Data faptului generator (dacă diferă)", "data", { optional: true, ajutor: "Opțional. Gol = încadrare pe data facturii. Completat = exigibilitate MIN(dată factură, ziua 15 luna următoare) — art. 284." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Extern", cheie: "vanzare_ic", titlu: "Livrare/prestare intracomunitară (VIES live)", ruta: "vanzare-ic", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare"),
    C("cod_tva_client", "Cod TVA client (ex. DE123456789)", "text"),
    C("tip", "Tip", "select", { optiuni: [["bunuri","Bunuri"],["servicii","Servicii"]] }),
    C("dovada_transport", "Dovada transport", "text", { optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Extern", cheie: "import_ec", titlu: "Import extracomunitar (DVI)", ruta: "import-extracomunitar", campuri: [
    C("data", "Data", "data"), C("valoare_vamala", "Valoare vamala (RON)"),
    C("cont_destinatie", "Cont destinatie", "text", { sugestie: "371" }),
    C("procent_taxa_vamala", "Taxa vamala %", "numar", { optional: true }),
    C("accize", "Accize", "numar", { optional: true }),
    C("accesorii", "Accesorii", "numar", { optional: true }),
    C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Extern", cheie: "export_ec", titlu: "Export extracomunitar (DVE)", ruta: "export-extracomunitar", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare"),
    C("tara_client", "Tara client", "text"),
    C("dovada_export", "Dovada export (DVE)", "text"),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "Personal și deconturi", cheie: "decont", titlu: "Decont deplasare / diurnă", ruta: "nota-decont-deplasare", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["avans","Avans deplasare (542)"],["decont","Decont final"]] }),
    C("sursa", "Sursa", "select", { optiuni: [["casa","Casa"],["banca","Banca"]] }),
    C("suma", "Suma avans", "numar", { cond: { camp: "fel", val: "avans" } }),
    C("avans", "Avans acordat", "numar", { cond: { camp: "fel", val: "decont" } }),
    C("diurna", "Diurna", "numar", { cond: { camp: "fel", val: "decont" }, optional: true }),
    C("transport", "Transport", "numar", { cond: { camp: "fel", val: "decont" }, optional: true }),
    C("cazare", "Cazare", "numar", { cond: { camp: "fel", val: "decont" }, optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Personal și deconturi", cheie: "contract_special", titlu: "Contracte speciale (zilieri, mandat, cenzori)", ruta: "nota-contract-special", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["zilier","Zilier"],["mandat","Mandat administrator"],["cenzor","Cenzor"]] }),
    C("brut", "Suma bruta"),
    C("sursa", "Sursa plata", "select", { optiuni: [["casa","Casa"],["banca","Banca"]] }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Personal și deconturi", cheie: "bacsis", titlu: "Bacșiș (HoReCa)", ruta: "nota-bacsis", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["incasare","Incasare"],["distribuire","Distribuire la salariati"]] }),
    C("suma", "Suma"),
    C("sursa", "Sursa", "select", { optiuni: [["card","Card"],["numerar","Numerar"]], cond: { camp: "fel", val: "incasare" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "Diverse", cheie: "sponsorizare", titlu: "Sponsorizare (credit fiscal)", ruta: "nota-sponsorizare", campuri: [
    C("data", "Data", "data"), C("suma", "Suma sponsorizata"),
    C("mod", "Mod", "select", { optiuni: [["contract","Contract (6582=401)"],["plata","Plata directa (6582=5121)"]], optional: true }),
    C("tip_impozit", "Tip impozit", "select", { optiuni: [["profit","Impozit pe profit"],["micro","Microintreprindere"]], optional: true }),
    C("cifra_afaceri", "Cifra de afaceri (pt credit)", "numar", { optional: true }),
    C("impozit_profit", "Impozit datorat (pt credit)", "numar", { optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "subventie", titlu: "Subvenții (445/741)", ruta: "nota-subventie", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["exploatare","Exploatare"],["investitii","Investitii (475)"],["reluare","Reluare la venituri"]] }),
    C("suma", "Suma", "numar", { optional: true }),
    C("moment", "Moment", "select", { optiuni: [["drept","La dreptul de a primi"],["incasare","La incasare"]], optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "chirie", titlu: "Chirii / comodat / refacturări", ruta: "nota-chirie", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["comodat","Comodat"],["chirie_platita","Chirie platita (612)"],["chirie_incasata","Chirie incasata (706)"],["refacturare","Refacturare utilitati"]] }),
    C("suma", "Suma"), C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "perisabilitati", titlu: "Perisabilități și scăzăminte", ruta: "nota-perisabilitati", campuri: [
    C("data", "Data", "data"),
    C("valoare_intrari", "Valoare intrari (baza calcul)"),
    C("procent_limita", "Procent limita HG 831/2004 (%)"),
    C("pierdere_constatata", "Pierdere constatata"),
    C("cont_stoc", "Cont stoc", "text", { optional: true, sugestie: "371" }),
    C("cota", "Cota TVA %", "numar", { optional: true, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "sgr", titlu: "SGR - garanție ambalaje", ruta: "nota-sgr", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["achizitie","Achizi\u021bie (garan\u021bii pl\u0103tite)"],["vanzare","V\u00e2nzare (garan\u021bii \u00eencasate)"],["restituire","Restituire"],["autofactura","Autofactura SGR"],["virare","Virare"]] }),
    C("nr_ambalaje", "Nr. ambalaje (0,50 lei/buc)", "numar", { optional: true }),
    C("suma", "Suma (alternativ la nr.)", "numar", { optional: true }),
    C("sursa", "Sursa", "select", { optiuni: [["casa","Casa"],["banca","Banca"]], optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "ong", titlu: "Operațiuni ONG (OMFP 3103/2017)", ruta: "nota-ong", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["venit","Venit AFSP"],["scutire","Calcul scutire art. 15 CF"]] }),
    C("suma", "Suma", "numar", { cond: { camp: "operatie", val: "venit" } }),
    C("fel", "Fel venit", "select", { optiuni: [["cotizatie","Cotizatie (731)"],["contributie","Contributie"],["donatie","Donatie (733)"],["sponsorizare","Sponsorizare primita (733)"],["financiar","Financiar (734)"]], cond: { camp: "operatie", val: "venit" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "lichidare", titlu: "Lichidare / radiere firmă", ruta: "nota-lichidare", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["vanzare_activ","V\u00e2nzare activ la lichidare"],["partaj","Partaj catre asociati"]] }),
    C("pret", "Pret vanzare", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("valoare_bruta", "Valoare bruta activ", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("amortizare_cumulata", "Amortizare cumulata", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("capital_social", "Capital social", "numar", { cond: { camp: "operatie", val: "partaj" } }),
    C("rezerve", "Rezerve", "numar", { cond: { camp: "operatie", val: "partaj" }, optional: true }),
    C("profituri", "Profituri nerepartizate", "numar", { cond: { camp: "operatie", val: "partaj" }, optional: true }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
];

const CATEGORII = [...new Set(REGISTRU.map((o) => o.cat))];

export async function ecranOperatiuni(corp, nav, t) {
  let opCurenta = null;

  const lista = (c) => {
    if (c) corp = c;
    nav.setInapoi(undefined);
    corp.innerHTML = `
      <h2 class="pf-titlu">Opera\u021biuni speciale</h2>
      <p class="pf-intro">Note contabile pentru opera\u021biuni punctuale. Toate intr\u0103 drept <b>ciorn\u0103</b> \u2014 se valideaz\u0103 din Registru jurnal.</p>
      ${CATEGORII.map((cat) => `
        <div style="display:block;margin-bottom:12px;background:var(--fundal);border:1px solid var(--linie);border-radius:var(--raza);padding:14px">
          <div class="pf-frand-nume" style="margin-bottom:8px">${esc(cat)}</div>
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            ${REGISTRU.filter((o) => o.cat === cat).map((o) =>
              `<button class="buton-secundar" data-op="${o.cheie}">${esc(o.titlu)}</button>`).join("")}
          </div>
        </div>`).join("")}`;
    corp.querySelectorAll("[data-op]").forEach((b) => b.addEventListener("click", () => {
      opCurenta = REGISTRU.find((o) => o.cheie === b.dataset.op);
      nav.mergi(opCurenta.titlu, formular);
    }));
  };

  const formular = (c) => {
    if (c) corp = c;
    const ziAzi = new Date().toISOString().slice(0, 10);
    const camp = (c) => {
      const cond = c.cond ? ` data-cond-camp="${c.cond.camp}" data-cond-val="${c.cond.val}"` : "";
      let input;
      if (c.tip === "select") {
        input = `<select id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">${(c.optional ? '<option value="">-</option>' : "") + c.optiuni.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("")}</select>`;
      } else if (c.tip === "data") {
        input = `<input type="date" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">`;
      } else if (c.tip === "numar") {
        input = `<input type="number" step="0.01" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}" placeholder="${c.sugestie || ""}">`;
      } else {
        input = `<input type="text" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}" placeholder="${c.sugestie || ""}">`;
      }
      const ajutor = c.ajutor ? `<span class="camp-ajutor">${esc(c.ajutor)}</span>` : "";
      return `<div class="camp"${cond}><label class="camp-eticheta" for="op-${c.nume}">${esc(c.eticheta)}${c.optional ? "" : '<span class="oblig">*</span>'}</label>${input}${ajutor}</div>`;
    };
    corp.innerHTML = `
      <h2 class="pf-titlu">${esc(opCurenta.titlu)}${_OP_AJUTOR[opCurenta.cheie] ? " " + semnAjutor(_OP_AJUTOR[opCurenta.cheie]) : ""}</h2>
      <div class="pf-frand" style="display:block">
        <div class="grila-campuri">
          ${opCurenta.campuri.map(camp).join("")}
        </div>
        ${opCurenta.multi ? '<div class="pf-frand-nume" style="margin:12px 0 6px">Solduri</div><div id="op-multi"></div>' : ""}
        <p style="margin-top:12px"><button class="buton-primar" id="op-trimite">Genereaz\u0103 nota (ciorn\u0103)</button></p>
        <div id="op-mesaj"></div>
      </div>`;

    // [multi] randuri repetabile (ex. reevaluare valuta)
    let randuriMulti = opCurenta.multi ? [0] : [];
    const zonaMulti = corp.querySelector("#op-multi");
    const randMulti = (i) => `<div class="grila-campuri grila-campuri-compacta">
      ${opCurenta.subcampuri.map((sc) => {
        if (sc.tip === "select") return `<div class="camp"><label class="camp-eticheta" for="m${i}-${sc.nume}">${esc(sc.eticheta)}</label><select id="m${i}-${sc.nume}" class="camp-input">${sc.optiuni.map(([v,l])=>`<option value="${v}">${esc(l)}</option>`).join("")}</select></div>`;
        const t2 = sc.tip === "numar" ? "number" : "text";
        return `<div class="camp"><label class="camp-eticheta" for="m${i}-${sc.nume}">${esc(sc.eticheta)}</label><input type="${t2}" step="0.0001" id="m${i}-${sc.nume}" class="camp-input" placeholder="${sc.sugestie||""}"></div>`;
      }).join("")}</div>`;
    if (opCurenta.multi && zonaMulti) {
      zonaMulti.innerHTML = randMulti(0) + '<p><button class="buton-secundar" id="op-plus-rand">+ Rand</button></p>';
      corp.querySelector("#op-plus-rand").addEventListener("click", () => {
        const i = randuriMulti.length; randuriMulti.push(i);
        const d = document.createElement("div"); d.innerHTML = randMulti(i);
        zonaMulti.insertBefore(d.firstElementChild, corp.querySelector("#op-plus-rand").parentElement);
      });
    }

    // vizibilitate conditionata
    const actualizeazaCond = () => {
      corp.querySelectorAll(".camp[data-cond-camp]").forEach((l) => {
        const sel = corp.querySelector(`#op-${l.dataset.condCamp}`);
        l.style.display = sel && sel.value === l.dataset.condVal ? "" : "none";
      });
    };
    opCurenta.campuri.filter((c) => c.tip === "select").forEach((c) =>
      corp.querySelector(`#op-${c.nume}`).addEventListener("change", actualizeazaCond));
    actualizeazaCond();

    corp.querySelector("#op-trimite").addEventListener("click", async () => {
      const zona = corp.querySelector("#op-mesaj");
      const corpReq = {};
      let lipsa = null;
      for (const c of opCurenta.campuri) {
        const el = corp.querySelector(`#op-${c.nume}`);
        const ascuns = el.closest(".camp").style.display === "none";
        if (ascuns) continue;
        const v = el.value;
        if (!v && !c.optional) { lipsa = c.eticheta; break; }
        if (v) corpReq[c.nume] = c.tip === "numar" ? parseFloat(v) : v;
      }
      if (lipsa) { arataMesaj(zona, "Camp obligatoriu: " + lipsa, "avert"); return; }
      if (opCurenta.multi) {
        corpReq[opCurenta.multi] = [...corp.querySelectorAll("#op-multi > div")].map((rand) => {
          const o = {};
          opCurenta.subcampuri.forEach((sc) => {
            const el = rand.querySelector(`[id$="-${sc.nume}"]`);
            if (el && el.value) o[sc.nume] = sc.tip === "numar" ? parseFloat(el.value) : el.value;
          });
          return o;
        }).filter((o) => Object.keys(o).length > 1 || (Object.keys(o).length === 1 && !o.tip));
        if (!corpReq[opCurenta.multi].length) { arataMesaj(zona, "Completeaza cel putin un rand.", "avert"); return; }
      }
      try {
        const r = await api.post(`/tenants/${t.id}/${opCurenta.ruta}`, corpReq);
        zona.innerHTML = `<p class="pf-intro">Notă generată (ciornă)${r.inregistrare_id ? " #" + r.inregistrare_id : ""}. O validezi din Registru jurnal.</p>`;
      } catch (e) {
        arataMesaj(zona, e.mesaj || e.message || "Nu am putut genera nota - verifica datele introduse si reincearca.", "eroare");
      }
    });
  };

  lista();
}

// precompletari_rest_v1
