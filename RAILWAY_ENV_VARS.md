# Railway Environment Variables

Copy these values into Railway's Variables section (replace with your actual values):

## Required Variables

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/nfl_platform?retryWrites=true&w=majority
```
**Get this from MongoDB Atlas → Connect → Connect your application**

```
DB_NAME=nfl_platform
```

```
JWT_SECRET=your-secret-key-here
```
**Generate a new one: `openssl rand -base64 32`**

```
GEMINI_API_KEY=your-gemini-api-key-here
```
**Get this from Google AI Studio: https://aistudio.google.com/apikey**

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
