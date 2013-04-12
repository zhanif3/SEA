rm -f -R z3py
mkdir z3py
wget "http://download-codeplex.sec.s-msft.com/Download/SourceControlFileDownload.ashx?ProjectName=z3&changeSetId=89c1785b7322" -O z3py/src.zip
cd z3py 
unzip src.zip

autoconf
./configure --with-python=/usr/bin/python2
python2 scripts/mk_make.py --nodotnet

cd build

make

cd .. 
echo "Z3py was installed"
