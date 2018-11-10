FROM gnailuy/de_base

WORKDIR /app

COPY . .
RUN mkdir -p logs

CMD ["--conf", "./resources/sample_conf.ini"]
ENTRYPOINT ["python", "main.py"]

