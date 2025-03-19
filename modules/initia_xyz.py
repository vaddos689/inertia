import asyncio
import random
from loguru import logger
from utils_accs import write_result
from eth_account.messages import encode_defunct
from eth_account import Account

from general_settings import semaphore, CAPSOLVER_API_KEY, RANDOM_PAUSE_BETWEEN_ACCOUNTS
from config import CAPTCHA_SITE_KEY
from modules.client import Client
from modules.captcha.capsolver import Capsolver


class InitiaXYZ:
    def __init__(self, account) -> None:
        self.account = account
        self.id = account['id']
        self.private_key = account['private_key']
        self.proxy = account['proxy']
        self.faucet_address = account['address']
        self.client = Client(self.id, self.private_key, self.proxy)
        self.account_eth = Account().from_key(self.private_key)
        self.captcha_site_key = CAPTCHA_SITE_KEY

    async def solve_captcha(self, url: str):
        capsolver = Capsolver(CAPSOLVER_API_KEY, self.client)
        cf_result = await capsolver.solve_turnstile(self.captcha_site_key, url)
        return cf_result
    
    async def faucet(self):        
        faucet_url = "https://app.testnet.initia.xyz/faucet"

        cf_result = await self.solve_captcha(url=faucet_url)
        if cf_result:
            logger.info(f'[{self.id}] [{self.faucet_address}] Successfully solved captcha')
        
        url = 'https://faucet-api.testnet.initia.xyz/claim'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://app.testnet.initia.xyz',
            'referer': 'https://app.testnet.initia.xyz/'
        }

        payload = {
            'address': self.faucet_address,
            'turnstile_response': cf_result
        }
        response = await self.client.session.post(url, headers=headers, json=payload)

        if response.status == 400:
            logger.error(f'[{self.id}] [{self.faucet_address}] exceed request limit')
            write_result(f'{self.faucet_address} INITIA_FAUCET EXCEED_REQUEST_LIMIT\n')
            return
        
        r = await response.json()

        if r['response']['tx_response']['txhash']:
            tx_hash = r['response']['tx_response']['txhash']
            logger.success(f'[{self.id}] [{self.faucet_address}] Faucet success: {tx_hash}')
            write_result(f'{self.faucet_address} INITIA_FAUCET {tx_hash}\n' )

        else:
            logger.error(f'[{self.id}] [{self.faucet_address}] Faucet error: {r}')
            write_result(f'{self.faucet_address} INITIA_FAUCET ERROR\n')
        
        sleep_time = random.randint(RANDOM_PAUSE_BETWEEN_ACCOUNTS[0], RANDOM_PAUSE_BETWEEN_ACCOUNTS[1])
        logger.info(f'[{self.id}] [{self.faucet_address}] Sleep {sleep_time} seconds before next account...')
        await asyncio.sleep(sleep_time)

async def start_module(account):
    async with semaphore:
        initia_xyz = InitiaXYZ(account)
        logger.info(f'Start [{initia_xyz.id}] account')
        await initia_xyz.faucet()
        await initia_xyz.client.session.close()


async def start_accounts_for_of_site_faucet(accounts):
    task = []
    for account in accounts:
        task.append(asyncio.create_task(start_module(account)))

    await asyncio.gather(*task)
    logger.success('All accounts processed')
