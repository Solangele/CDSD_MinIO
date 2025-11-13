1. Lancer un MinIO local (exemple Docker) :

```bash
docker run -d --name minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=rootuser \
  -e MINIO_ROOT_PASSWORD=rootpass123 \
  quay.io/minio/minio server /data --console-address ":9001"
```

2. Installer `mc` (MinIO Client) sur la machine hôte.
3. Installer les libs Python :

```bash
pip install minio
```

Le script va :

* Utiliser `mc` pour gérer **users + policies** (Admin API).
* Utiliser la lib `minio` pour **tester les accès** avec chaque user.

C’est réaliste par rapport à un environnement pro MinIO.

---

## 🧷 3. Les policies MinIO (IAM) 📜

### 3.1. Policy Admin : accès complet sur tous les buckets

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::admin-bucket",
        "arn:aws:s3:::admin-bucket/*",
        "arn:aws:s3:::manager-bucket",
        "arn:aws:s3:::manager-bucket/*",
        "arn:aws:s3:::client-bucket",
        "arn:aws:s3:::client-bucket/*"
      ]
    }
  ]
}
```

### 3.2. Policy Manager

Rappels :

* Full sur `manager-bucket`
* Pas de delete sur les autres

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ManagerOwnBucketFullAccess",
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::manager-bucket",
        "arn:aws:s3:::manager-bucket/*"
      ]
    },
    {
      "Sid": "ManagerOtherBucketsNoDelete",
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::admin-bucket",
        "arn:aws:s3:::admin-bucket/*",
        "arn:aws:s3:::client-bucket",
        "arn:aws:s3:::client-bucket/*"
      ]
    }
  ]
}
```

⚠️ On **n’ajoute pas** `DeleteObject` ni `DeleteBucket` sur les autres buckets ⇒ refusé par défaut.

### 3.3. Policy Client

Rappels :

* Full sur `client-bucket`
* Lecture seule sur `admin-bucket` et `manager-bucket`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ClientOwnBucketFullAccess",
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::client-bucket",
        "arn:aws:s3:::client-bucket/*"
      ]
    },
    {
      "Sid": "ClientReadOnlyOtherBuckets",
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::admin-bucket",
        "arn:aws:s3:::admin-bucket/*",
        "arn:aws:s3:::manager-bucket",
        "arn:aws:s3:::manager-bucket/*"
      ]
    }
  ]
}
```

---

## 🧪 4. TP : Script Python complet

🎓 Objectif pédagogique :

* Montrer comment **automatiser la configuration IAM MinIO**
* Montrer comment **vérifier les droits** par code
* Habituer les apprenants à **penser en tests d’accès** (comme un QA / SRE)

Le script ci-dessous :

1. Configure l’alias `mc`
2. Crée les buckets
3. Crée les policies (fichiers temporaires)
4. Crée les users et leur associe les policies
5. Vérifie les droits de chaque user par des opérations S3
6. Affiche clairement ✅ / ❌ pour chaque test

> À adapter si tu veux d’autres noms/mots de passe.

```python
import json
import os
import subprocess
from minio import Minio
from minio.error import S3Error

# =========================
# CONFIG GÉNÉRALE
# =========================

MINIO_ENDPOINT = "localhost:9000"
ROOT_USER = "rootuser"
ROOT_PASS = "rootpass123"

ADMIN_USER = "admin-user"
ADMIN_PASS = "AdminPass123"

MANAGER_USER = "manager-user"
MANAGER_PASS = "ManagerPass123"

CLIENT_USER = "client-user"
CLIENT_PASS = "ClientPass123"

ADMIN_BUCKET = "admin-bucket"
MANAGER_BUCKET = "manager-bucket"
CLIENT_BUCKET = "client-bucket"

ADMIN_POLICY_NAME = "admin-full-policy"
MANAGER_POLICY_NAME = "manager-policy"
CLIENT_POLICY_NAME = "client-policy"

MC_ALIAS = "local"

# =========================
# HELPERS
# =========================

def run(cmd, check=True):
    """Exécute une commande shell et affiche la sortie."""
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    if check and result.returncode != 0:
        raise SystemExit(f"Erreur commande: {' '.join(cmd)}")
    return result

def write_policy_file(name, content):
    """Écrit un fichier JSON de policy."""
    filename = f"{name}.json"
    with open(filename, "w") as f:
        json.dump(content, f, indent=2)
    print(f"Policy écrite dans {filename}")
    return filename

def create_minio_client(access_key, secret_key):
    return Minio(
        MINIO_ENDPOINT,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )

def expect_success(action_desc, func, *args, **kwargs):
    print(f"  ✓ {action_desc} (attendu: SUCCÈS)")
    try:
        func(*args, **kwargs)
        print("    -> OK")
    except S3Error as e:
        print(f"    -> ÉCHEC INATTENDU: {e}")
        raise

