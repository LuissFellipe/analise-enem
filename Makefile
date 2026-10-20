.PHONY: baixar preparar construir dados notebook dashboard site

ANO ?= 2023
ZIP := dados/bruto/microdados_enem_$(ANO).zip

$(ZIP):
	mkdir -p dados/bruto
	# O servidor do INEP manda a cadeia de certificados incompleta, e o curl a
	# recusa sem --insecure. O arquivo é público e não leva credencial nenhuma.
	curl -fL --insecure -A "Mozilla/5.0" -C - -o $(ZIP) https://download.inep.gov.br/microdados/microdados_enem_$(ANO).zip

baixar: $(ZIP)

preparar: baixar
	uv run python preparar/converter.py $(ANO)

construir:
	uv run python preparar/construir.py $(ANO)

dados: preparar construir

notebook:
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/analise.ipynb

dashboard:
	uv run streamlit run dashboard/app.py

site:
	uv run python preparar/exportar_site.py $(ANO)
	@echo "abra http://localhost:8003"
	uv run python -m http.server 8003 -d site
