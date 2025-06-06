# 文本信息抽取API服务

基于 FastAPI 构建的中文文本信息抽取系统，支持实体识别、关键词提取和关系发现，提供标准化 RESTful API 接口。

## 功能特性

- **多类型实体识别**  
  支持人名、地点、组织机构、日期等实体自动提取。
- **领域自适应**  
  通过自定义词典支持医疗、金融等垂直领域。
- **开箱即用**  
  内置自动生成交互式 API 文档（Swagger / ReDoc）。
- **高性能**  
  单请求平均处理时间 <100ms（视具体硬件环境而定）。

## 技术栈

| 组件     | 用途           |
|----------|----------------|
| FastAPI  | API 服务框架   |
| Jieba    | 中文分词与词性标注 |
| Pydantic | 数据模型验证   |
| Uvicorn  | ASGI 服务器    |

## 快速开始

### 安装依赖
```bash
pip install fastapi uvicorn jieba pydantic
