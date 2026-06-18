"""文本验证码识别路由"""

from fastapi import APIRouter, Depends, UploadFile
from pyrate_limiter import Duration, Rate

from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.plugin.ddddocr_server.schema.ocr import OcrBase64Param, OcrResult
from backend.plugin.ddddocr_server.service.captcha_service import captcha_service
from backend.plugin.ddddocr_server.utils import decode_base64, decode_upload
from backend.utils.limiter import RateLimiter

router = APIRouter()


@router.post(
    '',
    summary='文本验证码识别（文件上传）',
    dependencies=[Depends(RateLimiter(Rate(30, Duration.MINUTE)))],
)
async def recognize_ocr_upload(file: UploadFile) -> ResponseSchemaModel[OcrResult]:
    image = await decode_upload(file)
    result = await captcha_service.recognize_text(image=image)
    return response_base.success(data=OcrResult(result=result))


@router.post(
    '/base64',
    summary='文本验证码识别（base64）',
    dependencies=[Depends(RateLimiter(Rate(30, Duration.MINUTE)))],
)
async def recognize_ocr_base64(obj: OcrBase64Param) -> ResponseSchemaModel[OcrResult]:
    image = decode_base64(obj.image)
    result = await captcha_service.recognize_text(image=image)
    return response_base.success(data=OcrResult(result=result))
