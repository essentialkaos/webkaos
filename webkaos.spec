################################################################################

# rpmbuilder:qa-rpaths 0x0001,0x0002

################################################################################

%global crc_check pushd ../SOURCES ; sha512sum -c %{SOURCE100} ; popd

################################################################################

%define _cachedir  %{_localstatedir}/cache
%define _logdir    %{_localstatedir}/log
%define _rundir    %{_localstatedir}/run

%define __service    %{_sbin}/service
%define __chkconfig  %{_sbin}/chkconfig
%define __sysctl     %{_bindir}/systemctl

################################################################################

%define service_user   %{name}
%define service_group  %{name}
%define service_name   %{name}
%define service_home   %{_cachedir}/%{service_name}

%define nginx_version       1.26.2
%define lua_module_ver      0.10.27
%define lua_resty_core_ver  0.1.29
%define lua_resty_lru_ver   0.14
%define mh_module_ver       0.37
%define pcre_ver            8.45
%define zlib_ver            1.3.1
%define luajit_ver          2.1-20240314
%define luajit_raw_ver      2.1

# 1. Open https://chromiumdash.appspot.com/releases?platform=Linux and note the latest stable version.
# 2. Open https://chromium.googlesource.com/chromium/src/+/refs/tags/<version>/DEPS and note <boringssl_revision>.
%define boring_commit  4fa4804c8ab4521079af62dba5260a99c34b8a29

################################################################################

Summary:        Superb high performance web server
Name:           webkaos
Version:        %{nginx_version}
Release:        0%{?dist}
License:        2-clause BSD-like license
Group:          System Environment/Daemons
URL:            https://kaos.sh/webkaos

Source0:        https://nginx.org/download/nginx-%{version}.tar.gz
Source1:        %{name}.logrotate
Source2:        %{name}.init
Source3:        %{name}.sysconfig
Source4:        %{name}.conf
Source5:        %{name}.service
Source6:        %{name}-debug.service
Source7:        modules.conf
Source8:        nginx-wrapper

Source20:       ssl.conf
Source21:       ssl-wildcard.conf
Source22:       common.conf
Source23:       bots.conf
Source25:       cloudflare-ips.conf

Source30:       %{name}-index.html
Source31:       default.key
Source32:       default.crt

Source50:       https://github.com/openresty/lua-nginx-module/archive/v%{lua_module_ver}.tar.gz
Source51:       https://boringssl.googlesource.com/boringssl/+archive/%{boring_commit}.tar.gz
Source52:       https://github.com/openresty/headers-more-nginx-module/archive/v%{mh_module_ver}.tar.gz
Source53:       https://downloads.sourceforge.net/project/pcre/pcre/%{pcre_ver}/pcre-%{pcre_ver}.tar.gz
Source54:       https://zlib.net/zlib-%{zlib_ver}.tar.gz
Source55:       https://github.com/openresty/luajit2/archive/v%{luajit_ver}.tar.gz
Source59:       https://github.com/openresty/lua-resty-core/archive/v%{lua_resty_core_ver}.tar.gz
Source60:       https://github.com/openresty/lua-resty-lrucache/archive/v%{lua_resty_lru_ver}.tar.gz

Source100:      checksum.sha512

Patch0:         %{name}.patch
Patch1:         mime.patch
                # https://github.com/cloudflare/sslconfig/blob/master/patches/nginx__1.11.5_dynamic_tls_records.patch
Patch2:         %{name}-dynamic-tls-records.patch
                # https://github.com/ajhaydock/BoringNginx/blob/master/patches
Patch3:         boringssl.patch
Patch5:         boringssl-tls13-support.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  make perl golang cmake
%if 0%{?rhel} <= 8
BuildRequires:  gcc-toolset-11-gcc gcc-toolset-11-gcc-c++ gcc-toolset-11-binutils
%else
BuildRequires:  gcc-c++
%endif

Requires:       initscripts >= 8.36 kaosv >= 2.17
Requires:       gd libXpm libxslt

Requires:       systemd
Requires(pre):  shadow-utils

Provides:       %{name} = %{version}-%{release}
Provides:       webserver = %{version}-%{release}

################################################################################

%description
Superb high performance webserver based on Nginx code, with many
optimizations and improvements.

################################################################################

%package debug

Summary:   Debug version of webkaos
Group:     System Environment/Daemons
Requires:  %{name} >= %{version}

%description debug
Not stripped version of webkaos with the debugging log support

################################################################################

%package nginx

Summary:    Links for nginx compatibility
Group:      System Environment/Daemons
Requires:   %{name} >= %{version}

Conflicts:  nginx nginx-kaos tengine openresty

BuildArch:  noarch

%description nginx
Links for nginx compatibility.

################################################################################

%prep
%{crc_check}

%setup -qn nginx-%{nginx_version}

mkdir boringssl

tar xzvf %{SOURCE50}
tar xzvf %{SOURCE51} -C boringssl
tar xzvf %{SOURCE52}
tar xzvf %{SOURCE53}
tar xzvf %{SOURCE54}
tar xzvf %{SOURCE55}
tar xzvf %{SOURCE59}
tar xzvf %{SOURCE60}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

pushd boringssl
%patch5 -p1
popd

%build

# Renaming and moving docs
mv CHANGES    NGINX-CHANGES
mv CHANGES.ru NGINX-CHANGES.ru
mv LICENSE    NGINX-LICENSE
mv README     NGINX-README

mv lua-nginx-module-%{lua_module_ver}/README.markdown ./LUA-MODULE-README.markdown
mv lua-resty-core-%{lua_resty_core_ver}/README.markdown ./LUA-RESTY-CORE-README.markdown
mv lua-resty-lrucache-%{lua_resty_lru_ver}/README.markdown ./LUA-RESTY-LRU-README.markdown
mv headers-more-nginx-module-%{mh_module_ver}/README.markdown ./HEADERS-MORE-MODULE-README.markdown

