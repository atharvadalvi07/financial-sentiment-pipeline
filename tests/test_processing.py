import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType

@pytest.fixture(scope="module")
def spark():
    return (SparkSession.builder
            .master("local[1]")
            .appName("test")
            .getOrCreate())

def test_sentiment_schema(spark):
    """Sentiment DataFrame should have required columns."""
    schema = StructType([
        StructField("title", StringType()),
        StructField("ticker", StringType()),
        StructField("sentiment_label", StringType()),
        StructField("sentiment_score", FloatType()),
    ])
    data = [("Apple hits record high", "AAPL", "positive", 0.95)]
    df = spark.createDataFrame(data, schema)
    
    assert "sentiment_label" in df.columns
    assert "sentiment_score" in df.columns
    assert df.count() == 1

def test_label_values(spark):
    """Sentiment labels should only be positive, negative, or neutral."""
    schema = StructType([
        StructField("sentiment_label", StringType()),
        StructField("sentiment_score", FloatType()),
    ])
    data = [("positive", 0.9), ("negative", 0.1), ("neutral", 0.5)]
    df = spark.createDataFrame(data, schema)
    
    valid_labels = {"positive", "negative", "neutral"}
    actual_labels = {row.sentiment_label for row in df.collect()}
    assert actual_labels.issubset(valid_labels)