FROM ubuntu:latest

# Install necessary packages
RUN apt-get update
RUN apt-get install -y git sudo

ENV USER test
ENV USERGROUP test
ENV USERPASSWORD test
ENV USERHOME /home/$USER
ENV INSTALL_SCRIPT_DIR $USERHOME/.install-scripts

# Create the user
USER root
RUN groupadd admin
RUN adduser --quiet --home $USERHOME --gecos "$USER $USER,,," --disabled-password $USER
RUN usermod -a -G sudo $USER
RUN usermod -a -G admin $USER
RUN echo "$USER:$USERPASSWORD" | chpasswd

# Ensure user has passwordless sudo
COPY sudoers.awk /tmp/sudoers.awk
RUN cp /etc/sudoers /etc/sudoers.bak
RUN awk -f /tmp/sudoers.awk /etc/sudoers.bak > /etc/sudoers

# Switch to the user
USER $USER
WORKDIR $USERHOME

# Checkout scripts to non-empty directory
RUN git init
RUN git remote add origin https://github.com/dketley/linux-home.git
RUN echo yes | git fetch
# RUN git reset origin/master
RUN git checkout -t origin/master

# Run install scripts
RUN $INSTALL_SCRIPT_DIR/*

# Run bash by default
CMD ["/bin/bash"]
