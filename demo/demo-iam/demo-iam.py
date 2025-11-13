# mc alias set local http://localhost:9000 minioadmin minioadmin

# mc alias list


# mc mb local/datalake-bronze
# mc mb local/datalake-silver
# mc mb local/datalake-gold 

# mc admin user add local etl_user "etl_user"

# > mc admin user list local


# https://awspolicygen.s3.amazonaws.com/policygen.html

# arn:aws:s3:::datalake-bronze/*

# Statements added (1)

# Effect
# Allow


# Action
# s3:GetObject
# s3:DeleteObject
# s3:PutObject


# Resource(s)
# arn:aws:s3:::datalake-bronze/*


# Condition(s)
# None


# Remove
# Remove



# ===== va permettre de sortir le code JSON suivant =====
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Sid": "Statement1",
#       "Effect": "Allow",
#       "Action": [
#         "s3:GetObject",
#         "s3:DeleteObject",
#         "s3:PutObject"
#       ],
#       "Resource": "arn:aws:s3:::datalake-bronze/*"
#     }
#   ]
# }

# mc admin policy create local etl-bronze .\demo\demo-iam\etl-policy.json

