"""Проверка форматирования маршрута для Telegram."""

from routing.summary import build_route_summary


def test_build_route_summary_full_payload():
    response = {
        'routes': [{
            'distance': 3200.0,
            'duration': 600.0,
            'legs': [
                {
                    'distance': 1000.0,
                    'duration': 200.0,
                    'summary': 'Улица Дерибасовская',
                    'steps': [
                        {
                            'distance': 500.0,
                            'duration': 100.0,
                            'name': 'Улица Дерибасовская',
                            'maneuver': {'type': 'depart', 'modifier': 'straight'}
                        },
                        {
                            'distance': 500.0,
                            'duration': 100.0,
                            'name': 'Пушкинская',
                            'maneuver': {'type': 'turn', 'modifier': 'right'}
                        }
                    ]
                },
                {
                    'distance': 2200.0,
                    'duration': 400.0,
                    'summary': 'Площадь Греческая',
                    'steps': [
                        {
                            'distance': 2200.0,
                            'duration': 400.0,
                            'name': '',
                            'maneuver': {'type': 'arrive', 'modifier': None}
                        }
                    ]
                }
            ]
        }],
        'waypoints': [
            {'name': 'Старт', 'location': [30.7233, 46.4825]},
            {'name': 'Промежуточная', 'location': [30.7300, 46.4850]},
            {'name': '', 'location': [30.7400, 46.5000]}
        ]
    }

    summary = build_route_summary(response)

    assert summary['distance_km'] == 3.2
    assert summary['duration_min'] == 10.0
    assert summary['legs'][0]['origin'] == 'Старт'
    assert summary['legs'][0]['destination'] == 'Промежуточная'
    assert summary['legs'][1]['destination'] == '46.50000,30.74000'
    assert summary['legs'][0]['steps'][1]['instruction'] == 'Поверните направо по Пушкинская'
    assert 'Маршрут: 3.2 км · 10 мин' in summary['message']
    assert '1) Старт → Промежуточная' in summary['message']


def test_build_route_summary_empty():
    summary = build_route_summary({'routes': []})
    assert summary['message'] == 'Маршрут не найден.'
    assert summary['legs'] == []
