Name:           spot
Version:        0.1.0
Release:        1%{?dist}
Summary:        Synthetic Persona Obfuscation Tool
License:        GPL-3.0-or-later
URL:            https://github.com/example/SPOT
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  systemd-rpm-macros

Requires:       python3
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Recommends:     systemd
Suggests:       tor

%description
SPOT (Synthetic Persona Obfuscation Tool) is a privacy research
application for creating isolated synthetic personas and controlled
synthetic activity.

SPOT provides persona management, activity scheduling, browser
isolation, network policy, safety controls, local analytics, auditing,
and platform integration.

SPOT is designed to keep synthetic activity isolated from real
credentials, personal data, and personal browser profiles.

Network privacy features such as Tor and Whonix are integrations and
are not assumed to provide anonymity merely by installing SPOT.

%prep
%autosetup

%build
%py3_build

%install
%py3_install

# Configuration
install -D -m 0644 config/spot.example.yaml \
    %{buildroot}%{_sysconfdir}/spot/spot.example.yaml

install -D -m 0644 config/network.example.yaml \
    %{buildroot}%{_sysconfdir}/spot/network.example.yaml

install -D -m 0644 config/browser.example.yaml \
    %{buildroot}%{_sysconfdir}/spot/browser.example.yaml

install -D -m 0644 config/scheduler.example.yaml \
    %{buildroot}%{_sysconfdir}/spot/scheduler.example.yaml

install -D -m 0644 config/safety.example.yaml \
    %{buildroot}%{_sysconfdir}/spot/safety.example.yaml

install -D -m 0644 config/logging.example.yaml \
    %{buildroot}%{_sysconfdir}/spot/logging.example.yaml

# Personalities
cp -a personalities \
    %{buildroot}%{_datadir}/spot/

# Examples
cp -a examples \
    %{buildroot}%{_datadir}/spot/

# Documentation
cp -a docs \
    %{buildroot}%{_docdir}/%{name}/

# systemd service
install -D -m 0644 packaging/fedora/spot.service \
    %{buildroot}%{_unitdir}/spot.service

# tmpfiles
install -D -m 0644 packaging/fedora/spot.tmpfiles \
    %{buildroot}%{_tmpfilesdir}/spot.conf

%check
# The full SPOT test suite may require optional development
# dependencies and platform-specific test environments.
#
# Run the project test suite separately during CI.
:

%pre
getent group spot >/dev/null || groupadd --system spot
getent passwd spot >/dev/null || \
    useradd --system \
            --gid spot \
            --home-dir /var/lib/spot \
            --shell /sbin/nologin \
            spot

exit 0

%post
%tmpfiles_create %{_tmpfilesdir}/spot.conf
%systemd_post spot.service

%preun
%systemd_preun spot.service

%postun
%systemd_postun_with_restart spot.service

%files
%license LICENSE
%doc README.md
%doc %{_docdir}/%{name}/

%{_bindir}/*
%{python3_sitelib}/spot/

%config(noreplace) %{_sysconfdir}/spot/spot.example.yaml
%config(noreplace) %{_sysconfdir}/spot/network.example.yaml
%config(noreplace) %{_sysconfdir}/spot/browser.example.yaml
%config(noreplace) %{_sysconfdir}/spot/scheduler.example.yaml
%config(noreplace) %{_sysconfdir}/spot/safety.example.yaml
%config(noreplace) %{_sysconfdir}/spot/logging.example.yaml

%{_datadir}/spot/
%{_unitdir}/spot.service
%{_tmpfilesdir}/spot.conf

%dir %attr(0750,spot,spot) %{_sysconfdir}/spot
%dir %attr(0750,spot,spot) %{_sharedstatedir}/spot
%dir %attr(0750,spot,spot) %{_rundir}/spot
%dir %attr(0750,spot,spot) %{_localstatedir}/log/spot

%changelog
* Fri Sep 11 2026 SPOT Project <maintainers@example.invalid> - 0.1.0-1
- Initial Fedora packaging
- Add systemd service integration
- Add tmpfiles configuration
- Add dedicated SPOT service account
- Add systemd security hardening
- Preserve fail-closed privacy and isolation defaults
