import { neon } from "@neondatabase/serverless";

const sql = neon(process.env.DATABASE_URL);

const checkUsers = async () => {
  const users = await sql`SELECT id, name, email, created_at FROM "user"`;
  console.log("Users in database:", users);

  const sessions = await sql`SELECT id, user_id, token, expires_at FROM "session"`;
  console.log("Sessions in database:", sessions);
};

checkUsers().catch(console.error);
