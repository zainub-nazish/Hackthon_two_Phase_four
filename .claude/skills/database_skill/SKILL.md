---
name: database-skill
description: Design and manage relational databases including table creation, migrations, and scalable schema design.
---

# Database Skill – Schema & Migrations

## Instructions

1. **Schema Design**
   - Identify entities and relationships
   - Normalize tables appropriately
   - Define primary and foreign keys
   - Enforce constraints (NOT NULL, UNIQUE, CHECK)

2. **Table Creation**
   - Choose correct data types
   - Use meaningful table and column names
   - Add indexes for frequently queried fields
   - Define timestamps for auditing (`created_at`, `updated_at`)

3. **Migrations**
   - Create forward and rollback-safe migrations
   - Version and document schema changes
   - Avoid destructive changes in production
   - Handle data transformations carefully

4. **Relationships**
   - One-to-one, one-to-many, many-to-many
   - Use junction tables where required
   - Enforce referential integrity
   - Define cascading rules explicitly

5. **Performance & Scalability**
   - Add indexes strategically
   - Avoid over-indexing
   - Design for future growth
   - Keep schemas simple and flexible

## Best Practices
- Follow database normalization rules
- Use migrations for all schema changes
- Never edit production databases manually
- Keep schemas environment-agnostic
- Document schema decisions clearly
- Prefer explicit constraints over application-only validation

## Example Structure
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
