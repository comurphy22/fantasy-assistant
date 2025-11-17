# Railway Environment Variables

Copy these exact values into Railway's Variables section:

## Required Variables

```
MONGO_URI=mongodb+srv://connermurphy03_db_user:nVx3NYOGnZU4Bbbp@cluster0.srgfppn.mongodb.net/nfl_platform?retryWrites=true&w=majority
```

```
DB_NAME=nfl_platform
```

```
JWT_SECRET=abc123
```

(Or generate a new one: `openssl rand -base64 32`)

```
GEMINI_API_KEY=AIzaSyBqxQPcW5eBDP0X5YHomH7cLZi9jRA8jhU
```

```
PORT=8080
```

```
ENVIRONMENT=production
```

## Important Notes

- **Variable name is `MONGO_URI`** (not `MONGODB_URI`)
- **Value must be the FULL connection string** (not just the password)
- **DB_NAME should be `nfl_platform`** (not `Cluster0`)

## After Updating

Railway will automatically redeploy. Check the logs to verify the connection works.
