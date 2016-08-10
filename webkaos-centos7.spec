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

###############################################################################

%define service_user         %{name}
%define service_group        %{name}
%define service_name         %{name}
%define service_home         %{_cachedir}/%{service_name}

%define open_ssl_ver         1.0.2h
%define psol_ver             1.11.33.2
%define lua_module_ver       0.10.5
%define mh_module_ver        0.30
%define pcre_ver             8.39
%define zlib_ver             1.2.8

%define pagespeed_ver        %{psol_ver}-beta
%define pagespeed_fullver    release-%{pagespeed_ver}
%define pagespeed_cache_path %{service_home}/pagespeed

###############################################################################

Summary:              Superb high performance web server
Name:                 webkaos
Version:              1.11.3
Release:              0%{?dist}
License:              2-clause BSD-like license
Group:                System Environment/Daemons
Vendor:               Nginx / Google / CloudFlare / ESSENTIALKAOS
URL:                  http://essentialkaos.com

Source0:              http://nginx.org/download/nginx-%{version}.tar.gz
Source1:              %{name}.logrotate
Source2:              %{name}.init
Source3:              %{name}.sysconfig
Source4:              %{name}.conf

Source20:             pagespeed.conf
Source21:             pagespeed-enabled.conf
Source22:             pagespeed-access.pswd
Source23:             ssl.conf
Source24:             ssl-wildcard.conf
Source25:             common.conf
Source26:             bots.conf

Source30:             %{name}-index.html

Source50:             https://github.com/pagespeed/ngx_pagespeed/archive/%{pagespeed_fullver}.zip
Source51:             https://dl.google.com/dl/page-speed/psol/%{psol_ver}.tar.gz
Source52:             https://github.com/openresty/lua-nginx-module/archive/v%{lua_module_ver}.tar.gz
Source53:             https://www.openssl.org/source/openssl-%{open_ssl_ver}.tar.gz
Source54:             https://github.com/openresty/headers-more-nginx-module/archive/v%{mh_module_ver}.tar.gz
Source55:             http://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-%{pcre_ver}.tar.gz
Source56:             http://zlib.net/zlib-%{zlib_ver}.tar.gz

Patch0:               %{name}.patch
Patch1:               %{name}-dynamic-tls-records.patch
Patch2:               mime.patch

BuildRoot:            %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:             initscripts >= 8.36 kaosv >= 2.8
Requires:             gd libXpm libxslt libluajit

BuildRequires:        make gcc-c++ perl libluajit-devel

Requires(pre):        shadow-utils
Requires(post):       chkconfig

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

%{__unzip}    %{SOURCE50}
%{__tar} xzvf %{SOURCE51} -C ngx_pagespeed-%{pagespeed_fullver}
%{__tar} xzvf %{SOURCE52}
%{__tar} xzvf %{SOURCE53}
%{__tar} xzvf %{SOURCE54}
%{__tar} xzvf %{SOURCE55}
%{__tar} xzvf %{SOURCE56}

%patch0 -p1
%patch1 -p1
%patch2 -p1

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

%{__mv} ngx_pagespeed-%{pagespeed_fullver}/LICENSE    ./PAGESPEED-LICENSE
%{__mv} ngx_pagespeed-%{pagespeed_fullver}/README.md  ./PAGESPEED-README.md

%{__mv} lua-nginx-module-%{lua_module_ver}/README.markdown ./LUAMODULE-README.markdown
%{__mv} lua-nginx-module-%{lua_module_ver}/Changes         ./LUAMODULE-CHANGES

%{__mv} headers-more-nginx-module-%{mh_module_ver}/README.markdown ./HEADERSMORE-README.markdown

./configure \
        --prefix=%{_sysconfdir}/%{name} \
        --sbin-path=%{_sbindir}/%{name} \
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
        --with-mail \
        --with-mail_ssl_module \
        --with-file-aio \
        --with-ipv6 \
        --with-debug \
        --with-zlib=zlib-%{zlib_ver} \
        --with-pcre-jit \
        --with-pcre=pcre-%{pcre_ver} \
        --with-openssl-opt=no-krb5 \
        --with-openssl=openssl-%{open_ssl_ver} \
        --add-module=ngx_pagespeed-%{pagespeed_fullver} \
        --add-module=lua-nginx-module-%{lua_module_ver} \
        --add-module=headers-more-nginx-module-%{mh_module_ver} \
        --with-cc-opt="%{optflags} $(pcre-config --cflags) -DTCP_FASTOPEN=23" \
        $*
