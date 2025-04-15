CREATE TABLE posts (
  post_id INTEGER PRIMARY KEY UNIQUE NOT NULL,
  board_id TEXT NOT NULL,
  thread_id INTEGER NOT NULL,
  op INTEGER NOT NULL,
  last_bump INTEGER,
  sticky INTEGER,
  time INTEGER NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  subject TEXT,
  content TEXT NOT NULL,
  filename TEXT,
  file_actual TEXT,
  password TEXT,
  spoiler INTEGER NOT NULL,
  ip TEXT NOT NULL
);
