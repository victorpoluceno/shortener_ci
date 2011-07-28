from fabric.api import local, put, run, sudo, settings

def setup_ci():
    sudo("apt-get install python-dev")
    sudo("apt-get install python-virtualenv")
    sudo("apt-get install git-core")

    # install jenkins
    sudo("wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | apt-key add -")
    sudo("sh -c 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'")
    sudo("apt-get update")
    sudo("apt-get install jenkins")

    # install apache2
    sudo("apt-get install apache2")
    sudo("a2enmod proxy")
    sudo("a2enmod proxy_http")
    sudo("a2enmod vhost_alias")
  
    # config site
    sudo("a2dissite default")
    put("conf/jenkins", "/etc/apache2/sites-available/jenkins", use_sudo=True)
    sudo("a2ensite jenkins")

    # restart apache
    sudo("apache2ctl restart")


def setup_db():
    # install environment requirements
    sudo("apt-get install postgresql")
    sudo("apt-get install libpq-dev")

    # update pg_hba.conf to alow connection with postgresql
    put("conf/pg_hba.conf", "/etc/postgresql/8.4/main/pg_hba.conf", use_sudo=True)
    sudo("service postgresql restart")

    # create user, change password and create a new database
    with settings(warn_only=True):
        run("createuser -U postgres tests")
        run("psql -U postgres -c \"alter user tests with PASSWORD 'tests';\"")
        run("createdb -U tests rest_api")


def setup_queue():
    # install rabbitmq
    sudo("apt-get install rabbitmq-server")

    # add user, vhost, and set permission
    sudo("rabbitmqctl add_user tests tests")
    sudo("rabbitmqctl add_vhost tests-vhost")
    sudo("rabbitmqctl set_permissions -p tests-vhost tests \".*\" \".*\" \".*\"")
