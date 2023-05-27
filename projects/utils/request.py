import requests
import subprocess
import logging

from lib.common import run_and_forget, variables


def add_api_key(headers: dict):
    headers['Authorization'] =  f"Api-Key {variables.api_key}"


def get_internal_headers():
    headers =  {"Content-Type": "application/json"}
    add_api_key(headers)
    return headers

logger = logging.getLogger()

@run_and_forget
def start_vm(vm_name):
    url = 'some-url'
    requests.post(url, data=vm_name, headers=get_internal_headers())
