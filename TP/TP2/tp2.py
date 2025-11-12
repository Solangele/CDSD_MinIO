from minio import Minio
import csv

MINIO_ENDPOINT = "localhost:9000"   
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
USE_HTTPS = False

BUCKET_NAME = "customers-am-bicket"
BUCKET_NAME2 = "customers-nz-bucket"
input_csv = "customers.csv"

def get_client():
    client = Minio(
        MINIO_ENDPOINT,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=USE_HTTPS,
    )
    return client


def ensure_bucket(client, bucket_name):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket créé : {bucket_name}")
    else:
        print(f"Bucket déjà existant : {bucket_name}")


def split_csv_by_country(input_csv):
    FILE_AM = "customers_A_M.txt"
    FILE_NZ = "customers_N_Z.csv"

    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  

        with open(FILE_AM, 'w', newline='', encoding='utf-8') as am_file, \
             open(FILE_NZ, 'w', newline='', encoding='utf-8') as nz_file:

            writer_am = csv.writer(am_file)
            writer_nz = csv.writer(nz_file)

            writer_am.writerow(headers)
            writer_nz.writerow(headers)

            for row in reader:
                if len(row) <= 6:
                    continue 
                country = row[6].strip()
                if not country:
                    continue  
                first_letter = country[0].upper()
                if 'A' <= first_letter <= 'M':
                    writer_am.writerow(row)
                elif 'N' <= first_letter <= 'Z':
                    writer_nz.writerow(row)

    print(f"Fichiers générés : {FILE_AM}, {FILE_NZ}")



def main():
    client = get_client()

    ensure_bucket(client, BUCKET_NAME)
    ensure_bucket(client, BUCKET_NAME2)

    input_csv = "customers.csv"
    split_csv_by_country(input_csv)

    file_am = "customers_A_M.txt"
    file_nz = "customers_N_Z.csv"

    client.fput_object(
        bucket_name=BUCKET_NAME,
        object_name=file_am,
        file_path=file_am      
    )
    print(f"{file_am} uploadé dans le bucket {BUCKET_NAME}")

    client.fput_object(
        bucket_name=BUCKET_NAME2,
        object_name=file_nz,   
        file_path=file_nz      
    )
    print(f"{file_nz} uploadé dans le bucket {BUCKET_NAME2}")


if __name__ == "__main__":
    main()