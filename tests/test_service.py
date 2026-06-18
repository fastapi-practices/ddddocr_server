"""service 集成测试 —— 依赖模型加载（由 conftest 的 client fixture 启动 TestClient 时预热）"""

import asyncio
import pathlib

import pytest

from backend.plugin.ddddocr_server.service.captcha_service import captcha_service

ASSETS = pathlib.Path(__file__).parent / 'assets'

# 触发 app 启动 → lifespan 加载模型
pytestmark = pytest.mark.usefixtures('client')


def _read(name: str) -> bytes:
    return (ASSETS / name).read_bytes()


def test_recognize_text():
    img = _read('text.png')
    result = asyncio.run(captcha_service.recognize_text(image=img))
    assert isinstance(result, str) and result


def test_detect_objects():
    img = _read('click.png')
    boxes = asyncio.run(captcha_service.detect_objects(image=img))
    assert isinstance(boxes, list)
    for box in boxes:
        assert len(box) == 4


def test_match_slide():
    target = _read('slide_target.png')
    bg = _read('slide_bg.png')
    res = asyncio.run(captcha_service.match_slide(target=target, background=bg))
    assert set(res.keys()) == {'target_x', 'target_y'}
    assert isinstance(res['target_x'], int)
