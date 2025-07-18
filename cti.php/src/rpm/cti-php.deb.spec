Name:			cti-php
Version:		@version.number@
Release:		0
Epoch:			@build.number@
Group:			Publishing
Summary:		Copper PDF PHP driver
Source0:		cti-php-@aversion.number@.tar.gz
Requires:		php5 >= 5.1.0
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Vendor:			Zamasoft
License:		Commercial
URL:			http://copper-pdf.com/
Packager:		MIYABE Tatsuhiko
ExclusiveOS:	linux

%description
cti-php-@version.number@

%prep
rm -rf $RPM_BUILD_ROOT/*
mkdir -p $RPM_BUILD_ROOT%{_datadir}/php

%setup

%build

%install
cp -pr code/CTI $RPM_BUILD_ROOT%{_datadir}/php/

%pre

%post

%preun

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%{_datadir}/php/CTI
