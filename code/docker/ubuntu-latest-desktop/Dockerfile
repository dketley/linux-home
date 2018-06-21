FROM ubuntu:latest

ENV USER test
ENV USERGROUP test
ENV USERPASSWORD test
ENV USERHOME /home/$USER

# Install necessary packages
RUN apt-get update
RUN apt-get install -y git sudo

# Create the user
USER root
RUN adduser --quiet --home $USERHOME --gecos "$USER $USER,,," --disabled-password $USER
RUN echo "$USER:$USERPASSWORD" | chpasswd

# Switch to the user
USER $USER
WORKDIR $USERHOME

# Checkout scripts to non-empty directory
RUN git init
RUN git remote add origin https://github.com/dketley/linux-home.git
RUN echo yes | git fetch
# RUN git reset origin/master
RUN git checkout -t origin/master

# Run bash by default
CMD ["/bin/bash"]
