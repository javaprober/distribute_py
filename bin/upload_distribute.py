#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Program: 项目上线自动化
# Author : chenhao
# Date   : 2016-01-03

import ConfigParser
import datetime
import logging
import os
import paramiko
import re
import socket
import sys
import time
import traceback
from progressbar import Bar, ETA, \
  FileTransferSpeed, Percentage, \
  ProgressBar


def ssh2(host, port, username, password, cmds):
  '''
      链接远程服务器并执行命令
  '''
  try:
    paramiko.util.log_to_file('./../log/exec_cmd_' + time_str + '.log')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, int(port), username, password, timeout=5)
    # 执行命令文件中的命令
    for cmd in cmds:
      logging.info('running: ' + cmd)
      print 'running: ' + cmd
      stdin, stdout, stderr = ssh.exec_command(cmd)
      for out_msg in stdout.readlines():
        print out_msg
        
      for err_msg in stderr.readlines():
        print err_msg
    ssh.close()
    print 'command execute successful!'
    logging.info('command execute successful!')
  except Exception, e:
    print '%s\tError\n'%(host)
    print traceback.format_exc()
    __err_exit_show_msg(str(e))
       
def upload(conf, section):
  '''
  上传文件到远程服务器
  '''
  host = conf.get(section, 'host')
  port = conf.get(section, 'port')
  username = conf.get(section, 'username')
  password = conf.get(section, 'password')
  local_file = conf.get(section, 'local_file')
  remote_file = conf.get(section, 'remote_file')
    
  try:
    paramiko.util.log_to_file('../log/upload_' + time_str + '.log')
    logging.info('paramiko log created')
    t = paramiko.Transport((host, int(port)))
    t.connect(username=username, password=password)
    logging.info('connected host <' + host + '> successful')
    logging.info('Upload file SUCCESSFUL %s ' % datetime.datetime.now())
    sftp = paramiko.SFTPClient.from_transport(t)
    logging.info('Upload file SUCCESSFUL %s ' % datetime.datetime.now())
    print 'Beginning to upload file to %s  %s ' % (host, datetime.datetime.now())
    
    # 定义上传进度条样式
    widgets = ['Test: ', Percentage(), ' ',
              Bar(marker='#',left='[',right=']'),
              ' ', ETA(), ' ', FileTransferSpeed()]
    file_size = os.path.getsize(local_file)
    pbar = ProgressBar(widgets=widgets, maxval=file_size)
    # 开始进度条
    pbar.start()
    # 使用匿名方法接收上传返回值，并且显示进度条
    progress_bar = lambda transferred, toBeTransferred: pbar.update(transferred)
    # 开始上传
    sftp.put(local_file, remote_file, callback=progress_bar)
    pbar.finish()
    logging.info('Upload file SUCCESSFUL %s ' % datetime.datetime.now())
    print 'Upload file SUCCESSFUL %s ' % datetime.datetime.now()
    t.close()
    logging.info('sftp closed!')
  except Exception, e:
    logging.error('host: <' + host + '> connect error!')
    print host, 'connect error!'
    print traceback.format_exc()
    __err_exit_show_msg(str(e))

def exec_file_cmd(conf, section, cmd_file):
  '''
  u执行文件中的命令
  '''
  cmds = __get_cmds(cmd_file)
  exec_cmd(conf, section,cmds)
  
def exec_cmd(conf, section, cmd):
  '''
  u执行命令
  '''
  host = conf.get(section, 'host')
  port = conf.get(section, 'port')
  username = conf.get(section, 'username')
  password = conf.get(section, 'password')
  ssh2(host, port, username, password, cmd)
  
  
def backup_ori(conf, section):
  '''
  备份远程原文件
  '''
  host = conf.get(section, 'host')
  port = conf.get(section, 'port')
  username = conf.get(section, 'username')
  password = conf.get(section, 'password')
  remote_file = conf.get(section, 'remote_file')
  remote_ori_backup_dir = conf.get(section, 'remote_ori_backup_dir')
  # 获得备份后缀
  suffix_timestamp = time.localtime(float(time_str))
  suffix_time = time.strftime('%Y-%m-%d_%H-%M-%S', suffix_timestamp)
  backup_ori_cmd = [
    'mkdir -p {dir}'.format(dir = remote_ori_backup_dir),
    'cp {ori_file} {dir}/{new_file}_{time}'.format(ori_file = remote_file, 
                                                   dir = remote_ori_backup_dir,
                                                   new_file = os.path.basename(remote_file),
                                                   time = str(suffix_time)),
    'rm -f {ori_file}'.format(ori_file = remote_file)
  ]
  ssh2(host, port, username, password, backup_ori_cmd)
 
