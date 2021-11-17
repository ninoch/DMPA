# DMPA (Directed Mixed Preferential Attachment)

This is the source code of paper ["Emergence of Structural Inequalities in Scientific Citation Networks"](https://arxiv.org/pdf/2103.10944.pdf).
Please cite our work if you found the code or the data useful: 

```
@inproceedings{nettasinghe2021emergence,
  title={Emergence of Structural Inequalities in Scientific Citation Networks},
  author={Nettasinghe, Buddhika & Alipourfard, Nazanin & Krishnamurthy, Vikram and Lerman, Kristina},
  year={2021}
}
```

# Data 
Data can be found in [Open Science Framework](https://osf.io/djxtf/). The "management" field of study is the smallest dataset which you can download and check the code. 

# How to run? 
To run gender networks, specify the field of study and starting year as follow: 
```
python main.py --network_type=gender --field=management --from_year=1990 
```

To run affiliation networks, specify the field of study and starting year and the definition of elite universities (e.g. top-10/20/50/100) as follow: 
```
python main.py --network_type=affiliation --field=management --from_year=1990 --top=100
```

The maximum value of `--top` is 100. 

