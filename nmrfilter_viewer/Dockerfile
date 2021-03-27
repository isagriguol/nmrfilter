FROM continuumio/miniconda:latest
MAINTAINER Ricardo R. da Silva <ridasilva@usp.br>

ENV INSTALL_PATH /home/pylipids
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

RUN wget https://data.qiime2.org/distro/core/qiime2-2020.2-py36-linux-conda.yml
RUN conda env create -n qiime2-2020.2 --file qiime2-2020.2-py36-linux-conda.yml
#RUN rm qiime2-2020.2-py36-linux-conda.yml
RUN bash /opt/conda/bin/activate qiime2-2020.2
RUN /opt/conda/envs/qiime2-2020.2/bin/pip install pydotplus 
RUN bash /opt/conda/bin/deactivate

COPY environment.yml environment.yml
RUN conda env create -f environment.yml
RUN echo "source activate pylipids" > ~/.bashrc
ENV PATH /opt/conda/envs/pylipids/bin:$PATH


COPY . /home/pylipids 
RUN conda install -c anaconda graphviz
RUN pip install pydotplus
RUN Rscript -e 'install.packages("multcompView", repos="https://cloud.r-project.org")'

ENV FLASK_APP app.py 

RUN apt install sshpass
EXPOSE 5030
CMD sh /home/pylipids/run_server.sh 
