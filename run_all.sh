for field in management political_science psychology economics aps cs
do
	echo "***** Running for gender $field 1990 *****"
	python main.py --network_type=gender --field=$field --from_year=1990 > logs/gender-$field-1990.log
done

for field in management political_science psychology economics aps cs
do
	for top in 10 20 50 100
	do
		echo "***** Running for affiliation $field 1990 top-$top *****"
		python main.py --network_type=affiliation --field=$field --from_year=1990 --top=$top > logs/affiliation-top$top-$field-1990.log
	done
done
