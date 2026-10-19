.PHONY: baixar preparar construir dados notebook dashboard

ANO ?= 2023
ZIP := dados/bruto/microdados_enem_$(ANO).zip

$(ZIP):
	mkdir -p dados/bruto
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
