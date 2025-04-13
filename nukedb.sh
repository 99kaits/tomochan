#!/bin/sh
rm -rf -v uploads/*
rm -v tomochan.db
sqlite3 tomochan.db tomochan.sql
