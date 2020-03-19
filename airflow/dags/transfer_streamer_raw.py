# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from builtins import range
from datetime import timedelta, datetime, date
import os
import subprocess
from pprint import pprint
import pendulum

import airflow
from airflow.macros import ds_add, ds_format
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.email import send_email

local_tz = pendulum.timezone("America/New_York")

def notify_email(contextDict, **kwargs):
    """Send custom email alerts."""

    dag_id = contextDict['dag'].dag_id
    task_id = contextDict['task'].task_id

    # email title.
    title = "Airflow alert: {} {} Failed".format(dag_id, task_id)

    # email contents
    body = """
    Hi Everyone, <br>
    <br>
    There's been an error in the {} step of the {} job for {}.<br>
    <br>
    Forever yours,<br>
    Airflow bot <br>
    """.format(task_id, dag_id, contextDict['yesterday_ds'])

    send_email('welling@psc.edu', title, body)


args = {
    'owner': 'Airflow',
    'start_date': datetime(2020, 2, 1, tzinfo=local_tz),
    'xcom_push': True,
    'on_failure_callback': notify_email
}

def compute_yesterday_year(dag, yesterday):
    return yesterday[0:4]

dag = DAG(
    dag_id='transfer_streamer_raw',
    default_args=args,
    schedule_interval = '0 2 * * *',
    dagrun_timeout=timedelta(minutes=60),
    user_defined_macros={
        'yesterday_year' : compute_yesterday_year,
        'dest_root' : '/pylon5/be5fpap/jcolditz/streamer_raw',
        'src_root' : '/dest/streamer_raw',
        'src_host' : 'vm049',
        'real_user' : 'jcolditz' # must be able to sudo to this user
    }
)

verify_dest_dir = BashOperator(
    task_id='verify_dest_dir',
    bash_command='sudo -u {{real_user}} mkdir -p {{dest_root}}/{{yesterday_year(dag, yesterday_ds)}}',
    dag=dag,
)

run_rsync_transfer = BashOperator(
    task_id='run_rsync_transfer',
    bash_command= """ \
    sudo -u {{real_user}} rsync -azii --partial {{src_host}}:{{src_root}}/{{yesterday_ds_nodash}}\\* \
    {{dest_root}}/{{yesterday_year(dag, yesterday_ds)}} \
    | grep '^>f' | awk '{print $2}' | paste -sd ',' -
    """,
    dag=dag,
)

run_rsync_cksum = BashOperator(
    task_id='run_rsync_cksum',
    bash_command= """ \
    sudo -u {{real_user}} rsync -azcvi {{src_host}}:{{src_root}}/{{yesterday_ds_nodash}}\\* \
    {{dest_root}}/{{yesterday_year(dag, yesterday_ds)}}
    """,
    dag=dag,
)

def build_lcl_command(**kwargs):
    year = compute_yesterday_year(kwargs['dag'], kwargs['yesterday_ds'])
    file_l = kwargs['ti'].xcom_pull(task_ids='run_rsync_transfer')
    file_l = [word.strip() for word in file_l.split(',')]
    print('file_l: ', file_l)
    log_l = [word for word in file_l if '_log.tsv' in word]
    log_l += [word for word in file_l if '_errors.txt' in word]
    print('log_l: ', log_l)
    if not log_l:
        return 'echo "no logs to move"'
    dest_root = kwargs['dag'].user_defined_macros['dest_root']
    log_l = [os.path.join(dest_root, year, word)
             for word in log_l]
    cmd_l = ['mv'] + log_l + [os.path.join(dest_root, 'logs')]
    return ' '.join(cmd_l)

t_build_lcl_command = PythonOperator(
    task_id = 'build_lcl_command',
    python_callable = build_lcl_command,
    provide_context = True,
    dag=dag,
)

execute_lcl_command = BashOperator(
    task_id = 'execute_lcl_command',
    bash_command = """ \
    sudo -u {{real_user}} {{ti.xcom_pull(task_ids='build_lcl_command')}}
    """,
    dag=dag,
)

def build_remote_command(**kwargs):
    year = compute_yesterday_year(kwargs['dag'], kwargs['yesterday_ds'])
    file_l = kwargs['ti'].xcom_pull(task_ids='run_rsync_transfer')
    file_l = [word.strip() for word in file_l.split(',')]
    print('file_l: ', file_l)
    if not file_l:
        return 'echo "no files to move"'
    src_root = kwargs['dag'].user_defined_macros['src_root']
    src_host = kwargs['dag'].user_defined_macros['src_host']
    file_l = [os.path.join(src_root, word)
             for word in file_l]
    cmd_l = (['ssh', src_host, 'mv']
             + file_l + [os.path.join(src_root, 'copied_to_pylon5')])
    return ' '.join(cmd_l)

t_build_remote_command = PythonOperator(
    task_id = 'build_remote_command',
    python_callable = build_remote_command,
    provide_context = True,
    dag=dag,
)

execute_remote_command = BashOperator(
    task_id = 'execute_remote_command',
    bash_command = """ \
    sudo -u {{real_user}} {{ti.xcom_pull(task_ids='build_remote_command')}}
    """,
    dag=dag,
)

def build_remote_rm_command(**kwargs):
    target_ds = ds_format(ds_add(date.today().isoformat(), -10),
                          '%Y-%m-%d', '%Y%m%d')
    wildcard_str = '{}\\*'.format(target_ds)
    src_root = kwargs['dag'].user_defined_macros['src_root']
    src_host = kwargs['dag'].user_defined_macros['src_host']
    cmd_l = (['ssh', src_host, 'rm',
              os.path.join(src_root, 'copied_to_pylon5', wildcard_str)])
    return ' '.join(cmd_l)

t_build_remote_rm_command = PythonOperator(
    task_id = 'build_remote_rm_command',
    python_callable = build_remote_rm_command,
    provide_context = True,
    dag=dag,
)

execute_remote_rm_command = BashOperator(
    task_id = 'execute_remote_rm_command',
    bash_command = """ \
    sudo -u {{real_user}} {{ti.xcom_pull(task_ids='build_remote_rm_command')}}
    """,
    dag=dag,
)

run_this_last = BashOperator(
    task_id='run_this_last',
    bash_command=""" \
    echo "here: " {{ti.xcom_pull(task_ids='run_rsync_transfer')}}
    """,
    dag=dag,
)

(verify_dest_dir >> run_rsync_transfer >> run_rsync_cksum
 >> t_build_lcl_command >> execute_lcl_command
 >> t_build_remote_command >> execute_remote_command
 >> t_build_remote_rm_command >> execute_remote_rm_command
 >> run_this_last)

if __name__ == "__main__":
    dag.cli()
