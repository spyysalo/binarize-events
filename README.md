# Binarize events

Special-purpose conversion from BioNLP ST-formatted even structures to
binary relations

## Quickstart

Combine BioNLP ST'09 .a1 and .a2 files

```
mkdir tmp
for f in data/bionlp09_shared_task_training_data_rev2/*.a1; do
    cat ${f%.a1}.{a1,a2} > tmp/$(basename $f .a1).ann
done
```

Binarize

```
mkdir binarized
for f in tmp/*.ann; do python3 binarize.py $f > binarized/$(basename $f); done
```

Include texts

```
cp data/bionlp09_shared_task_training_data_rev2/*.txt binarized
```