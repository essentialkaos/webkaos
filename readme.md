# WEBKAOS

*webkaos* is a web-server based on latest version of Nginx.

### Feature list

* Improved default SSL preferencies (A+ by default on SSL Labs)
* Improved SSL/TLS performance
* Lua, Headers More and PageSpeed module from the box
* Improved SysV script
* Well-looking error pages
* Improved design of index pages
* Performance tuning for highload

### Installation

###### From ESSENTIAL KAOS Public repo for RHEL6/CentOS6

````
yum install -y http://release.yum.kaos.io/i386/kaos-repo-6.8-0.el6.noarch.rpm
yum install webkaos
````

###### Using [rpmbuilder](https://github.com/essentialkaos/rpmbuilder)

````
... install and configure rpmbuilder there
git clone https://github.com/essentialkaos/webkaos.git
cd webkaos/
rpmbuilder webkaos.spec -dl SOURCES/
rpmbuilder webkaos.spec -1 -V
````

### License

BSD 2-clause
