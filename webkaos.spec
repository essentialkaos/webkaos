###############################################################################

%define _posixroot        /
%define _root             /root
%define _bin              /bin
%define _sbin             /sbin
%define _srv              /srv
%define _home             /home
%define _lib32            %{_posixroot}lib
%define _lib64            %{_posixroot}lib64
%define _libdir32         %{_prefix}%{_lib32}
%define _libdir64         %{_prefix}%{_lib64}
%define _logdir           %{_localstatedir}/log
%define _rundir           %{_localstatedir}/run
%define _lockdir          %{_localstatedir}/lock/subsys
%define _cachedir         %{_localstatedir}/cache
%define _spooldir         %{_localstatedir}/spool
%define _crondir          %{_sysconfdir}/cron.d
%define _loc_prefix       %{_prefix}/local
%define _loc_exec_prefix  %{_loc_prefix}
%define _loc_bindir       %{_loc_exec_prefix}/bin
%define _loc_libdir       %{_loc_exec_prefix}/%{_lib}
%define _loc_libdir32     %{_loc_exec_prefix}/%{_lib32}
%define _loc_libdir64     %{_loc_exec_prefix}/%{_lib64}
%define _loc_libexecdir   %{_loc_exec_prefix}/libexec
%define _loc_sbindir      %{_loc_exec_prefix}/sbin
%define _loc_bindir       %{_loc_exec_prefix}/bin
%define _loc_datarootdir  %{_loc_prefix}/share
%define _loc_includedir   %{_loc_prefix}/include
%define _rpmstatedir      %{_sharedstatedir}/rpm-state
%define _pkgconfigdir     %{_libdir}/pkgconfig

%define __service         %{_sbin}/service
%define __chkconfig       %{_sbin}/chkconfig
%define __useradd         %{_sbindir}/useradd
%define __groupadd        %{_sbindir}/groupadd
%define __getent          %{_bindir}/getent
%define __sysctl          %{_bindir}/systemctl

###############################################################################

%define service_user         %{name}
%define service_group        %{name}
%define service_name         %{name}
%define service_home         %{_cachedir}/%{service_name}

%define boring_commit        e1068b76bd1d7f6ea06c90faa523ad8d562ec11b
%define psol_ver             1.12.34.2
%define lua_module_ver       0.10.10
%define mh_module_ver        0.32
%define pcre_ver             8.41
%define zlib_ver             1.2.11

%define pagespeed_ver        %{psol_ver}-stable
%define pagespeed_cache_path %{service_home}/pagespeed

###############################################################################

Summary:              Superb high performance web server
Name:                 webkaos
Version:              1.13.6
Release:              2%{?dist}
License:              2-clause BSD-like license
Group:                System Environment/Daemons
Vendor:               Nginx / Google / CloudFlare / ESSENTIALKAOS
URL:                  https://github.com/essentialkaos/webkaos

Source0:              https://nginx.org/download/nginx-%{version}.tar.gz
Source1:              %{name}.logrotate
Source2:              %{name}.init
Source3:              %{name}.sysconfig
Source4:              %{name}.conf
Source5:              %{name}.service
Source6:              %{name}-debug.service

Source20:             pagespeed.conf
Source21:             pagespeed-enabled.conf
Source22:             pagespeed-access.pswd
Source23:             ssl.conf
Source24:             ssl-wildcard.conf
Source25:             common.conf
Source26:             bots.conf

Source30:             %{name}-index.html

Source50:             https://github.com/pagespeed/ngx_pagespeed/archive/v%{pagespeed_ver}.tar.gz
Source51:             https://dl.google.com/dl/page-speed/psol/%{psol_ver}-x64.tar.gz
Source52:             https://github.com/openresty/lua-nginx-module/archive/v%{lua_module_ver}.tar.gz
Source53:             https://boringssl.googlesource.com/boringssl/+archive/%{boring_commit}.tar.gz
Source54:             https://github.com/openresty/headers-more-nginx-module/archive/v%{mh_module_ver}.tar.gz
Source55:             http://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-%{pcre_ver}.tar.gz
Source56:             http://zlib.net/zlib-%{zlib_ver}.tar.gz

