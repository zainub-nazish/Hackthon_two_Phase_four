---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, JWT handling, and Better Auth integration.
---

# Auth Skill – Secure Authentication

## Instructions

1. **Signup Flow**
   - Validate user input (email format, password strength)
   - Hash passwords using secure algorithms (bcrypt or argon2)
   - Prevent duplicate accounts
   - Store credentials securely

2. **Signin Flow**
   - Verify credentials securely
   - Use constant-time comparisons
   - Return standardized auth responses
   - Handle failed login attempts safely

3. **Password Security**
   - Never store plain-text passwords
   - Enforce strong password rules
   - Support password reset flows with secure tokens
   - Use salting and proper cost factors

4. **JWT Authentication**
   - Generate access and refresh tokens
   - Set proper expiration times
   - Validate and decode tokens securely
   - Implement token rotation and revocation
   - Store tokens securely (httpOnly cookies preferred)

5. **Better Auth Integration**
   - Configure Better Auth providers correctly
   - Handle sessions and callbacks
   - Validate auth state consistently
   - Align Better Auth with JWT or session strategy

6. **Validation (Mandatory)**
   - Validate all user inputs
   - Validate tokens, sessions, and payloads
   - Sanitize data before processing
   - Return safe error messages without leaking details

## Best Practices
- Follow OWASP authentication guidelines
- Use HTTPS only
- Implement rate limiting on auth routes
- Avoid exposing auth internals in errors
- Separate auth logic from UI logic
- Keep secrets in environment variables

## Example Structure
```ts
// Signup example
const hashedPassword = await bcrypt.hash(password, 12);

const user = await db.user.create({
  email,
  password: hashedPassword,
});

// JWT generation
const token = jwt.sign(
  { userId: user.id },
  process.env.JWT_SECRET,
  { expiresIn: "15m" }
);