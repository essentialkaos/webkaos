<p align="center"><a href="#readme"><img src=".github/images/card.svg"/></a></p>

<br/>

<p align="center"><a href="#feature-list">Feature list</a> • <a href="#installation">Installation</a> • <a href="#faq">FAQ</a> • <a href="#contributing">Contributing</a> • <a href="#license">License</a></p>

`webkaos` is a web-server based on the latest version of [Nginx](http://nginx.org).

### Feature list

* Improved default SSL/TLS preferencies
* [Dynamic TLS Records](DYNAMIC-TLS-RECORDS.md) support
* The latest version of [BoringSSL](https://boringssl.googlesource.com/boringssl/) with some state-of-the-art crypto features
* TLS 1.3 support (_RFC 8446_)
* [TCP Fast Open](https://en.wikipedia.org/wiki/TCP_Fast_Open) support
* [Lua](https://github.com/openresty/lua-nginx-module) and [Headers More](https://github.com/openresty/headers-more-nginx-module) modules from the box
* Improved SysV script
* Well-looking error pages
* Improved design of index pages
* Performance tuning for highload

### Installation

#### From ESSENTIAL KAOS Public repository (EL 8/9)

```bash
sudo dnf install -y https://pkgs.kaos.st/kaos-repo-latest.el$(grep 'CPE_NAME' /etc/os-release | tr -d '"' | cut -d':' -f5).noarch.rpm
sudo dnf install webkaos
```

#### Using Docker

Official webkaos images available on [GitHub Container Registry](https://kaos.sh/p/webkaos) and [Docker Hub](http://kaos.sh/d/webkaos). All Docker images support templating using environment variables.

Official images:

- `ghcr.io/essentialkaos/webkaos:ol8`
- `ghcr.io/essentialkaos/webkaos:ol8-unprivileged`
- `ghcr.io/essentialkaos/webkaos:ol9`
- `ghcr.io/essentialkaos/webkaos:ol9-unprivileged`
- `essentialkaos/webkaos:ol8`
- `essentialkaos/webkaos:ol8-unprivileged`
- `essentialkaos/webkaos:ol9`
- `essentialkaos/webkaos:ol9-unprivileged`

Usage examples:

```bash
# Image on OracleLinux 8
docker run --name my-webkaos -v /some/content:/usr/share/webkaos/html:ro -p 8080:80 -d essentialkaos/webkaos:ol8
```

```bash
# Unprivileged image on OracleLinux 8
docker run --name my-webkaos -v /some/content:/usr/share/webkaos/html:ro -p 8080:8080 -d essentialkaos/webkaos:ol8-unprivileged
```

Useful environment variables:

* `WEBKAOS_ENABLE_ENTRYPOINT_LOGS` - Enable logging for actions made by entrypoint script;
* `WEBKAOS_DISABLE_PROC_TUNE` - Disable automatic `worker_processes` tuning;
* `WEBKAOS_DISABLE_BUCKET_TUNE` - Disable automatic `server_names_hash_bucket_size` tuning;
* `WEBKAOS_DISABLE_TEMPLATES` - Disable automatic templates rendering.

#### Using [rpmbuilder](https://kaos.sh/rpmbuilder)

```bash
# install and configure rpmbuilder
git clone https://kaos.sh/webkaos
cd webkaos/
rpmbuilder webkaos.spec -dl SOURCES
rpmbuilder webkaos.spec -3 -V -I
```

### FAQ

**Q:** **_Why is it named webkaos?_**<br/>
**A:** The very first version of this webserver was named `nginx-kaos`. But it uses a lot of different, awesome projects and libraries, not only nginx. So, we decided to choose something neutral.

**Q:** **_Is it safe to use webkaos in production?_**<br/>
**A:** Yes. But we can't guarantee that there are no bugs in nginx, its modules, or used dependencies.

**Q:** **_Can I use Docker images with Kubernetes/Nomad/Rancher?_**<br/>
**A:** Yes.

**Q:** **_Can you provide packages for Ubuntu/Debian/FreeBSD?_**<br/>
**A:** Theoretically, yes. Practically, no. We use only RHEL-based distros in our infrastructure, and we can't provide the same quality of packages for other distros.

**Q:** **_Can you provide Alpine-based Docker images?_**<br/>
**A:** No. Using RPM packages simplify their support for us. There is a complex process of building and testing packages with different tools (_[rpmbuilder](https://kaos.sh/rpmbuilder), rpmlint, [perfecto](https://kaos.sh/perfecto), [bibop](https://kaos.sh/bibop), [shellcheck](https://github.com/koalaman/shellcheck)_) and we can't provide the same level of quality without them. Also, it is tough to write and maintain Dockerfiles with a large number of build actions and stages.

### Contributing

Before contributing to this project please read our [Contributing Guidelines](https://github.com/essentialkaos/.github/blob/master/CONTRIBUTING.md).

### License

[BSD 2-clause](LICENSE)

<p align="center"><a href="https://essentialkaos.com"><img src="https://gh.kaos.st/ekgh.svg"/></a></p>
