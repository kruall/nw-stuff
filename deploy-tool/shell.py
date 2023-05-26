import subprocess
import pipes


class ProcResult:
    def __init__(self, completed_process):
        self.return_code = completed_process.returncode
        self.stdout = completed_process.stdout.decode('utf-8') if completed_process.stdout else ''
        self.stderr = completed_process.stderr.decode('utf-8') if completed_process.stderr else ''


def run(*cmd):
    if len(cmd) == 1 and isinstance(cmd[0], str):
        shell_cmd = cmd[0]
    else:
        shell_cmd = ' '.join((pipes.quote(x) for x in cmd))
    return ProcResult(subprocess.run(shell_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
