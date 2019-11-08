# Building and running the examples

This Dockerfile will allow you to follow the examples by building it:

`docker build . -f Dockerfile`

and once it's built, the container must be run as follows:

`docker run  --cap-add SYS_PTRACE -it <hash of the built image>  /bin/bash`

Once you've logged in, activate the virtualenv:
```
root@80c18b8cb6d5:/# . /login/bin/activate
(login) root@80c18b8cb6d5:/# 
```

and change directory to `/data`, where the runnable test scripts are

```
cd /data
