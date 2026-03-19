import { submitBusinessData } from '../services/businessDataService.js';

export const submitData = async (req, res, next) => {
  try {
    const result = await submitBusinessData({
      userId: req.user.sub,
      payload: req.body.jsonPayload,
    });

    res.status(201).json({ data: result });
  } catch (error) {
    next(error);
  }
};
