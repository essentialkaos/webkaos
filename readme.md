<p align="center">
<img width="300" height="150" src="https://essentialkaos.com/github/webkaos-v3.png"/>
</p>

`webkaos` is a web-server based on latest version of [Nginx](http://nginx.org).

## Feature list

* Improved default SSL preferencies (A+ by default on [SSL Labs](https://www.ssllabs.com/ssltest/analyze.html?d=essentialkaos.com))
* Improved SSL/TLS performance
* [TCP Fast Open](https://en.wikipedia.org/wiki/TCP_Fast_Open) support (_only for CentOS7/RHEL7_)
* [Lua](https://github.com/openresty/lua-nginx-module), [Headers More](https://github.com/openresty/headers-more-nginx-module) and [PageSpeed](https://github.com/pagespeed/ngx_pagespeed) module from the box
* Improved SysV script
* Well-looking error pages
* Improved design of index pages
* Performance tuning for highload

## Installation

#### From ESSENTIAL KAOS Public repo for RHEL6/CentOS6

````
yum install -y https://yum.kaos.io/6/release/i386/kaos-repo-7.0-0.el6.noarch.rpm
yum install webkaos
````

#### From ESSENTIAL KAOS Public repo for RHEL7/CentOS7

````
yum install -y https://yum.kaos.io/7/release/x86_64/kaos-repo-7.0-0.el7.noarch.rpm
yum install webkaos
````

#### Using [rpmbuilder](https://github.com/essentialkaos/rpmbuilder)

````
... install and configure rpmbuilder there
git clone https://github.com/essentialkaos/webkaos.git
cd webkaos/
rpmbuilder webkaos.spec -dl SOURCES/
rpmbuilder webkaos.spec -1 -V -di
````

## License

BSD 2-clause
