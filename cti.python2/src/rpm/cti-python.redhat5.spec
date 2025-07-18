%define pythonlib %{_prefix}/lib/python2.4/site-packages

Name:			cti-python
Version:		@version.number@
Release:		0
Epoch:			@build.number@
Group:			Publishing
Summary:		Copper PDF Python driver
Source0:		cti-python-@aversion.number@.tar.gz
Requires:		python >= 2.4.0
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Vendor:			Zamasoft
License:		Commercial
URL:			http://copper-pdf.com/
Packager:		MIYABE Tatsuhiko
ExclusiveOS:	linux

%description
cti-python-@version.number@

%prep
rm -rf $RPM_BUILD_ROOT/*
mkdir -p $RPM_BUILD_ROOT%{pythonlib}

%setup

%build

%install
cp -pr code/* $RPM_BUILD_ROOT%{pythonlib}/

%pre

%post

%preun

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%{pythonlib}
