import tempfile

# create temp dir
with tempfile.TemporaryDirectory() as tempdirname:
    # do something
    print(tempdirname)  # /tmp/tmp23asioej
