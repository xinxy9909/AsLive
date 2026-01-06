"""
实时语音交互系统
ASR(实时语音识别) → LLM(流式生成) → TTS(流式播放)

核心算法：
1. 麦克风实时录音 + VAD 检测说话结束
2. ASR 识别用户语音
3. LLM 流式生成回复，按句子边界切分
4. TTS 流式合成并播放每个句子（边生成边播放）
"""
import time
import threading
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from typing import Optional, Callable

# 导入核心模块
from core.asr import ASRWrapper
from core.llm import LLMWrapper
from core.tts import TTSWrapper


class RealtimeSpeechPipeline:
    """实时语音交互管道"""
    
    def __init__(
        self,
        llm_model_path: str = "/Users/xing/AI/Project/LLM/qwen/Qwen3-4B",
        asr_model: str = "iic/SenseVoiceSmall",
        speak_id: str = "zf_001",
        speed: float = 1.0,
        sample_rate: int = 16000,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,  # 静音多久认为说话结束
    ):
        self.speak_id = speak_id
        self.speed = speed
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        
        # 句子边界分隔符
        self.sentence_delimiters = set(',。！？；.!?;\n')
        
        # 延迟加载模型
        print("=" * 60)
        print("正在初始化实时语音交互系统...")
        print("=" * 60)
        
        print("\n[1/3] 加载 ASR 模型...")
        self.asr = ASRWrapper(model_dir=asr_model)
        
        print("\n[2/3] 加载 LLM 模型...")
        self.llm = LLMWrapper(model_path=llm_model_path)
        
        print("\n[3/3] 加载 TTS 模型...")
        self.tts = TTSWrapper()
        
        print("\n" + "=" * 60)
        print("系统初始化完成！")
        print("=" * 60)
        
        # 对话历史
        self.conversation_history = []
        
        # 录音相关
        self.is_recording = False
        self.audio_buffer = []
        
    def _detect_silence(self, audio_chunk: np.ndarray) -> bool:
        """检测是否为静音"""
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        return rms < self.silence_threshold
    
    def record_with_vad(self, max_duration: float = 30.0) -> Optional[np.ndarray]:
        """
        使用 VAD 进行实时录音，检测到静音自动停止
        
        Args:
            max_duration: 最大录音时长（秒）
            
        Returns:
            录音的音频数据
        """
        print("\n🎤 开始录音... (说话后停顿将自动结束)")
        
        audio_chunks = []
        silence_start = None
        has_speech = False
        
        def audio_callback(indata, frames, time_info, status):
            nonlocal silence_start, has_speech
            
            chunk = indata[:, 0].copy()
            audio_chunks.append(chunk)
            
            is_silent = self._detect_silence(chunk)
            
            if not is_silent:
                has_speech = True
                silence_start = None
            elif has_speech:
                if silence_start is None:
                    silence_start = time.time()
        
        # 开始录音
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=int(self.sample_rate * 0.1),  # 100ms 块
            callback=audio_callback
        ):
            start_time = time.time()
            
            while True:
                time.sleep(0.05)
                
                # 检查是否超时
                if time.time() - start_time > max_duration:
                    print("⏰ 录音超时")
                    break
                
                # 检查静音时长
                if silence_start and (time.time() - silence_start) > self.silence_duration:
                    print("🔇 检测到静音，录音结束")
                    break
        
        if not audio_chunks:
            return None
            
        audio = np.concatenate(audio_chunks)
        duration = len(audio) / self.sample_rate
        print(f"📝 录音完成: {duration:.1f}秒")
        
        return audio
    
    def _clean_text_for_tts(self, text: str) -> str:
        """
        清理文本，移除不应被 TTS 朗读的内容
        只提取最后一轮助手回复
        """
        import re
    
        # 如果包含对话格式，提取最后一个 "助手:" 后面的内容
        if '助手:' in text or '助手：' in text:
            # 分割并取最后一个助手回复
            parts = re.split(r'助手[：:]\s*', text)
            if len(parts) > 1:
                # 取最后一个助手回复，并移除后续的 "用户:" 内容
                last_response = parts[-1]
                # 移除可能跟在后面的 "用户:" 开头的内容
                last_response = re.split(r'\n\s*用户[：:]', last_response)[0]
                text = last_response
        
        # 移除可能的角色前缀
        text = re.sub(r'^(用户|助手|User|Assistant)[：:]\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def process_streaming_llm_tts(self, user_text: str) -> str:
        """
        流式处理：边生成 LLM 边进行 TTS
        
        使用正确的 chat template，LLM 只会输出当前回复，不会输出历史
        跳过 <think>...</think> 标签内的内容
        
        Args:
            user_text: 用户输入文本
            
        Returns:
            完整的 LLM 回复
        """
        buffer = ""
        full_response = ""
        first_audio_time = None
        start_time = time.time()
        
        # 跟踪是否在 <think> 标签内
        in_think_tag = False
        
        # 添加当前用户输入到历史
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # 使用最近 6 条消息作为上下文
        context_messages = self.conversation_history[-6:]
        
        # 开始 TTS 流式会话
        self.tts.start_streaming_session()
        
        print("\n🤖 回复: ", end="", flush=True)
        
        # 使用新的多轮对话流式接口
        for chunk in self.llm.inference_stream_chat(context_messages):
            full_response += chunk
            print(chunk, end="", flush=True)
            
            # 累积到 buffer
            buffer += chunk
            
            # 检测句子边界：扫描 buffer 中是否包含分隔符
            while True:
                # 找到第一个分隔符的位置
                delimiter_pos = -1
                for i, char in enumerate(buffer):
                    if char in self.sentence_delimiters:
                        delimiter_pos = i
                        break
                
                if delimiter_pos == -1:
                    # 没有找到分隔符，继续累积
                    break
                
                # 提取分隔符之前的内容（包括分隔符）
                sentence = buffer[:delimiter_pos + 1]
                buffer = buffer[delimiter_pos + 1:]
                
                if first_audio_time is None:
                    first_audio_time = time.time()
                    latency = first_audio_time - start_time
                    print(f" [首句延迟: {latency:.2f}s]", end="", flush=True)
                
                # 清理文本后送入 TTS
                clean_text = self._clean_text_for_tts(sentence)
                if clean_text:
                    self.tts.stream_sentence(clean_text, speak_id=self.speak_id, speed=self.speed)
        
        # 处理剩余内容
        if buffer.strip():
            clean_text = self._clean_text_for_tts(buffer)
            if clean_text:
                self.tts.stream_sentence(clean_text, speak_id=self.speak_id, speed=self.speed)
        
        print()  # 换行
        
        # 结束 TTS 会话，等待播放完成
        self.tts.finish_streaming_session(out_dir="./output")
        
        # 保存回复到历史（移除 think 标签）
        clean_response = self._clean_text_for_tts(full_response)
        self.conversation_history.append({"role": "assistant", "content": clean_response.strip()})
        
        return full_response

    
    def run_with_audio_file(self, audio_path: str) -> str:
        """
        使用音频文件进行交互
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            LLM 回复
        """
        print(f"\n📂 使用音频文件: {audio_path}")
        
        # ASR 识别
        print("🎯 正在识别语音...")
        user_text = self.asr.transcribe(wav_dir=audio_path)
        print(f"📝 识别结果: {user_text}")
        
        # 流式 LLM + TTS
        response = self.process_streaming_llm_tts(user_text)
        
        return response
    
    def run_with_text(self, text: str) -> str:
        """
        直接使用文本进行交互（跳过 ASR）
        
        Args:
            text: 用户输入文本
            
        Returns:
            LLM 回复
        """
        print(f"\n📝 用户输入: {text}")
        
        # 流式 LLM + TTS
        response = self.process_streaming_llm_tts(text)
        
        return response
    
    def run_realtime(self) -> str:
        """
        实时麦克风录音 + ASR + LLM + TTS
        
        Returns:
            LLM 回复
        """
        # 录音
        audio = self.record_with_vad()
        
        if audio is None or len(audio) < self.sample_rate * 0.5:  # 至少 0.5 秒
            print("⚠️ 录音太短，请重新说话")
            return ""
        
        # 保存临时文件供 ASR 使用
        temp_path = "./temp_recording.wav"
        sf.write(temp_path, audio, self.sample_rate)
        
        # ASR 识别
        print("🎯 正在识别语音...")
        user_text = self.asr.transcribe(wav_dir=temp_path)
        print(f"📝 识别结果: {user_text}")
        
        if not user_text.strip():
            print("⚠️ 未识别到有效内容")
            return ""
        
        # 流式 LLM + TTS
        response = self.process_streaming_llm_tts(user_text)
        
        return response
    
    def interactive_loop(self):
        """
        交互式循环
        """
        print("\n" + "=" * 60)
        print("实时语音交互系统")
        print("=" * 60)
        print("命令：")
        print("  1 - 实时录音（VAD 自动检测结束）")
        print("  2 - 使用音频文件")
        print("  3 - 直接输入文本")
        print("  q - 退出")
        print("=" * 60)
        
        round_count = 0
        
        while True:
            round_count += 1
            print(f"\n--- 第 {round_count} 轮对话 ---")
            
            choice = input("请选择 (1/2/3/q): ").strip().lower()
            
            if choice == 'q':
                print("👋 再见！")
                break
            elif choice == '1':
                self.run_realtime()
            elif choice == '2':
                audio_path = input("请输入音频文件路径: ").strip()
                if Path(audio_path).exists():
                    self.run_with_audio_file(audio_path)
                else:
                    print(f"⚠️ 文件不存在: {audio_path}")
            elif choice == '3':
                text = input("请输入文本: ").strip()
                if text:
                    self.run_with_text(text)
            else:
                print("⚠️ 无效选择")


def main():
    """主函数"""
    pipeline = RealtimeSpeechPipeline(
        llm_model_path="/Users/xing/AI/Project/LLM/qwen/Qwen3-4B",
        asr_model="iic/SenseVoiceSmall",
        speak_id="zf_001",
        speed=1.0,
        silence_duration=1.5,  # 静音 1.5 秒后自动停止录音
    )
    
    pipeline.interactive_loop()


if __name__ == "__main__":
    main()
