"""点选验证码目标检测路由"""

from fastapi import APIRouter, UploadFile

from backend.common.response.response_schema import ResponseModel, response_base
from backend.plugin.ddddocr_server.schema.click import ClickBase64Param
from backend.plugin.ddddocr_server.service.captcha_service import captcha_service
from backend.plugin.ddddocr_server.utils import decode_base64, decode_upload

router = APIRouter()


@router.post('', summary='点选验证码检测（文件上传）')
async def detect_click_upload(file: UploadFile) -> ResponseModel:
    image = await decode_upload(file)
    boxes = await captcha_service.detect_objects(image=image)
    return response_base.success(data={'boxes': boxes})


@router.post('/base64', summary='点选验证码检测（base64）')
async def detect_click_base64(obj: ClickBase64Param) -> ResponseModel:
    image = decode_base64(obj.image)
    boxes = await captcha_service.detect_objects(image=image)
    return response_base.success(data={'boxes': boxes})
