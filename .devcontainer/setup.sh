#!/bin/bash
set -e

echo "Starting Dev Container setup..."

sudo apt-get update

# Configure Git if not already set
if [ -z "$(git config --global user.email)" ]; then
    if [ -n "$GIT_USER_EMAIL" ]; then
        echo "Configuring global git user.email from environment..."
        git config --global user.email "$GIT_USER_EMAIL"
    else
        echo "GIT_USER_EMAIL not set, skipping git config user.email..."
    fi
fi

if [ -z "$(git config --global user.name)" ]; then
    if [ -n "$GIT_USER_NAME" ]; then
        echo "Configuring global git user.name from environment..."
        git config --global user.name "$GIT_USER_NAME"
    else
        echo "GIT_USER_NAME not set, skipping git config user.name..."
    fi
fi

npm install -g @google/gemini-cli

# Persist Gemini CLI history by linking ~/.gemini to the project's .gemini directory
if [ ! -d ".gemini" ]; then
    mkdir .gemini
fi

if [ ! -L "/home/node/.gemini" ]; then
    echo "Linking /home/node/.gemini to $(pwd)/.gemini..."
    # If the directory exists and is not a symlink, back it up or remove it
    if [ -d "/home/node/.gemini" ]; then
        rm -rf /home/node/.gemini
    fi
    ln -s "$(pwd)/.gemini" "/home/node/.gemini"
fi

echo "Dev Container setup complete!"
