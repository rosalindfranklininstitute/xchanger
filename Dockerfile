FROM continuumio/miniconda3

WORKDIR /app


COPY .env .
RUN mkdir xchanger
COPY xchanger xchanger
COPY xchanger_requirements.txt .
RUN mkdir configs
COPY configs configs


# Make sure the environment is activated:
RUN  pip install -r xchanger_requirements.txt


ENTRYPOINT ["python", "-m", "xchanger.main"]