def expect_failure(action_desc, func, *args, **kwargs):
    print(f"  ✓ {action_desc} (attendu: REFUS)")
    try:
        func(*args, **kwargs)
        print("    -> PROBLÈME: l'action a RÉUSSI alors qu'elle devait échouer")
        raise SystemExit("Test de sécurité NON respecté.")
    except S3Error as e:
        print(f"    -> Refus OK ({e.code})")

# =========================
# 1. CONFIG MC + BUCKETS
# =========================

def setup_minio():
    print("\n=== Étape 1 : Configuration de l'alias mc ===")
    run(["mc", "alias", "set", MC_ALIAS, f"http://{MINIO_ENDPOINT}", ROOT_USER, ROOT_PASS])

    print("\n=== Étape 2 : Création des buckets ===")
    for bucket in [ADMIN_BUCKET, MANAGER_BUCKET, CLIENT_BUCKET]:
        run(["mc", "mb", f"{MC_ALIAS}/{bucket}"], check=False)  # ignore erreur si existe déjà

# =========================
# 2. POLICIES
# =========================

def create_policies():
    print("\n=== Étape 3 : Création des policies ===")

    admin_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:*"],
            "Resource": [
                f"arn:aws:s3:::{ADMIN_BUCKET}",
                f"arn:aws:s3:::{ADMIN_BUCKET}/*",
                f"arn:aws:s3:::{MANAGER_BUCKET}",
                f"arn:aws:s3:::{MANAGER_BUCKET}/*",
                f"arn:aws:s3:::{CLIENT_BUCKET}",
                f"arn:aws:s3:::{CLIENT_BUCKET}/*"
            ]
        }]
    }

    manager_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ManagerOwnBucketFullAccess",
                "Effect": "Allow",
                "Action": ["s3:*"],
                "Resource": [
                    f"arn:aws:s3:::{MANAGER_BUCKET}",
                    f"arn:aws:s3:::{MANAGER_BUCKET}/*"
                ]
            },
            {
                "Sid": "ManagerOtherBucketsNoDelete",
                "Effect": "Allow",
                "Action": [
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": [
                    f"arn:aws:s3:::{ADMIN_BUCKET}",
                    f"arn:aws:s3:::{ADMIN_BUCKET}/*",
                    f"arn:aws:s3:::{CLIENT_BUCKET}",
                    f"arn:aws:s3:::{CLIENT_BUCKET}/*"
                ]
            }
        ]
    }

    client_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ClientOwnBucketFullAccess",
                "Effect": "Allow",
                "Action": ["s3:*"],
                "Resource": [
                    f"arn:aws:s3:::{CLIENT_BUCKET}",
                    f"arn:aws:s3:::{CLIENT_BUCKET}/*"
                ]
            },
            {
                "Sid": "ClientReadOnlyOtherBuckets",
                "Effect": "Allow",
                "Action": [
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{ADMIN_BUCKET}",
                    f"arn:aws:s3:::{ADMIN_BUCKET}/*",
                    f"arn:aws:s3:::{MANAGER_BUCKET}",
                    f"arn:aws:s3:::{MANAGER_BUCKET}/*"
                ]
            }
        ]
    }

    admin_file = write_policy_file(ADMIN_POLICY_NAME, admin_policy)
    manager_file = write_policy_file(MANAGER_POLICY_NAME, manager_policy)
    client_file = write_policy_file(CLIENT_POLICY_NAME, client_policy)

    run(["mc", "admin", "policy", "add", MC_ALIAS, ADMIN_POLICY_NAME, admin_file])
    run(["mc", "admin", "policy", "add", MC_ALIAS, MANAGER_POLICY_NAME, manager_file])
    run(["mc", "admin", "policy", "add", MC_ALIAS, CLIENT_POLICY_NAME, client_file])

# =========================
# 3. USERS + ATTACH POLICIES
# =========================

def create_users():
    print("\n=== Étape 4 : Création des users et association des policies ===")

    run(["mc", "admin", "user", "add", MC_ALIAS, ADMIN_USER, ADMIN_PASS], check=False)
    run(["mc", "admin", "policy", "set", MC_ALIAS, ADMIN_POLICY_NAME, f"user={ADMIN_USER}"])

    run(["mc", "admin", "user", "add", MC_ALIAS, MANAGER_USER, MANAGER_PASS], check=False)
    run(["mc", "admin", "policy", "set", MC_ALIAS, MANAGER_POLICY_NAME, f"user={MANAGER_USER}"])

    run(["mc", "admin", "user", "add", MC_ALIAS, CLIENT_USER, CLIENT_PASS], check=False)
    run(["mc", "admin", "policy", "set", MC_ALIAS, CLIENT_POLICY_NAME, f"user={CLIENT_USER}"])

