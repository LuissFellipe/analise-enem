create or replace table nota_por_renda as
select
    p.faixa_renda,
    f.descricao,
    count(*) as participantes,
    round(avg(nota_media), 1) as nota_media,
    round(quantile_cont(nota_media, 0.25), 1) as p25,
    round(median(nota_media), 1) as mediana,
    round(quantile_cont(nota_media, 0.75), 1) as p75,
    round(avg(nota_mt), 1) as matematica,
    round(avg(nota_redacao), 1) as redacao
from participantes p
join faixas_renda f using (faixa_renda)
group by all
order by p.faixa_renda;

create or replace table nota_por_renda_escola as
select
    p.faixa_renda,
    f.descricao,
    p.tipo_escola,
    count(*) as participantes,
    round(avg(nota_media), 1) as nota_media
from participantes p
join faixas_renda f using (faixa_renda)
where p.tipo_escola is not null
group by all
order by p.faixa_renda, p.tipo_escola;

create or replace table ranking_uf as
with por_uf as (
    select
        uf,
        count(*) as participantes,
        avg(nota_media) as nota_media,
        avg(nota_media) filter (where tipo_escola = 'Pública') as media_publica,
        avg(nota_media) filter (where tipo_escola = 'Privada') as media_privada,
        avg(ordem_renda) as renda_media_ordinal
    from participantes
    group by uf
)
select
    rank() over (order by nota_media desc) as posicao,
    uf,
    participantes,
    round(nota_media, 1) as nota_media,
    round(media_publica, 1) as media_publica,
    round(media_privada, 1) as media_privada,
    round(media_privada - media_publica, 1) as diferenca_privada_publica,
    rank() over (order by media_publica desc) as posicao_publica,
    round(nota_media - avg(nota_media) over (), 1) as desvio_da_media_nacional
from por_uf
order by posicao;

create or replace table variancia_explicada as
with total as (
    select avg(nota_media) as media, var_pop(nota_media) as variancia, count(*) as n
    from participantes
    where tipo_escola is not null
),
grupos as (
    select 'Renda familiar' as fator, faixa_renda as grupo, count(*) as n, avg(nota_media) as media
    from participantes where tipo_escola is not null group by faixa_renda
    union all
    select 'Tipo de escola', tipo_escola, count(*), avg(nota_media)
    from participantes where tipo_escola is not null group by tipo_escola
    union all
    select 'Renda + escola', faixa_renda || '-' || tipo_escola, count(*), avg(nota_media)
    from participantes where tipo_escola is not null group by faixa_renda, tipo_escola
)
select
    fator,
    round(100 * sum(g.n * power(g.media - t.media, 2)) / (t.n * t.variancia), 1) as pct_variancia_explicada
from grupos g cross join total t
group by fator, t.n, t.variancia
order by pct_variancia_explicada;

create or replace table resumo as
select
    count(*) as participantes,
    count(*) filter (where tipo_escola is null) as escola_nao_informada,
    round(avg(nota_media), 1) as nota_media_geral,
    round(regr_r2(nota_media, ordem_renda), 3) as r2_renda_linear,
    round(corr(nota_media, ordem_renda), 3) as correlacao_renda
from participantes;
