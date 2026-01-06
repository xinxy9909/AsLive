from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import config

class ASRWrapper:
    
    def __init__(self, model_dir=config.ASR_MODEL_PATH, device="mps", vad_model="fsmn-vad"):
        self.model_dir = model_dir
        self.device = device
        self.vad_model = vad_model
        
        print("正在初始化ASR模型...")
        self.model = AutoModel(
            model=self.model_dir,
            trust_remote_code=True,
            remote_code="./model.py",    
            vad_model=self.vad_model,
            vad_kwargs={"max_single_segment_time": 30000},
            device=self.device,
        )
    
    def transcribe(self, wav_dir, language="auto", use_itn=True, batch_size_s=60, 
                   merge_vad=True, merge_length_s=15):
        print("正在开始ASR识别")
        res = self.model.generate(
            input=wav_dir,
            cache={},
            language=language,
            use_itn=use_itn,
            batch_size_s=batch_size_s,
            merge_vad=merge_vad,
            merge_length_s=merge_length_s,
        )
        
        text = rich_transcription_postprocess(res[0]["text"])
        print("ASR识别结束")
        return text
    
