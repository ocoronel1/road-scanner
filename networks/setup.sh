ufw allow 32001/tcp

mkdir -m 777 /data
mkfs.ext4 /dev/xvdc
echo '/dev/xvdc /data                   ext4    defaults,noatime        0 0' >> /etc/fstab
mount /data

apt-get update
apt install python3-pip -y
apt install unzip -y

apt-get install -y awscli
aws configure set aws_access_key_id $1
aws configure set aws_secret_access_key $2

aws s3 cp s3://w210-data/images/non-scenic.zip ./
unzip ./non-scenic.zip -d ./.data/non-scenic
rm ./non-scenic.zip

aws s3 cp s3://w210-data/images/scenic.zip ./
unzip ./scenic.zip -d ./.data/scenic
rm ./scenic.zip

docker build -t road_scanner_dev -f Dockerfile.dev .

