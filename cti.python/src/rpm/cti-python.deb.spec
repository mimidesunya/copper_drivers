%define pythonlib4 %{_prefix}/lib/python3.10/dist-packages
%define pythonlib5 %{_prefix}/lib/python3.11/dist-packages
%define pythonlib6 %{_prefix}/lib/python3.12/dist-packages

Name:           cti-python
Version:        @version.number@
Release:        0
Epoch:          @build.number@
Summary:        Copper PDF Python driver
Source0:        cti-python-@aversion.number@.tar.gz
Requires:       python3 >= 3.10
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
mkdir -p %{buildroot}%{pythonlib4}
mkdir -p %{buildroot}%{pythonlib5}
mkdir -p %{buildroot}%{pythonlib6}
cp -pr code/* %{buildroot}%{pythonlib4}/
cp -pr code/* %{buildroot}%{pythonlib5}/
cp -pr code/* %{buildroot}%{pythonlib6}/

%pre

%post

%preun

%clean
rm -rf %{buildroot}

%files
%{pythonlib4}
%{pythonlib5}
%{pythonlib6}
