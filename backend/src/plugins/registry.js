export const pluginRegistry = {
  revenuePulse: {
    name: 'Revenue Pulse',
    description: 'Summarizes revenue and cost movement for executive review.',
    transform: (payload) => ({
      revenue: payload.revenue || null,
      expenses: payload.expenses || null,
      margin: payload.revenue && payload.expenses ? payload.revenue - payload.expenses : null,
    }),
  },
  clientHealth: {
    name: 'Client Health',
    description: 'Flags churn and engagement indicators from submitted client metrics.',
    transform: (payload) => ({
      activeClients: payload.activeClients || 0,
      churnRate: payload.churnRate || 0,
      satisfactionScore: payload.satisfactionScore || null,
    }),
  },
};
