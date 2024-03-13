# certificate-expiry
A python script to check if certificates of provided list of hosts have expired or not. It will also determine expiry date for certificate if its not available in local trust store

# how to run
> pip install -r requirements.txt
> 
> python certificate-check.py host.com:8081 host2.com:8081

Note: 
- If no port provided it will use default 443 SSL port of HTTP
