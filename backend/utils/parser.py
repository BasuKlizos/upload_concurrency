import asyncio

async def parse_text(text):
    await asyncio.sleep(0.3)
    return {"parsed": text}
