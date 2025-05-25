from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict
import jieba
import jieba.posseg as pseg
import re
from pathlib import Path
import jieba.analyse


# 初始化FastAPI应用
app = FastAPI(
    title="文本信息抽取API",
    description="从文本中提取实体、关键词和关系",
    version="1.0.0"
)

# 安全加载自定义词典
custom_dict = Path("userdict.txt")
if not custom_dict.exists():
    # 创建默认词典文件（示例内容）
    default_words = ["阿里巴巴 10 nt", "腾讯 10 nt", "新冠病毒 10 nz"]
    custom_dict.write_text("\n".join(default_words), encoding="utf-8")
jieba.load_userdict(str(custom_dict))

# 数据模型定义
class EntityItem(BaseModel):
    type: str  # 实体类型
    value: str  # 实体内容
    start_pos: int  # 起始位置
    end_pos: int  # 结束位置

class TextRequest(BaseModel):
    text: str
    domain: str = "general"

class ExtractResponse(BaseModel):
    text: str
    domain: str
    entities: List[EntityItem]
    keywords: List[str]
    relations: List[Dict]

# 根路径
@app.get("/", summary="服务状态检查")
def home():
    return {
        "status": "running",
        "docs": {
            "Swagger UI": "/docs",
            "ReDoc": "/redoc"
        },
        "endpoints": {
            "文本抽取": {
                "path": "/extract",
                "method": "POST",
                "sample_request": {
                    "text": "示例文本",
                    "domain": "general"
                }
            }
        }
    }

# 核心抽取函数
def extract_info_from_text(text: str, domain: str) -> Dict:
    """文本信息抽取核心逻辑"""
    entities = []
    words = pseg.cut(text)
    
    # 实体识别
    for word, flag in words:
        entity_type = None
        if flag == 'nr':
            entity_type = "person"
        elif flag == 'ns':
            entity_type = "location"
        elif flag == 'nt' or '公司' in word:
            entity_type = "organization"
        
        if entity_type:
            start = text.find(word)
            entities.append({
                "type": entity_type,
                "value": word,
                "start_pos": start,
                "end_pos": start + len(word)
            })
    
    # 日期识别
    for match in re.finditer(r'\d{4}年\d{1,2}月\d{1,2}日', text):
        entities.append({
            "type": "date",
            "value": match.group(),
            "start_pos": match.start(),
            "end_pos": match.end()
        })
    
    # 关键词提取
    keywords = jieba.analyse.extract_tags(text, topK=5)
    
    # 简单关系抽取
    relations = []
    if len(entities) >= 2 and domain == "general":
        relations.append({
            "subject": entities[0]["value"],
            "predicate": "关联",
            "object": entities[1]["value"]
        })
    
    return {
        "entities": entities,
        "keywords": keywords,
        "relations": relations
    }

# 文本抽取接口
@app.post(
    "/extract",
    response_model=ExtractResponse,
    summary="文本信息抽取",
    responses={
        200: {"description": "成功返回抽取结果"},
        422: {"description": "请求参数验证失败"},
        500: {"description": "服务器内部错误"}
    }
)
async def extract_info(
    request: TextRequest = Body(..., examples={
        "general": {
            "summary": "通用领域示例",
            "value": {
                "text": "马云在1999年于杭州创立了阿里巴巴集团",
                "domain": "general"
            }
        },
        "business": {
            "summary": "商业领域示例",
            "value": {
                "text": "腾讯股价今日上涨5%至450港元",
                "domain": "business"
            }
        }
    })
):
    try:
        result = extract_info_from_text(request.text, request.domain)
        return {
            "text": request.text,
            "domain": request.domain,
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理失败: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True
    )