def backup_new(conf, section):
  '''
  备份远程新上传的文件
  '''
  host = conf.get(section, 'host')
  port = conf.get(section, 'port')
  username = conf.get(section, 'username')
  password = conf.get(section, 'password')
  remote_file = conf.get(section, 'remote_file')
  remote_backup_dir = conf.get(section, 'remote_backup_dir')
  # 获得备份后缀
  suffix_timestamp = time.localtime(float(time_str))
  suffix_time = time.strftime('%Y-%m-%d_%H-%M-%S', suffix_timestamp)
  backup_new_cmd = [
    'mkdir -p {dir}'.format(dir = remote_backup_dir),
    'cp {new_file} {dir}/{new_bak_file}_{time}'.format(new_file = remote_file, 
                                                   dir = remote_backup_dir,
                                                   new_bak_file = os.path.basename(remote_file),
                                                   time = str(suffix_time))
  ]
  ssh2(host, port, username, password, backup_new_cmd)
 
def select_section(conf_file_name):
  '''
  选择指定读取的配置文件项
  例如：*.conf配置文件中有多个配置项 a 和 b:
    [a]
    xxxxx
    [b]
    yyyyy
  '''
  # 检测指定的配置文件是否存在
  __check_file_exists(conf_file_name)
  # 读取配置文件
  conf = ConfigParser.ConfigParser()
  conf.read(conf_file_name)
  sections = conf.sections()
  # 选择配置文件选项界面
  print 'please choose confit item:'
  for index, value in enumerate(sections):
    print '  ', index, ':', value
  # 获取用户输入选项
  choose_section_tag = True
  while choose_section_tag:
    sec_index = raw_input('please choose one item default [0]:')
    
    if not sec_index.isdigit() or int(sec_index) >= len(sections):
      print 'choose invalid!'
      continue
    return conf, sections[int(sec_index)] 
    
def check_config(conf, section):
  '''
  检测配置文件的正确性
  '''
  logging.info('check config starting...')
  print 'check config starting...'
  
  # 检测配置文件中值是否都填写
  host = __checke_conf_key_value_empty(conf, section, 'host') # 检测配置文件中主机名
  port = __checke_conf_key_value_empty(conf, section, 'port') # 检测配置文件中端口
  username = __checke_conf_key_value_empty(conf, section, 'username') # 检测配置文件用户名
  password = __checke_conf_key_value_empty(conf, section, 'password') # 检测配置文件密码
  local_file = __checke_conf_key_value_empty(conf, section, 'local_file') # 检测配置文件本地需要上传文件
  remote_file = __checke_conf_key_value_empty(conf, section, 'remote_file') # 检测配置文件上传到远程的文件
  remote_backup_dir = __checke_conf_key_value_empty(conf, section, 'remote_backup_dir') # 检测配置文件远程备份目录
  remote_ori_backup_dir = __checke_conf_key_value_empty(conf, section, 'remote_ori_backup_dir') # 检测配置文件远程临时备份目录
#   start_cmd_file = __checke_conf_key_value_empty(conf, section, 'start_cmd_file') # 检测配置文件启动服务文件
#   stop_cmd_file = __checke_conf_key_value_empty(conf, section, 'stop_cmd_file') # 检测配置文件停止服务文件
  
  # 检测配置文件中的网络是否可用
#   __check_network_ping(host)
  # 检测ssh链接是否成功
  __check_ssh(host, int(port), username, password)
  # 检测本地需要上传的文件是否存在
  __check_file_exists(local_file)
  # 检测命令文件是否存在
#   __check_file_exists(start_cmd_file)
#   __check_file_exists(stop_cmd_file)
  
  print 'check config successful!!'
  logging.info('check config successful!!')

def __valid_ip(address):
  '''
  检测IP是否合法IP
  '''
  try: 
    socket.inet_aton(address)
    return True
  except:
    print traceback.format_exc()
    return False

