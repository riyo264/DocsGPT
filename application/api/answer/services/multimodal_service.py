import json
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from application.core.model_utils import get_api_key_for_provider
from application.core.settings import settings


def normalize_question_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Support both native fields and legacy JSON-encoded question payloads."""
    question = data.get("question", "")
    if isinstance(question, str) and question.strip().startswith("{"):
        try:
            parsed = json.loads(question)
            if isinstance(parsed, dict):
                data["question"] = parsed.get("text", data.get("question", ""))
                if not data.get("image_base64") and parsed.get("imageBase64"):
                    data["image_base64"] = parsed.get("imageBase64")
                if not data.get("image_mime_type") and parsed.get("imageMimeType"):
                    data["image_mime_type"] = parsed.get("imageMimeType")
        except json.JSONDecodeError:
            pass
    return data


def build_multimodal_message_parts(
    question: str,
    image_base64: str,
    docs_together: Optional[str] = None,
    image_mime_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    mime_type = image_mime_type or "image/png"
    message_parts: List[Dict[str, Any]] = []

    if docs_together:
        message_parts.append(
            {
                "type": "text",
                "text": "Use the following retrieved context when relevant:\n\n"
                f"{docs_together}",
            }
        )

    message_parts.append({"type": "text", "text": question})
    message_parts.append(
        {
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
        }
    )
    return message_parts


def run_multimodal_completion(
    question: str,
    image_base64: str,
    docs_together: Optional[str] = None,
    model_id: Optional[str] = None,
    image_mime_type: Optional[str] = None,
) -> str:
    llm = ChatOpenAI(
        model=model_id or "gpt-4o",
        api_key=get_api_key_for_provider("openai") or settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0,
    )

    response = llm.invoke(
        [
            SystemMessage(
                content="You are DocsGPT. Answer using provided context when available."
            ),
            HumanMessage(
                content=build_multimodal_message_parts(
                    question=question,
                    image_base64=image_base64,
                    docs_together=docs_together,
                    image_mime_type=image_mime_type,
                )
            ),
        ]
    )
    return response.content if isinstance(response.content, str) else str(response.content)
