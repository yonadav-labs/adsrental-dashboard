# Trusted Access

## Docker Setup

### Prerequisites

#### Mac OS

You can find all instructions [here](https://docs.docker.com/docker-for-mac/install/)

#### Linux

```bash
curl -fsSL get.docker.com -o- | bash
sudo usermod -aG docker $(whoami)
logout # this is needed to be able to use docker as current user
sudo curl -L https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod a+x /usr/local/bin/docker-compose

pip install -U awscli --user
export PATH=$PATH:~/.local/bin/
echo "export PATH=$PATH:~/.local/bin/" >> ~/.bashrc
aws --version
```

### Local development mode

```bash
docker-compose up --build
```

### Push docker image to ECR

```bash
docker-compose run web /app/scripts/image_push.sh
```

### Local production-like mode (remote DB)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Helpful scripts

```bash
# Update dev lambda
docker-compose run web /app/scripts/update_dev.sh

# Update production lambda
docker-compose run web /app/scripts/update_prod.sh
```
