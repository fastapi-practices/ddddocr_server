"""utils 纯逻辑单元测试（不依赖模型）"""

import pytest

from backend.common.exception import errors
from backend.plugin.ddddocr_server.utils import decode_base64


def test_decode_base64_plain():
    # b64('hello') == 'aGVsbG8='
    assert decode_base64('aGVsbG8=') == b'hello'


def test_decode_base64_with_data_prefix():
    # 调用方常带 data:image/png;base64, 前缀，应自动剥离
    assert decode_base64('data:image/png;base64,aGVsbG8=') == b'hello'


def test_decode_base64_invalid_raises():
    with pytest.raises(errors.RequestError):
        decode_base64('!!!not-valid-base64!!!')


import asyncio
import io

from starlette.datastructures import Headers, UploadFile

from backend.plugin.ddddocr_server.utils import decode_upload, transform_slide_result


def test_decode_upload_ok():
    f = UploadFile(filename='a.png', file=io.BytesIO(b'binary'), headers=Headers({'content-type': 'image/png'}))
    assert asyncio.run(decode_upload(f)) == b'binary'


def test_decode_upload_wrong_type():
    f = UploadFile(filename='a.gif', file=io.BytesIO(b'x'), headers=Headers({'content-type': 'image/gif'}))
    with pytest.raises(errors.RequestError):
        asyncio.run(decode_upload(f))


def test_decode_upload_empty():
    f = UploadFile(filename='a.png', file=io.BytesIO(b''), headers=Headers({'content-type': 'image/png'}))
    with pytest.raises(errors.RequestError):
        asyncio.run(decode_upload(f))


def test_transform_slide_result_ok():
    res = {'target_y': 50, 'target': [120, 50]}
    assert transform_slide_result(res) == {'target_x': 120, 'target_y': 50}


def test_transform_slide_result_empty_target():
    with pytest.raises(errors.ServerError):
        transform_slide_result({'target_y': 0, 'target': []})
