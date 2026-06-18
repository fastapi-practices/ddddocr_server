"""图片解码与结果转换工具（纯逻辑，无模型依赖）"""

import base64

from fastapi import UploadFile

from backend.common.exception import errors


def decode_base64(image: str) -> bytes:
    """将 base64 字符串解码为图片 bytes。

    支持自动剥离 `data:image/...;base64,` 前缀。

    :param image: base64 编码的图片字符串
    :return: 图片二进制
    """
    raw = image.strip()
    if raw.startswith('data:'):
        # 去掉 data:image/xxx;base64, 前缀
        raw = raw.split(',', 1)[1] if ',' in raw else raw
    try:
        return base64.b64decode(raw, validate=True)
    except Exception as e:
        raise errors.RequestError(msg=f'图片 base64 解码失败: {e!s}') from e


ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png'}


async def decode_upload(file: UploadFile) -> bytes:
    """读取上传文件并校验类型为 jpg/png。

    :param file: 上传的图片文件
    :return: 图片二进制
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise errors.RequestError(msg=f'仅支持 jpg/png 格式，当前为 {file.content_type}')
    data = await file.read()
    if not data:
        raise errors.RequestError(msg='图片内容为空')
    return data


def transform_slide_result(res: dict) -> dict:
    """将 ddddocr slide_match 原始返回转换为统一 schema 结构。

    ddddocr 返回: ``{'target_y': y, 'target': [x, y]}``
    统一输出:    ``{'target_x': x, 'target_y': y}``

    :param res: ddddocr slide_match 原始返回
    :return: 含 target_x / target_y 的字典
    """
    target = res.get('target') or []
    if len(target) < 2:
        raise errors.ServerError(msg='滑块识别结果异常')
    return {
        'target_x': int(target[0]),
        'target_y': int(res.get('target_y', target[1])),
    }