%if 0%{?rhel} <= 8
# Use gcc and gcc-c++ from DevToolSet 11
export PATH="/opt/rh/gcc-toolset-11/root/usr/bin:$PATH"
%endif

# LuaJIT2 Build ################################################################

export LUAJIT2_DIR=$(pwd)/luajit2-%{luajit_ver}

pushd luajit2-%{luajit_ver}
  %{__make} %{?_smp_mflags} PREFIX=%{_datadir}/%{name}/luajit
  %{__make} install DESTDIR=$LUAJIT2_DIR/build \
                    PREFIX=%{_datadir}/%{name}/luajit
popd

export LUAJIT_LIB="$LUAJIT2_DIR/build%{_datadir}/%{name}/luajit/lib"
export LUAJIT_INC="$LUAJIT2_DIR/build%{_datadir}/%{name}/luajit/include/luajit-2.1"

# BoringSSL Build ##############################################################

mkdir boringssl/build

pushd boringssl/build &> /dev/null
  cmake3 -DCMAKE_EXE_LINKER_FLAGS="-Wl,--no-as-needed -ldl -lstdc++" ../
  %{__make} %{?_smp_mflags}
popd

mkdir -p "boringssl/.openssl/lib"

pushd boringssl/.openssl &> /dev/null
  ln -s ../include
popd

cp boringssl/build/crypto/libcrypto.a boringssl/build/ssl/libssl.a boringssl/.openssl/lib

################################################################################

# perfecto:ignore
./configure \
    --prefix=%{_sysconfdir}/%{name} \
    --sbin-path=%{_sbindir}/%{name} \
    --modules-path=%{_libdir}/%{name}/modules \
    --conf-path=%{_sysconfdir}/%{name}/%{name}.conf \
    --error-log-path=%{_logdir}/%{name}/error.log \
    --http-log-path=%{_logdir}/%{name}/access.log \
    --pid-path=%{_rundir}/%{name}.pid \
    --lock-path=%{_rundir}/%{name}.lock \
    --http-client-body-temp-path=%{service_home}/client_temp \
    --http-proxy-temp-path=%{service_home}/proxy_temp \
    --http-fastcgi-temp-path=%{service_home}/fastcgi_temp \
    --http-uwsgi-temp-path=%{service_home}/uwsgi_temp \
    --http-scgi-temp-path=%{service_home}/scgi_temp \
    --user=%{service_user} \
    --group=%{service_group} \
    %{?_with_http_random_index_module} \
    %{?_with_http_xslt_module} \
    %{?_with_http_flv_module} \
    --with-http_v2_module \
    --with-http_gunzip_module \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gzip_static_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-http_auth_request_module \
    --with-stream \
    --with-stream_ssl_module \
    --with-stream_ssl_preread_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-file-aio \
    --with-ipv6 \
    --with-debug \
    --with-zlib=zlib-%{zlib_ver} \
    --with-pcre-jit \
    --with-pcre=pcre-%{pcre_ver} \
    --with-openssl=boringssl \
    --add-module=lua-nginx-module-%{lua_module_ver} \
    --add-module=headers-more-nginx-module-%{mh_module_ver} \
    --with-cc-opt="-g -O2 -fPIE -fstack-protector-all -DTCP_FASTOPEN=23 -D_FORTIFY_SOURCE=2 -Wformat -Werror=format-security -I ../boringssl/.openssl/include/" \
    --with-ld-opt="-Wl,-Bsymbolic-functions -Wl,-z,relro -L ../boringssl/.openssl/lib -L ../luajit2-%{luajit_ver}/lib -Wl,-rpath -Wl,%{_datadir}/%{name}/luajit/lib -ldl -lstdc++" \
    --with-compat \
    $*

# Fix "Error 127" during build with BoringSSL
touch boringssl/.openssl/include/openssl/ssl.h

%{__make} %{?_smp_mflags}

mv %{_builddir}/nginx-%{nginx_version}/objs/nginx \
        %{_builddir}/nginx-%{nginx_version}/objs/%{name}.debug

# perfecto:ignore
./configure \
    --prefix=%{_sysconfdir}/%{name} \
    --sbin-path=%{_sbindir}/%{name} \
    --modules-path=%{_libdir}/%{name}/modules \
    --conf-path=%{_sysconfdir}/%{name}/%{name}.conf \
    --error-log-path=%{_logdir}/%{name}/error.log \
    --http-log-path=%{_logdir}/%{name}/access.log \
    --pid-path=%{_rundir}/%{name}.pid \
    --lock-path=%{_rundir}/%{name}.lock \
    --http-client-body-temp-path=%{service_home}/client_temp \
    --http-proxy-temp-path=%{service_home}/proxy_temp \
    --http-fastcgi-temp-path=%{service_home}/fastcgi_temp \
    --http-uwsgi-temp-path=%{service_home}/uwsgi_temp \
    --http-scgi-temp-path=%{service_home}/scgi_temp \
    --user=%{service_user} \
    --group=%{service_group} \
    %{?_with_http_random_index_module} \
    %{?_with_http_xslt_module} \
    %{?_with_http_flv_module} \
    --with-http_v2_module \
    --with-http_gunzip_module \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_mp4_module \
    --with-http_gzip_static_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-http_auth_request_module \
    --with-stream \
    --with-stream_ssl_module \
    --with-stream_ssl_preread_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-file-aio \
    --with-ipv6 \
    --with-zlib=zlib-%{zlib_ver} \
    --with-pcre-jit \
    --with-pcre=pcre-%{pcre_ver} \
    --with-openssl=boringssl \
    --add-module=lua-nginx-module-%{lua_module_ver} \
    --add-module=headers-more-nginx-module-%{mh_module_ver} \
    --with-cc-opt="-g -O2 -fPIE -fstack-protector-all -DTCP_FASTOPEN=23 -D_FORTIFY_SOURCE=2 -Wformat -Werror=format-security -I ../boringssl/.openssl/include/" \
    --with-ld-opt="-Wl,-Bsymbolic-functions -Wl,-z,relro -L ../boringssl/.openssl/lib -L ../luajit2-%{luajit_ver}/lib -Wl,-rpath -Wl,%{_datadir}/%{name}/luajit/lib -ldl -lstdc++" \
    --with-compat \
    $*

