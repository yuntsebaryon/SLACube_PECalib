# SLACube_PECalib

## Set up the environment

Modify `setup.sh` script according to your environment.
For `SLACUBE_LAYOUT`, you can find the SLACube layout file at 
`/sdf/data/neutrino/yuntse/slacube/etc/layouts/slacube_layout-2.4.0.yaml`
on S3DF.

```shell
source setup.sh
```

## Laser/LED calibration data

Both `bin/analyzePESignal.py` and `bin/analyzePESignalList.py` 
calculate the mean value and the standard deviation
of each pixel channel, subtract the background (the
mean value of the background data),
save the result in the h5 format, and make plots.
`bin/analyzePESignal.py` handles a single signal and a background files, 
while `bin/analyzePESignalList.py` deals with filelists
containing multiple signal and background files.
Run
```shell
python bin/analyzePESignalList.py -h
```
to get the instruction.