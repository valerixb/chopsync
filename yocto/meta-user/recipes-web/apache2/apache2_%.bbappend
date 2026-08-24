#
# This recipe replaces standard apache configuration file
# /etc/apache2/httpd.conf
# with a version that enables cgi
#

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " file://httpd.conf"

do_install:append() {
    install -m 0644 ${WORKDIR}/httpd.conf ${D}${sysconfdir}/apache2/httpd.conf
    rm -f ${D}/usr/share/apache2/default-site/htdocs/index.html
}
