import asyncio
from api.gatherer import OsuDataFetcher

if __name__ == "__main__":
    asyncio.run(OsuDataFetcher().run())