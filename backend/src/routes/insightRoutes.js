import { Router } from 'express';
import { getAiInsight } from '../controllers/insightController.js';
import { authenticateToken, authorizeRoles } from '../middleware/authMiddleware.js';

const router = Router();

router.get('/ai', authenticateToken, authorizeRoles('admin', 'business_user', 'analyst'), getAiInsight);

export default router;
