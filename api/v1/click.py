"""点选验证码目标检测路由"""

from fastapi import APIRouter, Depends, UploadFile
from pyrate_limiter import Duration, Rate

from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.plugin.ddddocr_server.schema.click import ClickBase64Param, ClickResult
from backend.plugin.ddddocr_server.service.captcha_service import captcha_service
from backend.plugin.ddddocr_server.utils import decode_base64, decode_upload
from backend.utils.limiter import RateLimiter

router = APIRouter()


@router.post(
    '',
    summary='点选验证码检测（文件上传）',
    dependencies=[Depends(RateLimiter(Rate(30, Duration.MINUTE)))],
)
async def detect_click_upload(file: UploadFile) -> ResponseSchemaModel[ClickResult]:
    image = await decode_upload(file)
    boxes = await captcha_service.detect_objects(image=image)
    return response_base.success(data=ClickResult(boxes=boxes))


@router.post(
    '/base64',
    summary='点选验证码检测（base64）',
    dependencies=[Depends(RateLimiter(Rate(30, Duration.MINUTE)))],
)
async def detect_click_base64(obj: ClickBase64Param) -> ResponseSchemaModel[ClickResult]:
    image = decode_base64(obj.image)
    boxes = await captcha_service.detect_objects(image=image)
    return response_base.success(data=ClickResult(boxes=boxes))
