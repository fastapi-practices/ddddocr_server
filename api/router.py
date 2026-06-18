from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.ddddocr_server.api.v1.click import router as click_router
from backend.plugin.ddddocr_server.api.v1.ocr import router as ocr_router
from backend.plugin.ddddocr_server.api.v1.slide import router as slide_router

v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/ddddocr', tags=['验证码识别'])

v1.include_router(ocr_router, prefix='/ocr')
v1.include_router(click_router, prefix='/click')
v1.include_router(slide_router, prefix='/slide')
