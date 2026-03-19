import { Router } from 'express';
import { submitData } from '../controllers/dataController.js';
import { authenticateToken, authorizeRoles } from '../middleware/authMiddleware.js';

const router = Router();

router.post('/submit', authenticateToken, authorizeRoles('admin', 'business_user'), submitData);

export default router;
