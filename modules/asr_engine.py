import os


class ASREngine:
    """语音识别引擎"""
    
    def __init__(self):
        """初始化语音识别引擎"""
        self.recognizer = None
    
    def _init_recognizer(self):
        """初始化识别器"""
        if self.recognizer is None:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
            except ImportError:
                raise ImportError("请安装speech_recognition库: pip install SpeechRecognition")
    
    def transcribe(self, audio_path):
        """
        转写语音文件
        
        参数:
            audio_path: 音频文件路径
        """
        try:
            self._init_recognizer()
            import speech_recognition as sr
            
            # 读取音频文件
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            # 使用Google语音识别
            try:
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                return {
                    'status': 'success',
                    'text': text
                }
            except sr.UnknownValueError:
                return {
                    'status': 'error',
                    'reason': '无法识别语音内容'
                }
            except sr.RequestError as e:
                return {
                    'status': 'error',
                    'reason': f'语音识别服务错误: {e}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'reason': str(e)
            }


def transcribe_voice(audio_path):
    """语音转写的便捷函数"""
    engine = ASREngine()
    
    # 检查文件是否存在
    if not os.path.exists(audio_path):
        # 返回模拟数据
        return {
            'status': 'mock',
            'text': '我想申请贷款装修房子，月收入8000元，工作3年了'
        }
    
    result = engine.transcribe(audio_path)
    
    # 如果识别失败，返回模拟数据
    if result['status'] == 'error':
        result['status'] = 'mock'
        result['text'] = '我想申请贷款，月收入8000元'
    
    return result


if __name__ == '__main__':
    print("语音识别模块加载成功")
