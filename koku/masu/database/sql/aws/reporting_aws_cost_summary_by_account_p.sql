DELETE FROM {{schema | sqlsafe}}.reporting_aws_cost_summary_by_account_p
WHERE usage_start >= {{start_date}}::date
    AND usage_start <= {{end_date}}::date
    AND source_uuid = {{source_uuid}}
;

INSERT INTO {{schema | sqlsafe}}.reporting_aws_cost_summary_by_account_p (
    id,
    usage_start,
    usage_end,
    usage_account_id,
    account_alias_id,
    organizational_unit_id,
    unblended_cost,
    blended_cost,
    savingsplan_effective_cost,
    markup_cost,
    markup_cost_blended,
    markup_cost_savingsplan,
    currency_code,
    source_uuid
)
    SELECT uuid_generate_v4() as id,
        usage_start,
        usage_start as usage_end,
        usage_account_id,
        max(account_alias_id) as account_alias_id,
        max(organizational_unit_id) as organizational_unit_id,
        sum(unblended_cost) as unblended_cost,
        sum(blended_cost) as blended_cost,
        sum(coalesce(savingsplan_effective_cost, 0.0::numeric(24,9))) AS savingsplan_effective_cost,
        sum(markup_cost) as markup_cost,
        sum(coalesce(markup_cost_blended, 0.0::numeric(33,15))) AS markup_cost_blended,
        sum(coalesce(markup_cost_savingsplan, 0.0::numeric(33,15))) AS markup_cost_savingsplan,
        max(currency_code) as currency_code,
        {{source_uuid}}::uuid as source_uuid,
        row_number() over (partition by usage_start, usage_account_id order by sum(usage_amount) desc) as rank
    FROM {{schema | sqlsafe}}.reporting_awscostentrylineitem_daily_summary
    WHERE usage_start >= {{start_date}}::date
        AND usage_start <= {{end_date}}::date
        AND source_uuid = {{source_uuid}}::uuid
    GROUP BY usage_start, usage_account_id
;


/*
DELETE FROM {{schema | sqlsafe}}.reporting_aws_cost_summary_by_account_p
WHERE usage_start >= '2022-03-01'::date
    AND usage_start <= '2022-05-01'::date
    AND source_uuid = 'e91b0099-c3d2-49ad-af6c-422abb87482c'
;
*/

CREATE TABLE if not exists acct10001.reporting_aws_cost_rank_by_account_p
(
    id uuid not null,
    usage_start date not null,
    usage_rank int not null,
    usage_account_id text,
    account_alias_id bigint,
    organizational_unit_id bigint,
    others_count int,
    total_usage_amount numeric(36,16),
    unblended_cost numeric(36,16),
    blended_cost numeric(36,16),
    savingsplan_effective_cost numeric(36,16),
    markup_cost numeric(36,16),
    markup_cost_blended numeric(36,16),
    markup_cost_savingsplan numeric(36,16),
    currency_code text,
    source_uuid uuid,
    primary key (usage_start, id)
)
partition by range (usage_start);


-- Get ranked data for graph table
insert
  into acct10001.reporting_aws_cost_rank_by_account_p
       (
           usage_start,
           usage_rank,
           usage_account_id,
           account_alias_id,
           organizational_unit_id,
           others_count,
           total_usage_amount,
           unblended_cost,
           blended_cost,
           savingsplan_effective_cost,
           markup_cost,
           markup_cost_blended,
           markup_cost_savingsplan,
           currency_code,
           source_uuid
       )
-- Re-aggregate for rank > 5
select usage_start,
       case when usage_rank > 5  then 6 else usage_rank end::int as usage_rank,
       case when usage_rank > 5 then 'others' else usage_account_id end::text as usage_account_id,
       case when usage_rank > 5 then 0 else account_alias_id end::bigint as account_alias_id,
       case when usage_rank > 5 then 0 else organizational_unit_id end::int as organizational_unit_id,
       sum((usage_rank > 5)::bool::int)::int as others_count,
       sum(total_usage_amount) as total_usage_amount,
       sum(unblended_cost) as unblended_cost,
       sum(blended_cost) as blended_cost,
       sum(savingsplan_effective_cost) as savingsplan_effective_cost,
       sum(markup_cost) as markup_cost,
       sum(markup_cost_blended) as markup_cost_blended,
       sum(markup_cost_savingsplan) as markup_cost_savingsplan,
       max(currency_code) as currency_code,
       'e91b0099-c3d2-49ad-af6c-422abb87482c'::uuid as source_uuid
  from (
    -- Rank via row_number() for absolute ranking
    select
           row_number() over (partition by usage_start order by total_usage_amount desc ) as usage_rank,
           usage_start,
           usage_account_id,
           account_alias_id,
           organizational_unit_id,
           total_usage_amount,
           unblended_cost,
           blended_cost,
           savingsplan_effective_cost,
           markup_cost,
           markup_cost_blended,
           markup_cost_savingsplan,
           currency_code
      from (
        -- Initial Aggregation
        SELECT
            usage_start,
            usage_account_id,
            max(account_alias_id) as account_alias_id,
            max(organizational_unit_id) as organizational_unit_id,
            sum(usage_amount) as "total_usage_amount",
            sum(unblended_cost) as unblended_cost,
            sum(blended_cost) as blended_cost,
            sum(coalesce(savingsplan_effective_cost, 0.0::numeric(24,9))) AS savingsplan_effective_cost,
            sum(markup_cost) as markup_cost,
            sum(coalesce(markup_cost_blended, 0.0::numeric(33,15))) AS markup_cost_blended,
            sum(coalesce(markup_cost_savingsplan, 0.0::numeric(33,15))) AS markup_cost_savingsplan,
            max(currency_code) as currency_code
        FROM acct10001.reporting_awscostentrylineitem_daily_summary
        WHERE usage_start >= '2022-02-01'::date
            AND usage_start <= '2022-05-01'::date
            AND source_uuid = 'e91b0099-c3d2-49ad-af6c-422abb87482c'::uuid
        GROUP BY usage_start, usage_account_id
      ) as x
  ) as y
 GROUP by 1, 2, 3, 4, 5
 order by 1, 2 nulls last
;

/*
select usage_start,
       usage_rank,
       usage_account_id,
       others_count,
       blended_cost,
       total_cost,
       round((blended_cost / total_cost) * 100::numeric(36,16), 4) as cost_pct
from (
select usage_start,
       usage_rank,
       case when usage_account_id = '' then 'others' else usage_account_id end::text as "usage_account_id",
       others_count,
       blended_cost,
       sum(blended_cost) over w as "total_cost"
  from acct10001.reporting_aws_cost_rank_by_account_p
 where usage_start between '2022-03-01'::date and '2022-03-03'::date
window w as (partition by usage_start)
      ) as x
;
*/

-- Query for graph??
select usage_start,
       usage_account_id,
       avg(total_usage_amount) as avg_usage_amount,
       avg(blended_cost) as avg_blended_cost,
       sum(Blended_cost) as tot_blended_cost
  from acct10001.reporting_aws_cost_rank_by_account_p
 where usage_start between '2022-03-30'::date and '2022-04-02'::date
 group
    by usage_start,
       usage_account_id
 order
    by usage_start,
       case when usage_account_id = 'others' then 1 else 0 end::int,
       3 desc
;
