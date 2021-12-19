<p align="center"><a href="#readme"><img src="https://gh.kaos.st/webkaos.svg"/></a></p>

`webkaos` is a web-server based on the latest version of [Nginx](http://nginx.org).

## Feature list

* Improved default SSL/TLS preferencies (_A+ on [SSL Labs](https://www.ssllabs.com/ssltest/analyze.html?d=essentialkaos.com), [Immuni Web](https://www.immuniweb.com/ssl/?id=WHUz0U3v), [Mozilla Observatory](https://observatory.mozilla.org/analyze/essentialkaos.com), [CryptCheck](https://tls.imirhil.fr/https/essentialkaos.com) and [Security Headers](https://securityheaders.com/?q=essentialkaos.com&followRedirects=on)_)
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

```bash
sudo yum install -y yum install -y https://yum.kaos.st/kaos-repo-latest.el7.noarch.rpm
sudo yum install webkaos
```

#### Using Docker

Official webkaos images available on [Docker Hub](http://kaos.sh/d/webkaos).

Usage examples:

```bash
docker run --name my-webkaos -v /some/content:/usr/share/webkaos/html:ro -p 8080:80 -d essentialkaos/webkaos:centos7

```

```bash
docker run --name my-webkaos -v /some/content:/usr/share/webkaos/html:ro -p 8080:8080 -d essentialkaos/webkaos:centos7-unprivileged

```

Useful environment variables:

* `WEBKAOS_ENABLE_ENTRYPOINT_LOGS` - Enable logging for actions made by entrypoint script;
* `WEBKAOS_DISABLE_PROC_TUNE` - Disable automatic `worker_processes` tuning;
* `WEBKAOS_DISABLE_BUCKET_TUNE` - Disable automatic `server_names_hash_bucket_size` tuning.


#### Using [rpmbuilder](https://github.com/essentialkaos/rpmbuilder)

```bash
... install and configure rpmbuilder there
git clone https://github.com/essentialkaos/webkaos.git
cd webkaos/
rpmbuilder webkaos.spec -dl SOURCES/
rpmbuilder webkaos.spec -3 -V -di
```

### FAQ

**Q:** _Why is it named webkaos?_<br/>
**A:** The very first version of this webserver was named `nginx-kaos`. But it uses a lot of different, awesome projects and libraries, not only nginx. So, we decided to choose something neutral.

**Q:** _Is it safe to use webkaos in production?_<br/>
**A:** Yes.

**Q:** _Can you provide packages for Ubuntu/Debian/FreeBSD?_<br/>
**A:** Theoretically, yes. Practically, no. We use only RHEL-based distros in our infrastructure, and we can't provide the same quality of packages for other distros.

**Q:** _Can you provide Alpine-based Docker images?_<br/>
**A:** No. Using RPM packages simplify their support for us. There is a complex process of building and testing packages with different tools (_[rpmbuilder](https://kaos.sh/rpmbuilder), rpmlint, [perfecto](https://kaos.sh/perfecto), [bibop](https://kaos.sh/bibop), [shellcheck](https://github.com/koalaman/shellcheck)_) and we can't provide the same level of quality without them. Also, it is tough to write and maintain Dockerfiles with a large number of build actions and stages.

**Q:** _Why doesn't Dockerfile contain a package version?_<br/>
**A:** Webkaos is based on the latest, mainline (_unstable_) version of Nginx, every release of which contains different fixes. So it is important to use the latest version of webkaos, and not to stick to a particular one.

### License

[BSD 2-clause](LICENSE)

<p align="center"><a href="https://essentialkaos.com"><img src="https://gh.kaos.st/ekgh.svg"/></a></p>
