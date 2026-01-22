---
name: backend-skill
description: Build and manage backend APIs by generating routes, handling requests and responses, and connecting to databases.
---

# Backend Skill – API Routes & Data Access

## Instructions

1. **Route Generation**
   - Define clear and RESTful API routes
   - Use proper HTTP methods (GET, POST, PUT, DELETE)
   - Group routes by resource or domain
   - Apply versioning when necessary

2. **Request Handling**
   - Validate incoming request data
   - Parse headers, params, query strings, and body correctly
   - Handle authentication and authorization checks
   - Support async request handling where applicable

3. **Response Handling**
   - Return consistent JSON responses
   - Use appropriate HTTP status codes
   - Structure success and error responses clearly
   - Avoid leaking internal implementation details

4. **Database Connection**
   - Establish secure database connections
   - Use ORM or query builders appropriately
   - Handle connection pooling and lifecycle
   - Perform CRUD operations safely and efficiently

5. **Error Handling**
   - Catch and handle runtime and database errors
   - Return meaningful but safe error messages
   - Log errors without exposing sensitive data

## Best Practices
- Keep route handlers thin; move logic to services
- Validate all inputs before processing
- Use environment variables for configuration
- Follow separation of concerns
- Write scalable and maintainable backend code
- Ensure database queries are optimized

## Example Structure
```ts
// Example Express / FastAPI-style route
app.post("/users", async (req, res) => {
  const user = await db.user.create(req.body);
  res.status(201).json(user);
});
