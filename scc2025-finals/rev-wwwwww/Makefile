.PHONY: build dist clean

build:
	docker build . -t wwwwww

dist: cid = $(shell docker create wwwwww)
dist: build
	mkdir -p dist
	docker cp "${cid}:/app/wwwwww" dist/
	docker rm "${cid}"
	cp Dockerfile dist/
	tar -czvf wwwwww.tar.gz dist/

clean:
	-rm -rf dist/
	-docker rmi wwwwww
	-rm wwwwww.tar.gz
