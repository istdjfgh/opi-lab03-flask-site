"""Сайт магазину настільних ігор «Кубик» — лабораторна робота 03 (Flask + Jinja2).

Запуск:  python app.py  ->  http://127.0.0.1:5000
"""
from datetime import datetime

from flask import Flask, abort, render_template

import data

app = Flask(__name__)

# Пункти головного меню: (назва функції-обробника, підпис).
# Меню будується в base.html циклом, тому новий пункт додається одним рядком.
NAV_ITEMS = [
    ('home', 'Головна'),
    ('catalog', 'Каталог'),
    ('about', 'Про нас'),
    ('delivery', 'Доставка й оплата'),
    ('contacts', 'Контакти'),
]


@app.context_processor
def inject_globals():
    """Змінні, доступні в кожному шаблоні без явної передачі."""
    return {
        'shop': data.SHOP,
        'nav_items': NAV_ITEMS,
        'categories': data.CATEGORIES,
        'current_year': datetime.now().year,
    }


@app.template_filter('price')
def format_price(value):
    """Фільтр Jinja2: 1150 -> '1 150 грн'."""
    return f'{value:,.0f}'.replace(',', ' ') + ' грн'


@app.route('/')
def home():
    bestsellers = [game for game in data.GAMES if game['bestseller']]
    return render_template('home.html', bestsellers=bestsellers, advantages=data.ADVANTAGES)


@app.route('/catalog')
def catalog():
    return render_template('catalog.html', groups=data.games_by_category(), total=len(data.GAMES))


@app.route('/catalog/<slug>')
def game(slug):
    """Сторінка окремої гри: параметр адреси <slug> передається у функцію."""
    item = data.get_game(slug)
    if item is None:
        abort(404)
    related = [g for g in data.GAMES if g['category'] == item['category'] and g['slug'] != slug]
    return render_template('game.html', game=item, related=related)


@app.route('/about')
def about():
    years = datetime.now().year - data.SHOP['founded']
    return render_template('about.html', years=years, games_count=len(data.GAMES))


@app.route('/delivery')
def delivery():
    return render_template('delivery.html', methods=data.DELIVERY_METHODS,
                           payments=data.PAYMENT_METHODS, faq=data.FAQ)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html', hours=data.OPENING_HOURS)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