Patch0:               %{name}.patch
Patch1:               mime.patch
# https://github.com/cloudflare/sslconfig/blob/master/patches/nginx__1.11.5_dynamic_tls_records.patch
Patch2:               %{name}-dynamic-tls-records.patch
# https://github.com/ajhaydock/BoringNginx/blob/master/patches
Patch3:               boringssl.patch
# https://github.com/cloudflare/sslconfig/blob/master/patches/nginx__1.13.0_http2_spdy.patch
Patch4:               %{name}-http2-spdy.patch
Patch5:               boringssl-tls13-support.patch


# Patch for build with nginx >= 1.13.4
Patch6:               ngx_pagespeed-build-fix.patch

BuildRoot:            %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:             initscripts >= 8.36 kaosv >= 2.12
Requires:             gd libXpm libxslt libluajit

BuildRequires:        make perl libluajit-devel cmake golang

%if 0%{?rhel} >= 7
Requires:             systemd
BuildRequires:        gcc-c++
%else
Requires:             chkconfig
BuildRequires:        devtoolset-2-gcc-c++ devtoolset-2-binutils
%endif

Requires(pre):        shadow-utils

###############################################################################

%description
Superb high performance webserver based on Nginx code, with many
optimizations and improvements.

###############################################################################

%package debug

Summary:           Debug version of webkaos
Group:             System Environment/Daemons
Requires:          %{name} >= %{version}

%description debug
Not stripped version of webkaos with the debugging log support

###############################################################################

%package nginx

Summary:           Links for nginx compatibility
Group:             System Environment/Daemons
Requires:          %{name} >= %{version}

Conflicts:         nginx nginx-kaos tengine openresty

BuildArch:         noarch

%description nginx
Links for nginx compatibility.

###############################################################################

%prep
%setup -q -n nginx-%{version}

mkdir boringssl

%{__tar} xzvf %{SOURCE50}
%{__tar} xzvf %{SOURCE51} -C ngx_pagespeed-%{pagespeed_ver}
%{__tar} xzvf %{SOURCE52}
%{__tar} xzvf %{SOURCE53} -C boringssl
%{__tar} xzvf %{SOURCE54}
%{__tar} xzvf %{SOURCE55}
%{__tar} xzvf %{SOURCE56}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

pushd boringssl
%patch5 -p1
popd

pushd ngx_pagespeed-%{pagespeed_ver}
%patch6 -p1
popd

%build

# Fixed bug with ngx_pagespeed comilation on i386
%ifarch %ix86
  %define optflags -O2 -g -march=i686
%endif

# Renaming and moving docs
%{__mv} CHANGES    NGINX-CHANGES
%{__mv} CHANGES.ru NGINX-CHANGES.ru
%{__mv} LICENSE    NGINX-LICENSE
%{__mv} README     NGINX-README

%{__mv} ngx_pagespeed-%{pagespeed_ver}/LICENSE    ./PAGESPEED-LICENSE
%{__mv} ngx_pagespeed-%{pagespeed_ver}/README.md  ./PAGESPEED-README.md

%{__mv} lua-nginx-module-%{lua_module_ver}/README.markdown ./LUAMODULE-README.markdown

%{__mv} headers-more-nginx-module-%{mh_module_ver}/README.markdown ./HEADERSMORE-README.markdown

%if 0%{?rhel} < 7
# Use gcc and gcc-c++ from devtoolset for build on CentOS6
export PATH="/opt/rh/devtoolset-2/root/usr/bin:$PATH"
%endif

# BoringSSL Build ##############################################################

mkdir boringssl/build

pushd boringssl/build &> /dev/null
  cmake ../
  %{__make} %{?_smp_mflags}
popd

mkdir -p "boringssl/.openssl/lib"

pushd boringssl/.openssl &> /dev/null
  ln -s ../include
popd

cp boringssl/build/crypto/libcrypto.a boringssl/build/ssl/libssl.a boringssl/.openssl/lib