# =========================
# 4. TESTS DE VÉRIFICATION
# =========================

def upload_test_object(client, bucket, object_name, content):
    from io import BytesIO
    data = BytesIO(content.encode("utf-8"))
    client.put_object(bucket, object_name, data, length=len(content))

def delete_test_object(client, bucket, object_name):
    client.remove_object(bucket, object_name)

def list_bucket(client, bucket):
    return list(client.list_objects(bucket, recursive=True))

def get_test_object(client, bucket, object_name):
    data = client.get_object(bucket, object_name)
    body = data.read().decode("utf-8")
    data.close()
    data.release_conn()
    return body

def verify_admin():
    print("\n=== Vérification ADMIN ===")
    c = create_minio_client(ADMIN_USER, ADMIN_PASS)

    # Admin : doit tout pouvoir faire partout
    for bucket in [ADMIN_BUCKET, MANAGER_BUCKET, CLIENT_BUCKET]:
        obj = f"test-admin-{bucket}.txt"
        expect_success(f"ADMIN: upload dans {bucket}", upload_test_object, c, bucket, obj, "hello")
        expect_success(f"ADMIN: lecture dans {bucket}", get_test_object, c, bucket, obj)
        expect_success(f"ADMIN: suppression dans {bucket}", delete_test_object, c, bucket, obj)
        expect_success(f"ADMIN: list dans {bucket}", list_bucket, c, bucket)

def verify_manager():
    print("\n=== Vérification MANAGER ===")
    c = create_minio_client(MANAGER_USER, MANAGER_PASS)

    # 1) Son bucket : full access
    obj = "manager-own.txt"
    expect_success("MANAGER: upload dans son bucket", upload_test_object, c, MANAGER_BUCKET, obj, "ok")
    expect_success("MANAGER: read dans son bucket", get_test_object, c, MANAGER_BUCKET, obj)
    expect_success("MANAGER: delete dans son bucket", delete_test_object, c, MANAGER_BUCKET, obj)

    # 2) Buckets des autres : pas de delete

    # Sur admin-bucket
    obj_admin = "from-manager.txt"
    expect_success("MANAGER: upload dans admin-bucket", upload_test_object, c, ADMIN_BUCKET, obj_admin, "ok")
    expect_success("MANAGER: read dans admin-bucket", get_test_object, c, ADMIN_BUCKET, obj_admin)
    expect_failure("MANAGER: delete dans admin-bucket (doit être refusé)", delete_test_object, c, ADMIN_BUCKET, obj_admin)

    # Sur client-bucket
    obj_client = "from-manager.txt"
    expect_success("MANAGER: upload dans client-bucket", upload_test_object, c, CLIENT_BUCKET, obj_client, "ok")
    expect_success("MANAGER: read dans client-bucket", get_test_object, c, CLIENT_BUCKET, obj_client)
    expect_failure("MANAGER: delete dans client-bucket (doit être refusé)", delete_test_object, c, CLIENT_BUCKET, obj_client)

def verify_client():
    print("\n=== Vérification CLIENT ===")
    c = create_minio_client(CLIENT_USER, CLIENT_PASS)

    # 1) Son bucket : full access
    obj = "client-own.txt"
    expect_success("CLIENT: upload dans son bucket", upload_test_object, c, CLIENT_BUCKET, obj, "ok")
    expect_success("CLIENT: read dans son bucket", get_test_object, c, CLIENT_BUCKET, obj)
    expect_success("CLIENT: delete dans son bucket", delete_test_object, c, CLIENT_BUCKET, obj)

    # 2) Buckets admin & manager : read-only

    # admin-bucket : on suppose qu'il y a déjà un objet créé par admin/manager
    expect_success("CLIENT: list admin-bucket", list_bucket, c, ADMIN_BUCKET)
    expect_failure("CLIENT: upload dans admin-bucket (doit échouer)", upload_test_object, c, ADMIN_BUCKET, "client-in-admin.txt", "nope")

    # manager-bucket
    expect_success("CLIENT: list manager-bucket", list_bucket, c, MANAGER_BUCKET)
    expect_failure("CLIENT: upload dans manager-bucket (doit échouer)", upload_test_object, c, MANAGER_BUCKET, "client-in-manager.txt", "nope")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("=== TP MinIO Policies : Admin / Manager / Client ===")

    setup_minio()
    create_policies()
    create_users()
    verify_admin()
    verify_manager()
    verify_client()

    print("\n✅ Tous les tests de droits ont été exécutés.")
    print("Si aucune erreur critique n'est apparue, la configuration MinIO est CONFORME au cahier des charges.")
```


