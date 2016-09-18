#!/bin/bash

# source: https://www.outcoldman.com/en/archive/2015/07/28/docker-images-for-home-server-part-2/
GUACAMOLE_HOME="$HOME/.guacamole"
GUACAMOLE_EXT="$GUACAMOLE_HOME/extensions"
GUACAMOLE_LIB="$GUACAMOLE_HOME/lib"
GUACAMOLE_PROPERTIES="$GUACAMOLE_HOME/guacamole.properties"

start_guacamole() {
    cd /usr/local/tomcat
    exec catalina.sh run
}

start_guacamole