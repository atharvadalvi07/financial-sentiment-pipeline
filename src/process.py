from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    to_timestamp, col, length, dayofweek,
    hour, when, lit, trim
)


def run_processing(spark: SparkSession, input_path: str, output_path: str):
    df = spark.read.parquet(input_path)

    # Dedup
    df = df.dropDuplicates(["url"])

    # Null handling
    df = df.dropna(subset=["title", "publishedAt", "ticker"])
    df = df.fillna({"description": "", "content": ""})

    # Field selection — source already flat from Phase 2, no author field
    df = df.select(
        col("ticker"),
        col("title"),
        col("description"),
        col("content"),
        col("publishedAt"),
        col("source_name"),
        col("url")
    )

    # Derived columns
    df = df.withColumn("published_ts", to_timestamp(col("publishedAt"), "yyyy-MM-dd'T'HH:mm:ss'Z'"))
    df = df.withColumn("article_length", length(trim(col("title"))) + length(trim(col("description"))))
    df = df.withColumn("day_of_week", dayofweek(col("published_ts")))
    df = df.withColumn("hour_published", hour(col("published_ts")))
    df = df.withColumn(
        "during_market_hours",
        when(
            (col("day_of_week").between(2, 6)) &
            (col("hour_published").between(14, 20)),
            lit(True)
        ).otherwise(lit(False))
    )

    # Write partitioned by ticker for Phase 4 partition pruning
    df.write.mode("overwrite").partitionBy("ticker").parquet(output_path)
    return df


if __name__ == "__main__":
    spark = SparkSession.builder.appName("FinancialNewsProcessing").getOrCreate()
    run_processing(
        spark,
        input_path="/home/jovyan/work/data/processed/news_raw.parquet",
        output_path="/home/jovyan/work/data/cleaned/"
    )