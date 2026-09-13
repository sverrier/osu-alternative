-- Stores per-user metric counts + completion coverage date by bucket
-- Buckets:
--   mode_bucket: 0..3, 4 = total
--   fa_bucket:   0 = not FA, 1 = FA, 2 = total
--   diff_bucket: 0 = easy, 1 = hard, 2 = total
-- completed_up_to
--   9999-12-31 = no maps in bucket
--   1900-01-01 = maps exist but user has 0 qualifying scores for metric

CREATE TABLE IF NOT EXISTS public.userstats (
  user_id         BIGINT    NOT NULL,
  mode_bucket     SMALLINT  NOT NULL,
  fa_bucket       SMALLINT  NOT NULL,
  diff_bucket     SMALLINT  NOT NULL,
  metric_type     TEXT      NOT NULL,

  value           INTEGER   NOT NULL,   -- user's count for this metric/bucket
  total           INTEGER   NOT NULL,   -- universe beatmap count for this bucket

  completed_up_to DATE      NOT NULL,   -- coverage date per your rules
  lchg_time       TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT pk_userstats PRIMARY KEY (user_id, mode_bucket, fa_bucket, diff_bucket, metric_type),

  CONSTRAINT ck_userstats_counts_nonneg CHECK (value >= 0 AND total >= 0),
  CONSTRAINT ck_userstats_value_le_total CHECK (value <= total),

  CONSTRAINT ck_userstats_completed_up_to_range CHECK (
    completed_up_to >= DATE '1900-01-01'
    AND completed_up_to <= DATE '9999-12-31'
  )
);

-- For leaderboards / top-N queries by metric and bucket:
CREATE INDEX IF NOT EXISTS idx_userstats_leaderboard
  ON public.userstats (mode_bucket, fa_bucket, diff_bucket, metric_type, value DESC);

-- For "completion" queries (who is complete up to X) or sorting by completion date:
CREATE INDEX IF NOT EXISTS idx_userstats_completion
  ON public.userstats (mode_bucket, fa_bucket, diff_bucket, metric_type, completed_up_to DESC);

-- For per-user lookups (often redundant with PK but helps some plans):
CREATE INDEX IF NOT EXISTS idx_userstats_user
  ON public.userstats (user_id);