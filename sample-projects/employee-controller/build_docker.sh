if [ "$#" -ne 1 ]; then
    echo "Usage: build_docker.sh <image-name>"
    exit
fi
mvn package
docker build -t $1 .