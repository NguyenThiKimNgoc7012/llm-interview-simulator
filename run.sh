#!/bin/bash

# Kiểm tra MongoDB có đang chạy không
if pgrep -x "mongod" > /dev/null
then
    echo "✅ MongoDB is already running."
else
    echo "🚀 Starting MongoDB..."
    mongod --dbpath /opt/homebrew/var/mongodb --fork --logpath /opt/homebrew/var/log/mongodb/mongo.log
    sleep 2
fi

# Chạy app Python
echo "🚀 Running Python app..."
python3 app.py

