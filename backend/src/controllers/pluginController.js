import { listPlugins, loadPlugin } from '../services/pluginService.js';

export const getPlugins = async (_req, res, next) => {
  try {
    const result = await listPlugins();
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
};

export const loadPluginHandler = async (req, res, next) => {
  try {
    const result = await loadPlugin(req.body);
    res.status(201).json({ plugin: result });
  } catch (error) {
    next(error);
  }
};
