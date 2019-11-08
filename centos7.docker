## WEBKAOS IMAGE ###############################################################

FROM centos:7

ENV WK_VERSION 1.17.5

LABEL name="WEBKAOS Image on CentOS 7" \
      vendor="ESSENTIAL KAOS" \
      maintainer="Anton Novojilov" \
      license="EKOL" \
      version="2019.11.08"

RUN yum -y -q install https://yum.kaos.st/kaos-repo-latest.el7.noarch.rpm && \
    yum -y -q install webkaos-${WK_VERSION} webkaos-module-brotli && \
    rm -rf /var/cache/yum

RUN ln -sf /dev/stdout /var/log/webkaos/access.log \
    && ln -sf /dev/stderr /var/log/webkaos/error.log

EXPOSE 80

STOPSIGNAL SIGTERM

CMD ["webkaos", "-g", "daemon off;"]

################################################################################
