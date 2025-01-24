#!/bin/bash

# Set custom paths for configuration and data
XDG_CONFIG_HOME="/home/jsbien/git/tmp/geeqie-PT"
XDG_DATA_HOME="/home/jsbien/git/tmp/geeqie-PT" 

# Launch Geeqie
XDG_CONFIG_HOME="$XDG_CONFIG_HOME" XDG_DATA_HOME="$XDG_DATA_HOME" geeqie "$@"
