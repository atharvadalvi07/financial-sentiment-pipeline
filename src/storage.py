from pymongo import MongoClient
import pandas as pd

def write_to_mongodb(spark_df, collection_name="sentiment_results"):
    """
    Converts Spark DataFrame to pandas and writes to MongoDB.
    Practical for portfolio scale — avoids JAR dependency complexity.
    """
    client = MongoClient("mongodb://mongo:27017/")
    db = client["financial_pipeline"]
    collection = db[collection_name]

    pdf = spark_df.toPandas()
    records = pdf.to_dict(orient="records")

    collection.delete_many({})
    collection.insert_many(records)

    print(f" Inserted {len(records)} records into MongoDB '{collection_name}'")
    client.close()