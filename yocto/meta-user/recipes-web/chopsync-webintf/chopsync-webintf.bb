#
# This recipe copies to the image the web pages that allow
# command and control of the chopper synchronizer (via the SCPI server)
#

SUMMARY = "chopper synchronizer web interface"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://usr"

S = "${WORKDIR}"

#FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
RDEPENDS:${PN} += "python3-core bash"

do_install() {
    install -d ${D}/usr
    cp -r ${WORKDIR}/usr ${D}
    #cp --no-dereference --preserve=mode,timestamps,links -R ${WORKDIR}/usr ${D}
}

FILES:${PN} += "/usr"
