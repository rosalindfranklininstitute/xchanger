FROM continuumio/miniconda3

WORKDIR /app


COPY .env .
RUN mkdir xchanger
COPY xchanger xchanger
COPY xchanger_requirements.txt .
RUN mkdir configs
COPY configs configs
COPY setup.cfg .
COPY setup.py .

# Make sure the environment is activated:
RUN  pip install --upgrade build
RUN  pip install  -r xchanger_requirements.txt

RUN  python -m build
RUN  pip install -e .

CMD ["xchanger"]

