---
title: Installing Docker on Ubuntu
author: Tech Team
last_updated: 2022-01-15
version: 1.0
tags: [docker, installation, ubuntu]
---

# Installing Docker on Ubuntu

This guide walks you through installing Docker on Ubuntu 18.04 LTS.

## Prerequisites

- Ubuntu 18.04 LTS system
- Root or sudo access
- At least 4GB of RAM
- 64-bit processor

## Installation Steps

1. First, update your existing packages:
```bash
sudo apt-get update
sudo apt-get upgrade
```

2. Install required dependencies:
```bash
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
```

3. Add Docker's official GPG key:
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

4. Add Docker repository:
```bash
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
```

5. Install Docker:
```bash
sudo apt-get update
sudo apt-get install docker-ce
```

6. Start and enable Docker:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

7. Verify installation:
```bash
docker --version
sudo docker run hello-world
```

## Post-Installation Steps

To run Docker without sudo, add your user to the docker group:
```bash
sudo usermod -aG docker $USER
```

Log out and log back in for the changes to take effect.

## Troubleshooting

If you encounter the error "Cannot connect to the Docker daemon", make sure the docker service is running:
```bash
sudo systemctl status docker
```

## Version Compatibility

This guide is tested with:
- Docker CE 19.03
- Ubuntu 18.04 LTS

For newer versions of Ubuntu, please check the official Docker documentation. 