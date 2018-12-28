# PSF Entity Discovery

## Reason for Existance
PuPPy is one of the world's largest Python used groups. One part of PuPPy's mission is helping startups that use Python. This crawler helps reduce time finding these startups by following links into websites and then indexes one or two pages deep into the website.

## Deploying the Spiders

* Create an EC2 instance
* Create a `psf` record in `$HOME/.ssh/config`
* Run `bash operations.sh bootstrap`
* Run `bash operations.sh deploy`

### Deploying The Crawler - Extended

After launching an [AMI(debian) into EC2](https://cloud-images.ubuntu.com/locator/ec2/), you'll need to create an entry in your `$HOME/.ssh/config` file that looks like the following.
```
Host psf
  Hostname 127.0.0.1
  Port 22
  Username ubuntu
  IdentityFile ~/.ssh/ec2-access.pem
```

|SSH Config VarName|Value Definition|
|--------|----------|
|Hostname| IP Address of host|
|Port| Port available to connect ssh to on Host|
|Username| username used to connect with|
|IdentityFile| pem you've downloaded from AWS or provided by IT to you, to access the system|

For more info, run the following command in your terminal.
```
$ man ssh_config
```

## Inputs and Outputs

The inputs directory contains an array of CSV files that are scanned and the links are extracted and used as seeds in the PSF Crawler
https://github.com/jbcurtin/psf-startup-row-spider/tree/master/pyeye/inputs

An `outputs` directory is created parallel to the `inputs` directory with the extended CSVs
