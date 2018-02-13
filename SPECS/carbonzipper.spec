%define carbon_user carbon
%define carbon_group carbon
%define carbon_loggroup adm

%define debug_package %{nil}
%define _unitdir /usr/lib/systemd/system

Name:	        carbonzipper
Version:	0.73.2
Release:	3%{?dist}
Summary:	proxy to transparently merge graphite carbon backends

Group:		Development/Tools
License:	BSD-2-Clause License
URL:		https://github.com/go-graphite/carbonzipper


# NOTE: carbonzipper.tar.gz was created with the following commands.
# You need to install dep with the following command.
# go get -u github.com/golang/dep/...
#
# mkdir -p carbonzipper/go/src/github.com/go-graphite
# cd carbonzipper/go
# export GOPATH=$PWD
# cd src/github.com/go-graphite
# git clone https://github.com/go-graphite/carbonzipper
# cd carbonzipper
# git checkout 0.73.2
# dep ensure
# cd $GOPATH/../..
# rm -rf carbonzipper/go/pkg
# tar cf - carbonzipper | gzip -9 > carbonzipper.tar.gz
Source0:	carbonzipper.tar.gz

Source1:	carbonzipper.yaml
Source2:	carbonzipper.service
Source3:	logrotate

%{?systemd_requires}
BuildRequires:	systemd
BuildRequires:	golang >= 1.8

%description
CarbonZipper is the central part of a replacement graphite storage stack. It
proxies requests from graphite-web to a cluster of carbon storage backends.
Previous versions (available in the git history) were able to talk to python
carbon stores, but the current version requires the use of go-carbon or
graphite-clickhouse.

%prep
%setup -n %{name}

%build
export GOPATH=%{_builddir}/%{name}/go
cd %{_builddir}/%{name}/go/src/github.com/go-graphite/%{name}
go build

%install
%{__rm} -rf %{buildroot}
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir} -p %{buildroot}%{_localstatedir}/run/%{name}

%{__install} -pD -m 755 %{_builddir}/%{name}/go/src/github.com/go-graphite/%{name}/%{name} \
    %{buildroot}%{_sbindir}/%{name}
%{__install} -pD -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}.yaml
%{__install} -pD -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -pD -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%files
%defattr(-,root,root,-)
%{_sbindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.yaml
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %dir %{_localstatedir}/log/%{name}
%attr(0755,%{carbon_user},%{carbon_group}) %dir %{_localstatedir}/run/%{name}
%{_unitdir}/%{name}.service

%pre
# Add the "carbon" user
getent group %{carbon_group} >/dev/null || groupadd -r %{carbon_group}
getent passwd %{carbon_user} >/dev/null || \
    useradd -r -g %{carbon_group} -s /sbin/nologin \
    --no-create-home -c "carbon user"  %{carbon_user}
exit 0

%post
%systemd_post %{name}.service
if [ $1 -eq 1 ]; then
    # Touch and set permisions on default log files on installation

    if [ -d %{_localstatedir}/log/%{name} ]; then
        if [ ! -e %{_localstatedir}/log/%{name}/%{name}.log ]; then
            touch %{_localstatedir}/log/%{name}/%{name}.log
            %{__chmod} 640 %{_localstatedir}/log/%{name}/%{name}.log
            %{__chown} %{carbon_user}:%{carbon_loggroup} %{_localstatedir}/log/%{name}/%{name}.log
        fi
    fi
fi

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%changelog
* Tue Feb 13 2018 <hnakamur@gmail.com> - 0.73.2-3
- Fix systemd scripts.
  cf. https://fedoraproject.org/wiki/Packaging:Scriptlets?rd=Packaging:ScriptletSnippets#Systemd

* Tue Feb 13 2018 <hnakamur@gmail.com> - 0.73.2-2
- Specify PID file so that graceful restart works.

* Mon Nov 27 2017 <hnakamur@gmail.com> - 0.73.2-1
- 0.73.2

* Thu May 11 2017 <hnakamur@gmail.com> - 0.72-1
- 0.72
