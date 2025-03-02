## Elasticsearch Backend

### Installing dependencies

```bash
uv pip install -r requirements.txt
```

### Get the CA certificate

Start the elasticsearch cluster

```bash
docker compose up -d
```

Copy the CA certificate to the `deployment-design/elastic-backend` directory

```bash
docker cp deployment-design-es01-1:/usr/share/elasticsearch/config/certs/ca/ca.crt .
```

### Index the dataset

- Create a `.env` file with the correct password referencing `.env.sample`
- Update the `DATASET_PATH` in the `cv-index.py` file to the correct path where the dataset is located

```bash
source .venv/bin/activate # activate the virtual environment
export ELASTIC_PASSWORD=changeme # set the password according to the .env file
python cv-index.py
```
