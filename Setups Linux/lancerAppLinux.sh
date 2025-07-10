#!/bin/bash
docker load < mon_app_flask.tar
docker run -p 5000:5000 mon_app_flask
#renommer mon_app_flask par le nom du fichier.