%{__make} %{?_smp_mflags}

%{__mv} %{_builddir}/nginx-%{version}/objs/nginx \
        %{_builddir}/nginx-%{version}/objs/%{name}.debug

./configure \
        --prefix=%{_sysconfdir}/%{name} \
        --sbin-path=%{_sbindir}/%{name} \
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
        --with-mail \
        --with-mail_ssl_module \
        --with-file-aio \
        --with-ipv6 \
        --with-zlib=zlib-%{zlib_ver} \
        --with-pcre-jit \
        --with-pcre=pcre-%{pcre_ver} \
        --with-openssl-opt=no-krb5 \
        --with-openssl=openssl-%{open_ssl_ver} \
        --add-module=ngx_pagespeed-%{pagespeed_fullver} \
        --add-module=lua-nginx-module-%{lua_module_ver} \
        --add-module=headers-more-nginx-module-%{mh_module_ver} \
        --with-cc-opt="%{optflags} $(pcre-config --cflags) -DTCP_FASTOPEN=23" \
        $*
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}

%{make_install}

install -dm 755 %{buildroot}%{_datadir}/%{name}

%{__rm} -f %{buildroot}%{_sysconfdir}/%{name}/nginx.conf
%{__rm} -f %{buildroot}%{_sysconfdir}/%{name}/*.default
%{__rm} -f %{buildroot}%{_sysconfdir}/%{name}/fastcgi.conf

%{__rm} -rf %{buildroot}%{_sysconfdir}/%{name}/html

install -dm 755 %{buildroot}%{_sysconfdir}/%{name}/conf.d

install -dm 755 %{buildroot}%{_logdir}/%{name}
install -dm 755 %{buildroot}%{_rundir}/%{name}
install -dm 755 %{buildroot}%{_cachedir}/%{name}
install -dm 755 %{buildroot}%{_datadir}/%{name}/html
install -dm 755 %{buildroot}%{pagespeed_cache_path}

# Install html pages
install -pm 644 %{SOURCE30} \
                 %{buildroot}%{_datadir}/%{name}/html/index.html

ln -sf %{_datadir}/%{name}/html \
       %{buildroot}%{_sysconfdir}/%{name}/html

# Install SYSV init stuff
install -dm 755 %{buildroot}%{_initrddir}

install -pm 755 %{SOURCE2} \
                %{buildroot}%{_initrddir}/%{service_name}

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
ln -sf %{_initrddir}/%{service_name} %{buildroot}%{_initrddir}/nginx
ln -sf %{_sbindir}/%{name} %{buildroot}%{_sbindir}/nginx

###############################################################################

%pre
getent group %{service_group} >/dev/null || groupadd -r %{service_group}
getent passwd %{service_user} >/dev/null || useradd -r -g %{service_group} -s /sbin/nologin -d %{service_home} %{service_user}
exit 0

%post
if [[ $1 -eq 1 ]] ; then
  %{__chkconfig} --add %{name}

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
  %{__service} %{service_name} stop > /dev/null 2>&1
  %{__chkconfig} --del %{service_name}
fi

%postun
if [[ $1 -ge 1 ]] ; then
  %{__service} %{service_name} upgrade &>/dev/null || :
fi

%clean
%{__rm} -rf %{buildroot}

###############################################################################

%files
%defattr(-,root,root)
%doc NGINX-CHANGES NGINX-CHANGES.ru NGINX-LICENSE NGINX-README
%doc PAGESPEED-LICENSE PAGESPEED-README.md
%doc LUAMODULE-README.markdown LUAMODULE-CHANGES
%doc HEADERSMORE-README.markdown

%{_sbindir}/%{name}

%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/ssl
%dir %{_sysconfdir}/%{name}/conf.d

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

%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/html
%{_datadir}/%{name}/html/*

%attr(0755,%{service_user},%{service_group}) %dir %{_cachedir}/%{name}
%attr(0755,%{service_user},%{service_group}) %dir %{_logdir}/%{name}
%attr(0755,%{service_user},%{service_group}) %dir %{pagespeed_cache_path}

%files debug
%defattr(-,root,root)
%attr(0755,root,root) %{_sbindir}/%{name}.debug

%files nginx
%defattr(-,root,root)
%{_sysconfdir}/%{name}/nginx.conf
%{_sysconfdir}/nginx
%{_logdir}/nginx
%{_initrddir}/nginx
%{_sbindir}/nginx

###############################################################################

%changelog
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
