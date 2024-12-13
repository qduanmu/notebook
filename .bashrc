# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
if [ -d ~/.bashrc.d ]; then
	for rc in ~/.bashrc.d/*; do
		if [ -f "$rc" ]; then
			. "$rc"
		fi
	done
fi

unset rc

export WORKON_HOME=~/.virtualenvs
# export SWH_CONFIG_FILENAME=/home/qduanmu/.config/swh/deposit/server.yml
VIRTUALENVWRAPPER_PYTHON='/usr/bin/python3'
source /usr/bin/virtualenvwrapper.sh

# User specific aliases and functions
alias basheng='LC_ALL=C bash'
PS1="[\u@\h \W\$(git branch 2> /dev/null | grep -e '\* ' | sed 's/^..\(.*\)/(\1)/')]\$ "
export REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt
unset HTTP_PROXY
unset http_proxy
unset no_proxy
export HTTP_PROXY=squid.corp.redhat.com:3128
export HTTPS_PROXY=squid.corp.redhat.com:3128

export KOJI_DOWNLOAD=http://download.eng.bos.redhat.com/brewroot
export KOJI_WEBSERVICE=https://brewhub.engineering.redhat.com/brewhub
export KOJI_WEBURL=https://brewweb.engineering.redhat.com/brew
export LDAP_URI=ldap://ldap.corp.redhat.com:389
# export LDAP_USERS_DN=ou=users,dc=redhat,dc=com
export CORGI_API_STAGE=https://corgi-stage.prodsec.redhat.com/api/v1/
export CORGI_ACCESS_TOKEN=vohtueBah4aexoojoNaiPh7ti7Vim3Xe0raim4ba 
export CORGI_API_PROD=https://corgi.prodsec.redhat.com/api/v1/
export OLCS_EXTRACTCODE_CLI=/home/qduanmu/.virtualenvs/openlcs/bin/extractcode
export OLCS_SCANCODE_CLI=/home/qduanmu/.virtualenvs/openlcs/bin/scancode
export OSIDB_API_URL=https://osidb-stage.prodsec.redhat.com/api/v1/
export CORGI_API_URL=https://corgi-stage.prodsec.redhat.com/
# eval "$(_GRIFFON_COMPLETE=bash_source griffon)"
export OIDC_AUTH_URI=https://auth.stage.redhat.com/auth/realms/EmployeeIDP/protocol/openid-connect
export USER_OIDC_CLIENT_ID=openlcs-stage
export USER_OIDC_CLIENT_SECRET=f1873448-3a4e-4bf9-b3b3-07dbcd20831c
export TOKEN_SECRET_KEY=g48uEqBifrWwD5UTQyp_1Xz2zThTNCDqElVAbS9Bkzg=
export LOOKASIDE_CACHE_URL=https://pkgs.devel.redhat.com/repo
export ROOT_CA_URL=https://certs.corp.redhat.com/certs/2015-IT-Root-CA.pem
export ENG_CA_URL=https://engineering.redhat.com/Eng-CA.crt
export TITO_REPO_URL=http://10.0.154.231/openlcs/
export RHEL8_REPO_URL=http://download.eng.bos.redhat.com/brewroot/repos/brew-rhel-8/latest/x86_64/
export OPENSHIFT_CLI_URL=https://downloads-openshift-console.apps.ocp-c1.prod.psi.redhat.com/amd64/linux/oc.tar
export CONFLUENCE_URL=https://docs.engineering.redhat.com
# export CONFLUENCE_TOKEN=MDQxNTMzODQ0MDc4OtpTxU7vTMYhGBTgXgLddazQoLIF
export CONFLUENCE_TOKEN=NTk3NDI4NDk4MzQ4Oivbx0Ya1FkQhqmpLJykEWObZ9lD

export PATH="$PATH:$(yarn global bin)"
export PATH="$PATH:$HOME/go/bin"
export PATH="$PATH:$HOME/projects/complytime/bin"

export OSIM_URL=https://osim-stage.prodsec.redhat.com
export OSIDB_URL=https://osidb-stage.prodsec.redhat.com
export BUGZILLA_API_KEY=dhhmfPjvnRzdDLxK15P9U7PULPjgHZedgWk96NjY
export BUGZILLA_API_KEY=XCvXtFLOWq7WGcUBKJjS9VhgVPLWwStc0jghugHh
export BZ_API_KEY=XCvXtFLOWq7WGcUBKJjS9VhgVPLWwStc0jghugHh
export JIRA_API_KEY=NTg1OTY1Nzg0ODUwOuVglHt/BGzT+YFWVZu1ohbx0ICc

export PUBLIC_FLAW_CVE_ID=CVE-2007-97239
export EMBARGOED_FLAW_CVE_ID=CVE-2000-2000

export PIP_INDEX_URL=https://repository.engineering.redhat.com/nexus/repository/pypi.org/simple/

