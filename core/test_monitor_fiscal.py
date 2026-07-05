# -*- coding: utf-8 -*-
from core.monitor_fiscal import extrage_text


def test_extrage_text():
    h = "<html><script>x=1</script><body><h1>Titlu</h1><p>TVA 21% de la august</p></body></html>"
    t = extrage_text(h)
    assert "Titlu" in t and "TVA 21%" in t and "x=1" not in t
