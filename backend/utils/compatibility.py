import asyncio

async def get_analysis(parsed_cv):
    await asyncio.sleep(0.2)
    return {
        "analysis": "compatibility result"
    }
