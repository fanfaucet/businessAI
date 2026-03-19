import { Router } from 'express';
import { getPlugins, loadPluginHandler } from '../controllers/pluginController.js';
import { authenticateToken, authorizeRoles } from '../middleware/authMiddleware.js';

const router = Router();

router.get('/', authenticateToken, authorizeRoles('admin', 'analyst', 'business_user'), getPlugins);
router.post('/load', authenticateToken, authorizeRoles('admin', 'analyst'), loadPluginHandler);

export default router;
