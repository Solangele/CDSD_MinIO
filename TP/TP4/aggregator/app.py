import os
import pandas as pd
from util import s3_client, list_objects, get_object_bytes, put_object_bytes
import json

SILVER_BUCKET = os.getenv("SILVER_BUCKET", "silver")
GOLD_BUCKET = os.getenv("GOLD_BUCKET", "gold")

def aggregate_customers(df):
    # Exemple simple : compter le nombre de clients par pays
    return df.groupby("country").size().reset_index(name="customer_count")

def main():
    s3 = s3_client()
    while True:
        for key in list_objects(SILVER_BUCKET, "customers/"):
            try:
                data = get_object_bytes(SILVER_BUCKET, key)
                df = pd.read_csv(pd.io.common.BytesIO(data))
                df_agg = aggregate_customers(df)

                # Écrire dans gold au format JSON
                gold_key = key.replace("customers/", "customers_agg/").replace(".csv", ".json")
                put_object_bytes(GOLD_BUCKET, gold_key, df_agg.to_json(orient="records").encode("utf-8"), "application/json")
                print(f"[aggregator] {key} -> {gold_key} ✅")
            except Exception as e:
                print(f"[aggregator] ERROR: {e}")
        import time
        time.sleep(10)  # toutes les 10 secondes

if __name__ == "__main__":
    main()
