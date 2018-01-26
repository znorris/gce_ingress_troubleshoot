# README
This repo is meant to assist in the troubleshooting of a GKE ingress controller issue.

## Issue
Why would I experience downtime when I update more than one backend service at a time, but not when I updated a single backend? (Does it have something to do with the fact that the ingress no longer references the `app-z` backend?)

### Example
For instance, I had a single app & service handling requests for several hosts.
```
apiVersion: v1
items:
- apiVersion: extensions/v1beta1
  kind: Ingress
  spec:
    rules:
    - host: a.host
      http:
        paths:
        - backend:
            serviceName: app-z
            servicePort: 80
    - host: b.host
      http:
        paths:
        - backend:
            serviceName: app-z
            servicePort: 80
    - host: c.host
      http:
        paths:
        - backend:
            serviceName: app-z
            servicePort: 80
```
```
NAME          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
app-z         NodePort    10.0.0.1        <none>        80:30001/TCP     1d
```

I then added a new app/deployment and service for each of the three hosts.
```
NAME          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
app-a         NodePort    10.0.0.1        <none>        80:30002/TCP     1d
app-b         NodePort    10.0.0.1        <none>        80:30003/TCP     1d
app-c         NodePort    10.0.0.1        <none>        80:30004/TCP     1d
app-z         NodePort    10.0.0.1        <none>        80:30001/TCP     1d
```

I verified that the apps were responding to HCs and that the NodePorts were working.
Once that was complete I updated a single hosts backend in the ingress (`a.host`).
```
apiVersion: v1
items:
- apiVersion: extensions/v1beta1
  kind: Ingress
  spec:
    rules:
    - host: a.host
      http:
        paths:
        - backend:
            serviceName: app-a
            servicePort: 80
    - host: b.host
      http:
        paths:
        - backend:
            serviceName: app-z
            servicePort: 80
    - host: c.host
      http:
        paths:
        - backend:
            serviceName: app-z
            servicePort: 80
```


I waited for the load balancer to update, and for the new service/app to respond to this traffic. I also verified in the cloud console that the health check associated with this new backend was passing. This is how I would expect everything to work and it had zero downtime.

I then decided that I had 5 more hosts to update on the ingress controller, and that it would be faster to update the remaining hosts all at once.
```
apiVersion: v1
items:
- apiVersion: extensions/v1beta1
  kind: Ingress
  spec:
    rules:
    - host: a.host
      http:
        paths:
        - backend:
            serviceName: app-a
            servicePort: 80
    - host: b.host
      http:
        paths:
        - backend:
            serviceName: app-b
            servicePort: 80
    - host: c.host
      http:
        paths:
        - backend:
            serviceName: app-c
            servicePort: 80
```

Once that was done I began to see failing requests (HTTP 502 from load balancer) for roughly 5 minutes for those hosts I had changed in bulk. After the 5 minutes requests were OK. During that time the load balancer was logging these 502's:
```
jsonPayload:{
  @type:  "type.googleapis.com/google.cloud.loadbalancing.type.LoadBalancerLogEntry"   
  statusDetails:  "failed_to_connect_to_backend"   
 }
 ```

I then checked that the appropriate service/app was responding to requests for all hosts in the ingress controller. Everything looked good. I then went into cloud console and verified that the `app-z` backend was no longer present and that its HCs had been cleaned up as well. They were, so I then removed the old service and deployment/app.
```
NAME          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
app-a         NodePort    10.0.0.1        <none>        80:30002/TCP     1d
app-b         NodePort    10.0.0.1        <none>        80:30003/TCP     1d
app-c         NodePort    10.0.0.1        <none>        80:30004/TCP     1d
```
I'm now in my desired state and everything is working as expected.
