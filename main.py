import asyncio
from loguru import logger

from utils_accs import get_accounts
from modules.initia_xyz import start_accounts_for_of_site_faucet

async def start(module: str):
    accounts = get_accounts()
    logger.info(f'Загрузил {len(accounts)} аккаунтов')

    if module == 'of_site_faucet':
        logger.info('Start Of.site Faucet module')
        await start_accounts_for_of_site_faucet(accounts)

if __name__ == '__main__':
    action = int(input('\n1. Of site Faucet'
                        '\nSelect module: '))
    if action == 1:
        of_site_action = int(input('\n1. Faucet'
                                    '\nSelect action: '))
        if of_site_action == 1:
            asyncio.run(start('of_site_faucet'))
        

