import { prisma } from '../config/prisma.js';
import { pluginRegistry } from '../plugins/registry.js';
import { badRequest } from '../utils/httpErrors.js';

export const listPlugins = async () => {
  const plugins = await prisma.plugin.findMany({ orderBy: { name: 'asc' } });
  return {
    available: Object.entries(pluginRegistry).map(([key, plugin]) => ({
      key,
      name: plugin.name,
      description: plugin.description,
    })),
    active: plugins,
  };
};

export const loadPlugin = async ({ key, config = {} }) => {
  const plugin = pluginRegistry[key];
  if (!plugin) {
    throw badRequest('Unknown plugin key.');
  }

  return prisma.plugin.upsert({
    where: { name: plugin.name },
    update: {
      config,
      activeFlag: true,
    },
    create: {
      name: plugin.name,
      config,
      activeFlag: true,
    },
  });
};

export const applyActivePlugins = async (payload) => {
  const plugins = await prisma.plugin.findMany({ where: { activeFlag: true } });

  return plugins.map((plugin) => {
    const registryEntry = Object.values(pluginRegistry).find((entry) => entry.name === plugin.name);
    return {
      name: plugin.name,
      config: plugin.config,
      output: registryEntry ? registryEntry.transform(payload) : null,
    };
  });
};
