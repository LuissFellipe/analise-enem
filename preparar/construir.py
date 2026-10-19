import sys
from pathlib import Path

import duckdb

ANO = sys.argv[1] if len(sys.argv) > 1 else "2023"
BANCO = Path("dados/enem.duckdb")


def main():
    con = duckdb.connect(str(BANCO))
    con.execute(f"set variable parquet = 'dados/enem_{ANO}.parquet'")
    for arquivo in sorted(Path("sql").glob("*.sql")):
        print(f"executando {arquivo.name}")
        con.execute(arquivo.read_text())
    for (tabela,) in con.execute("select table_name from information_schema.tables order by 1").fetchall():
        linhas = con.execute(f"select count(*) from {tabela}").fetchone()[0]
        print(f"  {tabela}: {linhas:,} linhas")
    con.close()


if __name__ == "__main__":
    main()
