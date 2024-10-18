# Real Goats Bot Telegram Automation Script

GoatsBot is an automation script for completing missions, checking in, and spinning the slot machine on the Real Goats Bot Telegram. This script handles multiple accounts, automates login, mission completion, and daily check-ins.

[YOUTUBE CHANNEL](https://youtube.com/@d4rkcipherx) 

## Features
- **Watching Ads**: Every 5 minutes automatically watching ads to earn + 500 GOATS `NEW`
- **Automated Login**: Logs in automatically using account details.
- **Mission Completion**: Completes available missions and collects rewards.
- **Daily Check-in**: Checks in daily and collects rewards.
- **Slot Machine**: Spins the slot machine if coins are available.
- **Multi-account Support**: Automates For multiple accounts listed in `data.txt`.
- **Enable Proxies**: To use proxies, set `use_proxies` to `true` in `config.json`.

## Requirements

- Python 3.7+
- `aiohttp` for asynchronous HTTP requests
- `colorama` for colored output
- Other dependencies listed in `requirements.txt`

## Setup and Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/D4rkChiperX/Goats.git
cd Goats
```
**Create a virtual environment (optional but recommended)**

 ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
 ```
### Step 2: Install dependencies
You can install the required packages by running the following command:

```bash
pip install -r requirements.txt
```

### Step 3: Configure accounts
Create a `data.txt` file in the root directory.
Add Telegram authentication data for each account on a new line:

1. Use PC/Laptop or Use USB Debugging Phone
2. open the `real goats bot`
3. Inspect Element `(F12)` on the keyboard
4. at the top of the choose "`Application`" 
5. then select "`Session Storage`" 
6. Select the links "`dev.goatsbot.xyz`" and "`tgWebAppData`"
7. Take the value part of "`tgWebAppData`"
8. take the part that looks like this: 

```txt 
query_id=xxxxxxxxx-1
query_id=xxxxxxxxx-2
query_id=xxxxxxxxx-3
```
9. Decode query_id= with https://www.urldecoder.org/
10. add it to `data.txt` file or create it if you dont have one

### Step 4: Modify Configurations (Optional)
The `config.json` file allows you to modify script settings:
account_delay: Time (in seconds) between account operations.
looping: Time (in seconds) before starting a new loop of account runs.

### Configuration
You can adjust the bot's behavior via config.json:

```json
{
    "use_proxies": false,
    "account_delay": 5,
    "looping": 3800
  }  
```
`account_delay`: Delay in seconds between switching accounts.
`looping`: Time in seconds to wait before running all accounts again.

### Format of proxies.txt
The proxies.txt file should contain one proxy per line in the following format:

```ruby
username:password@ip:port
username:password@ip:port
```

### Step 5: Run the script
To start the bot, run:

```bash
python main.py
```

### Additional Information
`The script` uses asyncio for asynchronous operations to handle multiple tasks concurrently.
`Error handling` is implemented to gracefully manage login and mission completion failures.
Proxy Format The proxies should be listed in a `proxies.txt` file with the format `username:password@ip:port`, one proxy per line.
Random Proxy Assignment The script will assign a proxy from the list for each account.


## License
This project is licensed under the MIT License - see the LICENSE file for details.


