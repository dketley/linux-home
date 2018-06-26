FROM ubuntu:latest

# Install basic packages
RUN apt-get update && apt-get install -y \
    git \
    sudo

# Whether we're doing a local build
ARG LOCAL

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

# Ensure local copy of install scripts is available in case we're doing a dev build
COPY ./bin/ /tmp/bin/
RUN chown -R $USER:$USERGROUP /tmp/bin/

# Switch to the user
USER $USER
WORKDIR $USERHOME

# Checkout scripts to non-empty directory
RUN git init
RUN git remote add origin https://github.com/dketley/linux-home.git
RUN echo yes | git fetch
RUN git checkout -t origin/master

# If we're doing a local build, copy build scripts
RUN [ $LOCAL ] && rm -rf $INSTALL_SCRIPT_DIR/bin || true
RUN [ $LOCAL ] && mv /tmp/bin $INSTALL_SCRIPT_DIR/bin || true

# Run install scripts. Do this with multiple RUN commands to save time on build
WORKDIR $INSTALL_SCRIPT_DIR/bin
RUN ./docker
RUN ./flatpak
RUN ./todo-txt

# Run bash by default
WORKDIR $USERHOME
CMD ["/bin/bash"]
