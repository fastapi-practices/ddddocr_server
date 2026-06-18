"""ddddocr 模型单例与并发基础设施"""

import asyncio
import gc

from ddddocr import DdddOcr

# 最大并发推理数，防止突发请求打满 CPU
MAX_CONCURRENT_INFER = 8

_ocr_ins: DdddOcr | None = None
_det_ins: DdddOcr | None = None
_infer_semaphore: asyncio.Semaphore = asyncio.Semaphore(MAX_CONCURRENT_INFER)


def load_models() -> None:
    """启动时预热加载两个模型单例。

    ocr_ins: 文本分类(classification) + 滑块匹配(slide_match)
    det_ins: 点选目标检测(detection)
    """
    global _ocr_ins, _det_ins
    _ocr_ins = DdddOcr(show_ad=False)
    _det_ins = DdddOcr(det=True)


def dispose_models() -> None:
    """关闭时释放模型单例。"""
    global _ocr_ins, _det_ins
    _ocr_ins = None
    _det_ins = None
    gc.collect()


def get_ocr() -> DdddOcr:
    """获取 OCR 模型实例（文本+滑块）。"""
    if _ocr_ins is None:
        raise RuntimeError('OCR 模型未就绪，请检查 lifespan 加载')
    return _ocr_ins


def get_det() -> DdddOcr:
    """获取目标检测模型实例（点选）。"""
    if _det_ins is None:
        raise RuntimeError('检测模型未就绪，请检查 lifespan 加载')
    return _det_ins


def get_semaphore() -> asyncio.Semaphore:
    """获取推理并发信号量。"""
    return _infer_semaphore
