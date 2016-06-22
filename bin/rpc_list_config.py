#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Program: rpc 服务配置
# Author : chunxiao
# Date   : 2016-04-29
import collections

# rpc 服务名
rpc_list = {
    '0': 'second-party',
    '1': 'complaint',
    '2': 'first-party',
    '3': 'common-service',
    '4': 'operation-logging',
    '5': 'admin-server',
    '6': 'app-server',
    '7': 'first-party-server',
    '8': 'repay',
    '9': 'account',
    '10': 'taskpool',
    '11': 'taskorder',
    '12': 'commission',
    '13': 'repay-evidence',
}

# rpc 对应的目录
rpc_dir_name_list = {
    'first-party': 'first-party',
    'second-party': 'second-party',
    'complaint': 'complaint',
    'common-service': 'common-service',
    'operation-logging': 'operation-logging',
    'repay-evidence': 'repay-evidence',
    'repay': 'repay',
    'admin-server': 'admin-server',
    'app-server': 'app-server',
    'taskpool': 'taskpool',
    'taskorder': 'taskorder',
    'account': 'account',
    'first-party-server': 'first-party-server',
    'commission': 'commission',
}


def get_launcher_dir(name, is_rpc, no_parent_dir):
    if no_parent_dir:
        return '/target/'
    prefix_dir = ''
    if is_rpc:
        prefix_dir = name + '-launcher'
    else:
        prefix_dir = name
    print 'prefix_dir:', prefix_dir, name
    return prefix_dir + '/target/'


def get_launcher_file(name, is_rpc):
    prefix = ''
    if is_rpc:
        prefix = '-launcher'
    ret = name + prefix + '-1.0.0-SNAPSHOT-bin.zip'

    print 'launch file name:', ret
    return ret


def get_remote_file_by_dir_name(dir, is_rpc):
    return rpc_dir_name_list[dir] + '/' + get_launcher_file(rpc_dir_name_list[dir], is_rpc)


def get_local_file_by_dir_name(dir, is_rpc, dir_with_rpc, no_parent_dir, no_rpc_parent_dir):
    s = '';
    rpc_dir = ''
    if dir_with_rpc:
        s = '-rpc'
    if not no_rpc_parent_dir:
        rpc_dir = dir + '-rpc' + '/'
    return rpc_dir_name_list[dir] + s + '/trunk/' + rpc_dir + \
           get_launcher_dir(rpc_dir_name_list[dir], is_rpc, no_parent_dir) + \
           get_launcher_file(rpc_dir_name_list[dir], is_rpc)


def get_task_config_by_name(name):
    is_rpc = True
    dir_with_rpc = False
    no_parent_dir = False
    no_rpc_parent_dir = True
    if name == 'admin-server' or name == 'first-party-server' or name == 'app-server':
        is_rpc = False
        no_parent_dir = True
    if name == 'pushcenter-rpc' or name == 'repay' or name == 'taskorder' \
            or name == 'commission' or name == 'repay-evidence' or name == 'operation-logging':
        dir_with_rpc = True

    if name == 'repay-evidence' or name == 'taskpool' or name == 'operation-logging' or name == 'common-service':
        no_rpc_parent_dir = False
    return {
        'name': name,
        'src': name,
        'remote_file': get_remote_file_by_dir_name(rpc_dir_name_list[name], is_rpc),
        'local_file': get_local_file_by_dir_name(rpc_dir_name_list[name], is_rpc,
                                                 dir_with_rpc, no_parent_dir, no_rpc_parent_dir)
    }

RPC_LIST = collections.OrderedDict(sorted(rpc_list.items()))
