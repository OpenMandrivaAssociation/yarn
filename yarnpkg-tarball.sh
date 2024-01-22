#!/bin/sh
version=$(rpm -q --specfile --qf='%{version}\n' yarn.spec | head -n1)
timestamp=$(date +%Y%m%d)
rm -f v$version.tar.gz
wget https://github.com/yarnpkg/yarn/archive/v$version.tar.gz
tar zxf yarn-$version.tar.gz
cd yarn-$version
for file in $(ls -1 ../*.prebundle.patch 2>/dev/null); do
patch -p1 < $file
done
sed -i s'|"eslint-plugin-babel": "^5.0.0",|"eslint-plugin-babel": "^4.1.1",|' package.json
npm install
npm audit fix
cd ..
tar -zcf yarnpkg-v$version-bundled-$timestamp.tar.gz yarn-$version
