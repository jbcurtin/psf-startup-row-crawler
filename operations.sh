#!/usr/bin/env bash

spider_name='csvhunter'
config_file="$PWD/pyeye/config.yml"
opts_dir="$PWD/pyeye"
inputs="$PWD/pyeye/inputs"
outputs="$PWD/pyeye/outputs"

if [ "$1" == 'undeploy' ];then
  host='psf'
  username='ubuntu'
  ssh $username@$host "kill -9 $(ps aux|grep $spider_name|grep scrapy |awk '{print $2}')"
  ssh $username@$host "rm -rf pyeye"
fi
if [ "$1" == 'bootstrap' ]; then
  host='psf'
  username='ubuntu'
  ssh $username@$host 'export LC_ALL="en_US.UTF-8"; export LC_CTYPE="en_US.UTF-8"; export DEBIAN_FRONTEND=noninteractive && sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install htop rsync -y'
fi
if [ "$1" == 'deploy' ]; then
  host='psf'
  username='ubuntu'
  rsync -vpa . $host:/home/$username/pyeye \
    --filter=':- .gitignore' \
    --exclude .gitignore \
    --exclude .git
  cat > /tmp/$host-bootstrap.sh <<EOF
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales
sudo DEBIAN_FRONTEND=noninteractive apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
# sudo locale-gen --purge en_US.UTF-8
sudo DEBIAN_FRONTEND=noninteractive apt-get install python3 python3-dev build-essential virtualenv redis-server -y
pushd /home/$username/pyeye 2>/dev/null 1>/dev/null
bash \$PWD/operations.sh install
bash \$PWD/operations.sh start-all
popd 2>/dev/null 1>/dev/null
EOF
  scp /tmp/$host-bootstrap.sh $host:/tmp/$host-bootstrap.sh
  ssh $username@$host "bash /tmp/$host-bootstrap.sh"
fi

if [ "$1" == 'install' ]; then
  if [ ! -d "logs" ];then
    mkdir -p logs
  fi
  if [ ! -d "env" ]; then
    virtualenv -p $(which python3) env
    source env/bin/activate
    pip install -r requirements.txt
  fi
fi

if [ "$1" == 'render-cmds' ]; then
  command_path=$(mktemp)
  touch $command_path
  find $inputs -name "*.csv" | while read filename; do
    basename=$(basename "$filename")
    cat >> $command_path<<EOF
scrapy crawl $spider_name -a config_path="$config_file" -a input_file="$inputs/$basename" -a output_path="$outputs/$basename"
EOF
  done
  cat $command_path
fi
if [ "$1" == 'start-all' ]; then
  # So that we're not running type instances of the same cluster
  kill -9 $(ps aux|grep $spider_name|grep scrapy |awk '{print $2}')
  source env/bin/activate
  find $inputs -name "*.csv"| while read filename; do
    basename="$(basename "$filename")"
    pushd $opts_dir 1> /dev/null 2> /dev/null
    scrapy crawl $spider_name \
      -a config_path="$config_file" \
      -a input_file="$inputs/$basename" \
      -a output_path="$outputs/$basename" \
      1>> "../logs/$basename.log" \
      2>> "../logs/$basename.error.log" &
    sleep 1
    popd 1> /dev/null 2> /dev/null
  done
fi

if [ "$1" == 'kill-all' ]; then
  kill -9 $(ps aux|grep $spider_name|grep scrapy |awk '{print $2}')
fi

if [ "$1" == 'status' ]; then
  spider_count=$(ssh psf ps aux|grep crawl|grep -v grep|wc -l)
  echo "$spider_count spiders still running"
fi
