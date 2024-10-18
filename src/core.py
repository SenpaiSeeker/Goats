import os
import json
import random
import asyncio
from colorama import init, Fore, Style
from datetime import datetime
from urllib.parse import unquote
from json.decoder import JSONDecodeError
from aiohttp import ClientSession
from src.utils import read_config, countdown_timer, _clear

init(autoreset=True)
config = read_config()

class GoatsBot:
    def __init__(self, tg_auth_data: str, proxy: dict = None) -> None:
        self.proxy = proxy
        self.auth_data = tg_auth_data
        self.access_token = None
        self.access_token_expiry = 0
        userdata = self.extract_user_data(tg_auth_data)
        self.user_id = userdata.get("id")

    def create_session(self) -> ClientSession:
        return ClientSession()

    def get_proxy_url(self) -> str:
        if self.proxy:
            return f"http://{self.proxy['username']}:{self.proxy['password']}@{self.proxy['host']}:{self.proxy['port']}"
        return None

    @staticmethod
    def extract_user_data(auth_data: str) -> dict:
        try:
            return json.loads(unquote(auth_data).split("user=")[1].split("&auth")[0])
        except (IndexError, JSONDecodeError):
            return {}

    @staticmethod
    def decode_json(text: str) -> dict:
        try:
            return json.loads(text)
        except JSONDecodeError:
            return {"error": "Error decoding to JSON", "text": text}

    @staticmethod
    def get_proxies() -> list:
        proxies = []
        try:
            with open("proxies.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        username, password_host = line.strip().split(':', 1)
                        password, host_port = password_host.split('@')
                        host, port = host_port.split(':')
                        proxies.append({
                            "username": username,
                            "password": password,
                            "host": host,
                            "port": port
                        })
        except FileNotFoundError:
            print("Proxies file not found!")
        return proxies

    async def login(self, session) -> bool:
        proxy_url = self.get_proxy_url()
        headers = {
            "Rawdata": self.auth_data,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        async with session.post(
            "https://dev-api.goatsbot.xyz/auth/login",
            data={},
            headers=headers,
            proxy=proxy_url
        ) as resp:
            resp_text = await resp.text()
            try:
                resp_json = self.decode_json(resp_text)
            except Exception as e:
                return False
            if resp_json.get("statusCode"):
                print(Fore.RED + f"Error while logging in | {resp_json['message']}" + Style.RESET_ALL)
                return False

            access_token = resp_json["tokens"]["access"]["token"]
            self.access_token = access_token
            self.access_token_expiry = int(datetime.fromisoformat(resp_json["tokens"]["access"]["expires"].replace("Z", "+00:00")).timestamp())
            return True

    async def refresh_token(self, session) -> bool:
        token_data = await self.get_local_token(self.user_id)
        if not token_data:
            return False
        url = 'https://dev-api.goatsbot.xyz/auth/refresh-tokens'
        async with session.post(url, json={"refreshToken": token_data}) as resp:
            resp_json = json.loads(await resp.text())
            if resp_json.get("statusCode"):
                print(Fore.RED + f"Error refreshing token | {resp_json['message']}" + Style.RESET_ALL)
                return False

            access_token = resp_json["tokens"]["access"]["token"]
            refresh_token = resp_json["tokens"]["refresh"]["token"]
            self.access_token_expiry = int(datetime.fromisoformat(resp_json["tokens"]["access"]["expires"].replace("Z", "+00:00")).timestamp())
            await self.save_local_token(self.user_id, refresh_token)
            print(Fore.GREEN + "Token refreshed successfully." + Style.RESET_ALL)
            return True

    async def user_data(self, session) -> dict:
        if not self.access_token:
            if not await self.login(session):
                print(Fore.RED + "Failed to log in." + Style.RESET_ALL)
                return {}

        if await self.is_token_expired():
            if not await self.refresh_token(session):
                if not await self.login(session):
                    print(Fore.RED + "Failed to log in after token refresh." + Style.RESET_ALL)
                    return {}
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            async with session.get("https://api-me.goatsbot.xyz/users/me", headers=headers) as resp:
                content_type = resp.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    resp_text = await resp.text()
                    print(Fore.RED + f"Unexpected content type: {content_type}, Response text: {resp_text}" + Style.RESET_ALL)
                    return {}

                resp_json = await resp.json()
                if resp_json.get("statusCode"):
                    print(Fore.RED + f"Error getting profile data | {resp_json['message']}" + Style.RESET_ALL)
                    return {}

                return resp_json

        except Exception as e:
            print(Fore.RED + f"Exception while getting user data: {e}" + Style.RESET_ALL)
            return {}

    async def is_token_expired(self) -> bool:
        now = round(datetime.now().timestamp())
        return now >= self.access_token_expiry

    async def get_local_token(self, userid):
        if not os.path.exists("tokens.json"):
            open("tokens.json", "w").write(json.dumps({}))
        tokens = json.loads(open("tokens.json", "r").read())
        return tokens.get(str(userid))

    async def save_local_token(self, userid, token):
        tokens = json.loads(open("tokens.json", "r").read())
        tokens[str(userid)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

    async def watch_and_claim(self, session, account_number) -> bool:
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        watch_time = random.randint(16, 17)
        print(Fore.CYAN + f"[Account {account_number}] Watching ads for {watch_time} seconds..." + Style.RESET_ALL)
        ad_url = f"https://api.adsgram.ai/adv?blockId=2373&tg_id={self.user_id}&tg_platform=android&platform=Linux+aarch64&language=id"
        async with session.get(ad_url, headers=headers) as resp:
            resp = self.decode_json(await resp.text())

        if resp.get("statusCode"):
            print(Fore.RED + f"[Account {account_number}] Error watching ad | {resp['message']}" + Style.RESET_ALL)
            return False

        await countdown_timer(watch_time)

        mission_id = "66db47e2ff88e4527783327e"
        verify_url = f"https://dev-api.goatsbot.xyz/missions/action/{mission_id}"

        async with session.post(verify_url, headers=headers) as verify_resp:
            verify_resp = self.decode_json(await verify_resp.text())

        if verify_resp.get("status") == "success":
            print(Fore.GREEN + f"[Account {account_number}] Watching ads reward +200" + Style.RESET_ALL)
            return True
        else:
            print(Fore.RED + f"[Account {account_number}] Ads verification failed." + Style.RESET_ALL)
            return False

    async def complete_all_tasks(self, session, account_number):
        user_data = await self.user_data(session)
        if user_data:
            print(Fore.CYAN + f"[Account {account_number}] Username: {user_data.get('user_name')}" + Style.RESET_ALL)
            print(Fore.CYAN + f"[Account {account_number}] Balance: {user_data.get('balance')}" + Style.RESET_ALL)
            print(Fore.CYAN + f"[Account {account_number}] Telegram Age: {user_data.get('age')} years" + Style.RESET_ALL)

    async def run(self, option, account_number):
        async with self.create_session() as session:
            if not await self.login(session):
                return

            if option == '1':
                await self.watch_and_claim(session, account_number)
            elif option == '2':
                await self.complete_all_tasks(session, account_number)

async def main():
    print(Fore.YELLOW + "Select an option:" + Style.RESET_ALL)
    print(Fore.YELLOW + "1. Watch Ads & Claim" + Style.RESET_ALL)
    print(Fore.YELLOW + "2. Original Default Script" + Style.RESET_ALL)
    option = input(Fore.YELLOW + "Enter 1 or 2: " + Style.RESET_ALL).strip()

    if option not in ['1', '2']:
        print(Fore.RED + "Invalid option. Exiting..." + Style.RESET_ALL)
        return

    loop = config.get('looping', 3800)
    proxies_enabled = config.get('use_proxies', False)
    proxies = GoatsBot.get_proxies() if proxies_enabled else []

    while True:
        with open("data.txt", "r", encoding="utf-8") as file:
            accounts = [line.strip() for line in file if line.strip()]

        tasks = []
        for i, auth_data in enumerate(accounts, start=1):
            print(Fore.YELLOW + f"Account {i}/{len(accounts)}" + Style.RESET_ALL)
            print(Fore.YELLOW + "~" * 38 + Style.RESET_ALL)

            proxy = proxies[i % len(proxies)] if proxies_enabled and proxies else None

            bot = GoatsBot(auth_data.strip(), proxy=proxy)
            tasks.append(bot.run(option, i))

        await asyncio.gather(*tasks)

        print(Fore.YELLOW + "Clearing screen in 3 seconds..." + Style.RESET_ALL)
        await countdown_timer(3)
        _clear()

        await countdown_timer(loop)

if __name__ == "__main__":
    asyncio.run(main())