FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

LABEL    name="Vigor4 Ubuntu" \
         original-author="James Christensen <jchriste@jcvi.org>" \
         modified-by="Torstein Frengen <frengent@gmail.com>" \
         vendor="JCVI" \
         license="GPLv3" \
         build-date="20190204" \
         source-url="https://github.com/JCVenterInstitute/VIGOR4/blob/master/vigor4-ubuntu.docker" \
         modification-date="20240818"

# Install required packages, including missing build tools
RUN apt-get update && apt-get -y install \
    build-essential \
    autoconf \
    automake \
    autotools-dev \
    libtool \
    pkg-config \
    zlib1g-dev \
    libglib2.0-dev \
    git \
    maven \
    openjdk-11-jre-headless \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Clone and build Exonerate v2.4.0
RUN git clone https://github.com/nathanweeks/exonerate.git /tmp/exonerate \
    && cd /tmp/exonerate \
    && git checkout v2.4.0 \
    && autoreconf -i \
    && ./configure --disable-assert \
    && make \
    && make check \
    && make install \
    && rm -rf /tmp/exonerate

# Create the Vigor4 user
RUN useradd --inactive -1 --create-home --comment "Vigor4" --shell /bin/bash vigor4
USER vigor4
WORKDIR /home/vigor4

# Clone and set up Vigor4
RUN git clone https://github.com/JCVenterInstitute/VIGOR4.git vigor4-repo \
    && git clone https://github.com/JCVenterInstitute/VIGOR_DB vigor-db-repo \
    && mkdir /home/vigor4/vigor4-installs \
    && cd vigor4-repo \
    && mvn package \
    && (find target -maxdepth 1 -name 'vigor-4*.zip' | xargs unzip -d /home/vigor4/vigor4-installs) \
    && cd /home/vigor4 \
    && (ls -tr1 /home/vigor4/vigor4-installs/ | tail -n1) \
    && (ls -tr1 /home/vigor4/vigor4-installs/ | tail -n1 | xargs -I{} ln -s /home/vigor4/vigor4-installs/{} /home/vigor4/vigor4) \
    && (echo "\nreference_database_path=/home/vigor4/vigor-db-repo/Reference_DBs/\nexonerate_path=/usr/local/bin/exonerate\ntemporary_directory=/tmp\n" > /home/vigor4/vigor4/config/vigor.ini) \
    && (echo "\n(echo \$PATH| grep -q /home/vigor4/vigor4/bin) || PATH=\$PATH:/home/vigor4/vigor4/bin" >> /home/vigor4/.bashrc)
