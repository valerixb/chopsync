#
# This recipe replaces standard ntp configuration file:
# /etc/ntp.conf
# with a version customized for MaxIV
#

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " file://ntp.conf"

do_install:append() {
    install -m 644 ${WORKDIR}/ntp.conf ${D}${sysconfdir}
}
