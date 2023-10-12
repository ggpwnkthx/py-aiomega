from aiomega.aiomega import AsyncMegaApi
from aiomega.mega import MegaAccountDetails
import asyncio, os, logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s\t%(asctime)s (%(threadName)-10s) %(message)s",
)

async def main():
    async with AsyncMegaApi(
        email=os.getenv("mega_email"), password=os.getenv("mega_password")
    ) as mega:
        ad: MegaAccountDetails = (
            await mega.getAccountDetails()
        ).getMegaAccountDetails()
        logging.info(
            "Storage: {} of {} ({} %)".format(
                ad.getStorageUsed(),
                ad.getStorageMax(),
                100 * ad.getStorageUsed() / ad.getStorageMax(),
            )
        )

asyncio.run(main())