from minio import Minio
from minio.error import S3Error


def main():
    client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
    )

    # The file to upload, change this path if needed
    source_file = "./test-file.txt"

    # The destination bucket and filename on the MinIO server
    bucket_name = "python-test-bucke2"
    destination_file = "my-test-file.txt"
    
    # Make the bucket if it doesn't exist.
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name=bucket_name,
        object_name=destination_file,
        file_path=source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
        