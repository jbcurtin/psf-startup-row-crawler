BOT_NAME = 'pyeye'
SPIDER_MODULES = ['pyeye.spiders']
NEWSPIDER_MODULE = 'pyeye.spiders'
ROBOTSTXT_OBEY = True

# https://github.com/rmax/scrapy-redis#usage
ITEM_PIPELINES = {
#  'scrapy_redis.pipelines.RedisPipeline': 100,
  'pyeye.pipelines.CSVPipeline':100,
}
#REDIS_ITEMS_KEY = 'psf-items'

#%(spider)s:items'
REDIS_ITEMS_SERIALIZER = 'json.dumps'
REDIS_URL = 'redis://localhost:6379'
# DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
DEPTH_LIMIT = 2
CRAWLERA_ENABLED = True
CRAWLERA_APIKEY = ''
# SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
# SCHEDULER_PERSIST = False
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REFERER_ENABLED = True
SPIDER_MIDDLEWARES = {
  'pyeye.middlewares.CustomUserAgentMiddleware': 110,
  'scrapy.spidermiddlewares.referer.RefererMiddleware': 220,
}
DOWNLOADER_MIDDLEWARES = {
  # 'scrapy_crawlera.CrawleraMiddleware': 100,
  'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

RETRY_TIMES = 2
CONCURRENT_ITEMS = 1000
CONCURRENT_REQUESTS = 250
CONCURRENT_REQUESTS_PER_DOMAIN = 100
CONCURRENT_REQUESTS_PER_IP = 10
REACTOR_THREADPOOL_MAXSIZE = 100

# Operations configuration
RETRY_TIMES = 5
CONCURRENT_ITEMS = 50
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 3
CONCURRENT_REQUESTS_PER_IP = 3
REACTOR_THREADPOOL_MAXSIZE = 10

# RETRY_TIMES = 2
# CONCURRENT_ITEMS = 1
# CONCURRENT_REQUESTS = 1
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1
# REACTOR_THREADPOOL_MAXSIZE = 1

# COOKIES_DEBUG = False

# https://doc.scrapy.org/en/latest/topics/broad-crawls.html
COOKIES_ENABLED = True
REDIRECT_ENABLED = True
LOG_LEVEL = 'INFO'
AJAXCRAWL_ENABLED = False
FEED_EXPORT_ENCODING = 'utf-8'
DOWNLOAD_DELAY = 1.25

