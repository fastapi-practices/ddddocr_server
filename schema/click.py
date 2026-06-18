from pydantic import Field

from backend.common.schema import SchemaBase


class ClickBase64Param(SchemaBase):
    """点选检测 base64 入参"""

    image: str = Field(description='base64 编码的验证码图片')


class ClickResult(SchemaBase):
    """点选检测结果"""

    boxes: list[list[int]] = Field(description='目标框列表 [[x1,y1,x2,y2], ...]')
