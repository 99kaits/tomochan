#!/bin/sh
rm -rf -v app/uploads/*
rm -v tomochan.db
sqlite3 tomochan.db < tomochan.sql
