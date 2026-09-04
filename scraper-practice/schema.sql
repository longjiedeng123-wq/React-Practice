CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE stores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    english_name TEXT NOT NULL,
    chinese_name TEXT,
    base_unit_type TEXT,
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE price_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    original_price NUMERIC(10, 2),
    discount_price NUMERIC(10, 2),
    price_per_base_unit NUMERIC(10, 4),
    valid_dates TEXT,
    taxable BOOLEAN,
    has_crv BOOLEAN,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX idx_price_history_product_date ON price_history (product_id, scraped_at DESC);
CREATE INDEX idx_products_embedding ON products USING hnsw (embedding vector_cosine_ops);
ALTER TABLE products ADD CONSTRAINT unique_store_product UNIQUE(store_id, english_name);

CREATE OR REPLACE FUNCTION match_products (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)

RETURNS TABLE (
    id uuid,
    english_name text,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        products.id,
        products.english_name,
        1 - (products.embedding <=> query_embedding) AS similarity
    FROM products
    WHERE 1 - (products.embedding <=> query_embedding) > match_threshold
    ORDER BY products.embedding <=> query_embedding
    LIMIT match_count;
$$;