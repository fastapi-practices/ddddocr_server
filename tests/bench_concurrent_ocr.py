# -*- coding: utf-8 -*-
"""并发测试 /api/v1/ddddocr/ocr 端点

流程：
  1. 从验证码接口下载 20 张真实验证码图（下载方式参考
     A_2026/06/ka_ai_project/plugins/kfc/verificationCode.py）。
  2. 用线程池 20 路并发上传到 /api/v1/ddddocr/ocr 识别，统计成功率、
     延迟、吞吐，并通过「串行理论耗时 vs 并发墙钟耗时」的加速比
     验证后端推理是否阻塞 FastAPI 事件循环（run_in_threadpool + Semaphore(8)）。

前置：后端需在跑（在 backend/ 下执行 `python run.py`）。
用法：
    python backend/plugin/ddddocr_server/tests/bench_concurrent_ocr.py
"""

from __future__ import annotations

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

# ===== 配置 =====
CAPTCHA_URL = "https://esp.hwwt2.com/dmisv3/system/my/captcha"
OCR_ENDPOINT = "http://127.0.0.1:8000/api/v1/ddddocr/ocr"
IMAGE_COUNT = 20
CONCURRENCY = 20
TIMEOUT = 60
ASSETS_DIR = Path(__file__).parent / "bench_assets"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)


def download_one(idx: int) -> Path | None:
    """下载一张验证码图（参考 verificationCode.update_verification_image）。"""
    token = f"{int(time.time() * 1000)}{random.randint(1, 1000)}"
    try:
        resp = requests.get(
            CAPTCHA_URL, params={'_t': token}, headers={'User-Agent': UA}, timeout=15
        )
    except requests.RequestException as e:
        print(f'  下载 {idx:02d} 失败: {e}')
        return None
    if resp.status_code != 200 or not resp.content:
        print(f'  下载 {idx:02d} 失败: status={resp.status_code} bytes={len(resp.content)}')
        return None
    path = ASSETS_DIR / f'captcha_{idx:02d}.jpg'
    path.write_bytes(resp.content)
    return path


def download_images(n: int) -> list[Path]:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    images: list[Path] = []
    for i in range(n):
        p = download_one(i)
        if p:
            images.append(p)
    return images


def call_ocr(path: Path) -> tuple[int, float, str]:
    """上传单张图到 /api/v1/ddddocr/ocr 识别，返回 (status, 耗时, 识别文本)。"""
    with path.open('rb') as f:
        files = {'file': (path.name, f, 'image/jpeg')}
        t0 = time.perf_counter()
        resp = requests.post(OCR_ENDPOINT, files=files, timeout=TIMEOUT)
        elapsed = time.perf_counter() - t0
    try:
        body = resp.json()
    except ValueError:
        body = {}
    if resp.status_code == 200:
        text = body.get('data', {}).get('result', '')
    else:
        text = body.get('msg', '')
    return resp.status_code, elapsed, text


def main() -> None:
    print(f'[1/2] 下载 {IMAGE_COUNT} 张验证码图 <- {CAPTCHA_URL}')
    images = download_images(IMAGE_COUNT)
    print(f'      成功 {len(images)} 张')
    if not images:
        print('无图片可测，退出。请检查网络/验证码源。')
        return

    print(f'[2/2] 并发 {CONCURRENCY} 路请求 -> {OCR_ENDPOINT}')
    results: list[tuple[str, int, float, str]] = []
    wall = time.perf_counter()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        future_map = {pool.submit(call_ocr, p): p for p in images}
        for fut in as_completed(future_map):
            p = future_map[fut]
            try:
                code, elapsed, text = fut.result()
            except Exception as e:  # noqa: BLE001
                code, elapsed, text = -1, 0.0, f'异常:{e}'
            results.append((p.name, code, elapsed, text))
            print(f'      {p.name}: HTTP {code}  {elapsed:.3f}s  -> {text!r}')
    wall = time.perf_counter() - wall

    ok = [r for r in results if r[1] == 200]
    fail = [r for r in results if r[1] != 200]
    lat = [r[2] for r in ok]

    print('\n========== 汇总 ==========')
    print(f'请求数: {len(results)}   成功: {len(ok)}   失败: {len(fail)}')
    print(f'并发墙钟总耗时: {wall:.3f}s   吞吐: {len(results) / wall:.2f} req/s')
    if lat:
        print(
            f'单请求延迟(成功): avg={sum(lat) / len(lat):.3f}s  '
            f'min={min(lat):.3f}s  max={max(lat):.3f}s'
        )
    if len(ok) > 1:
        serial = sum(lat)
        speedup = serial / wall if wall > 0 else 0
        print(
            f'串行理论耗时: {serial:.3f}s   并发加速比: {speedup:.2f}x  '
            f'(>>1 表示推理真并发、事件循环未阻塞)'
        )
    if fail:
        print(f'失败明细: {[(r[0], r[1], r[3]) for r in fail]}')
    print(f'识别结果: {[r[3] for r in ok]}')


if __name__ == '__main__':
    main()
