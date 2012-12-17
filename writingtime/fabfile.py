from fabric.api import *

def live():
	env.hosts = ['clxvi@clxvi.webfactional.com']
	env['dir'] = '/home/clxvi/webapps/writing_time/writingtime'
	env.password = '138plus28'

def pull():
	run ('cd %s; git pull origin master; /home/clxvi/webapps/writing_time/apache2/bin/restart' % env['dir'])

def migration():
	run ('cd %s; python2.7 manage.py migrate' % env['dir'])

def debug_true():
	run ('cd %s; perl -pi -w -e "s/DEBUG = False/DEBUG = True/g;" settings_local.py; /etc/init.d/httpd restart' % env['dir'])

def debug_false():
	run ('cd %s; perl -pi -w -e "s/DEBUG = True/DEBUG = False/g;" settings_local.py; /etc/init.d/httpd restart' % env['dir'])