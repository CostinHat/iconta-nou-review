# -*- coding: utf-8 -*-
from core import plati

def test_provider_mock_implicit(monkeypatch):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("NETOPIA_API_KEY", raising=False)
    assert plati.provider_activ() == "mock"

def test_provider_stripe(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test")
    assert plati.provider_activ() == "stripe"

def test_provider_netopia(monkeypatch):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.setenv("NETOPIA_API_KEY", "x")
    assert plati.provider_activ() == "netopia"
