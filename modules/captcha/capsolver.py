import asyncio
from typing import Optional
from loguru import logger
from modules.client import Client


class Capsolver:
    def __init__(
        self,
        api_key: str,
        client: Client = None,
    ):
        self.api_key = api_key
        self.base_url = "https://api.capsolver.com"
        self.client = client
        self.proxy = self.client.proxy_init
        self.session = self.client.session

    def _format_proxy(self, proxy: str) -> str:
        if not proxy:
            return None
        if "@" in proxy:
            return proxy
        return proxy

    async def create_task(
        self,
        sitekey: str,
        pageurl: str,
        invisible: bool = False,
    ) -> Optional[str]:
        """Создает задачу на решение капчи"""
        data = {
            "clientKey": self.api_key,
            "appId": "0F6B2D90-7CA4-49AC-B0D3-D32C70238AD8",
            "task": {
                "type": "ReCaptchaV2Task",
                "websiteURL": pageurl,
                "websiteKey": sitekey,
                "isInvisible": False,
                # "pageAction": "drip_request",
            },
        }

        if self.proxy:
            data["task"]["proxy"] = self.proxy

        try:
            response = await self.session.post(
                f"{self.base_url}/createTask",
                json=data,
                timeout=30,
            )
            result = response.json()

            if "taskId" in result:
                return result["taskId"]

            logger.error(f"Error creating task: {result}")
            return None

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def get_task_result(self, task_id: str) -> Optional[str]:
        """Получает результат решения капчи"""
        data = {"clientKey": self.api_key, "taskId": task_id}

        max_attempts = 30
        for _ in range(max_attempts):
            try:
                response = await self.session.post(
                    f"{self.base_url}/getTaskResult",
                    json=data,
                    timeout=30,
                )
                result = await response.json()

                if result.get("status") == "ready":
                    # Handle both reCAPTCHA and Turnstile responses
                    solution = result.get("solution", {})
                    return solution.get("token") or solution.get("gRecaptchaResponse")
                elif "errorId" in result and result["errorId"] != 0:
                    logger.error(f"Error getting result: {result}")
                    return None

                await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"Error getting result: {e}")
                return None

        return None

    async def solve_recaptcha(
        self,
        sitekey: str,
        pageurl: str,
        invisible: bool = False,
    ) -> Optional[str]:
        """Решает RecaptchaV2 и возвращает токен"""
        task_id = await self.create_task(sitekey, pageurl, invisible)
        if not task_id:
            return None

        return await self.get_task_result(task_id)

    async def create_turnstile_task(
        self,
        sitekey: str,
        pageurl: str,
        action: Optional[str] = None,
        cdata: Optional[str] = None,
    ) -> Optional[str]:
        """Creates a Turnstile captcha solving task"""
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "AntiTurnstileTaskProxyLess",
                "websiteURL": pageurl,
                "websiteKey": sitekey,
            },
        }

        # if action or cdata:
        #     metadata = {}
        #     if action:
        #         metadata["action"] = action
        #     if cdata:
        #         metadata["cdata"] = cdata
        #     data["task"]["metadata"] = metadata

        try:
            response = await self.session.post(
                f"{self.base_url}/createTask",
                json=data,
                timeout=30,
            )
            result = await response.json()

            if "taskId" in result:
                return result["taskId"]

            logger.error(f"Error creating Turnstile task: {result}")
            return None

        except Exception as e:
            logger.error(f"Error creating Turnstile task: {e}")
            return None

    async def solve_turnstile(
        self,
        sitekey: str,
        pageurl: str,
        action: Optional[str] = None,
        cdata: Optional[str] = None,
    ) -> Optional[str]:
        """Solves Cloudflare Turnstile captcha and returns token"""
        task_id = await self.create_turnstile_task(
            sitekey=sitekey,
            pageurl=pageurl,
            action=action,
            cdata=cdata,
        )
        if not task_id:
            return None

        return await self.get_task_result(task_id)