import cors from 'cors';
import express from 'express';
import { env } from './config/env.js';
import authRoutes from './routes/authRoutes.js';
import dataRoutes from './routes/dataRoutes.js';
import insightRoutes from './routes/insightRoutes.js';
import pluginRoutes from './routes/pluginRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

export const app = express();

app.use(cors({ origin: env.corsOrigin }));
app.use(express.json({ limit: '1mb' }));

app.get('/health', (_req, res) => {
  res.status(200).json({ status: 'ok', service: 'AnnabanAI Business Suite API' });
});

app.use('/auth', authRoutes);
app.use('/data', dataRoutes);
app.use('/insights', insightRoutes);
app.use('/plugins', pluginRoutes);

app.use(errorHandler);
