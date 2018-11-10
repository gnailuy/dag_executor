## DAG Executor

### Prepare the environment

``` bash
virtualenv .env
pip install -r requirements.txt
source .env/bin/activate
```

### Prepare a configure file

See: `resources/sample_conf.ini`.

### Docker

``` bash
# Create a network if not exists
docker network create de
# Base Image
docker build -f Dockerfile_base -t gnailuy/de_base .
# DAG Executor
docker build -t gnailuy/dag_executor .
```

### Program usage

``` bash
docker run -d --network de --name dag_executor \
    -v /home/yuliang/de/logs:/app/logs \
    -v /home/yuliang/de/resources:/app/resources \
    -v /home/yuliang/de/modules:/app/modules \
    -v /home/yuliang/de/assets:/app/assets gnailuy/dag_executor

# OR

python main.py -h
```

### Module testing

``` bash
docker run -it --rm --network de --name dag_executor_test --entrypoint sh gnailuy/dag_executor
```

``` bash
python -m modules.example.example
```

