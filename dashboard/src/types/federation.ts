export type DashboardMode = 'sovereign' | 'coalition' | 'emergency' | 'simulation-only';

export type Role =
  | 'sovereign_operator'
  | 'coalition_analyst'
  | 'emergency_coordinator'
  | 'simulation_user'
  | 'auditor';

export interface ScopedSignal<TPayload> {
  id: string;
  jurisdictionId: string;
  mode: DashboardMode;
  payload: TPayload;
  auditCorrelationId: string;
}

export interface RiskMetric {
  label: string;
  value: number;
  confidence: number;
  rationale: string;
}
