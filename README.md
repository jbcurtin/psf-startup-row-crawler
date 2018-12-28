# PSF Entity Discovery

## Reason for Existance
The Python Software Foundation is interested in identifying startups that have been running for less than 2.5 years. This spider helps reduce time finding these startups by following links into websites and then indexes one or two pages deep into the website.

## Deploying the Spiders

* Create an EC2 instance
* Create a `psf` record in `$HOME/.ssh/config`
* Run `bash operations.sh bootstrap`
* Run `bash operations.sh deploy`

## Inputs and Outputs

The inputs directory contains an array of CSV files that are scanned and the links are extracted and used as seeds in the PSF Crawler
https://github.com/jbcurtin/psf-startup-row-spider/tree/master/pyeye/inputs

An `outputs` directory is created parallel to the `inputs` directory with the extended CSVs
