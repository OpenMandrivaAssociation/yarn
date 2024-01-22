%global npm_name yarn

%{?nodejs_find_provides_and_requires}

%global enable_tests 1

# don't require bundled modules
%global __requires_exclude_from ^(%{nodejs_sitelib}/yarn/lib/.*|%{nodejs_sitelib}/yarn/bin/yarn(|\\.cmd|\\.ps1|pkg.*))$

%global bundledate 20240122

Name:           yarn
Version:        1.22.21
Release:        1
Summary:        Fast, reliable, and secure dependency management.
URL:            https://github.com/yarnpkg/yarn
# we need tarball with node_modules
Source0:        yarnpkg-v%{version}-bundled-%{bundledate}.tar.gz
Source1:        yarnpkg-tarball.sh
License:        BSD

# These are applied by yarnpkg-tarball.sh
# async-CVE-2021-43138.prebundle.patch
# minimatch-CVE-2022-3517.prebundle.patch
# thenify-CVE-2020-7677.prebundle.patch
# decode-uri-component-CVE-2022-38900.prebundle.patch

# Backport fix for CVE-2021-35065 for bundled glob-parent
Patch1:         glob-parent-CVE-2021-35065.patch

BuildArch:      noarch

BuildRequires:  nodejs-packaging
BuildRequires:  nodejs

%description
Fast, reliable, and secure dependency management.

%prep
%autosetup -p1

%build
# use build script
npm run build

# remove build dependencies from node_modules
npm prune --production

%install
mkdir -p %{buildroot}%{nodejs_sitelib}/%{name}

cp -pr package.json lib bin node_modules \
    %{buildroot}%{nodejs_sitelib}/%{name}

mkdir -p %{buildroot}%{_bindir}
ln -sfr %{buildroot}%{nodejs_sitelib}/%{name}/bin/yarn.js %{buildroot}%{_bindir}/yarnpkg
ln -sfr %{buildroot}%{nodejs_sitelib}/%{name}/bin/yarn.js %{buildroot}%{_bindir}/yarn

# Fix the shebang in yarn.js because brp-mangle-shebangs fails to detect this properly (rhbz#1998924)
sed -e "s|^#!/usr/bin/env node$|#!/usr/bin/node|" \
    -i %{buildroot}%{nodejs_sitelib}/%{name}/bin/yarn.js

# Remove executable bits from bundled dependency tests
find %{buildroot}%{nodejs_sitelib}/%{name}/node_modules \
    -ipath '*/test/*' -type f -executable \
    -exec chmod -x '{}' +

%if 0%{?enable_tests}
%check
%nodejs_symlink_deps --check
if [[ $(%{buildroot}%{_bindir}/yarnpkg --version) == %{version} ]] ; then echo PASS; else echo FAIL && exit 1; fi
if [[ $(%{buildroot}%{_bindir}/yarn --version) == %{version} ]] ; then echo PASS; else echo FAIL && exit 1; fi
%endif


%files
%doc README.md
%license LICENSE
%{_bindir}/yarnpkg
%{_bindir}/yarn
%{nodejs_sitelib}/%{name}/
