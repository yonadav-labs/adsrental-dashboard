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
sudo curl -L https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod a+x /usr/local/bin/docker-compose
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
