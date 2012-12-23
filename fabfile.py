from fabric.api import *

def live():
	env.hosts = ['clxvi@clxvi.webfactional.com']
	env['dir'] = '/home/clxvi/webapps/writing_time/writingtime'
	env['apache2'] = '/home/clxvi/webapps/writing_time/apache2/bin/'
	env['branch'] = 'master'
	env['log'] = 'error_writing_time.log'
	env.password = '138plus28'

def dev():
	env.hosts = ['clxvi@clxvi.webfactional.com']
	env['dir'] = '/home/clxvi/webapps/writing_goal_dev/writingtime'
	env['apache2'] = '/home/clxvi/webapps/writing_goal_dev/apache2/bin/'
	env['branch'] = 'dev'
	env['log'] = 'error_writing_goal_dev.log'
	env.password = '138plus28'

def pull():
	run ('cd %s; git pull origin %s; %srestart' % (env['dir'], env['branch'], env['apache2']))

def log():
	run ('cat /home/clxvi/logs/user/%s' % env['log'])

def migration():
	run ('cd %s; python2.7 manage.py migrate' % env['dir'])

def debug_true():
	run ('cd %s; perl -pi -w -e "s/DEBUG = False/DEBUG = True/g;" settings_local.py; /etc/init.d/httpd restart' % env['dir'])

def debug_false():
	run ('cd %s; perl -pi -w -e "s/DEBUG = True/DEBUG = False/g;" settings_local.py; /etc/init.d/httpd restart' % env['dir'])