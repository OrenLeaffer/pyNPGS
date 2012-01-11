if test -z $3; then
    echo "usage $0 colorlist.txt filelist.txt ./origdir/"
    exit
fi

for i in `cat $2`; do
    echo $i
    python fixDC2.py $1 ./$3/$i $i
done
