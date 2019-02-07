# Adsrental Dashboard

## Docker Setup

### Prerequisites

#### Mac OS

You can find all instructions [here](https://docs.docker.com/docker-for-mac/install/)

#### Linux

```bash
curl -fsSL get.docker.com -o- | bash
sudo usermod -aG docker $(whoami)
logout # this is needed to be able to use docker as current user
sudo curl -L --fail https://github.com/docker/compose/releases/download/1.18.0/run.sh -o /usr/local/bin/docker-compose
sudo chmod a+x /usr/local/bin/docker-compose
```

### Local development mode

```bash
./scripts/install-venv.sh -d
docker-compose up --build web

# get latest DB backup
scp adsrental:/mnt/volume-nyc3-01/mysqldumps/dump_2019_02_06.sql.gz .

# install in to your running local DB
zcat ./dump_2019_02_06.sql.gz | mysql -u root -h 0.0.0.0 -P 23306 adsrental

# migrate just in case
docker-compose run web python manage.py migrate

# fix permissions for dbdata
sudo chmod a+rwx -R dbdata1

# open https://localhost:7443/admin/ in your browser
```

### Local production-like mode (remote DB)

```bash
docker-compose -f docker-compose.localdev.yml up --build
```

### Deploy

```bash
cd ~
git clone git@github.com:ads-inc/dashboard.git
ln -s ~/dashboard/scripts/pull.sh pull.sh
./pull.sh
```

Install crontab

```bash
cat crontab.txt | crontab
```

### RDP client

Use it to run automated commands or just quickly connect to EC2

```bash
./scripts/rdp.py <rpid>
```

### Fix EC2

Use this command to sync up running EC2 with ones you need

```bash
docker-compose run web python manage.py fix_ec2 --launch --terminate
```
