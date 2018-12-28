PSF Entity Discovery
--------------------

Deploying the Spiders
#####################


* Create an EC2 instance
* Create a `psf` record in `$HOME/.ssh/config`
* Run `bash operations.sh bootstrap`
* Run `bash operations.sh deploy`

Some of the :point-up: might need to be fixed to smooth out the automation.


Start Service
```
virtualenv -p $(which python3) env
source env/bin/activate
pip install -r requirements.txt
$ docker run -p 8050:8050 scrapinghub/splash
```

RoadMap
*******

```
Ok, I think I have a good-enough roadmap for what I'm calling `Pyeye`.  [ Please come up with a better name ]

( Phase 1 )

- Upgrade current spider to capture E-mails. ( Scheduled to work on this on Saturday, should be ready within two weeks. )

( Phase 2 )

- Dissassemble and rebuild parts of `Pyeye` into a more agnostic spider. Taking websites and csv, and returning data from those.

-- A unit of work will be based off a CSV or WebURL. ( 0.25c )

-- A unit of work for a CSV will return a CSVOutput with predefined inputs. ( Keywords, Phrases )

-- A unit of work for a WebSite will return an Index that you'll query via a WebSite I build. The search engine will be Elastic Search. It'll work much like google or bing, but with customized output that'll cator to making the user experiance better. 

( Phase 3 )

- Create the Company Technical Profile

( Phase 4 )

- Create the Company Buisness Profile ( Tools used by buisness and not technology. )



It'll take me a 1-3 months to get the website part up and running. I'm currently building a new framework on the scale of Django/Flask to help with this kind of stuff. Its about 60% complete. More on that later.
```
