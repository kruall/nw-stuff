import requests
import json
import time
import datetime
import os
import sys
import logging
from lib.ymq import receive_generation_request
from lib.common import run_and_forget, variables

from collections import deque

from transformers import GPTNeoXForCausalLM, GPTNeoXTokenizerFast

import torch
import threading


logger = logging.getLogger()
logging.basicConfig(filename=f'/home/{os.environ["HOME"]}/server.log', level=logging.INFO)
logger.info(f'cuda is available: {torch.cuda.is_available()}')
logger.info(f'torch version: {torch.__version__}')
logger.info(f'aws_access_key_id: {variables.aws_access_key_id}')
logger.info(f'aws_secret_access_key: {variables.aws_secret_access_key}')


class Request:
    def __init__(self, token, application_id, command, options, args=None):
        self.token = token
        self.application_id = application_id
        self.command = command
        self.options = options
        self.args = args

    def __str__(self):
        return f'{{{self.command}, {self.options}}}'


@run_and_forget
def request_task(url, json, headers):
    requests.patch(url, json=json, headers=headers)



class GeneratorWorker:
    def __init__(self):
        try:
            with open('model.txt') as f:
                self.link = f.readline().replace('\n', '').strip()
        except:
            self.link = 'EleutherAI/pythia-70m'
        logger.info(f'initial model is {self.link}')
        self.state = 'none'
        self.model = None
        self.tokenizer = None
        self.default_args = {'temperature': 1.3, 'max_length': 300, 'do_sample': True, 'num_beams': 5, 'no_repeat_ngram_size': 2}
        self.args = {}
        now = datetime.datetime.now()
        self.deadline = now + datetime.timedelta(minutes=60)
        self.model_init_errors = 0

    def init_model(self):
        try:
            start = datetime.datetime.now()
            self.state = 'loading'
            model = GPTNeoXForCausalLM.from_pretrained(self.link).half().cuda()
            tokenizer = GPTNeoXTokenizerFast.from_pretrained(self.link)
            logger.info(f'model {self.link} is loaded by {(datetime.datetime.now() - start).total_seconds():.2f}s')
            self.state = 'ready'
            self.tokenizer = tokenizer
            self.model = model
            logger.info('model is inited')
        except Exception as ex:
            self.state = 'error'
            logger.error(f'expception during handling {ex}')
            if self.model_init_errors > 5:
                sys.exit(1)

    def answer(self, req, text):
        args = (
            f'https://discord.com/api/v8/webhooks/{req.application_id}/{req.token}/messages/@original',
            {'content': text},
            {"Content-Type": "application/json"},
        )
        logger.info(f'send answer {args}')
        request_task(*args)

    def handle(self, req):
        logger.info(f'handle {req}')
        try:
            self.args = req.args
            if req.command == 'set':
                self.default_args[req.options[0]] = eval(req.options[1])

            if req.command == 'del':
                del self.default_args[req.options[0]]

            if req.command in ('args', 'set', 'del'):
                self.answer(req, str(self.args))
                return

            if req.command == 'model':
                old_link = self.link
                with open('model.txt', 'w') as f:
                    f.write(req.options[0])  
                self.link = req.options[0]
                self.model = None
                self.answer(req, f"model starts changing from {old_link} to {self.link}")
                self.init_model()
                return

            if self.model is None:
                try:
                    self.answer(req, f'model state: {self.state}')
                finally:
                    return

            if req.command == 'gen':
                prompt = req.options[0]
                input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to('cuda')
                gen_tokens = self.model.generate(input_ids, **self.args)
                gen_text = self.tokenizer.batch_decode(gen_tokens)[0]
                self.answer(req, f'**{prompt}**{gen_text[len(prompt):]}')
            else:
                self.answer(req, f'**UNKNOWN COMMAND**\n{req.command}\n{req.options}')
        except Exception as ex:
            logger.error(f'expception during handling {ex}')
            self.answer(req, f'**INTERNAL  ERROR**\n{req}\n{ex}')


    def run(self):
        logger.info('start queue handler')
        while True:
            try:
                body = receive_generation_request()
                if body is not None:
                    req = Request(body['token'], body['application_id'], body['command'], body['options'], body.get('args', self.default_args))
                else:
                    req = None
            except Exception as ex:
                logger.error(f'Error during receiving request {ex}')
                req = None

            now = datetime.datetime.now()
            if req is not None:
                self.deadline = max(self.deadline, now + datetime.timedelta(minutes=30))
                self.handle(req)
                continue

            if now > self.deadline:
                logger.info('power off')
                os.system("sudo systemctl poweroff")
                break

            time.sleep(0.5)



if __name__ == '__main__':
    generator = GeneratorWorker()
    logger.info('Script begun')
    generator.init_model()
    generator.run()
