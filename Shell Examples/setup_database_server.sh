#!/bin/bash

echo "Updating packages..."
sudo apt update -y
sudo apt upgrade -y
echo "Update Complete"

echo "Install Apache and mod_wsgi..."
sudo apt install -y apache2 apache2-dev
sudo apt install -y libapache2-mod-wsgi-py3
echo "Apache and mod_wsgi are installed."

echo "Install Python packages..."
python3 -m pip install flask yfinance numpy matplotlib pandas psycopg2-binary
echo "Python packages installed."

echo "Set up PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
echo "PostgreSQL Complete"

# Change ownership and permissions of /var/www
echo "Set up /var/www directory permissions..."
sudo chown -R $USER:$USER /var/www
chmod -R 755 /var/www
echo "Permissions set."

echo "Create Apache site configuration..."
echo "
<VirtualHost *:80>
    ServerName localhost
    WSGIScriptAlias / /var/www/g04econ/g04econ.wsgi
    <Directory /var/www/g04econ/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog \${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog \${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
" | sudo tee /etc/apache2/sites-available/g04econ.conf

echo "Apache site configuration is ready."

echo "Enabling site..."
sudo a2ensite g04econ
sudo service apache2 reload
echo "Site enabled and Apache reloaded."

echo "Setup Complete"

