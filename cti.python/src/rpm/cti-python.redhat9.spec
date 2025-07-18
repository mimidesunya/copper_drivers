%define pythonlib %{_prefix}/lib/python3.9/site-packages

Name:           cti-python
Version:        @version.number@
Release:        0%{?dist}
Epoch:          @build.number@
Summary:        Copper PDF Python driver
Source0:        cti-python-@aversion.number@.tar.gz
Requires:       python3 >= 3.9
Vendor:         Zamasoft
License:        Commercial
URL:            https://copper-pdf.com/
Packager:       MIYABE Tatsuhiko
ExclusiveOS:    linux

%description
cti-python-@version.number@

%prep
%setup -q

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{pythonlib}
cp -pr code/* %{buildroot}%{pythonlib}/

%pre

%post

%preun

%clean
rm -rf %{buildroot}

%files
%{pythonlib}
