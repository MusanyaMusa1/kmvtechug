-- =====================================================================================
-- KMVTECH Education - ADS: schedule your own banners, they stop and clear themselves
-- Run once in the Supabase SQL Editor (after 001-security-and-plans.sql). Safe to run again.
-- =====================================================================================

-- ---- 1. the ads and their daily view/click counts --------------------------------------
create table if not exists public.ads (
  id          uuid primary key default gen_random_uuid(),
  title       text not null check (char_length(btrim(title)) between 1 and 120),
  advertiser  text check (advertiser is null or char_length(advertiser) <= 120),
  image_path  text,
  link_url    text not null check (link_url ~* '^https?://[^[:space:]]+$' and char_length(link_url) <= 500),
  placements  text[] not null default array['home']
              check (cardinality(placements) >= 1 and placements <@ array['home', 'dashboard', 'courses']),
  starts_at   timestamptz not null,
  ends_at     timestamptz not null,
  is_paused   boolean not null default false,
  note        text,
  created_by  uuid references public.profiles(id),
  created_at  timestamptz not null default now(),
  check (ends_at > starts_at)
);
create index if not exists ads_schedule_idx on public.ads (starts_at, ends_at);

create table if not exists public.ad_stats (
  ad_id       uuid not null references public.ads(id) on delete cascade,
  day         date not null,
  impressions integer not null default 0,
  clicks      integer not null default 0,
  primary key (ad_id, day)
);

-- ---- 2. who can touch them: administrators only; visitors use the two functions below -----
alter table public.ads      enable row level security;
alter table public.ad_stats enable row level security;
drop policy if exists "Admins manage ads"      on public.ads;
drop policy if exists "Admins read ad stats"   on public.ad_stats;
create policy "Admins manage ads"    on public.ads      for all    using (public.is_admin()) with check (public.is_admin());
create policy "Admins read ad stats" on public.ad_stats for select using (public.is_admin());
revoke all on public.ads, public.ad_stats from anon;
grant  all on public.ads, public.ad_stats to authenticated, service_role;

-- ---- 3. what a visitor's browser asks for: only live ads, only the public details -----------
create or replace function public.get_ads(p_placement text, p_limit integer default 1)
returns table (id uuid, title text, advertiser text, image_path text, link_url text)
language sql security definer set search_path = public as $$
  select a.id, a.title, a.advertiser, a.image_path, a.link_url
    from public.ads a
   where not a.is_paused and a.starts_at <= now() and a.ends_at > now()
     and a.image_path is not null and p_placement = any (a.placements)
   order by random()
   limit greatest(1, least(coalesce(p_limit, 1), 5));
$$;
revoke all on function public.get_ads(text, integer) from public;
grant execute on function public.get_ads(text, integer) to anon, authenticated, service_role;

-- ---- 4. count a view or a click (only for ads that are live right now) ----------------------
create or replace function public.ad_track(p_ad_id uuid, p_event text)
returns void language plpgsql security definer set search_path = public as $$
begin
  if p_event not in ('view', 'click') then return; end if;
  if not exists (select 1 from public.ads where id = p_ad_id and not is_paused and starts_at <= now() and ends_at > now()) then return; end if;
  insert into public.ad_stats (ad_id, day, impressions, clicks)
  values (p_ad_id, (now() at time zone 'Africa/Kampala')::date, (p_event = 'view')::int, (p_event = 'click')::int)
  on conflict (ad_id, day) do update
    set impressions = public.ad_stats.impressions + excluded.impressions,
        clicks      = public.ad_stats.clicks + excluded.clicks;
end $$;
revoke all on function public.ad_track(uuid, text) from public;
grant execute on function public.ad_track(uuid, text) to anon, authenticated, service_role;

-- ---- 5. ads clear themselves: removed 30 days after they end (the numbers are kept until then) ----
create or replace function public.kmv_cleanup_ads(p_keep_days integer default 30)
returns integer language plpgsql security definer set search_path = public as $$
declare v_n integer;
begin
  delete from public.ads where ends_at < now() - make_interval(days => greatest(coalesce(p_keep_days, 30), 7));
  get diagnostics v_n = row_count;
  return v_n;
end $$;
revoke all on function public.kmv_cleanup_ads(integer) from public;
grant execute on function public.kmv_cleanup_ads(integer) to anon, authenticated, service_role;

-- ---- 6. a public place for the banner pictures, only administrators can add or remove them -----
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('ads', 'ads', true, 2097152, array['image/jpeg', 'image/png', 'image/webp', 'image/gif'])
on conflict (id) do update set public = true, file_size_limit = 2097152,
  allowed_mime_types = array['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
drop policy if exists "Admins manage ad images" on storage.objects;
create policy "Admins manage ad images" on storage.objects for all
  using (bucket_id = 'ads' and public.is_admin()) with check (bucket_id = 'ads' and public.is_admin());
