"""滑块验证码缺口匹配路由"""

from fastapi import APIRouter, Depends, UploadFile
from pyrate_limiter import Duration, Rate

from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.plugin.ddddocr_server.schema.slide import SlideBase64Param, SlideResult
from backend.plugin.ddddocr_server.service.captcha_service import captcha_service
from backend.plugin.ddddocr_server.utils import decode_base64, decode_upload
from backend.utils.limiter import RateLimiter

router = APIRouter()


@router.post(
    '',
    summary='滑块缺口匹配（文件上传）',
    dependencies=[Depends(RateLimiter(Rate(30, Duration.MINUTE)))],
)
async def match_slide_upload(target: UploadFile, bg: UploadFile) -> ResponseSchemaModel[SlideResult]:
    target_bytes = await decode_upload(target)
    bg_bytes = await decode_upload(bg)
    res = await captcha_service.match_slide(target=target_bytes, background=bg_bytes)
    return response_base.success(data=SlideResult(**res))


@router.post(
    '/base64',
    summary='滑块缺口匹配（base64）',
    dependencies=[Depends(RateLimiter(Rate(30, Duration.MINUTE)))],
)
async def match_slide_base64(obj: SlideBase64Param) -> ResponseSchemaModel[SlideResult]:
    target_bytes = decode_base64(obj.target)
    bg_bytes = decode_base64(obj.bg)
    res = await captcha_service.match_slide(target=target_bytes, background=bg_bytes)
    return response_base.success(data=SlideResult(**res))
