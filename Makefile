all:
	@./bin/run -d ./data

clean:
	find . -type f -name '*.pyc' -o -name '*.swp' -delete
