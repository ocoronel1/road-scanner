# RoadScanner
This UC Berkeley Master of Information in Data Science capstone project was developed by
[Spyros Garyfallos](mailto:spiros.garifallos@berkeley.edu), [Sergio Ferro](mailto:sm.ferro54@ischool.berkeley.edu), [Kaitlin Swinnerton](mailto:kswinnerton@ischool.berkeley.edu) and [Arjun Chakraborty](archakra@ischool.berkeley.edu)

## 1. Provision a cloud GPU machine

### Using AWS

If using AWS, as assumed by these setup instructions, provision an Ubuntu 18.04 `p2.xlarge` instance.  It's got older GPUs (Tesla K80) but is much cheaper.  Make sure to upgrade the storage space (e.g. 500 GB).  Also, make sure to pick a prebuilt Deep Learning AMI during the first step of the provisioning process. The most current version as of writing is `Deep Learning AMI (Ubuntu) Version 23.0 - ami-058f26d848e91a4e8`. This will already have `docker` and `nvidia-docker` pre-installed and will save you a lot of manual installation "fun".

### Using IBM Cloud

Provision a server to run the training code. You can you this server as your development environment too.  Using image `2263543`, `docker` and `nvidia-docker` are already installed.

Install the CLI, add your ssh public key, and get the key id
```
curl -fsSL https://clis.ng.bluemix.net/install/linux | sh
ibmcloud login
ibmcloud sl security sshkey-add LapKey --in-file ~/.ssh/id_rsa.pub
ibmcloud sl security sshkey-list
```

Provision a V100 using this key id

```
ibmcloud sl vs create \
    --datacenter=wdc07 \
    --hostname=v100a \
    --domain=dev \
    --image=2263543 \
    --billing=hourly \
    --network 1000 \
    --key={YOUR_KEY_ID} \
    --flavor AC2_8X60X100 \
    --san
```

Alternately, provision a slower, cheaper P100:

```
ibmcloud sl vs create \
  --datacenter=wdc07 \
  --hostname=p100a \
  --domain=dev \
  --image=2263543 \
  --billing=hourly \
  --network 1000 \
  --key={YOUR_KEY_ID} \
  --flavor AC1_8X60X100 \
  --san
```

	
Wait for the provisioning completion 
```
watch ibmcloud sl vs list
```

SSH on this host to setup the container.

```
ssh -i ~/.ssh/id_rsa {SERVER_IP}
```

## 2. Clone the project repo

If you haven't already, clone the project Git repo to your instance.  Doing so in your home directory is convenient, and this document assumes you have done so.

```
cd ~
git clone https://github.com/paloukari/road-scanner
```

## 3. Get the data and create the `road_scanner_dev` Docker image

### GPU OPTION: Build our `road_scanner_dev` base Docker image

In the project repo, `cd` into the `road-scanner/networks` directory:

```
cd ~/road-scanner/networks
chmod +x setup.sh
./setup.sh {YOUR_AWS_ID} {YOUR_AWS_KEY}
```

The [setup.sh](setup.sh) script downloads the data and creates the container. The AWS credentials are required because the script will download the data from an s3.
This script will also open 32001 port to allow remote debugging from VsCode into the container.

Alternativelly, run the script code:

```
ufw allow 32001/tcp

apt-get install -y awscli
aws configure set aws_access_key_id $1
aws configure set aws_secret_access_key $2

aws s3 cp s3://w210-data/images/non-scenic.zip ./
unzip ./non-scenic.zip -d ./.data/non-scenic
rm ./non-scenic.zip

aws s3 cp s3://w210-data/images/scenic.zip ./
unzip ./scenic.zip -d ./.data/scenic
rm ./scenic.zip
```

To build the image in the cloud:

```
docker build -t road_scanner_dev -f Dockerfile.dev .
docker build -t road_scanner_tf2_dev -f Dockerfile.tf2.dev .
```

## 4. Launch an `road_scanner_dev` Docker container

Run the `road_scanner_dev` Docker container with the following args.  

```
docker run \
    --rm \
    --runtime=nvidia \
    --name road_scanner_dev \
    -ti \
    -e JUPYTER_ENABLE_LAB=yes \
    -v /data:/data \
    -p 8888:8888 \
    -p 4040:4040 \
    -p 32001:22 \
    road_scanner_dev
```

Run the `road_scanner_tf2_dev` Docker container with the following args.  

```
docker run \
    --rm \
    --runtime=nvidia \
    --name road_scanner_tf2_dev \
    -ti \
    -e JUPYTER_ENABLE_LAB=yes \
    -v /data:/data \
    -p 8888:8888 \
    -p 4040:4040 \
    -p 32003:22 \
    road_scanner_tf2_dev
```
To start the jupyter server, run:
`bash -c 'source /etc/bash.bashrc && jupyter notebook --notebook-dir=/data --ip 0.0.0.0 --no-browser --allow-root'`

You will see them listed as `road_scanner_dev ` and `road_scanner_ft2d_ev ` when you run `docker ps -a`.  

### Verify Keras can see the GPU

Once inside the container, try running:

```
nvidia-smi
```
## 5. Start training

To start the default training pipeline, run
```
python3 networks/src/train.py
```

## 6. Run TensorBoard
After starting the training pipeline, to see the live TensorBoard results run:

```tensorboard --logdir=/data/road-scanner/networks/.results/tensorboard/ --port=4040```
