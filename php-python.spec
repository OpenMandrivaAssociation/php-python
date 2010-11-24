%define modname python
%define soname %{modname}.so
%define inifile A73_%{modname}.ini

Summary:	Embedded Python
Name:		php-%{modname}
Version:	0.9.0
Release:	%mkrel 0.0.r284003.3
Group:		Development/PHP
License:	PHP License
URL:		http://pecl.php.net/package/python
#Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
Source0:	%{modname}.tar.gz
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	php-devel >= 3:5.2.0
BuildRequires:	file
BuildRequires:	python-devel >= 2.5
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
This extension allows the Python interpreter to be embedded inside of PHP,
allowing for the instantiate and manipulation of Python objects from within
PHP.

%prep

%setup -q -n %{modname}

# fix permissions
find . -type f | xargs chmod 644

for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# python version fix
perl -pi -e "s|2\.5|%{py_ver}|g" config.m4

%build
%serverbuild

phpize
%configure2_5x --with-libdir=%{_lib} \
    --with-%{modname}=shared,%{_prefix}

%make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}/var/log/httpd

install -m0755 modules/%{soname} %{buildroot}%{_libdir}/php/extensions/

cat > %{buildroot}%{_sysconfdir}/php.d/%{inifile} << EOF
extension = %{soname}
EOF

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart >/dev/null || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart >/dev/null || :
    fi
fi

%clean
rm -rf %{buildroot}

%files 
%defattr(-,root,root)
%doc docs examples tests CREDITS
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/%{soname}

