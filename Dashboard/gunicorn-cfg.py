# -*- encoding: utf-8 -*-

bind = '0.0.0.0:8000'
# workers = 1
# accesslog = '-'
# loglevel = 'debug'
# capture_output = True
# enable_stdio_inheritance = True


# web: gunicorn -b 0.0.0.0:8000 --workers 1 --threads 100 BOTs.run_bot:app --log-file=-