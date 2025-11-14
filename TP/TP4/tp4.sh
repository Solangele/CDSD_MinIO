PS C:\Users\Administrateur\Desktop\DataLake> mc alias set angele http://localhost:9000 minioadmin minioadmin
Added `angele` successfully.

PS C:\Users\Administrateur\Desktop\DataLake> mc mb angele/bronze
Bucket created successfully `angele/bronze`.
PS C:\Users\Administrateur\Desktop\DataLake> mc mb angele/silver
Bucket created successfully `angele/silver`.
PS C:\Users\Administrateur\Desktop\DataLake> mc mb angele/gold
Bucket created successfully `angele/gold`.


PS C:\Users\Administrateur\Desktop\DataLake> docker build -t generator -f .\TP\TP4\generator\Dockerfile .\TP\TP4
[+] Building 27.2s (12/12) FINISHED                                                                                                                                                                      docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                                                                                                     0.0s
 => => transferring dockerfile: 521B                                                                                                                                                                                     0.0s 
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                                                                                      0.7s 
 => [auth] library/python:pull token for registry-1.docker.io                                                                                                                                                            0.0s 
 => [internal] load .dockerignore                                                                                                                                                                                        0.1s
 => => transferring context: 2B                                                                                                                                                                                          0.0s 
 => [1/6] FROM docker.io/library/python:3.11-slim@sha256:e4676722fba839e2e5cdb844a52262b43e90e56dbd55b7ad953ee3615ad7534f                                                                                                2.1s 
 => => resolve docker.io/library/python:3.11-slim@sha256:e4676722fba839e2e5cdb844a52262b43e90e56dbd55b7ad953ee3615ad7534f                                                                                                0.1s 
 => => sha256:65868b001a40155a1d3f5aa7f5a10ba02a7d55697301839dc047c9d549b670bc 248B / 248B                                                                                                                               0.3s 
 => => sha256:f002d17b63fe84a7f8a66f20cfa63aec4f6cd2a44069f05b6296b0abfcf2a8e1 14.36MB / 14.36MB                                                                                                                         1.2s 
 => => sha256:1ee9c106547f05aa380c4cdec2837c546439943d73d965a3fc49f228dc8be993 1.29MB / 1.29MB                                                                                                                           0.5s
 => => extracting sha256:1ee9c106547f05aa380c4cdec2837c546439943d73d965a3fc49f228dc8be993                                                                                                                                0.2s
 => => extracting sha256:f002d17b63fe84a7f8a66f20cfa63aec4f6cd2a44069f05b6296b0abfcf2a8e1                                                                                                                                0.6s 
 => => extracting sha256:65868b001a40155a1d3f5aa7f5a10ba02a7d55697301839dc047c9d549b670bc                                                                                                                                0.0s
 => [internal] load build context                                                                                                                                                                                        0.1s
 => => transferring context: 5.53kB                                                                                                                                                                                      0.0s
 => [2/6] WORKDIR /app                                                                                                                                                                                                   0.1s 
 => [3/6] COPY requirements.txt /app/requirements.txt                                                                                                                                                                    0.1s
 => [4/6] RUN pip install --no-cache-dir -r /app/requirements.txt                                                                                                                                                       14.0s
 => [5/6] COPY generator/app.py /app/app.py                                                                                                                                                                              0.2s
 => [6/6] COPY generator/util.py /app/util.py                                                                                                                                                                            0.1s
 => exporting to image                                                                                                                                                                                                   9.5s
 => => exporting layers                                                                                                                                                                                                  6.8s
 => => exporting manifest sha256:45d43a1f1f6ead077a41de34037d3c5e7f37bf638ab146184ae1a325081011b7                                                                                                                        0.0s
 => => exporting config sha256:d96f6a4a026b2ad09265fdd4c6cd5b3afd747673ec7d100510009b61bcff2c1a                                                                                                                          0.0s
 => => exporting attestation manifest sha256:66642bc7dca0ea45f3b2ac1c803901a892b088594f6968a2fcbc40d1232c0006                                                                                                            0.1s
 => => exporting manifest list sha256:0ed9942b6b095437b3dbabfd33c3c0d4a51645c32d67c2fa1a1fa1e51102f9ca                                                                                                                   0.0s 
 => => naming to docker.io/library/generator:latest                                                                                                                                                                      0.0s
 => => unpacking to docker.io/library/generator:latest                                                                                                                                                                   2.5s 

View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/m0meyv57vl17sfo1ce21uv4pp