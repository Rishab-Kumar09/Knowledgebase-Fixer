-- Enable necessary extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pg_trgm";

-- Create kb_articles table
create table kb_articles (
    id uuid default uuid_generate_v4() primary key,
    title text not null,
    content text not null,
    type text not null,
    version text,
    tags text[] default '{}',
    author text,
    created_at timestamp with time zone default now(),
    last_updated timestamp with time zone default now(),
    status text default 'active',
    metadata jsonb default '{}'::jsonb,
    search_vector tsvector
);

-- Create index for full-text search
create index kb_articles_search_idx on kb_articles using gin(search_vector);

-- Create index for tags array
create index kb_articles_tags_idx on kb_articles using gin(tags);

-- Create function to update search vector
create or replace function kb_articles_search_trigger() returns trigger as $$
begin
    new.search_vector :=
        setweight(to_tsvector('english', coalesce(new.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(new.content, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(array_to_string(new.tags, ' '), '')), 'C');
    return new;
end
$$ language plpgsql;

-- Create trigger to update search vector
create trigger kb_articles_search_update
    before insert or update
    on kb_articles
    for each row
    execute function kb_articles_search_trigger();

-- Create function for full-text search
create or replace function search_kb_articles(search_query text)
returns table (
    id uuid,
    title text,
    content text,
    type text,
    version text,
    tags text[],
    author text,
    created_at timestamp with time zone,
    last_updated timestamp with time zone,
    status text,
    metadata jsonb,
    rank real
)
language plpgsql
as $$
begin
    return query
    select
        a.*,
        ts_rank(a.search_vector, websearch_to_tsquery('english', search_query)) as rank
    from kb_articles a
    where a.search_vector @@ websearch_to_tsquery('english', search_query)
    order by rank desc;
end;
$$;

-- Create function to find related articles
create or replace function get_related_articles(article_id uuid)
returns table (
    id uuid,
    title text,
    content text,
    type text,
    version text,
    tags text[],
    author text,
    created_at timestamp with time zone,
    last_updated timestamp with time zone,
    status text,
    metadata jsonb,
    similarity real
)
language plpgsql
as $$
declare
    source_article kb_articles%rowtype;
begin
    -- Get the source article
    select * into source_article from kb_articles where id = article_id;
    
    -- Find related articles based on content similarity and shared tags
    return query
    select
        a.*,
        (
            similarity(a.content, source_article.content) * 0.6 +
            similarity(a.title, source_article.title) * 0.3 +
            array_length(array(select unnest(a.tags) intersect select unnest(source_article.tags)), 1)::float / 
            greatest(array_length(a.tags, 1), array_length(source_article.tags, 1))::float * 0.1
        ) as similarity
    from kb_articles a
    where a.id != article_id
    order by similarity desc
    limit 5;
end;
$$;

-- Create audit log table
create table kb_article_history (
    id uuid default uuid_generate_v4() primary key,
    article_id uuid references kb_articles(id),
    action text not null,
    changes jsonb not null,
    performed_by text,
    performed_at timestamp with time zone default now()
);

-- Create audit trigger function
create or replace function log_article_changes()
returns trigger
language plpgsql
as $$
begin
    if (tg_op = 'UPDATE') then
        insert into kb_article_history (article_id, action, changes, performed_by)
        values (
            old.id,
            'UPDATE',
            jsonb_build_object(
                'old', to_jsonb(old),
                'new', to_jsonb(new)
            ),
            current_user
        );
    elsif (tg_op = 'DELETE') then
        insert into kb_article_history (article_id, action, changes, performed_by)
        values (
            old.id,
            'DELETE',
            to_jsonb(old),
            current_user
        );
    end if;
    return null;
end;
$$;

-- Create audit trigger
create trigger kb_articles_audit
after update or delete on kb_articles
for each row execute function log_article_changes(); 