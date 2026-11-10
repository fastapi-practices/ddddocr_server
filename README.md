# ddddocr_server

基于 [ddddocr](https://github.com/sml2h3/ddddocr) 的本地验证码识别插件，提供文本识别、点选目标检测和滑块缺口匹配能力

## 插件类型

- 应用级插件

## 使用方式

1. 安装并启用插件后，重启后端服务
2. 提交待识别图片，获取对应的验证码识别结果
3. 部署环境需使用 glibc 基础镜像，Alpine/musl 不兼容 onnxruntime
4. 插件依赖变更后需重新构建镜像

## 卸载说明

- 卸载插件后，移除业务中的验证码识别调用
- 重新构建镜像以移除 ddddocr 相关依赖

## 联系方式

- 作者：`david`
- 反馈方式：提交 Issue 或 PR
