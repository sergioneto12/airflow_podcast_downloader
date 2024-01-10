# Podcast Summary DAG

This Python script implements an Airflow Directed Acyclic Graph (DAG) to summarize podcast episodes from a specified URL. It uses various libraries and Airflow's task-based approach to manage and summarize podcast episodes.

## Usage

### Prerequisites
- Python 3.x
- Airflow

### Setup
1. Clone the repository.
2. Install the required Python libraries using `pip install -r requirements.txt`.
3. Ensure Airflow is properly configured and running.

### Configuration
- `PODCAST_URL`: Set the URL of the podcast feed.
- `EPISODE_FOLDER`: Define the folder to store downloaded episodes.
- `FRAME_RATE`: Adjust the frame rate for audio processing.

### DAG Description

#### `podcast_summary()`
- DAG ID: 'podcast_summary'
- Schedule Interval: '@daily'
- Start Date: May 30th, 2022
- Catchup: False

#### Tasks

1. **create_table_sqlite**: Creates a SQLite table if it does not exist to store podcast episode details.
2. **get_episodes**: Retrieves podcast episodes from the specified URL.
3. **load_episodes**: Loads new episodes into the SQLite database.
4. **download_episodes**: Downloads up to 10 episodes and stores them in the defined folder.

### Execution
- Run the script in an Airflow environment to execute the tasks sequentially.

---

Note: This README provides an overview of the script's functionality, prerequisites, setup, configuration, and execution within an Airflow environment. Adjustments may be required based on specific use cases or configurations.
