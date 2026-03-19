import dotenv from 'dotenv';

dotenv.config();

const requiredVariables = ['DATABASE_URL', 'JWT_SECRET'];

for (const variable of requiredVariables) {
  if (!process.env[variable]) {
    console.warn(`[config] Missing required environment variable: ${variable}`);
  }
}

export const env = {
  port: Number(process.env.PORT || 4000),
  databaseUrl: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET || 'development-secret',
  openAiApiKey: process.env.OPENAI_API_KEY,
  openAiModel: process.env.OPENAI_MODEL || 'gpt-4o-mini',
  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:5173',
};
