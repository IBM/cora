from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import requests

class InferenceEngine:
    def __init__(self, model_id, max_tokens):
        self.model_id = model_id
        self.max_tokens = max_tokens 

    def __call__(self):
        pass

class HFInferenceEngine(InferenceEngine):
    def __init__(self, model_id, max_tokens, do_sample=False, temperature=1.0):
        super().__init__(model_id, max_tokens)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        self.do_sample = do_sample
        self.temperature = temperature
        
    def __call__(self, prompts):
        outputs = self.pipe(prompts, max_new_tokens=self.max_tokens, do_sample=self.do_sample, temperature=self.temperature)
        return [ output[0]["generated_text"][len(prompt):].strip() for output, prompt in zip(outputs, prompts) ]
