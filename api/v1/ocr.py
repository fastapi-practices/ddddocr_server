"""文本验证码识别路由"""

from fastapi import APIRouter, UploadFile

from backend.common.response.response_schema import ResponseModel, response_base
from backend.plugin.ddddocr_server.schema.ocr import OcrBase64Param
from backend.plugin.ddddocr_server.service.captcha_service import captcha_service
from backend.plugin.ddddocr_server.utils import decode_base64, decode_upload

router = APIRouter()


@router.post('', summary='文本验证码识别（文件上传）')
async def recognize_ocr_upload(file: UploadFile) -> ResponseModel:
    image = await decode_upload(file)
    result = await captcha_service.recognize_text(image=image)
    return response_base.success(data={'result': result})


@router.post('/base64', summary='文本验证码识别（base64）')
async def recognize_ocr_base64(obj: OcrBase64Param) -> ResponseModel:
    image = decode_base64(obj.image)
    result = await captcha_service.recognize_text(image=image)
    return response_base.success(data={'result': result})
