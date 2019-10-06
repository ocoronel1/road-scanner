ufw allow 32001/tcp

mkdir -m 777 /data
mkfs.ext4 /dev/xvdc
echo '/dev/xvdc /data                   ext4    defaults,noatime        0 0' >> /etc/fstab
mount /data

apt-get update
apt install python3-pip -y
apt install unzip -y

docker build -t road_scanner -f Dockerfile.dev .

