import os
import json
import requests
import xmltodict
import pendulum

from airflow.decorators import dag, task
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"
EPISODE_FOLDER = "episodes"
FRAME_RATE = 16000

@dag(
    dag_id='podcast_summary',
    schedule_interval="@daily",
    start_date=pendulum.datetime(2022, 5, 30),
    catchup=False,
)

def podcast_summary():

    created_database = SqliteOperator(
        task_id='create_table_sqlite',
        sql="""
            CREATE TABLE IF NOT EXISTS episodes (
                link TEXT PRIMARY KEY,
                title TEXT,
                filename TEXT,
                published TEXT,
                description TEXT,
                transcript TEXT
            )
        """,
        sqlite_conn_id='podcasts'
    )

    @task()
    def get_episodes():
        data = requests.get(PODCAST_URL)
        feed = xmltodict.parse(data.text)
        episodes = feed["rss"]["channel"]["item"]
        print(f"Found {len(episodes)} episodes.")
        return episodes

    podcast_episodes = get_episodes()
    created_database.set_downstream(podcast_episodes)

    @task()
    def load_episodes(episodes):
        hook = SqliteHook(sqlite_conn_id='podcasts')
        stored = hook.get_pandas_df('SELECT * FROM episodes;')
        new_episodes = []
        for episode in episodes:
            if episode['link'] not in stored['link'].values:
                filename = f"{episode['link'].split('/')[-1]}.mp3"
                new_episodes.append([episode['link'], episode['title'], episode['pubDate'], episode['description'], filename])
        hook.insert_rows(table='episodes', rows=new_episodes, target_fields=['link', 'title', 'published', 'description', 'filename'])

    load_episodes(podcast_episodes)

    @task()
    def download_episodes(episodes):
        path = os.getcwd()
        # print(os.path.join(path, 'episodes'))
        if not os.path.exists(os.path.join(path, 'episodes')):
            os.makedirs(os.path.join(path, 'episodes'))

        for episode in episodes[:10]:
            filename = f"{episode['link'].split('/')[-1]}.mp3"
            audio_path = os.path.join('episodes', filename)
            # audio_path = '/root/mnt/c/Users/sergi/onedrive/Área de Trabalho'
            if not os.path.exists(audio_path):
                print(f'Downloading {filename}')
                audio = requests.get(episode['enclosure']['@url'])
                with open(audio_path, 'wb+') as f:
                    f.write(audio.content)

    download_episodes(podcast_episodes)

summary = podcast_summary()