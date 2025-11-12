docker stop $(docker ps -q)  

docker rm $(docker ps -qa)  


  docker run -d `
  --name minio `
  -p 9000:9000 `
  -p 9001:9001 `
  -e "MINIO_ROOT_USER=minioadmin" `
  -e "MINIO_ROOT_PASSWORD=minioadmin" `
  -v "C:\Users\Administrateur\Documents\data-lake\demo\minio-data:/data" `
  quay.io/minio/minio server /data --console-address ":9001"
  
  
https://docs.min.io/enterprise/aistor-object-store/reference/cli/?tab=quickstart-windows


Invoke-WebRequest https://dl.min.io/client/mc/release/windows-amd64/mc.exe -OutFile C:\mc.exe

setx PATH "$($env:PATH);C:\"

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser


https://docs.min.io/enterprise/aistor-object-store/reference/cli/?tab=mc-alias-examples-aistor-server


 mc alias set angele http://localhost:9000 minioadmin minioadmin (mettre angele)
 
 
 mc --help
   6 mc admin --help
   7 mc admin info --help
   8 mc admin info angele
   9 mc --help
  10 mc mb angele/mon-bucket
  11 mc mb angele/mon-second-bucket
  12 mc ls angele
  13 mc stat angele/demo
 mc rb --force angele/mon-second-bucket


mc cp .\data.csv angele/mon-bucket/

 mc cp angele/mon-bucket/fichier3.txt .\data\.