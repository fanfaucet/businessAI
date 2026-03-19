import { generateInsight } from '../services/insightService.js';

export const getAiInsight = async (req, res, next) => {
  try {
    const result = await generateInsight(req.user.sub);
    res.status(200).json({ insight: result });
  } catch (error) {
    next(error);
  }
};
