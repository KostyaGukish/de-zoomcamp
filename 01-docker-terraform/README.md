# Module 1 Homework solutions

## Question 1. Understanding docker first run

To run docker with the `python:3.12.8` image in an interactive mode, using the `bash` entrypoint, and get the `pip` version, you must run these commands in WSL terminal.

`docker run -it --entrypoint=bash python:3.12.8`

`pip -V`

Answer: `24.3.1`.

## Question 2. Understanding Docker networking and docker-compose

`postgres:5432`


## Prepare Postgres

create docker-network: `docker network create pg-network`

create pg db

```
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name pg-database \
  postgres:13
```

check pg connection:
`pgcli -h localhost -p 5432 -u root -d ny_taxi`
`\dt` - to see availible tables

so we can see that there are no tables


To download data and put it to the Postgers you should run this in your bash terminal

TO build docker: `docker build -t taxi_ingest:v001 .`

```
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"

docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=green_tripdata \
    --url=${URL}  
```

```
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=taxi_zone_lookup \
    --url=${URL} 
```

```
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"

python load-data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=green_tripdata \
  --url=${URL}
```

```
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

python load-data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=taxi_zone_lookup \
  --url=${URL}
```

`\dt` - to see availible tables
we can see two tables

run pgAdmin
```
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```

To run docker-compose file `docker-compose up -d`
To stop `docker-compose down`

## Question 3. Trip Segmentation Count

104802, 198924, 109603, 27678, 35189

```
SELECT count(*) FROM green_tripdata
WHERE lpep_pickup_datetime::date >= date '2019-10-1'
	AND lpep_dropoff_datetime::date < date '2019-11-1'
	AND trip_distance > 10
	-- AND trip_distance <= 10
```

## Question 4. Longest trip for each day

```
SELECT lpep_pickup_datetime::date FROM green_tripdata
WHERE trip_distance = (SELECT MAX(t.trip_distance) FROM green_tripdata AS t)
```

2019-10-31

## Question 5. Three biggest pickup zones

```
SELECT 
	CONCAT(taxi_zone_lookup."Borough", ' ', taxi_zone_lookup."Zone") AS loc,
	SUM(total_amount) AS ta 
FROM green_tripdata
JOIN taxi_zone_lookup 
	ON taxi_zone_lookup."LocationID" = green_tripdata."PULocationID"
WHERE lpep_pickup_datetime::date = date '2019-10-18'
GROUP BY loc
HAVING SUM(total_amount) > 13000
ORDER BY ta DESC
```

East Harlem North, East Harlem South, Morningside Heights

## Question 6. Largest tip

```
WITH df AS (
	SELECT 
		green_tripdata.*,
		dro."Zone" AS drop_zone
	FROM green_tripdata
	JOIN taxi_zone_lookup AS pu
		ON pu."LocationID" = green_tripdata."PULocationID"
	JOIN taxi_zone_lookup AS dro
		ON dro."LocationID" = green_tripdata."DOLocationID"
	WHERE pu."Zone" = 'East Harlem North'
		AND to_char(green_tripdata.lpep_pickup_datetime, 'YYYY-MM') = '2019-10'
)

SELECT drop_zone FROM df
WHERE tip_amount = (SELECT MAX(t.tip_amount) FROM df AS t)
```

JFK Airport

## Question 7. Terraform Workflow

terraform init, terraform apply -auto-approve, terraform destroy
