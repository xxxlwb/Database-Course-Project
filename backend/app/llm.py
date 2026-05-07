import json
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from .config import settings

log = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.use_mock = settings.llm_mock or not settings.minimax_api_key
        if not self.use_mock:
            self.client = OpenAI(
                api_key=settings.minimax_api_key,
                base_url=settings.minimax_base_url,
            )

    def chat_json(self, system: str, user: str, mock_fallback: dict) -> dict:
        """Return JSON dict from LLM; on mock or failure, return mock_fallback."""
        if self.use_mock:
            log.info("LLM mock mode")
            return mock_fallback
        try:
            resp = self.client.chat.completions.create(
                model=settings.minimax_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            txt = resp.choices[0].message.content or "{}"
            return json.loads(txt)
        except Exception as e:
            log.warning(f"LLM call failed, using mock: {e}")
            return mock_fallback


llm = LLMClient()


# Helpers ----------------------------------------------------------

COG_MAP_SYSTEM = """你是知识抽取助手。给定一段文档文本，输出 JSON：
{
  "summary": "<200字摘要>",
  "key_entities": [{"name": "...", "type": "person|project|task|concept|decision|event|place|other"}],
  "themes": ["主题词", ...],
  "timeline": [{"time": "...", "event": "..."}],
  "structural_patterns": ["..."]
}
"""

EXTRACT_SYSTEM = """你是知识抽取助手。给定一段文本和已知实体清单，抽取 JSON：
{
  "entities": [{"name": "...", "type": "person|project|task|concept|decision|event|place|other"}],
  "relationships": [{"source": "...", "target": "...", "type": "...", "description": "..."}]
}
只抽取文本中明确提到的实体和关系，不要编造。
"""


def gen_cognitive_map(content: str) -> Dict[str, Any]:
    return llm.chat_json(
        COG_MAP_SYSTEM,
        f"文档内容：\n{content[:3000]}",
        mock_fallback={
            "summary": content[:200],
            "key_entities": [],
            "themes": [],
            "timeline": [],
            "structural_patterns": [],
        },
    )


def gen_extraction(content: str, known_entities: List[str]) -> Dict[str, Any]:
    return llm.chat_json(
        EXTRACT_SYSTEM,
        f"已知实体：{json.dumps(known_entities, ensure_ascii=False)}\n\n文本：\n{content[:3000]}",
        mock_fallback={"entities": [], "relationships": []},
    )
