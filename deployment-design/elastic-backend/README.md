## Elasticsearch Backend

The purpose of this backend is to index the dataset into the elasticsearch cluster.

### Indexing the dataset

Uses `uv` as the package manager. Installation instructions can be found [here](https://docs.astral.sh/uv/getting-started/installation/).

#### Installing dependencies

- Create the virtual environment

```bash
uv venv
```

- Activate the virtual environment

```bash
source .venv/bin/activate
```

- Install the dependencies

```bash
uv pip install -r requirements.txt
```

### Set the environment variables

```bash
cp .env.sample .env
```

- Set the password in the `.env` file

```bash
ELASTIC_PASSWORD=changeme
KIBANA_PASSWORD=changeme
```

#### Get the CA certificate from the elasticsearch cluster

- Get the CA certificate for the python client in index script to connect to the elasticsearch cluster.

- Start the elasticsearch cluster (without the search ui; comment out the `search-ui` service in the `docker-compose.yml` file) from the `deployment-design` directory

```bash
cd deployment-design
docker compose up -d
```

- Copy the CA certificate to the `deployment-design/elastic-backend` directory

```bash
cd deployment-design/elastic-backend
docker cp deployment-design-es01-1:/usr/share/elasticsearch/config/certs/ca/ca.crt .
```

- Create a `.env` file with the correct password referencing `.env.sample`
- Update the `DATASET_PATH` in the `cv-index.py` file to the correct path where the dataset is located

```bash
source .venv/bin/activate # activate the virtual environment
export ELASTIC_PASSWORD=changeme # set the password according to the .env file
python cv-index.py
```
