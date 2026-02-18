from __future__ import annotations

import asyncio
from functools import partial
from deep_translator import GoogleTranslator


async def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
) -> str:
    """Переводит текст асинхронно (оборачивает sync-вызов)."""
    if source_lang == target_lang:
        return text

    loop = asyncio.get_running_loop()
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    result = await loop.run_in_executor(
        None,
        partial(translator.translate, text),
    )
    return result or text
