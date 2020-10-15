%if 0%{?fedora} > 12 || 0%{?epel} >= 6
%bcond_without python3
%else
%bcond_with python3
%endif

%if 0%{?epel} >= 7
%bcond_without python3_other
%endif

%if 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif
%if 0%{with python3}
%{!?__python3: %global __python3 /usr/bin/python3}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python3_pkgversion: %global python3_pkgversion 3}
%endif  # with python3

%global project_name object-validator
%global project_description %{expand:
This module is intended for validation of Python objects. For this time it's
supposed to be used for validation of configuration files represented as JSON
or for validation of JSON-PRC requests, but it can be easily extended to
validate arbitrary Python objects or to support custom validation rules.}

%bcond_without tests

Name:    python-%project_name
Version: 0.2.1
Release: 1%{?dist}
Summary: Python object validation module

Group:   Development/Libraries
License: MIT
URL:     https://github.com/KonishchevDmitry/%project_name
Source:  http://pypi.python.org/packages/source/o/%project_name/%project_name-%version.tar.gz

BuildArch:     noarch
BuildRequires: make
BuildRequires: python2-devel python-setuptools
%if 0%{with tests}
BuildRequires: pytest >= 2.2.4
%endif  # with tests

%description %{project_description}


%if 0%{with python3}
%package -n python%{python3_pkgversion}-%project_name
Summary: %{summary}
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-setuptools
%if 0%{with tests}
BuildRequires: python%{python3_pkgversion}-pytest >= 2.2.4
%endif  # with tests
%description -n python%{python3_pkgversion}-%project_name %{project_description}
%endif  # with python3


%if 0%{with python3_other}
%package -n python%{python3_other_pkgversion}-%project_name
Summary: %{summary}
BuildRequires: python%{python3_other_pkgversion}-devel
BuildRequires: python%{python3_other_pkgversion}-setuptools
%if 0%{with tests}
BuildRequires: python%{python3_other_pkgversion}-pytest >= 2.2.4
%endif  # with tests
%description -n python%{python3_other_pkgversion}-%project_name %{project_description}
%endif  # with python3_other


%prep
%setup -n %project_name-%version -q


%build
make PYTHON=%{__python2}
%if 0%{with python3}
make PYTHON=%{__python3}
%endif  # with python3
%if 0%{with python3_other}
make PYTHON=%{__python3_other}
%endif  # with python3_other


%check
%if 0%{with tests}
make PYTHON=%{__python2} check
%if 0%{with python3}
make PYTHON=%{__python3} check
%endif  # with python3
%if 0%{with python3_other}
make PYTHON=%{__python3_other} check
%endif  # with python3_other
%endif  # with tests


%install
[ "%buildroot" = "/" ] || rm -rf "%buildroot"

make PYTHON=%{__python2} INSTALL_FLAGS="-O1 --root '%buildroot'" install
%if 0%{with python3}
make PYTHON=%{__python3} INSTALL_FLAGS="-O1 --root '%buildroot'" install
%endif  # with python3
%if 0%{with python3_other}
make PYTHON=%{__python3_other} INSTALL_FLAGS="-O1 --root '%buildroot'" install
%endif  # with python3_other


%files
%defattr(-,root,root,-)
%{python2_sitelib}/object_validator.py*
%{python2_sitelib}/object_validator-%{version}-*.egg-info
%doc ChangeLog README INSTALL

%if 0%{with python3}
%files -n python%{python3_pkgversion}-%project_name
%defattr(-,root,root,-)
%{python3_sitelib}/object_validator.py
%{python3_sitelib}/__pycache__/object_validator.*.py*
%{python3_sitelib}/object_validator-%{version}-*.egg-info
%doc ChangeLog README INSTALL
%endif  # with python3

%if 0%{with python3_other}
%files -n python%{python3_other_pkgversion}-%project_name
%defattr(-,root,root,-)
%{python3_other_sitelib}/object_validator.py
%{python3_other_sitelib}/__pycache__/object_validator.*.py*
%{python3_other_sitelib}/object_validator-%{version}-*.egg-info
%doc ChangeLog README INSTALL
%endif  # with python3_other


%clean
[ "%buildroot" = "/" ] || rm -rf "%buildroot"


%changelog
* Sun Feb 10 2019 Mikhail Ushanov <gm.mephisto@gmail.com> - 0.2.0-3
- Enable tests for python36

* Wed Jan 09 2019 Mikhail Ushanov <gm.mephisto@gmail.com> - 0.2.0-2
- Add python3 package build for EPEL

* Thu Jan 11 2018 Dmitry Konishchev <konishchev@gmail.com> - 0.2.0-1
- Base class for number types with min/max validators
- flake8 linting and tox tests automation

* Tue Apr 26 2016 Dmitry Konishchev <konishchev@gmail.com> - 0.1.6-1
- Bump version because of PyPI error

* Tue Apr 26 2016 Dmitry Konishchev <konishchev@gmail.com> - 0.1.5-1
- min_length and max_length options for List validator

* Thu Sep 03 2015 Dmitry Konishchev <konishchev@gmail.com> - 0.1.4-1
- regex option for String validator

* Wed Feb 25 2015 Dmitry Konishchev <konishchev@gmail.com> - 0.1.3-1
- min_length and max_length options for String validator

* Tue Dec 16 2014 Dmitry Konishchev <konishchev@gmail.com> - 0.1.2-1
- delete_unknown parameter for DictScheme validator

* Mon Nov 24 2014 Dmitry Konishchev <konishchev@gmail.com> - 0.1.1-1
- New version.

* Fri Jul 05 2013 Dmitry Konishchev <konishchev@gmail.com> - 0.1-1
- New package.
