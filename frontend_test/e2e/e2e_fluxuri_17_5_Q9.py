"""Probe de candidat. Firme de test ale aplicației, câte o execuție completă pe dimensiune."""
import re
from email.message import Message
from urllib.parse import unquote
from datetime import timedelta
from decimal import Decimal
from urllib.parse import urlsplit

import pytest
from conftest import BAZA
from e2e_bloc_a import _api, _ok, CLIENT, _deschide_factura, _pdf_text, emite_api
from e2e_lot92 import firma_cv, firma_cv_noua  # fixturi native pytest

@pytest.fixture(params=[(1366,768),(603,590)], ids=["laptop","mic"])
def pagina(patron,request):
    u=urlsplit(BAZA)
    assert (u.scheme,u.hostname,u.port) in (("http","localhost",8019),("http","127.0.0.1",8019))
    w,h=request.param
    patron.pg.set_viewport_size({"width":w,"height":h})
    return patron

def test_f089_iesirea_inaintea_intrarii_este_atomica(pagina,firma_cv):
    """Un stoc prezent de 200 ar permite greșit ieșirea de 150 la o dată cu sold zero."""
    from core.ceas_proba import DATA_REF
    e=pagina
    cale=f'/tenants/{firma_cv["tenant_id"]}/stocuri'
    doc="Intrare probă Q7"
    intrare=_ok(_api(e,"POST",cale+"/intrare",dict(denumire="Articol Q7 "+str(firma_cv["tenant_id"])+" "+str(e.pg.viewport_size["width"]),
                um="buc",data=DATA_REF.isoformat(),cantitate=200,pret_unitar=10,document=doc)),"intrare")
    aid=intrare["articol_id"]
    fisa=cale+f"/articole/{aid}/fisa"
    inainte=_ok(_api(e,"GET",fisa),"fișa inițială")
    assert len(inainte["linii"])==1 and Decimal(inainte["linii"][0]["sold_cantitate"])==200
    iesire=dict(articol_id=aid,cantitate=150,data=(DATA_REF-timedelta(days=1)).isoformat(),document="Ieșire Q7")
    r=_api(e,"POST",cale+"/iesire",iesire)
    dupa=_ok(_api(e,"GET",fisa),"fișa după refuz")
    assert r["status"] in (400,409,422) and dupa==inainte
    mesaj=str(r["json"]).casefold()
    assert re.search(r"stoc|disponibil",mesaj) and re.search(r"(?<![\d-])0(?:[,.]0+)?(?!\d)",mesaj),mesaj
    iesire["data"]=DATA_REF.isoformat()
    _ok(_api(e,"POST",cale+"/iesire",iesire),"ieșire la data cu stoc")
    linii=_ok(_api(e,"GET",fisa),"fișa finală")["linii"]
    assert len(linii)==2 and Decimal(linii[-1]["sold_cantitate"])==50

def test_f045_pdf_adresa_si_numele_descarcat(pagina,firma_cv):
    e=pagina
    factura=emite_api(e,firma_cv)
    fid=factura["factura_id"]
    _deschide_factura(e,firma_cv,fid)
    downloads=[]
    popups=[]
    def la_descarcare(fisier):
        downloads.append(fisier)

    def la_fereastra(fereastra):
        popups.append(fereastra)

    from contextlib import ExitStack
    with ExitStack() as ascultatori:
        for eveniment, functie in (("download", la_descarcare), ("popup", la_fereastra)):
            e.pg.on(eveniment, functie)
            ascultatori.callback(e.pg.remove_listener, eveniment, functie)
        with e.pg.expect_response(lambda r:urlsplit(r.url).path.endswith(f"/facturi/{fid}/pdf")) as raspuns:
            e.pg.locator("#fd-pdf").click()
        r=raspuns.value
        assert r.ok and "application/pdf" in r.headers.get("content-type","")
        pdf=r.body()
        # Evenimentele de descărcare/deschidere pot urma după răspunsul HTTP.
        from time import monotonic
        termen=monotonic()+10
        while not downloads and not any(x.url not in ("","about:blank") for x in popups) and monotonic()<termen:
            e.pg.wait_for_timeout(100)
        if downloads:
            f=downloads[0]
            nume=f.suggested_filename
            assert f.path().read_bytes()==pdf
        else:
            assert popups, "PDF-ul nu s-a deschis"
            url=popups[-1].url
            if url.startswith("blob:"):
                # Un blob anonim pierde numele transmis de API.
                nume=unquote(url.rsplit("/",1)[-1])
            else:
                assert urlsplit(url).path==urlsplit(r.url).path, url
                header=Message()
                header["Content-Disposition"]=r.headers.get("content-disposition","")
                nume=header.get_filename() or unquote(urlsplit(url).path.rsplit("/",1)[-1])
    serie=re.fullmatch(r"(.*?)([0-9]+)",factura["numar"])
    assert serie and serie[1] and nume.lower().endswith(".pdf")
    assert re.search(re.escape(serie[1])+r"[\s_.-]*(?:nr[. _-]*)?0*"+str(int(serie[2]))+r"(?!\d)",nume,re.I),nume
    assert pdf.startswith(b"%PDF-")
    text,_=_pdf_text(pdf)
    assert CLIENT["#em-adresa"].casefold() in text.casefold(),text
