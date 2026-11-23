"""Тести сайту: усі сторінки відкриваються, меню й посилання працюють, 404 для неіснуючих адрес.

Запуск: python -m pytest
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data  # noqa: E402
from app import NAV_ITEMS, app  # noqa: E402


@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


@pytest.mark.parametrize('path, heading', [
    ('/', 'Збирайте друзів'),
    ('/catalog', 'Настільні ігри'),
    ('/about', 'Ми любимо настільні ігри'),
    ('/delivery', 'Як отримати замовлення'),
    ('/contacts', 'Завітайте до нас'),
])
def test_static_pages_render(client, path, heading):
    response = client.get(path)
    assert response.status_code == 200
    assert heading in response.get_data(as_text=True)


def test_menu_contains_all_pages_and_marks_current(client):
    html = client.get('/about').get_data(as_text=True)
    for _, label in NAV_ITEMS:
        assert label in html
    assert 'href="/about" aria-current="page"' in html


@pytest.mark.parametrize('game', data.GAMES, ids=lambda g: g['slug'])
def test_every_game_page_works(client, game):
    response = client.get(f'/catalog/{game["slug"]}')
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert game['title'] in html
    assert data.CATEGORIES[game['category']]['title'] in html


def test_catalog_lists_every_game(client):
    html = client.get('/catalog').get_data(as_text=True)
    for game in data.GAMES:
        assert f'/catalog/{game["slug"]}' in html


def test_home_shows_only_bestsellers(client):
    html = client.get('/').get_data(as_text=True)
    for game in data.GAMES:
        assert (game['title'] in html) == game['bestseller']


def test_price_filter_formats_thousands(client):
    assert '2 350 грн' in client.get('/catalog/terraforming-mars').get_data(as_text=True)


def test_unknown_game_returns_404(client):
    response = client.get('/catalog/no-such-game')
    assert response.status_code == 404
    assert 'Такої сторінки немає' in response.get_data(as_text=True)


def test_unknown_page_returns_404(client):
    assert client.get('/missing').status_code == 404


def test_pages_are_responsive(client):
    html = client.get('/').get_data(as_text=True)
    assert 'name="viewport"' in html
    css = client.get('/static/css/style.css').get_data(as_text=True)
    assert '@media (max-width: 960px)' in css


def test_get_game_helper():
    assert data.get_game('azul')['title'] == 'Азул'
    assert data.get_game('nope') is None


def test_games_by_category_skips_empty_categories():
    groups = data.games_by_category()
    assert all(games for _, _, games in groups)
    assert sum(len(games) for _, _, games in groups) == len(data.GAMES)
