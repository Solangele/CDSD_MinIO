import os
import pandas as pd
from util import s3_client, list_objects, get_object_bytes, put_object_bytes

BRONZE_BUCKET = os.getenv("BRONZE_BUCKET", "bronze")
SILVER_BUCKET = os.getenv("SILVER_BUCKET", "silver")

def clean_customers(df):
    # Exemple simple : supprimer les lignes sans email
    df = df[df['email'].notnull() & (df['email'] != "")]
    return df

def main():
    s3 = s3_client()
    while True:
        # Lister tous les fichiers CSV dans bronze/customers/
        for key in list_objects(BRONZE_BUCKET, "customers/"):
            try:
                data = get_object_bytes(BRONZE_BUCKET, key)
                df = pd.read_csv(pd.io.common.BytesIO(data))
                df_clean = clean_customers(df)

                # Écrire dans silver
                silver_key = key.replace("customers/", "customers/")
                put_object_bytes(SILVER_BUCKET, silver_key, df_clean.to_csv(index=False).encode("utf-8"), "text/csv")
                print(f"[cleaner] {key} -> {silver_key} ✅")
            except Exception as e:
                print(f"[cleaner] ERROR: {e}")
        import time
        time.sleep(5)  # toutes les 5 secondes

if __name__ == "__main__":
    main()
