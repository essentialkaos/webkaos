<p align="center"><a href="#readme"><img src="https://gh.kaos.st/webkaos.svg"/></a></p>

`webkaos` is a web-server based on latest version of [Nginx](http://nginx.org).

## Feature list

* Improved default SSL/TLS preferencies (A+ on [SSL Labs](https://www.ssllabs.com/ssltest/analyze.html?d=essentialkaos.com), [High-Tech Bridge](https://www.htbridge.com/ssl/?id=WHUz0U3v) and [Mozilla Observatory](https://observatory.mozilla.org/analyze.html?host=essentialkaos.com))
* [Dynamic TLS Records](https://blog.cloudflare.com/optimizing-tls-over-tcp-to-reduce-latency/) support
* Latest version of [BoringSSL](https://boringssl.googlesource.com/boringssl/) with some state-of-the-art crypto features
* TLS 1.3 support (RFC 8446)
* [TCP Fast Open](https://en.wikipedia.org/wiki/TCP_Fast_Open) support (only for CentOS7/RHEL7)
* [Lua](https://github.com/openresty/lua-nginx-module) and [Headers More](https://github.com/openresty/headers-more-nginx-module) modules from the box
* [HTTP/2 + SPDY/3.1](https://blog.cloudflare.com/open-sourcing-our-nginx-http-2-spdy-code/) support
* Improved SysV script
* Well-looking error pages
* Improved design of index pages
* Performance tuning for highload

### Installation

#### From ESSENTIAL KAOS Public repo for RHEL6/CentOS6

````
[sudo] yum install -y https://yum.kaos.st/6/release/x86_64/kaos-repo-9.1-0.el6.noarch.rpm
[sudo] yum install webkaos
````

#### From ESSENTIAL KAOS Public repo for RHEL7/CentOS7

````
[sudo] yum install -y https://yum.kaos.st/7/release/x86_64/kaos-repo-9.1-0.el7.noarch.rpm
[sudo] yum install webkaos
````

#### Using [rpmbuilder](https://github.com/essentialkaos/rpmbuilder)

````
... install and configure rpmbuilder there
git clone https://github.com/essentialkaos/webkaos.git
cd webkaos/
rpmbuilder webkaos.spec -dl SOURCES/
rpmbuilder webkaos.spec -1 -V -di
````

### License

BSD 2-clause

<p align="center"><a href="https://essentialkaos.com"><img src="https://gh.kaos.st/ekgh.svg"/></a></p>
