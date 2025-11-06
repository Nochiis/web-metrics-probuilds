-- schema_metrics.sql

-- Sitio y páginas
CREATE TABLE IF NOT EXISTS sites (
  id SERIAL PRIMARY KEY,
  domain TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pages (
  id SERIAL PRIMARY KEY,
  site_id INTEGER REFERENCES sites(id) ON DELETE CASCADE,
  path TEXT NOT NULL,
  full_url TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 1 Disponibilidad (status code)
CREATE TABLE IF NOT EXISTS availability (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  status_code INTEGER,
  final_url TEXT
);

-- 2 Tiempo de carga (total_load_ms)
CREATE TABLE IF NOT EXISTS load_time (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  total_load_ms INTEGER
);

-- 3 TTFB
CREATE TABLE IF NOT EXISTS ttfb (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  ttfb_ms INTEGER
);

-- 4 Numero de recursos
CREATE TABLE IF NOT EXISTS num_requests (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  requests_count INTEGER
);

-- 5 Tamaño total de recursos
CREATE TABLE IF NOT EXISTS total_bytes (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  bytes BIGINT
);

-- 6 Cantidad de imagenes
CREATE TABLE IF NOT EXISTS images_count (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  images_count INTEGER
);

-- 7 Imagenes sin alt
CREATE TABLE IF NOT EXISTS images_missing_alt (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  missing_alt_count INTEGER
);

-- 8 Cantidad de enlaces
CREATE TABLE IF NOT EXISTS links_count (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  links_total INTEGER,
  internal_links INTEGER,
  external_links INTEGER
);

-- 9 Word count (contenido visible)
CREATE TABLE IF NOT EXISTS word_count (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  words INTEGER
);

-- 10 Title + meta description (SEO basic)
CREATE TABLE IF NOT EXISTS seo_basic (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  title TEXT,
  has_title BOOLEAN,
  meta_description TEXT,
  has_meta_description BOOLEAN
);

-- Recursos (opcional: detalle por capture)
CREATE TABLE IF NOT EXISTS resources (
  id SERIAL PRIMARY KEY,
  page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  captured_at TIMESTAMPTZ DEFAULT now(),
  resource_url TEXT,
  resource_type TEXT,
  status_code INTEGER,
  size_bytes BIGINT
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_availability_pageid ON availability (page_id, captured_at);
CREATE INDEX IF NOT EXISTS idx_loadtime_pageid ON load_time (page_id, captured_at);
