create or replace table participantes as
with base as (
    select
        NU_INSCRICAO as inscricao,
        SG_UF_PROVA as uf,
        case TP_ESCOLA when '2' then 'Pública' when '3' then 'Privada' end as tipo_escola,
        TP_SEXO as sexo,
        Q006 as faixa_renda,
        ascii(Q006) - ascii('A') + 1 as ordem_renda,
        try_cast(NU_NOTA_CN as double) as nota_cn,
        try_cast(NU_NOTA_CH as double) as nota_ch,
        try_cast(NU_NOTA_LC as double) as nota_lc,
        try_cast(NU_NOTA_MT as double) as nota_mt,
        try_cast(NU_NOTA_REDACAO as double) as nota_redacao
    from read_parquet(getvariable('parquet'))
    where TP_PRESENCA_CN = '1'
      and TP_PRESENCA_CH = '1'
      and TP_PRESENCA_LC = '1'
      and TP_PRESENCA_MT = '1'
      and TP_STATUS_REDACAO = '1'
      and Q006 between 'A' and 'Q'
)
select
    *,
    (nota_cn + nota_ch + nota_lc + nota_mt + nota_redacao) / 5 as nota_media
from base
where nota_cn > 0 and nota_ch > 0 and nota_lc > 0 and nota_mt > 0;

create or replace table faixas_renda as
select * from (values
    ('A', 'Nenhuma renda'),
    ('B', 'Até R$ 1.320'),
    ('C', 'R$ 1.320 a 1.980'),
    ('D', 'R$ 1.980 a 2.640'),
    ('E', 'R$ 2.640 a 3.300'),
    ('F', 'R$ 3.300 a 3.960'),
    ('G', 'R$ 3.960 a 5.280'),
    ('H', 'R$ 5.280 a 6.600'),
    ('I', 'R$ 6.600 a 7.920'),
    ('J', 'R$ 7.920 a 9.240'),
    ('K', 'R$ 9.240 a 10.560'),
    ('L', 'R$ 10.560 a 11.880'),
    ('M', 'R$ 11.880 a 13.200'),
    ('N', 'R$ 13.200 a 15.840'),
    ('O', 'R$ 15.840 a 19.800'),
    ('P', 'R$ 19.800 a 26.400'),
    ('Q', 'Acima de R$ 26.400')
) as t(faixa_renda, descricao);
