%define pythonlib1 %{_prefix}/lib/python2.5/dist-packages
%define pythonlib2 %{_prefix}/lib/python2.6/dist-packages
%define pythonlib3 %{_prefix}/lib/python2.7/dist-packages

Name:			cti-python
Version:		@version.number@
Release:		0
Epoch:			@build.number@
Group:			Publishing
Summary:		Copper PDF Python driver
Source0:		cti-python-@aversion.number@.tar.gz
Requires:		python >= 2.7.0
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
mkdir -p $RPM_BUILD_ROOT%{pythonlib1}
mkdir -p $RPM_BUILD_ROOT%{pythonlib2}
mkdir -p $RPM_BUILD_ROOT%{pythonlib3}

%setup

%build

%install
cp -pr code/* $RPM_BUILD_ROOT%{pythonlib1}/
cp -pr code/* $RPM_BUILD_ROOT%{pythonlib2}/
cp -pr code/* $RPM_BUILD_ROOT%{pythonlib3}/

%pre

%post

%preun

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%{pythonlib1}
%{pythonlib2}
%{pythonlib3}
