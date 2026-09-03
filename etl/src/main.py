import asyncio
from core.database import db
from downloaders.download_data import Download
async def main():
    downloader = Download()
    try:
        await downloader.download_data()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())