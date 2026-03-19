import OpenAI from 'openai';
import { prisma } from '../config/prisma.js';
import { env } from '../config/env.js';
import { getLatestBusinessData } from './businessDataService.js';
import { applyActivePlugins } from './pluginService.js';

const client = env.openAiApiKey
  ? new OpenAI({ apiKey: env.openAiApiKey })
  : null;

const buildFallbackInsight = (payload, pluginOutputs) => {
  const summary = [];

  if (payload.revenue) {
    summary.push(`Revenue reported: ${payload.revenue}.`);
  }

  if (payload.expenses) {
    summary.push(`Expenses reported: ${payload.expenses}.`);
  }

  if (payload.churnRate) {
    summary.push(`Churn rate reported: ${payload.churnRate}%.`);
  }

  if (pluginOutputs.length > 0) {
    summary.push(`Loaded plugins evaluated ${pluginOutputs.length} business utility module(s).`);
  }

  summary.push('Add an OPENAI_API_KEY to generate model-backed strategic recommendations.');
  return summary.join(' ');
};

export const generateInsight = async (userId) => {
  const businessData = await getLatestBusinessData(userId);
  const pluginOutputs = await applyActivePlugins(businessData.jsonPayload);

  let insightText;

  if (client) {
    const response = await client.responses.create({
      model: env.openAiModel,
      input: [
        {
          role: 'system',
          content: 'You are an enterprise business intelligence analyst. Provide concise, actionable insights with risk and opportunity framing.',
        },
        {
          role: 'user',
          content: `Analyze this business data and plugin output: ${JSON.stringify({ payload: businessData.jsonPayload, pluginOutputs })}`,
        },
      ],
    });

    insightText = response.output_text;
  } else {
    insightText = buildFallbackInsight(businessData.jsonPayload, pluginOutputs);
  }

  const insight = await prisma.insight.create({
    data: {
      userId,
      dataId: businessData.id,
      insightText,
    },
  });

  return {
    ...insight,
    pluginOutputs,
  };
};
