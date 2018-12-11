import subprocess

from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class CurrentBranchView(ListAPIView):
    """Return the current branch."""

    def get(self, request, *args, **kwargs):
        content = {'current branch': self.get_current_branch()}
        return Response(content)

    def get_current_branch(self):
        process = subprocess.Popen(['git', 'branch'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdoutput, stderroutput = process.communicate(timeout=15)
        try:
            stdoutput_in_string = stdoutput.decode()
            current_branch = stdoutput_in_string.split('* ')[1].split('\n')[0]
            process.kill()
            return current_branch
        except TimeoutError:
            return None
