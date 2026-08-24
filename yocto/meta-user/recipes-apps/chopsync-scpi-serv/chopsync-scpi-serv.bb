#
# This file is the chopsync-scpi-serv recipe.
#
# lines for sysV are commented: we use systemd
# so we do not need to put a start/stop script in /etc/init.d
#

SUMMARY = "chopsync SCPI server"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = \
    "file://chopsync-scpi-serv \
     file://chopsync-scpi-serv-init \
     file://chopsync-scpi-serv.service \
     file://scpi.conf \
    "

S = "${WORKDIR}"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
  
inherit update-rc.d systemd

INITSCRIPT_NAME = "chopsync-scpi-serv-init"
INITSCRIPT_PARAMS = "start 99 S ."
  
SYSTEMD_PACKAGES = "${PN}"
SYSTEMD_SERVICE:${PN} = "chopsync-scpi-serv.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"


do_install() {
        if ${@bb.utils.contains('DISTRO_FEATURES', 'sysvinit', 'true', 'false', d)}; then
            install -d ${D}${sysconfdir}/init.d/
            install -m 0755 ${WORKDIR}/chopsync-scpi-serv-init ${D}${sysconfdir}/init.d/
        fi

        install -d ${D}/${bindir}
        install -d ${D}/${sysconfdir}
        install -m 0755 ${S}/chopsync-scpi-serv ${D}/${bindir}
        install -d ${D}${systemd_system_unitdir}
        install -m 0644 ${WORKDIR}/chopsync-scpi-serv.service ${D}${systemd_system_unitdir}
        install -m 0644 ${WORKDIR}/scpi.conf ${D}${sysconfdir}
}

FILES:${PN} += "${@bb.utils.contains('DISTRO_FEATURES','sysvinit','${sysconfdir}/*', '', d)}"
FILES:${PN} += "${sysconfdir}/scpi.conf"
