"""验证码识别服务"""

from starlette.concurrency import run_in_threadpool

from backend.plugin.ddddocr_server.core import get_det, get_ocr, get_semaphore
from backend.plugin.ddddocr_server.utils import transform_slide_result


class CaptchaService:
    """验证码识别服务（静态方法 + 强制关键字参数）"""

    @staticmethod
    async def recognize_text(*, image: bytes) -> str:
        """
        文本验证码识别

        :param image: 图片二进制
        :return: 识别出的文本
        """
        async with get_semaphore():
            return await run_in_threadpool(get_ocr().classification, image)

    @staticmethod
    async def detect_objects(*, image: bytes) -> list[list[int]]:
        """
        点选验证码目标检测

        :param image: 图片二进制
        :return: 目标框列表 [[x1, y1, x2, y2], ...]
        """
        async with get_semaphore():
            boxes = await run_in_threadpool(get_det().detection, image)
            return [[int(v) for v in box] for box in boxes]

    @staticmethod
    async def match_slide(*, target: bytes, background: bytes) -> dict:
        """
        滑块缺口匹配

        :param target: 滑块小块图片二进制
        :param background: 背景大图二进制
        :return: {'target_x': x, 'target_y': y}
        """
        async with get_semaphore():
            res = await run_in_threadpool(get_ocr().slide_match, target, background, True)
            return transform_slide_result(res)


captcha_service = CaptchaService()
