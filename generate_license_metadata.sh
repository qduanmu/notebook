#!/bin/bash

code_url=http://git.app.eng.bos.redhat.com/git/oslc-license-metadata.git
git clone -b develop $code_url
pushd oslc-license-metadata
git archive -o ../license-metadata.tar.gz --prefix=licenses/ HEAD:licenses
popd
rm -rf oslc-license-metadata
