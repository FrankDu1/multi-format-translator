import json
import hashlib
import hmac
import base64
import time
import os
import requests
from urllib.parse import quote_plus

class AliTranslateClient:
    def __init__(self, access_key_id=None, access_key_secret=None):
        """
        初始化阿里云翻译客户端
        建议通过环境变量 ALI_ACCESS_KEY_ID 和 ALI_ACCESS_KEY_SECRET 管理密钥
        """
        self.access_key_id = access_key_id or os.getenv('ALI_ACCESS_KEY_ID')
        self.access_key_secret = access_key_secret or os.getenv('ALI_ACCESS_KEY_SECRET')
        self.endpoint = os.getenv('ALI_TRANSLATOR_ENDPOINT', 'https://mt.cn-hangzhou.aliyuncs.com')
        self.api_version = "2018-10-12"
        
    def _get_timestamp(self):
        """获取UTC时间戳"""
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    def _percent_encode(self, string):
        """URL编码"""
        return quote_plus(string).replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
    
    def _sign(self, params, access_key_secret):
        """生成签名"""
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        canonicalized_query_string = ''
        for k, v in sorted_params:
            canonicalized_query_string += '&' + self._percent_encode(k) + '=' + self._percent_encode(v)
        string_to_sign = 'POST&%2F&' + self._percent_encode(canonicalized_query_string[1:])
        key = access_key_secret + '&'
        signature = hmac.new(key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1).digest()
        signature_base64 = base64.b64encode(signature).decode('utf-8')
        return signature_base64
    
    def translate(self, text, source_lang='zh', target_lang='en', format_type='text', scene='title'):
        """
        调用翻译API
        """
        params = {
            'Action': 'Translate',
            'Format': 'JSON',
            'Version': self.api_version,
            'AccessKeyId': self.access_key_id,
            'SignatureMethod': 'HMAC-SHA1',
            'Timestamp': self._get_timestamp(),
            'SignatureVersion': '1.0',
            'SignatureNonce': str(int(time.time() * 1000)),
            'SourceLanguage': source_lang,
            'TargetLanguage': target_lang,
            'SourceText': text,
            'FormatType': format_type,
            'Scene': scene
        }
        params['Signature'] = self._sign(params, self.access_key_secret)
        url = f"{self.endpoint}/"
        try:
            response = requests.post(url, data=params, timeout=10)
            result = response.json()
            if result.get('Code') == '200':
                return {
                    'success': True,
                    'translated_text': result.get('Data', {}).get('Translated'),
                    'request_id': result.get('RequestId'),
                    'word_count': result.get('Data', {}).get('WordCount')
                }
            else:
                return {
                    'success': False,
                    'error_code': result.get('Code'),
                    'error_message': result.get('Message')
                }
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }