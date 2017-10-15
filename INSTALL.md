# How to Chef up a rPi


1. Config rasp-config to enable camera and set hostname & enable ssh
2. Configure wpa_suplicant
3. Install Chef:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install ruby awscli bundler git autoconf automake pkgconf libtool libjpeg8-dev build-essential libzip-dev libavformat-dev libavcodec-dev libavutil-dev libswscale-dev libavdevice-dev
mkdir src
git clone https://github.com/Motion-Project/motion.git src/motion
cd src/motion/
autoreconf -fiv && ./configure && make
sudo make install
```
4. This next step takes forever:
```
sudo gem install chef —verbose
```
5. From your chef_repo:
```
knife bootstrap -N NODENAME -x pi -P raspberry --sudo IP_of_rPi
```
6. On your Raspberry Pi (if you need an encrypted databag shared secret):
```
sudo -s
echo <password> | md5sum > /etc/chef/encrypted_data_bag_secret
chmod 400 /etc/chef/encrypted_data_bag_secret
```