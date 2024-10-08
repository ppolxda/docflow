export CUR_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
export CUR_PATH="$(cd -- "$CUR_PATH" && pwd)"
cd $CUR_PATH
docker-compose -f docker-compose.es.yml -f docker-compose.db.yml up -d
