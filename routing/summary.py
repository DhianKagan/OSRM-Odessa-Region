"""Утилиты форматирования маршрутов OSRM для интеграции с ботами."""



_MANEUVER_TEXT = {
    'depart': 'Начните движение',
    'arrive': 'Вы прибыли',
    'turn': 'Поверните',
    'continue': 'Продолжайте движение',
    'new name': 'Продолжайте движение',
    'merge': 'Перестройтесь',
    'on ramp': 'Сверните на съезд',
    'off ramp': 'Съезд',
    'fork': 'Держитесь',
    'end of road': 'В конце дороги поверните',
    'roundabout': 'На круговом движении',
    'use lane': 'Следуйте указаниям полос'
}

_MODIFIER_TEXT = {
    'left': 'налево',
    'right': 'направо',
    'sharp left': 'резко налево',
    'sharp right': 'резко направо',
    'slight left': 'слегка налево',
    'slight right': 'слегка направо',
    'straight': 'прямо',
    'uturn': 'развернитесь'
}


def _meters_to_kilometers(value):
    """Переводит метры в километры с округлением."""
    return round(value / 1000, 2)


def _seconds_to_minutes(value):
    """Переводит секунды в минуты с округлением."""
    return round(value / 60, 1)


def _fallback_waypoint_name(location, index):
    """Формирует читаемое имя точки, когда OSRM не прислал название."""
    if len(location) >= 2:
        lon, lat = location[0], location[1]
        return "{:.5f},{:.5f}".format(lat, lon)
    return "Точка {}".format(index)


def _humanize_step(step):
    """Генерирует простое текстовое описание манёвра."""
    maneuver = step.get('maneuver', {})
    step_type = maneuver.get('type')
    modifier = maneuver.get('modifier')
    name = step.get('name') or ''

    base = _MANEUVER_TEXT.get(step_type, 'Двигайтесь дальше')
    suffix = _MODIFIER_TEXT.get(modifier, modifier) if modifier else ''
    parts = [base]
    if suffix:
        parts.append(suffix)
    text = ' '.join(part for part in parts if part).strip().capitalize()

    if name:
        if step_type != 'arrive':
            text = "{} по {}".format(text, name)
        else:
            text = "{} к {}".format(text, name)
    return text or 'Двигайтесь дальше'


def build_route_summary(response):
    """Преобразует ответ OSRM в удобный для Telegram формат."""
    routes = response.get('routes') or []
    if not routes:
        return {
            'distance_km': 0.0,
            'duration_min': 0.0,
            'legs': [],
            'message': 'Маршрут не найден.'
        }

    route = routes[0]
    legs = route.get('legs') or []
    waypoints = response.get('waypoints') or []


    waypoint_names = []

    for idx, waypoint in enumerate(waypoints):
        name = waypoint.get('name')
        if not name:
            name = _fallback_waypoint_name(waypoint.get('location', ()), idx + 1)
        waypoint_names.append(name)

    legs_payload = []
    total_distance = _meters_to_kilometers(route.get('distance', 0.0))
    total_duration = _seconds_to_minutes(route.get('duration', 0.0))
    message_lines = ["Маршрут: {:.1f} км · {:.0f} мин".format(total_distance, total_duration)]

    for index, leg in enumerate(legs):
        leg_distance = _meters_to_kilometers(leg.get('distance', 0.0))
        leg_duration = _seconds_to_minutes(leg.get('duration', 0.0))
        summary = leg.get('summary') or 'Безымянный участок'
        origin = (
            waypoint_names[index]
            if index < len(waypoint_names)
            else "Точка {}".format(index + 1)
        )
        destination = (
            waypoint_names[index + 1]
            if index + 1 < len(waypoint_names)
            else "Точка {}".format(index + 2)
        )
        steps = []
        for step in leg.get('steps') or []:
            steps.append({
                'instruction': _humanize_step(step),
                'distance_km': _meters_to_kilometers(step.get('distance', 0.0)),
                'duration_min': _seconds_to_minutes(step.get('duration', 0.0))
            })

        legs_payload.append({
            'origin': origin,
            'destination': destination,
            'distance_km': leg_distance,
            'duration_min': leg_duration,
            'summary': summary,
            'steps': steps
        })

        message_lines.append(
            "{}) {} → {}: {:.1f} км · {:.0f} мин".format(
                index + 1,
                origin,
                destination,
                leg_distance,
                leg_duration
            )
        )

    return {
        'distance_km': total_distance,
        'duration_min': total_duration,
        'legs': legs_payload,
        'message': '\n'.join(message_lines)
    }

