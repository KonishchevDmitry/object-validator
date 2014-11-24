%define project_name object-validator
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

# Run tests
%global with_check 1

Name:    python-%project_name
Version: 0.1.1
Release: 1%{?dist}
Summary: Python object validation module

Group:   Development/Libraries
License: GPLv3
URL:     https://github.com/KonishchevDmitry/%project_name
Source:  http://pypi.python.org/packages/source/o/%project_name/%project_name-%version.tar.gz

Requires: python

BuildArch:     noarch
BuildRequires: make, python-setuptools
%if 0%{?with_check}
BuildRequires: pytest >= 2.2.4
%endif

%description
This module is intended for validation of Python objects. For this time it's
supposed to be used for validation of configuration files represented as JSON
or for validation of JSON-PRC requests, but it can be easily extended to
validate arbitrary Python objects or to support custom validation rules.


%prep
%setup -n %project_name-%version -q


%build
make PYTHON=%__python


%if 0%{?with_check}
%check
make PYTHON=%__python check
%endif


%install
[ "%buildroot" = "/" ] || rm -rf "%buildroot"

make PYTHON=%__python INSTALL_FLAGS="-O1 --root '%buildroot'" install


%files
%defattr(-,root,root,-)
%python_sitelib/object_validator*


%clean
[ "%buildroot" = "/" ] || rm -rf "%buildroot"


%changelog
* Mon Nov 24 2014 Dmitry Konishchev <konishchev@gmail.com> - 0.1.1-1
- New version.

* Fri Jul 05 2013 Dmitry Konishchev <konishchev@gmail.com> - 0.1-1
- New package.
