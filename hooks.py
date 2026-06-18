"""插件生命周期 hook：启动预热模型 / 关闭释放"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.plugin.ddddocr_server.core import dispose_models, load_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """startup 预热加载（启动慢 1-3s，常驻内存 ~100-200MB）；shutdown 释放。"""
    # startup
    load_models()
    yield
    # shutdown
    dispose_models()
