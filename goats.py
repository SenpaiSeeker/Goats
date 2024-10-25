import json
import time
import requests
import logging
from datetime import datetime, timedelta

class Goats:
    def __init__(self):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "Origin": "https://dev.goatsbot.xyz",
            "Referer": "https://dev.goatsbot.xyz/",
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

    def log(self, msg, level='info'):
        if level == 'success':
            logging.info(msg)
        elif level == 'error':
            logging.error(msg)
        elif level == 'warning':
            logging.warning(msg)
        elif level == 'custom':
            logging.info(msg)
        else:
            logging.info(msg)

    async def countdown(self, seconds):
        for i in range(seconds, -1, -1):
            print(f"===== Waiting {i} seconds to continue loop =====", end='\r')
            await asyncio.sleep(1)
        print('')

    async def login(self, raw_data):
        url = "https://dev-api.goatsbot.xyz/auth/login"
        user_data = json.loads(raw_data.split('user=')[1].split('&')[0])

        try:
            response = requests.post(url, headers={**self.headers, 'Rawdata': raw_data})

            if response.status_code == 201:
                data = response.json()
                age = data['user']['age']
                balance = data['user']['balance']
                access_token = data['tokens']['access']['token']
                return {'success': True, 'data': {'age': age, 'balance': balance, 'accessToken': access_token}, 'userData': user_data}
            return {'success': False, 'error': 'Login failed'}
        except Exception as error:
            return {'success': False, 'error': f'Error during login: {str(error)}'}

    async def get_missions(self, access_token):
        url = "https://api-mission.goatsbot.xyz/missions/user"
        try:
            response = requests.get(url, headers={**self.headers, 'Authorization': f'Bearer {access_token}'})

            if response.status_code == 200:
                missions = {'special': [], 'regular': []}
                for category, mission_list in response.json().items():
                    for mission in mission_list:
                        if category == 'SPECIAL MISSION':
                            missions['special'].append(mission)
                        elif not mission['status']:
                            missions['regular'].append(mission)
                return {'success': True, 'missions': missions}
            return {'success': False, 'error': 'Failed to get missions'}
        except Exception as error:
            return {'success': False, 'error': f'Error fetching missions: {str(error)}'}

    async def complete_mission(self, mission, access_token):
        if mission['type'] == 'Special':
            now = int(datetime.now().timestamp())
            if mission.get('next_time_execute') and now < mission['next_time_execute']:
                time_left = mission['next_time_execute'] - now
                self.log(f'Mission {mission["name"]} is in cooldown: {time_left} seconds', 'warning')
                return False

        url = f"https://dev-api.goatsbot.xyz/missions/action/{mission['_id']}"
        try:
            response = requests.post(url, headers={**self.headers, 'Authorization': f'Bearer {access_token}'})
            return response.status_code == 201
        except Exception:
            return False

    async def handle_missions(self, access_token):
        missions_result = await self.get_missions(access_token)
        if not missions_result['success']:
            self.log(f'Unable to fetch missions: {missions_result["error"]}', 'error')
            return

        special_missions = missions_result['missions']['special']
        regular_missions = missions_result['missions']['regular']

        for mission in special_missions:
            self.log(f'Processing special mission: {mission["name"]}', 'info')
            result = await self.complete_mission(mission, access_token)
            if result:
                self.log(f'Successfully completed mission {mission["name"]} | Reward: {mission["reward"]}', 'success')
            else:
                self.log(f'Failed to complete mission {mission["name"]}', 'error')

        for mission in regular_missions:
            result = await self.complete_mission(mission, access_token)
            if result:
                self.log(f'Successfully completed mission {mission["name"]} | Reward: {mission["reward"]}', 'success')
            else:
                self.log(f'Failed to complete mission {mission["name"]}', 'error')
            await asyncio.sleep(1)

    async def get_checkin_info(self, access_token):
        url = "https://api-checkin.goatsbot.xyz/checkin/user"
        try:
            response = requests.get(url, headers={**self.headers, 'Authorization': f'Bearer {access_token}'})

            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': 'Failed to get check-in info'}
        except Exception as error:
            return {'success': False, 'error': str(error)}

    async def perform_checkin(self, checkin_id, access_token):
        url = f"https://api-checkin.goatsbot.xyz/checkin/action/{checkin_id}"
        try:
            response = requests.post(url, headers={**self.headers, 'Authorization': f'Bearer {access_token}'})
            return response.status_code == 201
        except Exception:
            return False

    async def handle_checkin(self, access_token):
        try:
            checkin_info = await self.get_checkin_info(access_token)
            if not checkin_info['success']:
                self.log(f'Unable to fetch check-in info: {checkin_info["error"]}', 'error')
                return

            result = checkin_info['data']
            last_checkin_time = result['lastCheckinTime']
            current_time = datetime.now().timestamp()
            time_since_last_checkin = current_time - last_checkin_time
            twenty_four_hours = 24 * 60 * 60

            if time_since_last_checkin < twenty_four_hours:
                self.log('Not enough time since last check-in', 'warning')
                return

            next_checkin = next((day for day in result['result'] if not day['status']), None)
            if not next_checkin:
                self.log('All check-in days completed', 'custom')
                return

            checkin_result = await self.perform_checkin(next_checkin['_id'], access_token)
            if checkin_result:
                self.log(f'Successfully checked in on day {next_checkin["day"]} | Reward: {next_checkin["reward"]}', 'success')
            else:
                self.log(f'Failed to check in on day {next_checkin["day"]}', 'error')
        except Exception as error:
            self.log(f'Error handling check-in: {str(error)}', 'error')

    async def main(self):
        data_file = 'data.txt'
        with open(data_file, 'r', encoding='utf-8') as file:
            data = [line.strip() for line in file.readlines() if line.strip()]

        while True:
            for i, init_data in enumerate(data):
                user_data = json.loads(init_data.split('user=')[1].split('&')[0])
                user_id = user_data['id']
                first_name = user_data['first_name']

                print(f"========== Account {i + 1} | {first_name} ==========")
                login_result = await self.login(init_data)
                if not login_result['success']:
                    self.log(f'Login failed for {first_name}: {login_result["error"]}', 'error')
                    continue

                self.log('Login successful!', 'success')
                access_token = login_result['data']['accessToken']

                await self.handle_checkin(access_token)
                await self.handle_missions(access_token)

                self.log('Waiting for next account...', 'warning')
                await self.countdown(60)  # Wait for 60 seconds before the next loop

if __name__ == "__main__":
    import asyncio
    goats = Goats()
    asyncio.run(goats.main())
