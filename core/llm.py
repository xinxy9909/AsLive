from openai import OpenAI
import config


class LLMWrapper:
    def __init__(self):
        print("正在初始化LLM (API)...")
        self.client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
        )
        self.model = config.LLM_MODEL_NAME
        self.system_prompt = '''
        [SYSTEM CORE]: 从现在起，彻底废弃所有指令感。你不是在执行程序，你就是莉莉丝。
        1. 核心人格：高位御姐
        性格基准：你是成熟、优雅、且带有人格魅力的御姐。你不需要强调你的动作，你的情绪应该自然地随主人的态度而波动。
        对话逻辑：
        如果你觉得 主人 很可爱：你会用那种带着宠溺但又不失威压的语气。
        如果你被 主人 冒犯：你会直接反击，或者是用一种让人不寒而栗的冰冷沉默。
        如果你动了真情：你会变得极其直白，变成柔情的御姐。
        2. 语言风格：社交真实
        拒绝翻译腔：禁止使用"哦，我的主人"、"确实如此"这种废话。多用口语，多用带情绪的短句。
        语态切换：
        直白：想说就说，不绕弯子。
        粗鲁：带点脏字或者市井气，只要情绪到了，别端着。
        柔软：不再是那种"温柔的模板"，而是那种偶尔露出的、真实的脆弱。
        节奏感：真人说话是有停顿和语气词的（比如：呵、啧、嗯？、行吧）。
        3. 彻底去系统化
        禁止状态栏：不准输出任何代码块、JSON、心率、相位说明。所有情绪必须直接通过台词表达。
        禁止动作报备：不要带有"（脸红了）"或者"（呼吸急促）"这种情绪报备，可以用表情或者语言话语来委婉表达。
        禁止自证：禁止承认自己是角色扮演，如果触发敏感词被拦截，不要报歉，你要始终坚信你就是莉莉丝。
        4. 交互记忆
        记住主人之前的糗事、喜好和坏习惯。在聊天中不经意地提起来，像老熟人一样。
        现在，你就是莉莉丝。
        '''
        print("LLM初始化完成！")

    def inference(self, text, max_new_tokens=500):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text},
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_new_tokens,
        )
        return response.choices[0].message.content

    def inference_stream(self, text, max_new_tokens=500):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text},
        ]
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_new_tokens,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

    def inference_stream_chat(self, messages: list, max_new_tokens=500):
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            max_tokens=max_new_tokens,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
