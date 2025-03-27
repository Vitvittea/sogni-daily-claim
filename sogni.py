# -*- coding: utf-8 -*-
import requests
import time
import json

TOKEN_FILE = 'token.txt'
CLAIM_ENDPOINT = 'https://api.sogni.ai/v2/account/reward/claim'
REWARD_ENDPOINT = 'https://api.sogni.ai/v2/account/rewards'
DAILY_BOOST_ID = '2'
CHECK_INTERVAL_MINUTES = 60
CHECK_INTERVAL_SECONDS = CHECK_INTERVAL_MINUTES * 60

def print_banner():
    print('=' * 50)
    print('      Auto Claim Daily Bot - BILAL STUDIO    ')
    print('=' * 50)

def get_token():
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f'Error reading token file: {e}')
        exit(1)

def check_reward_status(token):
    headers = {
        'accept': '*/*',
        'authorization': token,
        'content-type': 'application/json',
        'Referer': 'https://app.sogni.ai/'
    }
    try:
        response = requests.get(REWARD_ENDPOINT, headers=headers)
        response_data = response.json()

        if response.status_code == 401:
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Invalid token. Please check your token.')
            return False

        if response_data.get('status') == 'success':
            rewards = response_data['data']['rewards']
            daily_boost = next((r for r in rewards if r['id'] == DAILY_BOOST_ID), None)
            
            if daily_boost and daily_boost.get('canClaim') == 1:
                return True

            if daily_boost and 'lastClaimTimestamp' in daily_boost and 'claimResetFrequencySec' in daily_boost:
                next_available_time = (daily_boost['lastClaimTimestamp'] + daily_boost['claimResetFrequencySec']) * 1000
                time_until_available = next_available_time - time.time() * 1000
                if time_until_available > 0:
                    hours = int(time_until_available / (60 * 60 * 1000))
                    minutes = int((time_until_available % (60 * 60 * 1000)) / (60 * 1000))
                    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Next claim available in {hours} hours {minutes} minutes.')
        return False
    except Exception as e:
        print(f'Error checking reward status: {e}')
        return False

def claim_daily_boost(token):
    headers = {
        'accept': '*/*',
        'authorization': token,
        'content-type': 'application/json',
        'Referer': 'https://app.sogni.ai/'
    }
    data = json.dumps({'claims': [DAILY_BOOST_ID]})
    try:
        response = requests.post(CLAIM_ENDPOINT, headers=headers, data=data)
        response_data = response.json()
        if response_data.get('status') == 'success':
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Daily boost claimed successfully!')
            return True
        else:
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Failed to claim daily boost:', response_data)
    except Exception as e:
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Error claiming daily boost: {e}')
    return False

def check_and_claim():
    while True:
        token = get_token()
        if check_reward_status(token):
            claim_daily_boost(token)
        else:
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Daily boost not available for claiming yet.')
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    print_banner()
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Starting Daily Boost Claim Bot...')
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Bot will check for rewards every {CHECK_INTERVAL_MINUTES} minutes.')
    check_and_claim()

