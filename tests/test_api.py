"""API 集成测试 —— 免认证，直接用 client fixture"""

import base64
import pathlib

import pytest

ASSETS = pathlib.Path(__file__).parent / 'assets'


@pytest.fixture()
def text_png_b64() -> str:
    return base64.b64encode((ASSETS / 'text.png').read_bytes()).decode()


@pytest.fixture()
def click_png_b64() -> str:
    return base64.b64encode((ASSETS / 'click.png').read_bytes()).decode()


# ---------- OCR ----------


def test_ocr_base64_ok(client, text_png_b64):
    resp = client.post('/ddddocr/ocr/base64', json={'image': text_png_b64})
    assert resp.status_code == 200
    body = resp.json()
    assert body['code'] == 200
    assert 'result' in body['data']


def test_ocr_base64_invalid(client):
    resp = client.post('/ddddocr/ocr/base64', json={'image': '!!!'})
    assert resp.status_code == 400


def test_ocr_upload_ok(client):
    with (ASSETS / 'text.png').open('rb') as f:
        resp = client.post('/ddddocr/ocr', files={'file': ('text.png', f, 'image/png')})
    assert resp.status_code == 200
    assert 'result' in resp.json()['data']


def test_ocr_upload_wrong_type(client):
    resp = client.post('/ddddocr/ocr', files={'file': ('a.gif', b'x', 'image/gif')})
    assert resp.status_code == 400


# ---------- Click ----------


def test_click_base64_ok(client, click_png_b64):
    resp = client.post('/ddddocr/click/base64', json={'image': click_png_b64})
    assert resp.status_code == 200
    body = resp.json()
    assert body['code'] == 200
    assert 'boxes' in body['data']


def test_click_upload_ok(client):
    with (ASSETS / 'click.png').open('rb') as f:
        resp = client.post('/ddddocr/click', files={'file': ('click.png', f, 'image/png')})
    assert resp.status_code == 200
    assert 'boxes' in resp.json()['data']


# ---------- Slide ----------


def test_slide_base64_ok(client):
    target_b64 = base64.b64encode((ASSETS / 'slide_target.png').read_bytes()).decode()
    bg_b64 = base64.b64encode((ASSETS / 'slide_bg.png').read_bytes()).decode()
    resp = client.post('/ddddocr/slide/base64', json={'target': target_b64, 'bg': bg_b64})
    assert resp.status_code == 200
    data = resp.json()['data']
    assert set(data.keys()) == {'target_x', 'target_y'}


def test_slide_base64_missing_bg(client):
    resp = client.post('/ddddocr/slide/base64', json={'target': 'aGVsbG8='})  # 缺 bg
    assert resp.status_code == 422


def test_slide_upload_ok(client):
    with (ASSETS / 'slide_target.png').open('rb') as tf, (ASSETS / 'slide_bg.png').open('rb') as bf:
        resp = client.post(
            '/ddddocr/slide',
            files={'target': ('t.png', tf, 'image/png'), 'bg': ('b.png', bf, 'image/png')},
        )
    assert resp.status_code == 200
