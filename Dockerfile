FROM --platform=linux/amd64 python:3.9 
RUN apt-get update
#install system depend
RUN apt-get install -y software-properties-common
#Download and install Fire
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A6DCF7707EBC211F
RUN apt-add-repository "deb http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu bionic main" -y
RUN apt-get update -y
RUN apt-get install firefox -y
# Download and install geckodriver
RUN GECKODRIVER_VERSION=$(curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+') && \
    wget https://github.com/mozilla/geckodriver/releases/download/"$GECKODRIVER_VERSION"/geckodriver-"$GECKODRIVER_VERSION"-linux64.tar.gz && \
    tar -xvzf geckodriver* && \
    chmod +x geckodriver && \
    mv geckodriver /usr/local/bin
ENV DISPLAY=:99
#Install depend and cop files
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "scraper/gorilla_scraper_firefox.py"]

