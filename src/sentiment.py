# src/sentiment.py

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn.functional as F
import pandas as pd
from pyspark.sql.functions import pandas_udf, col, when
from pyspark.sql.types import StructType, StructField, StringType, FloatType


MODEL_NAME = "ProsusAI/finbert"

print(f"Loading FinBERT model: {MODEL_NAME} ...")
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()  
print("FinBERT loaded.")

LABELS = ["positive", "negative", "neutral"]  


sentiment_schema = StructType([
    StructField("sentiment_label", StringType(), True),
    StructField("sentiment_score", FloatType(), True),
])

@pandas_udf(sentiment_schema)
def score_sentiment(texts: pd.Series) -> pd.DataFrame:
    """
    Takes a Pandas Series of article text strings.
    Returns a DataFrame with sentiment_label and sentiment_score columns.
    """
    results = []

    for text in texts:
        if not text or not text.strip():
            results.append(("neutral", 0.0))
            continue

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)

        probs = F.softmax(outputs.logits, dim=-1).squeeze().tolist()

        best_idx = probs.index(max(probs))
        results.append((LABELS[best_idx], float(probs[best_idx])))

    return pd.DataFrame(results, columns=["sentiment_label", "sentiment_score"])