.PHONY: all clean test build run

IMAGE_NAME = haylinmoore/drone-image-optimizer:latest

all: test

clean:
	rm -rf ./test
	rm -rf ./cache

test: clean build
	mkdir -p test cache
	docker run --rm \
		-v "$$(pwd)/test/:/test" \
		-v "$$(pwd)/test_images/:/test_images/" \
		-v "$$(pwd)/test.py:/app/test.py" \
		-v "$$(pwd)/cache:/cache" \
		--entrypoint "python3" \
		$(IMAGE_NAME) "/app/test.py"
		
build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run -v "$$(pwd)/test:/drone/src" -v "$$(pwd)/cache:/cache" -e PLUGIN_CACHE_DIR=/cache -e PLUGIN_SOURCE_DIR=/drone/src $(IMAGE_NAME)
