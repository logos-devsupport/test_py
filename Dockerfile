FROM fedora:31
RUN dnf -y update
RUN dnf -y install libgpiod-utils i2c-tools libi2c-devel gcc python3-devel
python3-pip
RUN pip3 install enviroplus
RUN dnf -y install python3-numpy python3-i2c-tools python3-pillow
python3-setuptools python3-libgpiod python3-libgpiod python3-RPi.GPIO
RUN dnf -y install python3-cffi
RUN python3 -m pip install sounddevice
RUN dnf -y install portaudio
RUN dnf clean all
