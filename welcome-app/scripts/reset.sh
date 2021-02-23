#!/bin/bash

echo "Copying config.."
cp ~/.kube/istio ~/.kube/config

echo "Deleting backend authpolicy.."
kubectl delete authorizationpolicy -n welcome-app backend-authpolicy

echo "Deleting application to reset it.."
kubectl delete -f ../base-manifests

echo "Confirming namespace was terminated.."
while [ ! -n "$(kubectl get namespace welcome-app 2>&1 > /dev/null)" ]; do
    sleep 1
done

echo "Creating namespace.."
kubectl apply -f ../base-manifests/namespace.yaml
sleep 3

echo "Copying pull secret from authservice namespace.."
kubectl get secret private-registry --namespace=authservice --export -o yaml | kubectl apply --namespace=welcome-app -f -

echo "Creating application resources.."
kubectl apply -f ../base-manifests

echo "Patching envoyFilter selector.."
kubectl get envoyfilter -n istio-system authservice -o yaml | sed 's/auth: enabled/auth: none/g' | kubectl apply -f -