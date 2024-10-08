# Music Database and Recommendation System Project

This project is a music database and recommendation system built using Docker container architecture. It consists of three main Docker images:

1. **mysql** - The database for storing music-related data.
2. **music-db-api** - The API that interacts with the music database.
3. **music-recsys-api** - The API that provides music recommendations.

## Getting Started

To run the project, you need Docker installed. The system is designed to work with Docker containers, and the necessary images will be pulled or built when you run the Docker Compose file.

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- `.env` file with the following variables for database connection and API keys (make sure this file is in the root directory):
  - 'CLIENT_ID'
  - 'CLIENT_SECRET'
  - 'MYSQL_ROOT_PASSWORD'
  - 'MYSQL_DATABASE'
  - 'MYSQL_HOST'
  - 'MYSQL_PORT'


### Running the Containers

To start the application, use the following command:

```bash
docker-compose up
