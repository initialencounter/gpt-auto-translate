import asyncio
import aiohttp
import websockets
import hashlib
import pyperclip
import openai
import json
import time
import pyautogui
from ocr import gettext, localion

# openai的apikey
apikey = 'xxx'
appid = 'xxx'
secret_key = 'xxx'


class BaiduTranslator:
    def __init__(self, appid, secret_key):
        self.appid = appid
        self.secret_key = secret_key

    async def translate(self, prompt, from_lang='en', to_lang='zh'):
        q = prompt
        salt = str(int(time.time() * 1000))
        sign = self._signature(q, salt)
        data = {
            'q': q,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('http://api.fanyi.baidu.com/api/trans/vip/translate', data=data) as resp:
                json_resp = await resp.json()

        if 'error_code' in json_resp and int(json_resp['error_code']):
            raise Exception('errorCode: ' + str(json_resp['error_code']))

        if 'trans_result' not in json_resp:
            raise Exception('invalid response')

        return json_resp['trans_result'][0]['dst']

    def _signature(self, q, salt):
        sign = self.appid + q + salt + self.secret_key
        sign = hashlib.md5(sign.encode()).hexdigest()
        return sign


class Client():
    def __init__(self, apikey, proxy_reverse='https://api.openai.com', temperature=0):
        self.apikey = apikey
        self.proxy_reverse = proxy_reverse
        self.temperature = temperature

        openai.api_base = proxy_reverse + '/v1'
        self.source = '英文'
        self.target = '中文'
        self.session = [{'role': 'system','content': '你是一个翻译引擎，请将'+self.source+'文本翻译为'+self.target+'，只需要翻译不需要解释。当你从文本中检测到非'+self.source+'文本时，请将它作为专有名词，当你无法做出翻译使请将状态码改成500，否则状态码是200，请严格按照下面json格式给到翻译结果：\n{code:200,result:翻译的结果}，如果你明白了请说同意，然后我们开始。'},
                        {'role': 'assistant', 'content': '好的，我明白了，请给我文本。'},
                        {'role':'user','content':'Hello world'},
                        {'role': 'assistant', 'content': '{"code": 200, "result": "你好世界"}'},
                        {'role': 'user', 'content': 'A8c��)��A7	;��C�a���z�2A1'},
                        {'role': 'assistant', 'content': '{"code": 500, "result": ""}'}]

    async def translate(self, prompt=''):
        seg = {'role': 'user', 'content': prompt}
        self.session.append(seg)
        res = await self.chat_with_gpt(self.session)
        self.session.append({'role': 'assistant', 'content': res})
        length = len(json.dumps(self.session, indent=2))
        while length > 3000:
            del self.session[6]
            length = len(json.dumps(self.session, indent=2))
        return res

    async def chat_with_gpt(self, messages):
        try:
            openai.api_key = self.apikey
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            resp = resp['choices'][0]['message']['content']
        except openai.OpenAIError as e:
            print('openai 接口报错: ' + str(e))
            resp = str(e)
        return resp

        # '''aiohttp'''
        # headers = {
        #     'Authorization': f'Bearer {self.apikey}',
        #     'Content-Type': 'application/json'
        # }
        # data = {
        #     'model': 'gpt-3.5-turbo',
        #     'temperature': self.temperature,
        #     'top_p': 1,
        #     'frequency_penalty': 0,
        #     'presence_penalty': 0,
        #     'messages': messages
        # }
        # async with aiohttp.ClientSession() as session:
        # try:
        #     async with session.post(
        #             f"{self.proxy_reverse}/v1/chat/completions",
        #             headers=headers,
        #             json=data
        #     ) as response:
        #         response_data = await response.json()
        #         return response_data['choices'][0]['message']['content']

        # except Exception as error:
        #     print(str(error))
        #     return str(error)


def seconds_to_str(seconds):
    """
    时间戳转为 天 时 分 秒
    :param seconds: int or float
    :return: str
    eg: 360 --> 6分0秒
    """

    days = int(seconds // (3600 * 24))
    hours = int((seconds // 3600) % 24)
    minutes = int((seconds // 60) % 60)
    seconds = round(seconds % 60)
    if days > 0:
        return f'{days}天{hours}时{minutes}分{seconds}秒'
    if hours > 0:
        return f'{hours}时{minutes}分{seconds}秒'
    if minutes > 0:
        return f'{minutes}分{seconds}秒'
    return f'{seconds}秒'


# 实例化客户端
x, y, w, h = 0, 0, 1000, 1000
client = Client(apikey=apikey)
baidu_client = BaiduTranslator(appid=appid, secret_key=secret_key)


# 创建ws服务端
async def echo(websocket, path):
    global initialize, x, y, w, h
    async for message in websocket:
        print(message)
        if (message == 'paste20230501'):
            pyautogui.hotkey('ctrl', 'v')
            await websocket.send('paste20230501')
            continue
        if (message == 'init20230501'):
            x, y, w, h = localion()
        if message == 'do20230501':
            time_start = time.time()
            text = gettext(x, y, w, h)
            print(text)
            # 发送请求
            """
            openai
            """
            translate_text = await client.translate(prompt=text)
            translate_text = json.loads(translate_text)
            """
            百度api
            """
            # translate_text = await baidu_client.translate(prompt=text)
            # translate_text = text
            if translate_text["result"] and translate_text["code"] == 200:
                pyperclip.copy(translate_text["result"])
            else:
                pyperclip.copy('')
                await websocket.send('pass20230501')
            # 计算时间
            print(f'用时：{seconds_to_str(time.time() - time_start)}')
            if websocket.open:
                await websocket.send('done20230501')
            else:
                print("WebSocket connection is closed.")


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
