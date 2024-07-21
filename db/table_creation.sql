-- Create a user_types table
CREATE TABLE user_types (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) UNIQUE NOT NULL
);

-- Insert default user types
INSERT INTO user_types (type) VALUES ('student'), ('professor'), ('recruiter'), ('other');


CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    user_type_id INTEGER REFERENCES user_types(id),
    rating INTEGER NOT NULL,
    feedback TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
