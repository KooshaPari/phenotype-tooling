-- 4SGM Database Setup for Supabase
-- Run this in Supabase SQL Editor

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  sku TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT,
  price REAL NOT NULL,
  quantity_on_hand INTEGER NOT NULL DEFAULT 0,
  category TEXT,
  product_metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS ix_products_category ON products(category);

-- Chat Sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_chat_sessions_user_id ON chat_sessions(user_id);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding JSONB,
  doc_metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_documents_title ON documents(title);

-- Insert sample products
INSERT INTO products (id, sku, name, description, price, quantity_on_hand, category) VALUES
('1', 'LAPTOP-PRO-15', 'Laptop Pro 15"', 'High-performance laptop', 1299.99, 5, 'electronics'),
('2', 'MOUSE-WIRELESS', 'Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 50, 'accessories'),
('3', 'HUB-USB-C', 'USB-C Hub', 'Multi-port USB-C hub', 49.99, 30, 'accessories'),
('4', 'MONITOR-4K', 'Monitor 4K', '4K UHD monitor', 399.99, 10, 'electronics'),
('5', 'KEYBOARD-MECH', 'Keyboard Mechanical', 'Mechanical gaming keyboard', 149.99, 20, 'accessories'),
('6', 'WEBCAM-HD', 'Webcam HD', '1080p HD webcam', 79.99, 15, 'electronics'),
('7', 'HEADPHONES-PRO', 'Headphones Pro', 'Noise-cancelling headphones', 199.99, 25, 'audio'),
('8', 'LAMP-LED', 'Desk Lamp LED', 'LED desk lamp', 59.99, 40, 'lighting')
ON CONFLICT (id) DO NOTHING;