################################################################################

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
        --with-http_spdy_module \
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
        --add-module=ngx_pagespeed-%{pagespeed_ver} \
        --add-module=lua-nginx-module-%{lua_module_ver} \
        --add-module=headers-more-nginx-module-%{mh_module_ver} \
        --with-cc-opt="-g -O2 -fPIE -fstack-protector-all -DTCP_FASTOPEN=23 -D_FORTIFY_SOURCE=2 -Wformat -Werror=format-security -I ../boringssl/.openssl/include/" \
        --with-ld-opt="-Wl,-Bsymbolic-functions -Wl,-z,relro -L ../boringssl/.openssl/lib" \
        --with-compat \
        $*

# Fix "Error 127" during build with BoringSSL
touch boringssl/.openssl/include/openssl/ssl.h

%{__make} %{?_smp_mflags}

%{__mv} %{_builddir}/nginx-%{version}/objs/nginx \
        %{_builddir}/nginx-%{version}/objs/%{name}.debug

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
        --with-http_spdy_module \
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
        --add-module=ngx_pagespeed-%{pagespeed_ver} \
        --add-module=lua-nginx-module-%{lua_module_ver} \
        --add-module=headers-more-nginx-module-%{mh_module_ver} \
        --with-cc-opt="-g -O2 -fPIE -fstack-protector-all -DTCP_FASTOPEN=23 -D_FORTIFY_SOURCE=2 -Wformat -Werror=format-security -I ../boringssl/.openssl/include/" \
        --with-ld-opt="-Wl,-Bsymbolic-functions -Wl,-z,relro -L ../boringssl/.openssl/lib" \
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
install -dm 755 %{buildroot}%{pagespeed_cache_path}

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

%if 0%{?rhel} >= 7
# Install systemd stuff
install -dm 755 %{buildroot}%{_unitdir}

install -pm 644 %{SOURCE5} \
                %{buildroot}%{_unitdir}/
install -pm 644 %{SOURCE6} \
                %{buildroot}%{_unitdir}/
%endif

# Install log rotation stuff
install -dm 755 %{buildroot}%{_sysconfdir}/logrotate.d

install -pm 644 %{SOURCE1} \
                %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Directory for extra configs
install -dm 755 %{buildroot}%{_sysconfdir}/%{name}/xtra

# Install configs
install -pm 644 %{SOURCE4} \
                %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf

# Install XTRA configs
install -pm 644 %{SOURCE20} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE21} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE22} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE23} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE24} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE25} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/
install -pm 644 %{SOURCE26} \
                %{buildroot}%{_sysconfdir}/%{name}/xtra/

install -dm 755 %{buildroot}%{_sysconfdir}/sysconfig

install -pm 644 %{SOURCE3} \
                %{buildroot}%{_sysconfdir}/sysconfig/%{name}

install -pm 644 %{_builddir}/nginx-%{version}/objs/%{name}.debug \
                %{buildroot}%{_sbindir}/%{name}.debug

install -dm 755 %{buildroot}%{_sysconfdir}/%{name}/ssl

# Create links for compatibility with nginx
ln -sf %{_sysconfdir}/%{name}/ %{buildroot}%{_sysconfdir}/nginx
ln -sf %{_sysconfdir}/%{name}/%{name}.conf %{buildroot}%{_sysconfdir}/%{name}/nginx.conf
ln -sf %{_logdir}/%{name}/ %{buildroot}%{_logdir}/nginx
ln -sf %{_sbindir}/%{name} %{buildroot}%{_sbindir}/nginx
ln -sf %{_initrddir}/%{service_name} %{buildroot}%{_initrddir}/nginx

%if 0%{?rhel} >= 7
ln -sf %{_unitdir}/%{name}.service %{buildroot}%{_unitdir}/nginx.service
ln -sf %{_unitdir}/%{name}-debug.service %{buildroot}%{_unitdir}/nginx-debug.service
%endif

###############################################################################

%pre
getent group %{service_group} >/dev/null || groupadd -r %{service_group}
getent passwd %{service_user} >/dev/null || useradd -r -g %{service_group} -s /sbin/nologin -d %{service_home} %{service_user}
exit 0


%post
# Ensure secure permissions (CVE-2013-0337)
%{__chown} root:root %{_logdir}/%{name}

