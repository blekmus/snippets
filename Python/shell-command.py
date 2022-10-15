import subprocess


def run_command(shell_command):
    with open('output.log', "a") as outfile:
        subprocess.run(shell_command,
                       shell=True,
                       stdout=outfile,
                       stderr=outfile)
