



# awk



```sh
awk '{print $2,$4}' employees.txt 
awk '$3=="Engineering" {print $2,$4}'  employees.txt 
awk -F, 'NR>1 {print $1, $2+$3+$4}' /root/awklab/scores.csv > /root/awklab/totals.txt
awk '$4 > 75000 {print $2, $4}' /root/awklab/employees.txt > /root/awklab/high-salary.txt
```


# CUT

```sh
cut -d' ' -f1 access.log | sort | uniq -c | sort -rn > ip-report.txt

cut -d',' -f2,3 /root/log 


sort -rn
uniq -c
```

# Grep

```sh
i
n
c
r
-E "Err|WARN"
```

```sh
grep -E "ERROR|WARN" server.log > warnings-errors.txt 
```



# Json
show human readable json 
```sh
jq '.' users.json
```

find a key
```sh
jq '.users[0].name' users.json
```



```sh
 jq '.[] | select(.active= "true"  and  .role=="developer") .name ' users.json  > active-devs.txt
```

```sh
jq '[.[] | select(.active == true)] | length' /root/jqlab/users.json > /root/jqlab/count.txt
```