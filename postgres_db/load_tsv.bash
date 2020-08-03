#! /usr/bin/ -e

scriptdir=/pylon5/be5fpap/welling/db_filter
datadir=/pylon5/be5fpap/jcolditz/parser_out/db_data

#tblname=tsvtbl
tblname=tsvtbl

for fname in "$@"
do
    case $fname in
	/*) fullname=$fname ;;
	*) fullname=$datadir/$fname ;;
    esac
    echo 'loading ' $fname
    columns=`head -1 $fullname | sed 's/\t/,/g'`
    python $scriptdir/fix_tsv.py $fullname \
	| /usr/pgsql-9.6/bin/psql -d tweets \
	-c "\COPY ${tblname}(${columns}) FROM STDIN CSV DELIMITER E'\t' HEADER;"
    echo $fullname >> uploaded_files.txt
done
