from pydantic import Field

from backend.common.schema import SchemaBase


class OcrBase64Param(SchemaBase):
    """文本识别 base64 入参"""

    image: str = Field(description='base64 编码的验证码图片')


class OcrResult(SchemaBase):
    """文本识别结果"""

    result: str = Field(description='识别出的文本')
