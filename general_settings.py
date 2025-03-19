import asyncio

CAPSOLVER_API_KEY = ''

ACCOUNTS_RANGE = [21, 21]  # from 1 to ... (if 0, 0 then all accounts)

RANDOM_PAUSE_BETWEEN_ACCOUNTS = [5, 15]

semaphore = asyncio.Semaphore(1) # number of simultaneously working accounts