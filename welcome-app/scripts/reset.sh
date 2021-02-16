#!/bin/bash

echo "Deleting backend authpolicy.."
kubectl delete authorizationpolicy -n welcome-app backend-authpolicy
kubectl delete authorizationpolicy -n welcome-app internal-tester-authpolicy

echo "Deleting application to reset it.."
kubectl delete -f ../base-manifests

echo "Confirming namespace was terminated.."
while [ ! -n "$(kubectl get namespace welcome-app 2>&1 > /dev/null)" ]; do
    sleep 1
done

echo "Creating namespace.."
kubectl apply -f ../base-manifests/namespace.yaml
kubectl apply -f ../base-manifests/tester-namespace.yaml
sleep 3

echo "Creating application resources.."
kubectl apply -f ../base-manifests