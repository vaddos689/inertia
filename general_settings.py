import asyncio

CAPSOLVER_API_KEY = 'CAP-900BBF35FC6AFAD7B112FF78AB4557DB1F1295AAE1D2124A5CA4CEE32E934461'

ACCOUNTS_RANGE = [21, 21]  # from 1 to ... (if 0, 0 then all accounts)

RANDOM_PAUSE_BETWEEN_ACCOUNTS = [5, 15]

semaphore = asyncio.Semaphore(1) # number of simultaneously working accounts