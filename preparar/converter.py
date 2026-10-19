import sys
import zipfile
from pathlib import Path

import duckdb

ANO = sys.argv[1] if len(sys.argv) > 1 else "2023"
DADOS = Path("dados")
ZIP = DADOS / "bruto" / f"microdados_enem_{ANO}.zip"
PARQUET = DADOS / f"enem_{ANO}.parquet"

COLUNAS = [
    "NU_INSCRICAO",
    "SG_UF_PROVA",
    "TP_ESCOLA",
    "TP_SEXO",
    "TP_COR_RACA",
    "TP_PRESENCA_CN",
    "TP_PRESENCA_CH",
    "TP_PRESENCA_LC",
    "TP_PRESENCA_MT",
    "TP_STATUS_REDACAO",
    "NU_NOTA_CN",
    "NU_NOTA_CH",
    "NU_NOTA_LC",
    "NU_NOTA_MT",
    "NU_NOTA_REDACAO",
    "Q006",
]


def main():
    if PARQUET.exists():
        print(f"{PARQUET} já existe")
        return
    with zipfile.ZipFile(ZIP) as z:
        nome = next(
            n for n in z.namelist()
            if n.upper().endswith(f"MICRODADOS_ENEM_{ANO}.CSV")
        )
        csv = DADOS / "bruto" / Path(nome).name
        if not csv.exists():
            print(f"extraindo {nome}")
            with z.open(nome) as origem, open(csv, "wb") as destino:
                while bloco := origem.read(1 << 24):
                    destino.write(bloco)
    print(f"convertendo para {PARQUET}")
    duckdb.sql(f"""
        copy (
            select {", ".join(COLUNAS)}
            from read_csv('{csv}', delim=';', header=true, encoding='latin-1',
                          all_varchar=true)
        ) to '{PARQUET}' (format parquet, compression zstd)
    """)
    csv.unlink()
    total = duckdb.sql(f"select count(*) from '{PARQUET}'").fetchone()[0]
    print(f"{total:,} inscritos gravados")


if __name__ == "__main__":
    main()