def __check_file_exists(conf_file_name):
  '''
  检测指定的配置文件是否存在
  '''
  if not os.path.exists(conf_file_name):
    logging.error('can not find config file: ' + conf_file_name)
    __err_exit_show_msg('can not find config file: ' + conf_file_name)
  return conf_file_name

def __checke_conf_key_value_empty(conf, section, key):
  '''
  检测配置文件的key是否存在
  '''
  try:
    value = conf.get(section, key)
    # 检测配置文件中的值是否为空
    if value:
      return value
    else:
      msg = '''
      ERROR  The key:{key} value is empty in conf file
      '''.format(key = key)
      __err_exit_show_msg(msg)
  except ConfigParser.NoOptionError:
    print traceback.format_exc()
    msg = '''
      ERROR  cannot find key:{key} in conf file
    '''.format(key = key)
    __err_exit_show_msg(msg)

def __check_network_ping(host):
  if not __valid_ip(host):
    __err_exit_show_msg('host: ' + host + ' invalid')
  if 0 <> os.system('ping -n 1 -w 5 ' + host):
    __err_exit_show_msg('host: ' + host + ' cannot ping...')
 
def __check_ssh(host, port, username, password):
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password, timeout=5)
    ssh.close()
  except Exception as e:
    print traceback.format_exc()
    msg = '''
    SSH connect failure. 
    please check your host/port/username/password
    host    :  {host}
    port    :  {port}
    username:  {username}
    password:  {password}
    '''.format(host = host, port = port,
               username=username, 
               password=password)
    __err_exit_show_msg(msg)

def __get_cmds(cmd_file):
  '''
  冲文件中获取执行命令
  '''
  with open(cmd_file, 'r') as cmd_f:
    pattern = re.compile('(^\s*#|^\s*$)')
    func = lambda x: x if not re.match(pattern, x) else None
    cmds = [cmd for cmd in cmd_f]
    return filter(func , cmds)
    
def __err_exit_show_msg(msg):
  '''
  发生错误的时候显示相关错误信息并且退出程序
  '''
  print 'ERROR:  ' + msg
  logging.error('ERROR:  ' + msg)
  os.system('pause')
  sys.exit() 
    
if __name__=='__main__':
  try:
    # 设置日志文件
    time_str = str(time.time())
    log_file = '../log/upload_distribution_' + time_str + '.log'
    logging.basicConfig(level=logging.INFO,
                      format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                      filename=log_file,
                      filemode='w',
                      datefmt='%Y-%m-%d %X')

    # 定义配置文件路径
    conf_file_name = '../conf/upload_distribute.conf'
    # 选择配置文件section
    conf, section = select_section(conf_file_name)
    # 检测配置文件正确性
    check_config(conf, section)
    # 执行停止命令
#     stop_cmd_file = conf.get(section, 'stop_cmd_file')
#     exec_file_cmd(conf, section, stop_cmd_file)
    src = conf.get(section, 'src')
    if src.strip()=='':
        print 'src is null'
        __err_exit_show_msg('src file is null !!!')
#     __check_file_exists(src)
    
    remote_file = conf.get(section, 'remote_file')
    awk_cmd = '''awk \'{print$2}\''''
    stop_cmd = [
            'cd {src} && sh bin/stop.sh'.format(src = src),
            'ps -ef | grep '+src+' | grep -v grep | '+awk_cmd+' | xargs kill -9'
    ]
    exec_cmd(conf, section, stop_cmd)
    
    # 备份原文件
    backup_ori(conf, section)
    
    #删除解压文件
    rm_other_file_cmd = [
            'cd {src} && rm -rf *'.format(src = src)
    ]
    exec_cmd(conf, section, rm_other_file_cmd)
    
    # 上传文件
    upload(conf, section)
    # 备份新上传的文件
#     backup_new(conf, section)
    # 执行启动命令
#     start_cmd_file = conf.get(section, 'start_cmd_file')
#     exec_file_cmd(conf, section, start_cmd_file)
    start_cmd = [
        'cd {src} && unzip -uo {remote_file} && sh bin/start.sh product'.format(remote_file = remote_file,src = src)
    ]
    exec_cmd(conf, section, start_cmd)
    # 监听服务是否启动成功
    
    # 实行完毕暂停
#     os.system('pause')
  except Exception as e:
    print traceback.format_exc()
    __err_exit_show_msg(str(e))
