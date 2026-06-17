import logging
import asyncio
import torch
from transformers import MBartForConditionalGeneration, AutoModelForSeq2SeqLM
from transformers import AlbertTokenizer, AutoTokenizer

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.model_name = "ai4bharat/IndicBART"
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        self.is_loading = False

    async def initialize(self):
        if self.is_initialized or self.is_loading:
            return

        try:
            self.is_loading = True
            logger.info("Starting Translation Service initialization...")
            logger.info(f"Loading IndicBART model: {self.model_name}")

            # IndicBART uses AlbertTokenizer
            self.tokenizer = await asyncio.to_thread(
                AutoTokenizer.from_pretrained, 
                self.model_name, 
                do_lower_case=False, 
                use_fast=False, 
                keep_accents=True
            )
            
            # Using AutoModelForSeq2SeqLM
            self.model = await asyncio.to_thread(
                AutoModelForSeq2SeqLM.from_pretrained,
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            )
            
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                
            self.model.eval()
            self.is_initialized = True
            logger.info("Translation Service initialized successfully.")
        except Exception as e:
            logger.error(f"Error during Translation Service initialization: {e}", exc_info=True)
        finally:
            self.is_loading = False

    async def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        if not self.is_initialized:
            logger.warning("Translation Service not initialized, returning original text.")
            return text

        if not text or not text.strip():
            return text

        try:
            # IndicBART lang codes: <2en> for English, <2ml> for Malayalam
            # Actually, standard IndicBART uses different lang codes, let's configure properly:
            # IndicBART requires appending the target language tag to the input text
            # Wait, the official ai4bharat/IndicBART usage for translation:
            # "translate Malayalam to English: " -> but actually it uses special tokens.
            # Usually: input text is passed to tokenizer.
            # Let's use the simplest sequence generation.
            
            # The ai4bharat/IndicBART tokenizer uses specific language codes as eos tokens.
            # English: <2en>, Malayalam: <2ml>
            # The input should end with the source language token, and decoder starts with target language token.
            
            _src_lang = "<2ml>" if src_lang == "ml" else "<2en>"
            _tgt_lang = "<2en>" if tgt_lang == "en" else "<2ml>"
            
            inp = text + " </s> " + _src_lang
            inputs = self.tokenizer(inp, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
            bos_token_id = self.tokenizer._convert_token_to_id(_tgt_lang)
            
            outputs = await asyncio.to_thread(
                self.model.generate,
                **inputs,
                use_cache=True,
                num_beams=4,
                max_length=256,
                min_length=1,
                early_stopping=True,
                pad_token_id=self.tokenizer.pad_token_id,
                bos_token_id=bos_token_id,
                decoder_start_token_id=bos_token_id
            )
            
            decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return decoded.strip()
        except Exception as e:
            logger.error(f"Translation failed: {e}", exc_info=True)
            return text

    async def translate_ml_to_en(self, text: str) -> str:
        return await self.translate(text, src_lang="ml", tgt_lang="en")

    async def translate_en_to_ml(self, text: str) -> str:
        return await self.translate(text, src_lang="en", tgt_lang="ml")
