## Prerequisites

* **Docker** and **Docker Compose** installed on your system.

## Repository Structure

flink-take-home-test-main/
├── .venv/               # Python virtual environment (can be ignored)
├── data-generator/
│   ├── data_generator.py # Python script to generate ad events.
│   ├── Dockerfile       # Dockerfile for building the data generator image.
│   └── requirements.txt # Python dependencies for the data generator.
├── flink-job/
│   ├── ad_click_job.py   # PyFlink script for processing ad events.
│   └── Dockerfile       # Dockerfile for building the Flink job image.
├── .gitignore            # Specifies intentionally untracked files that Git should ignore.
├── docker-compose.yml     # Docker Compose configuration for the entire system.
└── INSTRUCTIONS.md      # (Original instructions - can be removed or kept)

* `.venv/`:  (If present) This directory contains a Python virtual environment. It can be ignored for running the solution, but might be important for development.
* `data-generator/`: This directory contains the code for generating simulated ad impression and click events.
    * `data_generator.py`: The Python script responsible for generating the ad event data.
    * `Dockerfile`:  The Dockerfile used to build a Docker image for running the data generator.
    * `requirements.txt`: Lists the Python dependencies required by `data_generator.py` (e.g., `kafka-python`).
* `flink-job/`:  This directory contains the code for the Flink job that processes the ad event data.
    * `ad_click_job.py`:  The PyFlink script that defines the Flink data processing pipeline.
    * `Dockerfile`: The Dockerfile used to build a Docker image for running the Flink job.
* `.gitignore`: Specifies intentionally untracked files that Git should ignore.
* `docker-compose.yml`:  The Docker Compose file that defines the entire application stack, including Zookeeper, Kafka, the data generator, and Flink.
* `INSTRUCTIONS.md`: (If present) The original instructions for the take-home test.

## Running the Solution

To run the ad click analytics pipeline, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone <your_repository_url>
    cd <your_repository_directory>
    ```

2.  **Start the Docker Compose environment:**

    ```bash
    docker-compose up -d
    ```

    This command will:

    * Build the Docker images for the `data-generator` and `flink-job` services.
    * Start all the services defined in `docker-compose.yml` (Zookeeper, Kafka, data generator, Flink JobManager, Flink TaskManager, Flink Job).

3.  **Wait for the services to start:**

    It may take a few moments for all the services to start, especially Kafka and Flink. You can use `docker ps` to check the status of the containers.

## Viewing the Results

The Flink job processes the ad impression and click events and outputs the results to Kafka topics. You can view these results using the `kafka-console-consumer.sh` script within the Kafka container.

### Accessing the Kafka Container

1.  **Enter the Kafka container:**

    ```bash
    docker exec -it kafka bash
    ```

### Viewing CTR Results

1.  **Run the Kafka console consumer for the CTR topic:**

    ```bash
    /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic campaign-ctr-results --from-beginning --property print.key=true
    ```

    This command will display the Click-Through Rate (CTR) for each campaign in 1-minute windows.

### Viewing Engagement Metrics

1.  **Run the Kafka console consumer for the engagement metrics topic:**

    ```bash
    /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic device-engagement-results --from-beginning --property print.key=true
    ```

    This command will display the user engagement metrics (impression count and unique user count) for each device type in 1-minute windows.

### Flink Web UI (Monitoring)

You can also monitor the Flink job execution through the Flink web UI:

1.  **Open your web browser and navigate to `http://localhost:8081`.**

    This will provide a dashboard showing the status of your Flink job, including running tasks, logs, and metrics.

## Code Explanation

* **`data-generator/data_generator.py`**: This Python script generates simulated ad impression and click events and publishes them to the Kafka topics `ad-impressions` and `ad-clicks`.  The generated events include fields like `impression_id`, `user_id`, `campaign_id`, `ad_id`, `device_type`, `browser`, `event_timestamp`, and `cost` for impressions, and `click_id`, `impression_id`, `user_id`, and `event_timestamp` for clicks.

* **`flink-job/ad_click_job.py`**: This PyFlink script defines the streaming data pipeline that processes the ad events.  It performs the following:
    * **Creates Flink tables** (`ad_impressions` and `ad_clicks`) connected to the corresponding Kafka topics, defining the schema and necessary connectors.
    * **Calculates the Click-Through Rate (CTR)** by campaign in 1-minute tumbling windows using Flink's Table API. This involves joining impression and click events (or using windowed aggregations) and calculating the CTR as the ratio of clicks to impressions.
    * **Calculates user engagement metrics** by device type in 1-minute tumbling windows.  These metrics include the count of impressions and the count of unique users for each device type.
    * **Writes the processed results** to new Kafka topics: `campaign-ctr-results` (for CTR) and `device-engagement-results` (for engagement metrics).

## Important Notes

* This solution provides a basic implementation of the requirements.
* (Optional) Anomaly detection was not implemented due to time constraints, but could be added by analyzing the CTR and engagement metrics for deviations from expected patterns.
* (Optional) Unit tests for the Flink jobs were not implemented due to time constraints, but could be added using Flink's testing framework.
* (Optional) A more sophisticated dashboard for visualization could be integrated using tools like Grafana, connecting to Kafka or a database sink, but this was not included in this implementation.