# Fix "Error 127" during build with BoringSSL
touch boringssl/.openssl/include/openssl/ssl.h

%{__make} %{?_smp_mflags}

%install
rm -rf %{buildroot}

%{make_install}

install -dm 755 %{buildroot}%{_datadir}/%{name}

rm -f %{buildroot}%{_sysconfdir}/%{name}/nginx.conf
rm -f %{buildroot}%{_sysconfdir}/%{name}/*.default
rm -f %{buildroot}%{_sysconfdir}/%{name}/fastcgi.conf

rm -rf %{buildroot}%{_sysconfdir}/%{name}/html

install -dm 755 %{buildroot}%{_sysconfdir}/%{name}/conf.d
install -dm 755 %{buildroot}%{_sysconfdir}/%{name}/stream.conf.d

install -dm 755 %{buildroot}%{_logdir}/%{name}
install -dm 755 %{buildroot}%{_rundir}/%{name}
install -dm 755 %{buildroot}%{_cachedir}/%{name}
install -dm 755 %{buildroot}%{_datadir}/%{name}/html

# Install modules dirs
install -dm 755 %{buildroot}%{_libdir}/%{name}/modules
install -dm 755 %{buildroot}%{_datadir}/%{name}/modules

ln -sf %{_datadir}/%{name}/modules \
       %{buildroot}%{_sysconfdir}/%{name}/modules

# Install html pages
install -pm 644 %{SOURCE30} \
                %{buildroot}%{_datadir}/%{name}/html/index.html

ln -sf %{_datadir}/%{name}/html \
       %{buildroot}%{_sysconfdir}/%{name}/html

# Install SYSV init stuff
install -dm 755 %{buildroot}%{_initrddir}

install -pm 755 %{SOURCE2} \
                %{buildroot}%{_initrddir}/%{service_name}

install -dm 755 %{buildroot}%{_unitdir}

install -pm 644 %{SOURCE5} \
                %{buildroot}%{_unitdir}/
install -pm 644 %{SOURCE6} \
                %{buildroot}%{_unitdir}/

# Install log rotation stuff
install -dm 755 %{buildroot}%{_sysconfdir}/logrotate.d

install -pm 644 %{SOURCE1} \
                %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Directory for extra configs
install -dm 755 %{buildroot}%{_sysconfdir}/%{name}/xtra

# Install configs
install -pm 644 %{SOURCE4} \
                %{buildroot}%{_sysconfdir}/%{name}/
install -pm 644 %{SOURCE7} \
                %{buildroot}%{_sysconfdir}/%{name}/

# Install extra configs
install -pm 644 %{SOURCE20} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE21} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE22} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE23} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE25} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/

install -dm 755 %{buildroot}%{_sysconfdir}/sysconfig

install -pm 644 %{SOURCE3} \
                %{buildroot}%{_sysconfdir}/sysconfig/%{name}

install -pm 644 %{_builddir}/nginx-%{nginx_version}/objs/%{name}.debug \
                %{buildroot}%{_sbindir}/%{name}.debug

# Create directory for certificates and copy dummy certificate
install -dm 755 %{buildroot}%{_sysconfdir}/%{name}/ssl

install -pm 600 %{SOURCE31} \
                %{buildroot}%{_sysconfdir}/%{name}/ssl
install -pm 600 %{SOURCE32} \
                %{buildroot}%{_sysconfdir}/%{name}/ssl

# Install LuaJIT
install -dm 755 %{buildroot}%{_datadir}/%{name}/luajit

cp -rp luajit2-%{luajit_ver}/build%{_datadir}/%{name}/luajit/* \
       %{buildroot}%{_datadir}/%{name}/luajit/

rm -f %{buildroot}%{_datadir}/%{name}/luajit/lib/*.a
rm -rf %{buildroot}%{_datadir}/%{name}/luajit/bin

cp -rp lua-resty-core-%{lua_resty_core_ver}/lib/* \
       %{buildroot}%{_datadir}/%{name}/luajit/share/luajit-%{luajit_raw_ver}/
cp -rp lua-resty-lrucache-%{lua_resty_lru_ver}/lib/resty/* \
       %{buildroot}%{_datadir}/%{name}/luajit/share/luajit-%{luajit_raw_ver}/resty/

find %{buildroot}%{_datadir}/%{name}/luajit/share/luajit-%{luajit_raw_ver}/ -name '*.md' -delete

# Create links and scripts for compatibility with nginx
install -pm 755 %{SOURCE8} %{buildroot}%{_sbindir}/nginx

ln -sf %{_sysconfdir}/%{name}/ %{buildroot}%{_sysconfdir}/nginx
ln -sf %{_sysconfdir}/%{name}/%{name}.conf %{buildroot}%{_sysconfdir}/%{name}/nginx.conf
ln -sf %{_logdir}/%{name}/ %{buildroot}%{_logdir}/nginx
ln -sf %{_initrddir}/%{service_name} %{buildroot}%{_initrddir}/nginx

ln -sf %{_unitdir}/%{name}.service %{buildroot}%{_unitdir}/nginx.service
ln -sf %{_unitdir}/%{name}-debug.service %{buildroot}%{_unitdir}/nginx-debug.service

################################################################################

%pre
getent group %{service_group} >/dev/null || groupadd -r %{service_group}
getent passwd %{service_user} >/dev/null || useradd -r -g %{service_group} -s /sbin/nologin -d %{service_home} %{service_user}
exit 0

%post
# Ensure secure permissions (CVE-2013-0337)
chown -h root:root %{_logdir}/%{name}

if [[ $1 -eq 1 ]] ; then
  %{__sysctl} enable %{name}.service &>/dev/null || :

  # Generate unique nonce for common.conf
  sed -i "s/{RANDOM}/`mktemp -u XXXXXXXXXXXX`/" \
         %{_sysconfdir}/%{name}/xtra/common.conf
fi

# Increasing bucket size for x64
%ifarch %ix86
  sed -i 's/{BUCKET_SIZE}/32/g' \
         %{_sysconfdir}/%{name}/%{name}.conf &>/dev/null || :
  sed -i 's/{BUCKET_SIZE}/32/g' \
         %{_sysconfdir}/%{name}/%{name}.conf.rpmnew &>/dev/null || :
%else
  sed -i 's/{BUCKET_SIZE}/64/g' \
         %{_sysconfdir}/%{name}/%{name}.conf &>/dev/null || :
  sed -i 's/{BUCKET_SIZE}/64/g' \
         %{_sysconfdir}/%{name}/%{name}.conf.rpmnew &>/dev/null || :
%endif

################################################################################

%preun
if [[ $1 -eq 0 ]] ; then
  %{__sysctl} --no-reload disable %{name}.service &>/dev/null || :
  %{__sysctl} stop %{name}.service &>/dev/null || :
fi

%postun
if [[ $1 -ge 1 ]] ; then
  %{__sysctl} daemon-reload &>/dev/null || :
fi

%clean
rm -rf %{buildroot}

################################################################################

%files
%defattr(-,root,root)
%doc NGINX-CHANGES NGINX-CHANGES.ru NGINX-LICENSE NGINX-README
%doc *-README.markdown

%{_sbindir}/%{name}

%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/conf.d
%dir %{_sysconfdir}/%{name}/stream.conf.d

%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/modules.conf
%config(noreplace) %{_sysconfdir}/%{name}/xtra/bots.conf
%config(noreplace) %{_sysconfdir}/%{name}/xtra/cloudflare-ips.conf
%config(noreplace) %{_sysconfdir}/%{name}/xtra/common.conf
%config(noreplace) %{_sysconfdir}/%{name}/xtra/ssl-wildcard.conf
%config(noreplace) %{_sysconfdir}/%{name}/xtra/ssl.conf

%config(noreplace) %{_sysconfdir}/%{name}/ssl/default.key
%config(noreplace) %{_sysconfdir}/%{name}/ssl/default.crt

%config %{_sysconfdir}/%{name}/mime.types
%config %{_sysconfdir}/%{name}/fastcgi_params
%config %{_sysconfdir}/%{name}/scgi_params
%config %{_sysconfdir}/%{name}/uwsgi_params
%config %{_sysconfdir}/%{name}/koi-utf
%config %{_sysconfdir}/%{name}/koi-win
%config %{_sysconfdir}/%{name}/win-utf

%{_sysconfdir}/%{name}/html

%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%{_initrddir}/%{service_name}
%{_unitdir}/%{name}.service

%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/html
%{_datadir}/%{name}/html/*
%{_datadir}/%{name}/luajit/*

%dir %{_datadir}/%{name}/modules
%{_sysconfdir}/%{name}/modules

%{_logdir}/%{name}

%attr(0755,%{service_user},%{service_group}) %dir %{_cachedir}/%{name}
%attr(0755,%{service_user},%{service_group}) %dir %{_libdir}/%{name}/modules

%files debug
%defattr(-,root,root)
%attr(0755,root,root) %{_sbindir}/%{name}.debug
%{_unitdir}/%{name}-debug.service

%files nginx
%defattr(-,root,root)
%{_sysconfdir}/%{name}/nginx.conf
%{_sysconfdir}/nginx
%{_logdir}/nginx
%{_sbindir}/nginx
%{_initrddir}/nginx
%{_unitdir}/nginx.service
%{_unitdir}/nginx-debug.service

################################################################################

%changelog
* Thu Aug 15 2024 Anton Novojilov <andy@essentialkaos.com> - 1.26.2-0
- Nginx updated to 1.26.2 with fixes for CVE-2024-7347
- More Headers module updated to 0.37
- lua-nginx-module updated to 0.10.27
- lua-resty-lru updated to 0.14
- lua-resty-core updated to 0.1.29

* Fri Jun 14 2024 Anton Novojilov <andy@essentialkaos.com> - 1.26.1-0
- Nginx updated to 1.26.1

* Sun Jun 02 2024 Anton Novojilov <andy@essentialkaos.com> - 1.26.0-2
- ngx_brotli module removed due to serious problems and lack of support

* Fri May 31 2024 Anton Novojilov <andy@essentialkaos.com> - 1.26.0-1
- Brotli updated to the latest commit to fix a bug that caused workers to
  shut down

* Fri May 03 2024 Anton Novojilov <andy@essentialkaos.com> - 1.26.0-0
- Nginx updated to 1.26.0
- BoringSSL updated to the latest stable version for Chromium
- Zlib updated to 1.3.1
- Brotli updated to the latest version
- LuaJIT updated to 2.1-20240314
- lua-nginx-module updated to 0.10.26
- lua-resty-core updated to 0.1.28
- NAXSI module removed due to discontinued development
- End of support for CentOS 7

* Wed Jun 21 2023 Anton Novojilov <andy@essentialkaos.com> - 1.24.0-0
- Nginx updated to 1.24.0 (mainline → stable)
- BoringSSL updated to the latest stable version for Chromium

* Wed Mar 29 2023 Anton Novojilov <andy@essentialkaos.com> - 1.23.4-0
- Nginx updated to 1.23.4
- lua-nginx-module updated to 0.10.24
- lua-resty-core updated to 0.1.26
- BoringSSL updated to the latest stable version for Chromium

* Thu Dec 01 2022 Anton Novojilov <andy@essentialkaos.com> - 1.23.3-0
- Nginx updated to 1.23.3
- zlib updated to 1.2.13 with fixes for CVE-2022-37434
- BoringSSL updated to the latest stable version for Chromium
- ngx_brotli updated to the latest commit
- brotli updated to the latest commit

* Sat Oct 22 2022 Anton Novojilov <andy@essentialkaos.com> - 1.23.2-0
- Nginx updated to 1.23.2 with fixes for CVE-2022-41741, CVE-2022-41742
- BoringSSL updated to the latest stable version for Chromium
- LuaJIT updated to 2.1-20220915
- lua-resty-core updated to 0.1.24
- lua-nginx-module updated to 0.10.22
- Added extra config with Cloudflare IPs

* Tue Aug 02 2022 Anton Novojilov <andy@essentialkaos.com> - 1.23.1-0
- Nginx updated to 1.23.1
- More Headers module updated to 0.34

* Mon Jul 04 2022 Anton Novojilov <andy@essentialkaos.com> - 1.23.0-0
- Nginx updated to 1.23.0
- BoringSSL updated to the latest stable version
- LuaJIT updated to 2.1-20220411
- lua-nginx-module updated to 0.10.21
- lua-resty-core updated to 0.1.23
- lua-resty-lru updated to 0.13
- Using GCC 9 for build

* Thu Jan 27 2022 Anton Novojilov <andy@essentialkaos.com> - 1.21.6-0
- Nginx updated to 1.21.6
- LuaJIT updated to 2.1-20220111

* Tue Jan 11 2022 Anton Novojilov <andy@essentialkaos.com> - 1.21.5-0
- Nginx updated to 1.21.5
- BoringSSL updated to the latest stable version
- LuaJIT updated to 2.1-20211210

* Sat Dec 11 2021 Anton Novojilov <andy@essentialkaos.com> - 1.21.4-1
- Removed duplicate of $http_referer from timed_combined log format

* Sat Nov 13 2021 Anton Novojilov <andy@essentialkaos.com> - 1.21.4-0
- Nginx updated to 1.21.4
- BoringSSL updated to the latest version
- lua-nginx-module updated to 0.10.20
- Updated link to PCRE

* Wed Sep 08 2021 Anton Novojilov <andy@essentialkaos.com> - 1.21.3-0
- Nginx updated to 1.21.3
- BoringSSL updated to the latest version
- PCRE updated to 8.45
- lua-resty-core updated to 0.1.22
- lua-resty-lru updated to 0.11
- Improved default configuration file

* Wed May 26 2021 Anton Novojilov <andy@essentialkaos.com> - 1.21.0-0
- Nginx updated to 1.21.0 with fix for CVE-2021-23017
- BoringSSL updated to the latest version
- LuaJIT updated to 2.1-20210510

* Wed Apr 07 2021 Anton Novojilov <andy@essentialkaos.com> - 1.19.9-0
- Nginx updated to 1.19.9
- BoringSSL updated to the latest version

* Tue Mar 09 2021 Anton Novojilov <andy@essentialkaos.com> - 1.19.7-0
- Nginx updated to 1.19.7
- BoringSSL updated to the latest version
- LuaJIT updated to 2.1-20201027
- Lua module updated to 0.10.19

* Thu Dec 03 2020 Anton Novojilov <andy@essentialkaos.com> - 1.19.5-0
- Nginx updated to 1.19.5

* Wed Dec 02 2020 Anton Novojilov <andy@essentialkaos.com> - 1.19.4-0
- Nginx updated to 1.19.4
- BoringSSL updated to the latest version
- LuaJIT updated to 2.1-20201027
- NAXSI module updated to 1.3

* Mon Oct 26 2020 Anton Novojilov <andy@essentialkaos.com> - 1.19.3-0
- Nginx updated to 1.19.3
- BoringSSL updated to the latest version
- brotli module updated to the latest stable release
- LuaJIT updated to 2.1-20201012-2
- NAXSI module updated to 1.1a
- Fixed bug with using system LuaJIT instead of OpenResty's fork

* Sat Jun 13 2020 Anton Novojilov <andy@essentialkaos.com> - 1.19.0-1
- Fixed bug with unclosed if condition in postun scriptlet
- Added dark mode support to error pages

* Wed May 27 2020 Anton Novojilov <andy@essentialkaos.com> - 1.19.0-0
- Nginx updated to 1.19.0
- Fixed minor bug in init script
- Updated dynamic TLS records patch for compatibility with the latest version

* Wed May 27 2020 Anton Novojilov <andy@essentialkaos.com> - 1.17.10-0
- Nginx updated to 1.17.10
- BoringSSL updated to the latest version
- brotli module updated to the latest stable release
- Improved init script
- Dropped CentOS 6 support

* Wed Mar 11 2020 Anton Novojilov <andy@essentialkaos.com> - 1.17.9-1
- Added http_auth_request_module

* Sun Mar 08 2020 Anton Novojilov <andy@essentialkaos.com> - 1.17.9-0
- Nginx updated to 1.17.9
- BoringSSL updated to the latest version

* Tue Feb 18 2020 Anton Novojilov <andy@essentialkaos.com> - 1.17.8-0
- Nginx updated to 1.17.8
- LuaJIT updated to 2.1-20200102
- PCRE updated to 8.44
- BoringSSL updated to the latest version
- Using DevToolSet 7 for build

* Wed Dec 25 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.7-0
- Nginx updated to 1.17.7

* Wed Nov 20 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.6-0
- Nginx updated to 1.17.6

* Fri Nov 08 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.5-0
- Nginx updated to 1.17.5
- BoringSSL updated to the latest version
- Removed ssl_dhparam from default configuration

* Fri Nov 08 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.4-1
- Added webserver to Provides

* Wed Sep 25 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.4-0
- Nginx updated to 1.17.4
- BoringSSL updated to the latest version
- Switched to official ngx_brotli repository

* Thu Aug 29 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.3-1
- Improved dynamic modules support
- Added brotli dynamic module
- Added NAXSI dynamic module

* Wed Aug 14 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.3-0
- Nginx updated to 1.17.3 with fixes for CVE-2019-9511 (Data dribble),
  CVE-2019-9513 (Resource loop) and CVE-2019-9516 (Zero‑length headers leak)
- BoringSSL updated to the latest version
- Added checksums for all sources

* Wed Jul 24 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.2-1
- resty-core disabled by default

* Wed Jul 24 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.2-0
- Nginx updated to 1.17.2
- BoringSSL updated to the latest version

* Sat Jun 29 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.1-0
- Nginx updated to 1.17.1
- BoringSSL updated to the latest version
- LuaJIT updated to 2.1-20190626
- Lua module updated to 0.10.15
- Using cmake3 for BoringSSL build

* Wed Jun 12 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.0-1
- Init script improvements

* Tue May 21 2019 Anton Novojilov <andy@essentialkaos.com> - 1.17.0-0
- Nginx updated to 1.17.0
- Improved styles for error and index pages
- Dropped SPDY support

* Thu May 16 2019 Anton Novojilov <andy@essentialkaos.com> - 1.15.12-0
- Nginx updated to 1.15.12
- BoringSSL updated to the latest version
- LuaJIT updated to 2.1-20190507

* Wed May 15 2019 Anton Novojilov <andy@essentialkaos.com> - 1.15.11-0
- Nginx updated to 1.15.11

* Tue Apr 09 2019 Anton Novojilov <andy@essentialkaos.com> - 1.15.10-0
- Nginx updated to 1.15.10
- BoringSSL updated to the latest version
- LuaJIT updated to 2.1-20190329
- Updated BoringSSL patch for compatibility with the latest version

* Thu Feb 28 2019 Anton Novojilov <andy@essentialkaos.com> - 1.15.9-0
- Nginx updated to 1.15.9
- LuaJIT replaced by OpenResty's fork
- Fixed exit code for failed validation while restart in init script

* Thu Feb 28 2019 Anton Novojilov <andy@essentialkaos.com> - 1.15.8-0
- Nginx updated to 1.15.8
- PCRE updated to 8.43
- Lua module updated to 0.10.14
- BoringSSL updated to the latest version
- Updated dynamic TLS records patch for compatibility with the latest version
- Added patch for building BoringSSL on CentOS 6

* Thu Nov 29 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.7-0
- Nginx updated to 1.15.7
- BoringSSL updated

* Thu Nov 08 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.6-0
- Nginx updated to 1.15.6 with fixes for CVE-2018-16843, CVE-2018-16844
  and CVE-2018-16845
- BoringSSL updated to the latest version

* Wed Oct 03 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.5-1
- BoringSSL updated to the latest version

* Tue Oct 02 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.5-0
- Nginx updated to 1.15.5

* Thu Sep 27 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.4-0
- Nginx updated to 1.15.4
- PageSpeed removed
- Updated dynamic TLS records patch for compatibility with the latest version
- Updated BoringSSL patch for compatibility with the latest version

* Sun Sep 02 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.3-0
- Nginx updated to 1.15.3
- BoringSSL updated to latest version
- Updated dynamic TLS records patch for compatibility with the latest version

* Thu Jul 26 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.2-0
- Nginx updated to 1.15.2
- BoringSSL updated to the latest version

* Wed Jul 04 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.1-1
- Dropped TLSv1 support
- Dropped support of TLS_RSA_WITH_AES_256_CBC_SHA and
  TLS_RSA_WITH_AES_128_CBC_SHA

* Wed Jul 04 2018 Anton Novojilov <andy@essentialkaos.com> - 1.15.1-0
- Nginx updated to 1.15.1
- BoringSSL updated to latest version

* Thu May 31 2018 Anton Novojilov <andy@essentialkaos.com> - 1.14.0-0
- Nginx updated to 1.14.0
- Lua module updated to 0.10.13
- BoringSSL updated to latest version
- Improved default settings
- Improved init script

* Fri Apr 13 2018 Anton Novojilov <andy@essentialkaos.com> - 1.13.12-0
- Nginx updated to 1.13.12
- BoringSSL updated to latest version

* Wed Apr 04 2018 Anton Novojilov <andy@essentialkaos.com> - 1.13.11-0
- Nginx updated to 1.13.11

* Tue Apr 03 2018 Anton Novojilov <andy@essentialkaos.com> - 1.13.10-1
- Google Public DNS replaced by Cloudflare Public DNS
- Using devtoolset-3 for build on all systems
- BoringSSL updated to latest version
- Lua module updated to 0.10.12rc2

* Tue Mar 20 2018 Anton Novojilov <andy@essentialkaos.com> - 1.13.10-0
- Nginx updated to 1.13.10
- PCRE updated to 8.42
- BoringSSL updated to latest version

* Fri Mar 09 2018 Anton Novojilov <andy@essentialkaos.com> - 1.13.9-1
- Improved configuration files

* Sun Feb 25 2018 Anton Novojilov <andy@essentialkaos.com> - 1.13.9-0
- Nginx updated to 1.13.9
- BoringSSL updated to latest version
- HTTP2+SPDY patch recreated for compatibility with latest version

* Mon Jan 22 2018 Anton Novojilov <andy@essentialkaos.com> - 1.13.8-0
- Nginx updated to 1.13.8
- BoringSSL updated to latest version
- PageSpeed updated to 1.12.34.3-stable
- Improved PageSpeed build

* Tue Nov 28 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.7-0
- Nginx updated to 1.13.7
- BoringSSL updated to latest version
- Lua module updated to 0.10.11
- More Headers module updated to 0.33
- Fixed bug with autostart on CentOS6

* Tue Nov 07 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.6-2
- Added '--with-compat' option for improved compatibility with dynamic modules
- Improved extended preferences

* Wed Oct 18 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.6-1
- Fixed TLS 1.3 support

* Sat Oct 14 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.6-0
- Nginx updated to 1.13.6
- BoringSSL updated to latest version

* Wed Sep 20 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.5-0
- Nginx updated to 1.13.5
- BoringSSL updated to latest version

* Mon Aug 21 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.4-2
- Added support of HTTP status code 418 (I'm a teapot)

* Sat Aug 12 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.4-1
- Added Cloudflare's patch for SPDY support

* Thu Aug 10 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.4-0
- Nginx updated to 1.13.4
- BoringSSL updated to latest version
- Lua module updated to 0.10.10

* Wed Jul 12 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.3-0
- Nginx updated to 1.13.3 with CVE-2017-7529 fix

* Fri Jul 07 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.2-0
- Nginx updated to 1.13.2
- BoringSSL updated to latest version
- PCRE updated to 8.41
- Lua module updated to 0.10.8
- PageSpeed updated to 1.12.34.2-stable

* Wed Apr 26 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.0-0
- Nginx updated to 1.13.0
- BoringSSL updated to latest version
- TLS 1.3 enabled by default

* Wed Apr 19 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.13-1
- Added AES128-SHA to list of supported ciphers

* Sun Apr 09 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.13-0
- Nginx updated to 1.11.13

* Thu Apr 06 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.12-1
- BoringSSL updated to latest version
- Improved SSL preferences
- Enabled dynamic TLS records by default
- PCRE JIT enabled by default

* Mon Mar 27 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.12-0
- Nginx updated to 1.11.12
- Specs for CentOS6 and CentOS7 merged into one spec

* Thu Mar 23 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.11-0
- Nginx updated to 1.11.11
- BoringSSL updated to latest version

* Mon Feb 20 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.10-1
- Webserver name removed from error pages for security purposes

* Fri Feb 17 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.10-0
- Nginx updated to 1.11.10
- BoringSSL updated to latest version
- Added directory stream.conf.d for stream configs
- Fixed bugs in systemd unit files

* Thu Jan 19 2017 Anton Novojilov <andy@essentialkaos.com> - 1.11.8-0
- Nginx updated to 1.11.8
- PageSpeed updated to 1.12.34.2
- PCRE updated to 8.40
- zlib updated to 1.2.11
- BoringSSL updated to latest version
- Fixed bug in systemd unit file

* Fri Nov 18 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.6-0
- Nginx updated to 1.11.6
- BoringSSL updated to latest version

* Sun Nov 13 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.5-2
- Added dynamic modules support
- Added systemd support

* Wed Nov 09 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.5-1
- BoringSSL updated to latest version
- Lua module updated to 0.10.7
- More Headers module updated to 0.32
- Added request_id to log output and X-Request-ID header

* Fri Oct 14 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.5-0
- Nginx updated to 1.11.5
- OpenSSL replaced by BoringSSL

* Fri Sep 23 2016 Gleb Goncharov <g.goncharov@fun-box.ru> - 1.11.4-0
- Nginx updated to 1.11.4
- OpenSSL updated to 1.0.2i
- PageSpeed updated to 1.11.33.4
- Lua module updated to 0.10.6
- More Headers module updated to 0.31

* Fri Aug 19 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.3-1
- Fixed bug with log format

* Tue Aug 09 2016 Gleb Goncharov <g.goncharov@fun-box.ru> - 1.11.3-0
- Nginx updated to 1.11.3

* Wed Jul 13 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.2-0
- Nginx updated to 1.11.2
- PCRE updated to 8.39

* Fri Jun 17 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.1-2
- Added TCP Fast Open support

* Tue Jun 14 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.1-1
- Added patch for dynamic TLS records size

* Wed Jun 01 2016 Anton Novojilov <andy@essentialkaos.com> - 1.11.1-0
- Nginx updated to 1.11.1 with CVE-2016-4450 fix
- Lua module updated to 0.10.5
- MoreHeaders module updated to 0.30
- PageSpeed updated to 1.11.33.2
- Fixed arch for webkaos-nginx package

* Wed May 04 2016 Anton Novojilov <andy@essentialkaos.com> - 1.10.0-1
- OpenSSL updated to 1.0.2h

* Wed Apr 27 2016 Anton Novojilov <andy@essentialkaos.com> - 1.10.0-0
- Nginx updated to 1.10.0
- PageSpeed updated to 1.9.32.14
- Lua module updated to 0.10.2
- OpenSSL updated to 1.0.2g
- Added pcre with jit and zlib

* Wed Feb 10 2016 Anton Novojilov <andy@essentialkaos.com> - 1.9.10-1
- PageSpeed updated to 1.9.32.13

* Fri Jan 29 2016 Anton Novojilov <andy@essentialkaos.com> - 1.9.10-0
- Nginx updated to 1.9.10
- MoreHeaders module updated to 0.29
- Lua module updated to 0.10.0
- OpenSSL updated to 1.0.2f
- Added status code 451 (Unavailable For Legal Reasons)

* Thu Dec 10 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.9-0
- Nginx updated to 1.9.9
- OpenSSL updated to 1.0.2e

* Sun Nov 22 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.7-0
- Nginx updated to 1.9.7
- Lua module updated to 0.9.19
- MoreHeaders module updated to 0.28
- Improved init script

* Wed Oct 28 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.6-0
- Nginx updated to 1.9.6
- PageSpeed updated to 1.9.32.10
- Lua module updated to 0.9.17
- MoreHeaders module updated to 0.26.1

* Wed Sep 23 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.5-0
- Nginx updated to 1.9.5

* Wed Aug 19 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.4-0
- Nginx updated to 1.9.4
- PageSpeed updated to 1.9.32.6

* Tue Aug 11 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.3-3
- Removed custom error pages
- Added hi-res image for default page

* Tue Aug 11 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.3-2
- Fixed some minor bugs in init script

* Sun Aug 09 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.3-1
- Added latest version of MoreHeaders module

* Fri Jul 17 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.3-0
- Nginx updated to 1.9.3

* Fri Jul 10 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.2-1
- OpenSSL updated to 1.0.2d
- Added some SSL improvements

* Tue Jul 07 2015 Anton Novojilov <andy@essentialkaos.com> - 1.9.2-0
- Nginx updated to 1.9.2
- OpenSSL updated to 1.0.2c
- PageSpeed updated to 1.9.32.4
- Lua module updated to 0.9.16

* Mon May 25 2015 Anton Novojilov <andy@essentialkaos.com> - 1.8.0-2
- Fixed minor bug with listing empty dirs in autoindex module

* Fri May 22 2015 Anton Novojilov <andy@essentialkaos.com> - 1.8.0-1
- Minor fixes in pagespeed config
- Small fixes in spec file

* Mon Apr 27 2015 Anton Novojilov <andy@essentialkaos.com> - 1.8.0-0
- Nginx updated to 1.8.0

* Fri Apr 17 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.12-0
- Nginx updated to 1.7.12

* Thu Mar 26 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.11-0
- Nginx updated to 1.7.11

* Fri Mar 20 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.10-3
- OpenSSL updated to 1.0.2a

* Fri Feb 20 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.10-2
- Lua module updated to 0.9.15
- Fixed various bugs in config files
- Improved extra configs storing scheme

* Wed Feb 11 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.10-0
- Nginx updated to 1.7.10
- Lua module updated to 0.9.14

* Fri Jan 23 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.9-5
- OpenSSL updated to 1.0.2

* Wed Jan 21 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.9-4
- OpenSSL updated to 1.0.1l

* Fri Jan 09 2015 Anton Novojilov <andy@essentialkaos.com> - 1.7.9-3
- OpenSSL updated to 1.0.1k
- PageSpeed updated to 1.9.32.3

* Mon Dec 29 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.9-2
- Improved autoindex output
- Improved spec
- Improved config
- Removed version from pagespeed header

* Wed Dec 24 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.9-0
- Nginx updated to 1.7.9

* Mon Dec 15 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.8-2
- Updated default SSL preferences for A+ rating on QUALYS SSL Server Test

* Fri Dec 05 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.8-0
- Nginx updated to 1.7.8
- Lua module updated to 0.9.13

* Tue Oct 28 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.7-0
- Nginx updated to 1.7.7
- PageSpeed updated to 1.9.32.2
- Init script migrated to kaosv2

* Sat Oct 18 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.6-3
- OpenSSL updated to 1.0.1j

* Thu Oct 16 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.6-2
- Small fixes in error logging

* Fri Oct 10 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.6-1
- Improved initd script
- Increased build speed

* Fri Oct 10 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.6-0
- Nginx updated to 1.7.6
- PageSpeed updated to 1.9.32.1
- Added common.conf with preferred performances
- Improved ssl.conf

* Mon Sep 15 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.5-0
- Added dh generation to init script
- Nginx updated to 1.7.5
- Lua module updated to 0.9.13rc1
- Some minor improvements

* Thu Aug 21 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.4-2
- Lua module updated to 0.9.11
- Improved init file

* Fri Aug 08 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.4-1
- Improved init file

* Fri Aug 08 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.4-0
- OpenSSL updated to 1.0.1i
- Nginx updated to 1.7.4
- Fixed possible bug with error message output

* Mon Aug 04 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.3-1
- Added compatibility with nginx init

* Tue Jul 15 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.3-0
- Nginx updated to 1.7.3
- Lua module updated to 0.9.10
- Added openresty and tengine to conflicts

* Wed Jun 25 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.2-0
- Nginx updated to 1.7.2
- PageSpeed module updated to 1.8.31.4
- Minor fixes

* Fri Jun 06 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.1-4
- Fixed minor bug in init file
- OpenSSL updated to 1.0.1h
- Lua module updated to 0.9.8
- PageSpeed module updated to 1.8.31.3

* Tue Jun 03 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.1-3
- Improved spec file
- Improved init script (added soft-restart command)

* Fri May 30 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.1-1
- Fixed package compatibility with nginx & nginx-kaos

* Wed May 21 2014 Anton Novojilov <andy@essentialkaos.com> - 1.7.1-0
- PageSpeed disabled by default
- PageSpeed updated to 1.8.31.2
- TrimUrl filter enabled by default
- Fixed bug with basic auth and error files
