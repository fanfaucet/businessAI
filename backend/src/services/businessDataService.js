import { prisma } from '../config/prisma.js';
import { badRequest, notFound } from '../utils/httpErrors.js';

export const submitBusinessData = async ({ userId, payload }) => {
  if (!payload || typeof payload !== 'object') {
    throw badRequest('jsonPayload must be a valid JSON object.');
  }

  return prisma.businessData.create({
    data: {
      userId,
      jsonPayload: payload,
    },
  });
};

export const getLatestBusinessData = async (userId) => {
  const data = await prisma.businessData.findFirst({
    where: { userId },
    orderBy: { timestamp: 'desc' },
  });

  if (!data) {
    throw notFound('No business data found for this user.');
  }

  return data;
};
