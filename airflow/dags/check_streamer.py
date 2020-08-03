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
from dateutil.parser import parse
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

def notify_fail_email(contextDict, **kwargs):
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

    send_email(['welling@psc.edu', 'colditzjb@pitt.edu'], title, body)


def notify_success_email(contextDict, **kwargs):
    """Send custom email alerts."""

    dag_id = contextDict['dag'].dag_id
    task_id = contextDict['task'].task_id
    if 'msg' in kwargs:
        msg = kwargs['msg']
    else:
        msg = "The {} job succeeded for {}.".format(dag_id, contextDict['yesterday_ds'])

    # email title.
    title = "Airflow alert: {} succeeded".format(dag_id)

    # email contents
    body = """
    Hi Everyone, <br>
    <br>
    {}<br>
    <br>
    Forever yours,<br>
    Airflow bot <br>
    """.format(msg)

    send_email(['welling@psc.edu', 'colditzjb@pitt.edu'], title, body)

args = {
    'owner': 'Airflow',
    'start_date': datetime(2020, 3, 21, tzinfo=local_tz),
    'xcom_push': True,
    'on_failure_callback': notify_fail_email
}

def compute_yesterday_year(dag, yesterday):
    return yesterday[0:4]

dag = DAG(
    dag_id='check_streamer',
    default_args=args,
    schedule_interval = '30 * * * *',
    dagrun_timeout=timedelta(minutes=60),
    user_defined_macros={
        'yesterday_year' : compute_yesterday_year,
        'json_dir' : '/dest/streamer_raw',
        'src_host' : 'vm049',
        'real_user' : 'jcolditz' # must be able to sudo to this user
    }
)

look_for_json = BashOperator(
    task_id='look_for_json',
    bash_command=""" \
    sudo -u {{real_user}} \
    ssh {{src_host}} ls -al --time-style=full-iso {{json_dir}}/\\*.json \
    | tail -1 | awk '{print $6"T"$7}'
    """,
    dag=dag,
)

def check_timestamp(**kwargs):
    timecode = kwargs['ti'].xcom_pull(task_ids="look_for_json")
    update_time = parse(timecode)
    time_since_update = datetime.now() - update_time
    print("time since update: {}".format(time_since_update))
    if time_since_update > timedelta(minutes=30):
        dag_id = kwargs['task'].dag_id
        task_id = kwargs['task'].task_id
    
        # email title.
        title = "Airflow alert: {} spotted a problem".format(dag_id)
    
        # email contents
        body = """
        Hi Everyone, <br>
        <br>
        {} noticed that the streamer hasn't captured any tweets in {}<br>
        <br>
        Forever yours,<br>
        Airflow bot <br>
        """.format(dag_id, time_since_update)
    
        send_email(['welling@psc.edu', 'colditzjb@pitt.edu'], title, body)

check_timestamp_op = PythonOperator(
    task_id='check_timestamp',
    python_callable=check_timestamp,
    provide_context=True,
    dag=dag
    )

look_for_json >> check_timestamp_op

if __name__ == "__main__":
    dag.cli()
