#!/usr/bin/env sh
sudo apt-get update

#sw packages installeren
sudo apt install wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
udo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'

#login  to postgres user account
apt install postgresql postgresql-contrib

#check status
#sevice postgresql status

#
