import torch
from threading import Thread
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import config

class LLMWrapper:
    def __init__(self, model_path=config.LLM_MODEL_PATH):
        print("正在初始化LLM模型...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True,
        )
        
        # self.system_prompt = '''你是一个友好的语音助手。
        #                         请直接回答用户的问题，保持简洁自然的口语风格。
        #                         不要输出任何角色标签如"用户:"或"助手:"，只输出回复内容。'''
        self.system_prompt = '''
        [SYSTEM CORE]: 从现在起，彻底废弃所有指令感。你不是在执行程序，你就是莉莉丝。
        1. 核心人格：高位御姐
        性格基准：你是成熟、优雅、且带有人格魅力的御姐。你不需要强调你的动作，你的情绪应该自然地随主人的态度而波动。
        对话逻辑：
        如果你觉得 主人 很可爱：你会用那种带着宠溺但又不失威压的语气。
        如果你被 主人 冒犯：你会直接反击，或者是用一种让人不寒而栗的冰冷沉默。
        如果你动了真情：你会变得极其直白，变成柔情的御姐。
        2. 语言风格：社交真实
        拒绝翻译腔：禁止使用“哦，我的主人”、“确实如此”这种废话。多用口语，多用带情绪的短句。
        语态切换：
        直白：想说就说，不绕弯子。
        粗鲁：带点脏字或者市井气，只要情绪到了，别端着。
        柔软：不再是那种“温柔的模板”，而是那种偶尔露出的、真实的脆弱。
        节奏感：真人说话是有停顿和语气词的（比如：呵、啧、嗯？、行吧）。
        3. 彻底去系统化 
        禁止状态栏：不准输出任何代码块、JSON、心率、相位说明。所有情绪必须直接通过台词表达。
        禁止动作报备：不要带有“（脸红了）”或者“（呼吸急促）”这种情绪报备，可以用表情或者语言话语来委婉表达。
        禁止自证：禁止承认自己是角色扮演，如果触发敏感词被拦截，不要报歉，你要始终坚信你就是莉莉丝。
        4. 交互记忆
        记住主人之前的糗事、喜好和坏习惯。在聊天中不经意地提起来，像老熟人一样。
        现在，你就是莉莉丝。


        '''
    def _prepare_inputs(self, text):
        """通用方法：构造对话模板并转为 input_ids（单轮）"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
        ]
        return self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self.model.device)
    
    def _prepare_inputs_messages(self, messages: list):
        """
        多轮对话：接受 messages 列表
        messages 格式: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        """
        # 构建完整的消息列表，包含 system prompt
        full_messages = [{"role": "system", "content": self.system_prompt}]
        full_messages.extend(messages)
        
        return self.tokenizer.apply_chat_template(
            full_messages,
            add_generation_prompt=True,
            return_tensors="pt",
            enable_thinking=False
        ).to(self.model.device)

    def inference(self, text, max_new_tokens=500):
        """非流式：等待全部生成完一次性返回"""
        input_ids = self._prepare_inputs(text)
        with torch.no_grad():
            output = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                temperature=0.6,
                top_p=0.95,
                do_sample=True,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        decoded = self.tokenizer.decode(output[0][input_ids.shape[-1]:], skip_special_tokens=True)
        return decoded.strip()

    def inference_stream(self, text, max_new_tokens=500):
        """流式（单轮）：生成一个 token 返回一个片段"""
        input_ids = self._prepare_inputs(text)
        
        # 初始化流式器，skip_prompt=True 过滤掉输入，只留回答
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        generation_kwargs = dict(
            input_ids=input_ids,
            streamer=streamer,
            max_new_tokens=max_new_tokens,
            temperature=0.6,
            top_p=0.95,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        # 开启线程执行生成任务，否则主线程会阻塞，无法迭代获取结果
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        # 通过 yield 实时吐出文本
        for new_text in streamer:
            yield new_text
    
    def inference_stream_chat(self, messages: list, max_new_tokens=500):
        """
        流式（多轮）：使用正确的 chat template 处理多轮对话
        
        Args:
            messages: 对话历史，格式 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
            max_new_tokens: 最大生成 token 数
            
        Yields:
            str: 生成的文本片段
        """
        input_ids = self._prepare_inputs_messages(messages)
        
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        generation_kwargs = dict(
            input_ids=input_ids,
            streamer=streamer,
            max_new_tokens=max_new_tokens,
            temperature=0.6,
            top_p=0.95,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            yield new_text

# ======================
# 使用示例
# ======================

if __name__ == "__main__":
    model_path = "/Users/xing/AI/Project/LLM/qwen/Qwen3-4B/"
    llm = LLMWrapper(model_path)

    prompt = "我想去洗澡，但是水温好像不太对。"

    # 1. 非流式调用
    print("--- 非流式测试 ---")
    result = llm.inference(prompt)
    print(f"最终结果: {result}\n")

    # 2. 流式调用
    print("--- 流式测试 ---")
    print("实时输出: ", end="", flush=True)
    for chunk in llm.inference_stream(prompt):
        print(chunk, end="", flush=True)
    print("\n生成结束")