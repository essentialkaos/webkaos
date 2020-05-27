<p align="center"><a href="#readme"><img src="https://gh.kaos.st/webkaos.svg"/></a></p>

`webkaos` is a web-server based on the latest version of [Nginx](http://nginx.org).

## Feature list

* Improved default SSL/TLS preferencies (_A+ on [SSL Labs](https://www.ssllabs.com/ssltest/analyze.html?d=essentialkaos.com), [High-Tech Bridge](https://www.htbridge.com/ssl/?id=WHUz0U3v) and [Mozilla Observatory](https://observatory.mozilla.org/analyze/essentialkaos.com)_)
* [Dynamic TLS Records](https://blog.cloudflare.com/optimizing-tls-over-tcp-to-reduce-latency/) support
* The latest version of [BoringSSL](https://boringssl.googlesource.com/boringssl/) with some state-of-the-art crypto features
* TLS 1.3 support (_RFC 8446_)
* [TCP Fast Open](https://en.wikipedia.org/wiki/TCP_Fast_Open) support
* [Lua](https://github.com/openresty/lua-nginx-module) and [Headers More](https://github.com/openresty/headers-more-nginx-module) modules from the box
* [Brotli](https://github.com/eustas/ngx_brotli) and [NAXSI](https://github.com/nbs-system/naxsi) as dynamic modules
* Improved SysV script
* Well-looking error pages
* Improved design of index pages
* Performance tuning for highload

### Installation

#### From ESSENTIAL KAOS Public repo for RHEL7/CentOS7

````
[sudo] yum install -y yum install -y https://yum.kaos.st/kaos-repo-latest.el7.noarch.rpm
[sudo] yum install webkaos
````

#### Using [rpmbuilder](https://github.com/essentialkaos/rpmbuilder)

````
... install and configure rpmbuilder there
git clone https://github.com/essentialkaos/webkaos.git
cd webkaos/
rpmbuilder webkaos.spec -dl SOURCES/
rpmbuilder webkaos.spec -3 -V -di
````

### License

BSD 2-clause

<p align="center"><a href="https://essentialkaos.com"><img src="https://gh.kaos.st/ekgh.svg"/></a></p>