if [[ $1 -eq 1 ]] ; then
  %{__sysctl} enable %{name}.service &>/dev/null || :

  if [[ -d %{_logdir}/%{name} ]] ; then
    if [[ ! -e %{_logdir}/%{name}/access.log ]]; then
      touch %{_logdir}/%{name}/access.log
      %{__chmod} 640 %{_logdir}/%{name}/access.log
      %{__chown} %{service_user}: %{_logdir}/%{name}/access.log
    fi

    if [[ ! -e %{_logdir}/%{name}/error.log ]] ; then
      touch %{_logdir}/%{name}/error.log
      %{__chmod} 640 %{_logdir}/%{name}/error.log
      %{__chown} %{service_user}: %{_logdir}/%{name}/error.log
    fi
  fi
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

###############################################################################

%preun
if [[ $1 -eq 0 ]] ; then
%if 0%{?rhel} >= 7
  %{__sysctl} --no-reload disable %{name}.service &>/dev/null || :
  %{__sysctl} stop %{name}.service &>/dev/null || :
%else
  %{__service} %{service_name} stop > /dev/null 2>&1
  %{__chkconfig} --del %{service_name}
%endif
fi

%postun
if [[ $1 -ge 1 ]] ; then
%if 0%{?rhel} >= 7
  %{__sysctl} daemon-reload &>/dev/null || :
%endif
  %{__service} %{service_name} upgrade &>/dev/null || :
fi


%clean
rm -rf %{buildroot}

###############################################################################

%files
%defattr(-,root,root)
%doc NGINX-CHANGES NGINX-CHANGES.ru NGINX-LICENSE NGINX-README
%doc PAGESPEED-LICENSE PAGESPEED-README.md
%doc LUAMODULE-README.markdown
%doc HEADERSMORE-README.markdown

%{_sbindir}/%{name}

%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/ssl
%dir %{_sysconfdir}/%{name}/conf.d
%dir %{_sysconfdir}/%{name}/stream.conf.d

%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/xtra/pagespeed-access.pswd
%config(noreplace) %{_sysconfdir}/%{name}/xtra/pagespeed.conf
%config(noreplace) %{_sysconfdir}/%{name}/xtra/pagespeed-enabled.conf
%config %{_sysconfdir}/%{name}/xtra/common.conf
%config %{_sysconfdir}/%{name}/xtra/ssl.conf
%config %{_sysconfdir}/%{name}/xtra/ssl-wildcard.conf
%config %{_sysconfdir}/%{name}/xtra/bots.conf

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

%if 0%{?rhel} >= 7
%{_unitdir}/%{name}.service
%endif

%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/html
%{_datadir}/%{name}/html/*

%dir %{_datadir}/%{name}/modules
%{_sysconfdir}/%{name}/modules

%{_logdir}/%{name}

%attr(0755,%{service_user},%{service_group}) %dir %{_cachedir}/%{name}
%attr(0755,%{service_user},%{service_group}) %dir %{pagespeed_cache_path}
%attr(0755,%{service_user},%{service_group}) %dir %{_libdir}/%{name}/modules

%files debug
%defattr(-,root,root)
%attr(0755,root,root) %{_sbindir}/%{name}.debug
%if 0%{?rhel} >= 7
%{_unitdir}/%{name}-debug.service
%endif

%files nginx
%defattr(-,root,root)
%{_sysconfdir}/%{name}/nginx.conf
%{_sysconfdir}/nginx
%{_logdir}/nginx
%{_sbindir}/nginx
%{_initrddir}/nginx
%if 0%{?rhel} >= 7
%{_unitdir}/nginx.service
%{_unitdir}/nginx-debug.service
%endif

###############################################################################

%changelog
* Tue Nov 07 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.6-2
- Added '--with-compat' option for improved compatibility with dynamic modules
- Improved extended preferences

* Wed Oct 18 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.6-1
- Fixed TLS 1.3 support

* Sat Oct 14 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.6-0
- Nginx updated to 1.13.5
- BoringSSL updated to latest version

* Wed Sep 20 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.5-0
- Nginx updated to 1.13.5
- BoringSSL updated to latest version

* Mon Aug 21 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.4-2
- Added support of HTTP status code 418 (I'm a teapot)

* Sat Aug 12 2017 Anton Novojilov <andy@essentialkaos.com> - 1.13.4-1
- Added CloudFlare's patch for SPDY support

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
- Added common.conf with prefered performances
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
- Fixed posible bug with error message output

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
