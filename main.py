import asyncio
from loguru import logger

from utils_accs import get_accounts
from general_settings import ACCOUNTS_RANGE
from modules.initia_xyz import start_accounts_for_of_site_faucet

async def start(module: str):
    accounts = get_accounts()

    start_index = ACCOUNTS_RANGE[0]
    end_index = ACCOUNTS_RANGE[1]

    if start_index == 0 and end_index == 0:
        accounts_to_process = accounts
    
    elif start_index != 0 and end_index == 0:
        accounts_to_process = accounts[start_index - 1:]

    else:
        accounts_to_process = accounts[start_index - 1:end_index]

    accounts_to_process_ids = [account['id'] for account in accounts_to_process]

    print([account['id'] for account in accounts_to_process])

    logger.info(f'Загрузил {len(accounts_to_process)} аккаунтов')
    logger.info(f'Все id аккаунтов для работы: {accounts_to_process_ids}')

    if module == 'of_site_faucet':
        logger.info('Start Of.site Faucet module')
        await start_accounts_for_of_site_faucet(accounts_to_process)

if __name__ == '__main__':
    action = int(input('\n1. Of site Faucet'
                        '\nSelect module: '))
    if action == 1:
        of_site_action = int(input('\n1. Faucet'
                                    '\nSelect action: '))
        if of_site_action == 1:
            asyncio.run(start('of_site_faucet'))
