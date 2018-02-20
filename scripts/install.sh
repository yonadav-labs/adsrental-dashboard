apt install -y libvirt-bin qemu-kvm
usermod -a -G libvirtd $(whoami)
newgrp libvirtd

# if [ ! -f "/usr/local/bin/docker-machine-driver-kvm2" ]; then
#     curl -LO https://github.com/dhiltgen/docker-machine-kvm/releases/download/v0.10.0/docker-machine-driver-kvm2 && chmod +x docker-machine-driver-kvm2 && mv docker-machine-driver-kvm2 /usr/local/bin/
# fi
if [ ! -f "/usr/local/bin/kubectl" ]; then
    curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.9.3/bin/linux/amd64/kubectl && chmod +x kubectl && mv kubectl /usr/local/bin/
fi
if [ ! -f "/usr/local/bin/minicube" ]; then
    curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.25.0/minikube-linux-amd64 && chmod +x minikube && mv minikube /usr/local/bin/
fi

export MINIKUBE_WANTUPDATENOTIFICATION=false
export MINIKUBE_WANTREPORTERRORPROMPT=false
export MINIKUBE_HOME=$HOME
export CHANGE_MINIKUBE_NONE_USER=true
mkdir $HOME/.kube || true
touch $HOME/.kube/config

export KUBECONFIG=$HOME/.kube/config
sudo -E ./minikube start --vm-driver=none

# this for loop waits until kubectl can access the api server that Minikube has created
for i in {1..150}; do # timeout for 5 minutes
   ./kubectl get po &> /dev/null
   if [ $? -ne 1 ]; then
      break
  fi
  sleep 2
done
