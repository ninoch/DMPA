for i in management,1000 aps,1000 psychology,1000 political_science,10 economics,1000 cs,1000
do 
	field=${i%,*};
	delta=${i#*,};
	for top in 10 20 50 100 
	do
		echo "***** Running for affiliation $field 1990 top-$top delta=$delta *****"
		python fig3.py --network_type=affiliation --field=$field --from_year=1990 --top=$top --delta=$delta > logs/d$delta-affiliation-top$top-$field-1990.log
	done 
done 

 # aps,1000 psychology,1000 political_science,10 economics,1000 cs,1000