FROM alpine:3.22.2

ARG TARGETARCH
ARG BUILD_ARCH
ARG BUILD_VERSION=0.1.0

LABEL io.hass.name="Rex" \
      io.hass.description="Private Rex terminal server" \
      io.hass.type="addon" \
      io.hass.version="${BUILD_VERSION}" \
      io.hass.arch="amd64|aarch64"

RUN apk add --no-cache bash ca-certificates curl git jq nano ncurses-terminfo openssh-client linux-pam tzdata

# Rex 0.1.0-preview.13; pin the release and its published archive checksums.
RUN set -eu; \
    case "${TARGETARCH:-${BUILD_ARCH}}" in \
      amd64) arch=amd64; sha=f7300c96f61f4e7da30c425481ad3dc734e9fc8138203272ff44bcf8bc7484b4 ;; \
      arm64|aarch64) arch=arm64; sha=0e71bb14271cc99ac47c55be0b98ad31e70e060654bd350c6fd4e55a2c4b6f82 ;; \
      *) echo "Unsupported architecture" >&2; exit 1 ;; \
    esac; \
    curl --fail --show-error --location --retry 3 \
      "https://blob.superlogical.com/download/rex/preview/1b6654811346488b696ded8f3c7e6701c57242f1/rex-linux-${arch}-musl.tar.gz" \
      --output /tmp/rex.tar.gz; \
    echo "${sha}  /tmp/rex.tar.gz" | sha256sum -c -; \
    mkdir /tmp/rex-unpack; \
    tar -xzf /tmp/rex.tar.gz -C /tmp/rex-unpack; \
    install -m 0755 /tmp/rex-unpack/rex /usr/local/bin/rex; \
    rm -rf /tmp/rex.tar.gz /tmp/rex-unpack

ENV HOME=/data/home \
    SHELL=/bin/bash \
    REX_SERVER=/run/rex/server.sock \
    TERM=xterm-256color

COPY run.sh /usr/local/bin/run-rex
RUN chmod 0755 /usr/local/bin/run-rex
WORKDIR /config
CMD ["/usr/local/bin/run-rex"]
