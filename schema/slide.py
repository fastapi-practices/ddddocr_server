from pydantic import Field

from backend.common.schema import SchemaBase


class SlideBase64Param(SchemaBase):
    """滑块匹配 base64 入参"""

    target: str = Field(description='base64 编码的滑块小块图片')
    bg: str = Field(description='base64 编码的背景大图')


class SlideResult(SchemaBase):
    """滑块匹配结果"""

    target_x: int = Field(description='缺口横向偏移')
    target_y: int = Field(description='缺口纵向偏移')
