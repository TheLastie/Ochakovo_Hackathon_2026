"""Editable copy and convention-based video discovery, refreshed per page request."""
import json

from django.conf import settings


def load_content():
    data = json.loads((settings.BASE_DIR / 'web/content.json').read_text())
    directory = settings.BASE_DIR / 'web/public/videos'

    def video(key, configured):
        result = dict(configured)
        for extension in ('mp4', 'webm'):
            filename = f'{key}.{extension}'
            if (directory / filename).is_file():
                result['src'] = f'/static/videos/{filename}?v={
                    (
                        directory /
                        filename).stat().st_mtime_ns}'
                break
        captions = f'{key}.ru.vtt'
        if (directory / captions).is_file():
            result['captions'] = f'/static/videos/{captions}?v={
                (
                    directory /
                    captions).stat().st_mtime_ns}'
        return result

    data['brandVideo'] = {**data['brandVideo'],
                          **video('brand', data['brandVideo'])}
    for role in data['roles'] + \
            ([data['bonusRole']] if data.get('bonusRole') else []):
        role['video'] = video(
            role['id'], role.get(
                'video', {
                    'src': '', 'captions': ''}))
    return data


def role_choices():
    return [(role['id'], role['title']) for role in load_content()['roles']]


def application_role_choices():
    # Historical applications keep readable labels after the playable roster
    # changes.
    current = role_choices()
    historical = [(r['id'], r['title']) for r in load_content().get(
        'retiredRoles', []) if r['id'] not in dict(current)]
    return current + historical + \
        [('line', 'Оператор линии'), ('technologist',
                                      'Технолог'), ('undecided', 'Пока выбирает')]
