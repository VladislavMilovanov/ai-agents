UV ?= uv
IMAGE ?= tg-llm-bot:local

# setuptools editable ставит .pth с именем на `_`; Python ≥3.11 не подхватывает такие файлы — сборка без editable.
export UV_NO_EDITABLE := 1

.PHONY: install run docker-build docker-run

install:
	$(UV) sync

run: install
	$(UV) run python -m tg_llm_bot

docker-build:
	docker build -t $(IMAGE) .

docker-run: docker-build
	docker run --rm -it --env-file .env $(IMAGE)
