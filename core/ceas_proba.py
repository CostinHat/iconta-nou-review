# -*- coding: utf-8 -*-
"""Ceasul fix al testelor de browser (15.1-E5, R10): un test care compară ce arată ecranul cu „azi” primește un moment de referință fix, nu ceasul
calendarului. Pagina (`new Date()`) și testul (`DATA_REF`) văd aceeași zi, oricând rulează poarta (și peste miezul nopții)."""
import datetime

DATA_REF = datetime.date(2026, 11, 3)
MOMENT_REF = datetime.datetime(2026, 11, 3, 10, 0, 0)


def pagina_cu_ceas_fix(browser, **kw):
    """O pagină nouă într-un context al cărui `Date` e fixat la MOMENT_REF (temporizatoarele merg mai departe)."""
    ctx = browser.new_context(**kw)
    ctx.clock.set_fixed_time(MOMENT_REF)
    return ctx.new_page()
