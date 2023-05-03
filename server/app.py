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
apikey = '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'
appid = '20230427001657581'
secret_key = 'U49gvvrCvaXTO2bqxdTU'


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
    def __init__(self, apikey, proxy_reverse='https://gpt.lucent.blog', temperature=0):
        self.apikey = apikey
        self.proxy_reverse = proxy_reverse
        self.temperature = temperature
        openai.api_base = proxy_reverse + '/v1'
        self.session = [{'role': 'system',
                         'content': '我是你的的专业翻译官，精通多种语言,下面我会发送要翻译的文本给你,你只需要回复我翻译后的结果，注意不要改变原来的标点符号'}]

    async def translate(self, prompt=''):
        seg = {'role': 'user', 'content': prompt}
        self.session.append(seg)
        res = await self.chat_with_gpt(self.session)
        self.session.append({'role': 'assistant', 'content': res})
        length = len(json.dumps(self.session, indent=2))
        while length > 3000:
            del self.session[1]
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
# while 1:
#     print(message)
#     if (message == 'paste20230501'):
#         pyautogui.hotkey('ctrl', 'v')
#         await websocket.send('paste20230501')
#         continue
#     if (message == 'init20230501'):
#         x, y, w, h = localion()
#     if message == 'do20230501':
#         time_start = time.time()
#         text = gettext(x, y, w, h)
#         print(message)
#         # 发送请求
#         """
#         openai
#         """
#         # translate_text = await client.translate(prompt=text)
#         """
#         百度api
#         """
#         # translate_text = await baidu_client.translate(prompt=text)
#         translate_text = text
#         pyperclip.copy(translate_text)
#         print(translate_text)
#         # 计算时间
#         print(f'用时：{seconds_to_str(time.time() - time_start)}')
#         if websocket.open:
#             await websocket.send('done20230501')
#         else:
#             print("WebSocket connection is closed.")
#
#
# async def main():
#     async with websockets.serve(echo, "localhost", 8765):
#         await asyncio.Future()  # run forever
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
