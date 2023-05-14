# Copyright 1999-2023 Gentoo Authors 
# Distributed under the terms of the GNU General Public License v2 
 
# please keep this ebuild at EAPI 7 -- sys-apps/portage dep 
EAPI=7 
 
DISTUTILS_USE_PEP517=setuptools
PYTHON_COMPAT=( python3_{9..11} pypy3 ) 
 
inherit distutils-r1
 
DESCRIPTION="Curses based Solitaire in python"
HOMEPAGE="https://github.com/adrenlinerush/curses_solitaire"
SRC_URI="https://github.com/adrenlinerush/curses_solitaire/releases/download/v${PV}/${P}.tar.gz"
 
LICENSE="GPL-2" 
SLOT="0" 
KEYWORDS="amd64 arm64" 
