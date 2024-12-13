#!/bin/bash

deps=('patch' 'simplejson' 'attrs' 'PyYAML' 'tempora' 'bitarray' 'publicsuffix2' 'pytz' 'pluggy' 'lxml' 'requests' 'pyahocorasick' 'pdfminer.six' 'contextlib2' 'typing' 'Beautifulsoup4' 'backports.os' 'packageurl-python' 'chardet' 'fingerprints' 'pygments' 'schematics-patched' 'pefile' 'unicodecsv' 'text-unidecode' 'colorama' 'pymaven-patch' 'click' 'future' 'boolean.py' 'Beautifulsoup' 'yg.lockfile' 'pycryptodome' 'bz2file' 'psutil' 'spdx-tools' 'url' 'binaryornot' 'license-expression' 'html5lib' 'zc.lockfile''six' 'py2-ipaddress' 'MarkupSafe' 'jaraco.timing' 'jinja2' 'intbitset' 'nltk')

for d in "${deps[@]}"
do
    echo $d
    pip uninstall $d --yes
done

