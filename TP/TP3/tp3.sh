# Simulation d'une organisation avec : 
# admin : super utilisateur ((GET, PUT, DELETE, LIST) sur les 3 buckets)
# manager : responsable métier (GET, PUT, DELETE, LIST sur son bucket, GET, PUT, LIST sur les deux autres)
# client : utilisateur final (GET, PUT, DELETE, LIST sur son bucket, GET, LIST sur les deux autres)

# Buckets :
# admin-bucket 
# manager-bucket 
# client-bucket


mc alias set tp3 http://localhost:9000 minioadmin minioadmin

PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc mb tp3/admin-bucket
Bucket created successfully `tp3/admin-bucket`.
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc mb tp3/manager-bucket
Bucket created successfully `tp3/manager-bucket`.
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc mb tp3/client-bucket



PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin policy create tp3 admin-bucket .\admin-bucket.json      
Created policy `admin-bucket` successfully.
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin policy create tp3 manager-bucket .\manager-bucket.json  
Created policy `manager-bucket` successfully.
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin policy create tp3 client-bucket .\client-bucket.json  
Created policy `client-bucket` successfully.


PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin user add tp3 admin_user "admin_pass"
Added user `admin_user` successfully.
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin user add tp3 manager_user "manager_pass"
Added user `manager_user` successfully.
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin user add tp3 client_user "client_pass"
Added user `client_user` successfully.


PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin policy attach tp3 admin-bucket --user admin_user
Attached Policies: [admin-bucket]
To User: admin_user
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin policy attach tp3 manager-bucket --user manager_user
Attached Policies: [manager-bucket]
To User: manager_user
PS C:\Users\Administrateur\Desktop\DataLake\TP\TP3> mc admin policy attach tp3 client-bucket --user client_user
Attached Policies: [client-bucket]
To User: client_user

