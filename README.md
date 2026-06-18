# ddddocr_server

基于 [ddddocr](https://github.com/sml2h3/ddddocr) 的本地验证码识别服务插件。

## 功能

- 文本验证码 OCR（`/api/v1/ddddocr/ocr`）
- 点选验证码目标检测（`/api/v1/ddddocr/click`）
- 滑块缺口距离匹配（`/api/v1/ddddocr/slide`）

每类识别都提供两种调用方式：

| 方式 | Content-Type | 说明 |
|------|--------------|------|
| 文件上传 | `multipart/form-data` | 直接上传 jpg/png，字段名 `file`（滑块为 `target` + `bg`） |
| base64 | `application/json` | 传 base64 编码字符串，支持 `data:image/png;base64,` 前缀 |

## 端点一览

| 方法 | 路径 | 入参 | 返回 data |
|------|------|------|-----------|
| POST | `/api/v1/ddddocr/ocr` | `file` (UploadFile, jpg/png) | `{"result": "识别文本"}` |
| POST | `/api/v1/ddddocr/ocr/base64` | `{"image": "<base64>"}` | `{"result": "识别文本"}` |
| POST | `/api/v1/ddddocr/click` | `file` (UploadFile, jpg/png) | `{"boxes": [[x1,y1,x2,y2], ...]}` |
| POST | `/api/v1/ddddocr/click/base64` | `{"image": "<base64>"}` | `{"boxes": [[x1,y1,x2,y2], ...]}` |
| POST | `/api/v1/ddddocr/slide` | `target` + `bg` (两个 UploadFile) | `{"target_x": x, "target_y": y}` |
| POST | `/api/v1/ddddocr/slide/base64` | `{"target": "<b64>", "bg": "<b64>"}` | `{"target_x": x, "target_y": y}` |

所有端点返回 fba 统一响应壳：`{"code": 200, "msg": "Success", "data": {...}}`。
图片格式仅支持 `image/jpeg`、`image/png`，其他类型返回 400；base64 解码失败返回 400。

## 调用示例（curl）

文本识别（base64）：

```bash
# 把图片转成 base64（去掉换行）
B64=$(base64 -w 0 captcha.png)

curl -X POST 'http://localhost:8000/api/v1/ddddocr/ocr/base64' \
  -H 'Content-Type: application/json' \
  -d "{\"image\": \"$B64\"}"
# {"code":200,"msg":"Success","data":{"result":"a1b2"}}
```

文本识别（文件上传）：

```bash
curl -X POST 'http://localhost:8000/api/v1/ddddocr/ocr' \
  -F 'file=@captcha.png'
```

滑块匹配（文件上传，target 小块 + bg 背景图）：

```bash
curl -X POST 'http://localhost:8000/api/v1/ddddocr/slide' \
  -F 'target=@slide_target.png' \
  -F 'bg=@slide_bg.png'
# {"code":200,"msg":"Success","data":{"target_x":120,"target_y":50}}
```

## 依赖

- `ddddocr`：验证码识别核心库，已正常安装。
- `onnxruntime`：随 `ddddocr` 自动装入，用于模型推理。镜像基础**必须为 glibc**（Debian/Ubuntu 系），onnxruntime **不兼容 musl/Alpine**。
- `Pillow` / `numpy`：随 ddddocr 装入。

## 架构

- 2 个 ddddocr 模型单例由插件 `hooks.py` 的 lifespan 在应用启动时预热（`ocr_ins` 做文本分类 + 滑块匹配，`det_ins` 做点选检测），常驻内存约 100-200MB。
- 所有推理通过 `run_in_threadpool` 包裹，并用 `Semaphore(8)` 限并发，**不阻塞 FastAPI 事件循环**。
- 无数据库依赖，不落库。

## 部署提醒

- `requirements.txt` 新增 `ddddocr` → **依赖发生变化，需重新 build 镜像**（`docker build → save tar → FileZilla 传到生产机 → docker load`），见 `fba_zoom/CLAUDE.md` 部署指南。
- **无 migrate SQL**（本插件不落库，部署前无需执行任何 SQL）。
- 镜像基础必须为 glibc（Debian/Ubuntu），**不可用 Alpine/musl**，否则 onnxruntime 无法运行。

## API 文档

启动后端后访问 Swagger：`http://localhost:8000/docs`，6 个端点位于「验证码识别」分组下。
