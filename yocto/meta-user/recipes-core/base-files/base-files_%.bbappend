FILESEXTRAPATHS:prepend  := "${THISDIR}/files:"

#SRC_URI += "file://product \
#            file://version \
#           "

dirs755:append = " ${sysconfdir}/maxiv"

do_install:append () {
	      echo "${MAXIV_PRODUCT}" > ${D}${sysconfdir}/maxiv/product
	      echo "${MAXIV_VERSION}" > ${D}${sysconfdir}/maxiv/version
        # install -m 0755 ${WORKDIR}/product ${D}${sysconfdir}/maxiv/product
        # install -m 0755 ${WORKDIR}/version ${D}${sysconfdir}/maxiv/version
}
