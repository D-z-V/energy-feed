import torch
from transformers import pipeline
import gc

summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small", device=0)

gc.collect()
torch.cuda.empty_cache()