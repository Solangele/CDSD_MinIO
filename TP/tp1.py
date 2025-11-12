from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource
from minio.deleteobjects import DeleteObject
import os


def main():
    # 1 : connexion au serveur MinIO
    client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
    )

    # 3: création d'un fichier local
    source_file = "./tp1.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write("Bonjour ! Voici le fichier texte du tp1\n")
        f.write("Deuxième ligne de texte.\n")
        f.write("Troisième ligne : upload vers MinIO réussi.\n")
    print(f"Fichier {source_file} créé avec succès.")

    # 2 : création d'un bucket
    bucket_name = "python-tp1"
    destination_file = "test-tp1.txt"
    
    # Make the bucket if it doesn't exist.
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # 4 : envoi du fichier local vers le bucket MinIO
    client.fput_object(
        bucket_name=bucket_name,
        object_name=destination_file,
        file_path=source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )


    # 5 : affichage de la liste des fichiers du bucket
    print("Liste des fichiers dans le bucket :")
    objects = client.list_objects(bucket_name)
    for obj in objects:
        print(f"- {obj.object_name} (taille : {obj.size} octets)")


    # 6 : copie d'un objet
    source_object = "test-tp1.txt"
    copied_object = "copie-test-tp1.txt"
    copy_source = CopySource(bucket_name, source_object)
    client.copy_object(bucket_name, copied_object, copy_source)
    print(f"\nObjet '{source_object}' copié vers '{copied_object}' dans le bucket '{bucket_name}'.")


    # 7 : Renommage d'un objet
    old_name = "copie-test-tp1.txt"
    new_name = "renomme-test-tp1.txt"

    rename_source = CopySource(bucket_name, old_name)
    client.copy_object(bucket_name, new_name, rename_source)

    client.remove_object(bucket_name, old_name)
    print(f"\nObjet '{old_name}' renommé en '{new_name}' (copie + suppression).")


    # 8 : Téléchargement d'un objet
    local_download_path = "./telecharge-test-tp1.txt"
    client.fget_object(
        bucket_name=bucket_name,
        object_name=new_name,
        file_path=local_download_path,
    )
    print(f"\nFichier '{new_name}' téléchargé localement sous '{local_download_path}'.")


    # 9 : suppression d'un objet
    print("Suppression d’objets dans le bucket...")

    # Suppression d’un seul objet :
    client.remove_object(bucket_name, destination_file)
    print(f"- '{destination_file}' supprimé.")

    # Suppression multiple :
    objects_to_delete = [new_name]
    objects_to_delete = [DeleteObject("renomme-test-tp1.txt")]
    for error in client.remove_objects(bucket_name, objects_to_delete):
        print("Erreur lors de la suppression :", error)


    # 10 : Nettoyage local
    print("Nettoyage des fichiers locaux...")
    for fichier in [source_file, local_download_path]:
        if os.path.exists(fichier):
            os.remove(fichier)
            print(f"- {fichier} supprimé.")
        else:
            print(f"- {fichier} n'existe pas (déjà supprimé ou jamais créé).")

    print("\n✅ Fin du script : tout est propre !")



if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
        