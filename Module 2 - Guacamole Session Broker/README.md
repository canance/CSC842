# Guacamole Session Broker

## Purpose
This script is designed to be a proof of concept for a [Guacamole](http://guacamole.incubator.apache.org/) session broker.  At work we currently use Guacamole to allow access to a virtualized desktop environment via the web browser.  We use xrdp to manage the sessions; however, that has some limitations:
- Users have to log in multiple times
  1. Once for mod_auth_kerb
  2. Once for xrdp
- Screen resolutions cannot be changed
- Sound does not work

The main goal of this script is to:
- Authenticate a user
- Launch a vncserver as that user
- Edit guacamole's user-mapping.xml configuration to connect to the newly created vncserver


## Usage
```
$ cd docker
$ docker-compose up
```

- Open a browser and view http://localhost:5000
- Login with the the user name 'test_user' and password 'password'

## Future Development
- Use kerberos authentication
- Create a [custom authenticator](http://guacamole.incubator.apache.org/doc/gug/custom-auth.html) for Guacamole
- Add a database backend to support multiple users and multiple connections
- Use kerberos [service-for-user-to-proxy](https://ssimo.org/blog/id_011.html) to connect to the SSH server without the uesr's password

## Dependencies
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/install/)


