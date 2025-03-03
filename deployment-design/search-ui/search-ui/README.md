### Search UI

#### Install Dependencies

```bash
npm install
```

#### Running the search UI

To run the search UI app, we need to get an API key from the elasticsearch cluster, set it as environment variable and run the search UI app.

- Comment out the `search-ui` service in the `docker-compose.yml` file, to run the elastic search containers only.

```yaml
# ...

#  comment this out in docker-compose.yml
#   search-ui:
#     image: search-ui
#     build:
#       context: ./search-ui/search-ui
#       dockerfile: Dockerfile
#     ports:
#       - 3000:3000
#     depends_on:
#       - es01

# ...
```

- Run the following command to start the elasticsearch containers:

```bash
docker compose up -d
```

- Generate the API key from the elasticsearch cluster and add it to the `.env.local` file.

```bash
# Replace 'password123' with your actual Elasticsearch password
curl -k -X POST "https://localhost:9200/_security/api_key" \
  -u elastic:password123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cv-transcriptions-readonly",
    "role_descriptors": {
      "cv_transcriptions_reader": {
        "cluster": ["monitor"],
        "indices": [
          {
            "names": ["cv-transcriptions"],
            "privileges": ["read", "view_index_metadata"]
          }
        ]
      }
    }
  }'

# Expected output
# {"id":"PMn-WZUBZaNZ_4jC2Cm2","name":"cv-transcriptions-readonly","api_key":"ZFWCpyWmQfCJdvFB0xqaxg","encoded":"UE1uLVdaVUJaYU5aXzRqQzJDbTI6WkZXQ3B5V21RZkNKZHZGQjB4cWF4Zw=="}%

```

- Copy the `encoded` field from the expected output and add it to the `.env.local` file under `deployment-design/search-ui/search-ui/.env.local`.

```bash
cp .env.sample .env.local
```

```bash
NEXT_PUBLIC_ELASTICSEARCH_API_KEY=<change this to the encoded field from the expected output>
```

- Close the containers by running the following command:

```bash
docker compose down
```

- Uncomment the `search-ui` service in the `docker-compose.yml` file, to run the search UI.

```yaml
# ...

#  uncomment this out in docker-compose.yml
search-ui:
  image: search-ui
  build:
    context: ./search-ui/search-ui
    dockerfile: Dockerfile
  ports:
    - 3000:3000
  depends_on:
    - es01
# ...
```

- Run the following command to start the search UI with the elasticsearch cluster:

```bash
docker compose up -d
```

- Check the search UI app by opening the following URL in the browser:

```bash
http://localhost:3000
```

- Shutdown the containers by running the following command:

```bash
docker compose down
```

### Local development

Comment out the `search-ui` service in the `docker-compose.yml` file, to run the elasticsearch containers only.

Start the elasticsearch containers by running the following command:

```bash
docker compose up -d
```

Develop the search UI locally by running the following command:

```bash
npm run dev
```
