import React, { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import { LoadingSpinner, Skeleton } from '@/components/common/LoadingSpinner';
import {
  DocumentChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

interface OverviewData {
  total_candidates: number;
  active_requirements: number;
  placements_mtd: number;
  revenue_mtd: number;
  candidates_trend: Array<{ month: string; value: number }>;
  placements_trend: Array<{ month: string; value: number }>;
}

interface FunnelStage {
  stage: string;
  count: number;
  conversion_percent: number;
}

interface FunnelData {
  stages: FunnelStage[];
  total_sourced: number;
  total_placed: number;
  overall_conversion_percent: number;
}

interface Supplier {
  rank: number;
  name: string;
  fill_rate: number;
  avg_time_to_fill_days: number;
  quality_score: number;
  compliance_score: number;
  active_placements: number;
  composite_score: number;
}

interface ScorecardData {
  suppliers: Supplier[];
}

interface FinancialMonth {
  month: string;
  billed: number;
  paid: number;
  margin: number;
}

interface ClientFinancial {
  client_name: string;
  billed: number;
  paid: number;
  margin: number;
  placements: number;
}

interface FinancialData {
  total_billed: number;
  total_paid: number;
  gross_margin: number;
  margin_percent: number;
  by_client: ClientFinancial[];
  monthly_trend: FinancialMonth[];
}

interface ComplianceType {
  type: string;
  count: number;
  passed: number;
  percent: number;
}

interface ComplianceData {
  overall_compliance_percent: number;
  by_type: ComplianceType[];
  expiring_items_count: number;
  high_risk_gaps: number;
  overall_risk_level: string;
}

interface SLAMetric {
  metric: string;
  target: number;
  actual: number;
  score: number;
}

interface SLAData {
  overall_sla_score: number;
  metrics: SLAMetric[];
  breach_count_mtd: number;
  trend_direction: string;
}

export const Reports: React.FC = () => {
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [funnelData, setFunnelData] = useState<FunnelData | null>(null);
  const [scorecardData, setScorecardData] = useState<ScorecardData | null>(null);
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [complianceData, setComplianceData] = useState<ComplianceData | null>(null);
  const [slaData, setSLAData] = useState<SLAData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const [overview, funnel, scorecard, financial, compliance, sla] = await Promise.all([
          fetch('/api/v1/reports/overview').then(r => r.json()).catch(() => ({ data: {} })),
          fetch('/api/v1/reports/recruitment-funnel').then(r => r.json()).catch(() => ({ data: {} })),
          fetch('/api/v1/reports/supplier-scorecard').then(r => r.json()).catch(() => ({ data: {} })),
          fetch('/api/v1/reports/financial-summary').then(r => r.json()).catch(() => ({ data: {} })),
          fetch('/api/v1/reports/compliance-summary').then(r => r.json()).catch(() => ({ data: {} })),
          fetch('/api/v1/reports/sla-performance').then(r => r.json()).catch(() => ({ data: {} })),
        ]);

        setOverviewData(overview.data);
        setFunnelData(funnel.data);
        setScorecardData(scorecard.data);
        setFinancialData(financial.data);
        setComplianceData(compliance.data);
        setSLAData(sla.data);
      } catch (error) {
        console.error('Failed to fetch reports:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const getStatusColor = (value: number, threshold: number = 80) => {
    if (value >= threshold) return 'text-green-600 dark:text-green-400';
    if (value >= threshold - 15) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getStatusBgColor = (value: number, threshold: number = 80) => {
    if (value >= threshold) return 'bg-green-50 dark:bg-green-900/20';
    if (value >= threshold - 15) return 'bg-yellow-50 dark:bg-yellow-900/20';
    return 'bg-red-50 dark:bg-red-900/20';
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
    return `$${value.toFixed(0)}`;
  };

  return (
    <div className="p-4 md:p-6 space-y-6 pb-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Reports & Analytics</h1>
          <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">Platform-wide metrics and insights</p>
        </div>
        <DocumentChartBarIcon className="w-8 h-8 text-primary-500" />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32 rounded-lg" />)
        ) : (
          <>
            <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Total Placements</p>
                  <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                    {overviewData?.placements_mtd || 0}
                  </p>
                  <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-2">This month</p>
                </div>
                <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <CheckCircleIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Active Requirements</p>
                  <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                    {overviewData?.active_requirements || 0}
                  </p>
                  <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-2">Open positions</p>
                </div>
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <DocumentTextIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Revenue MTD</p>
                  <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                    {formatCurrency(overviewData?.revenue_mtd || 0)}
                  </p>
                  <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-2">Current month</p>
                </div>
                <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <CurrencyDollarIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Candidates</p>
                  <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                    {overviewData?.total_candidates || 0}
                  </p>
                  <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-2">In pipeline</p>
                </div>
                <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                  <ClockIcon className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Recruitment Funnel */}
      <Card>
        <CardHeader>Recruitment Funnel</CardHeader>
        <CardBody>
          {loading ? (
            <Skeleton className="h-64" />
          ) : funnelData ? (
            <div className="space-y-4">
              {funnelData.stages.map((stage, idx) => (
                <div key={stage.stage}>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-neutral-900 dark:text-white">{stage.stage}</span>
                      <span className="text-xs bg-neutral-100 dark:bg-neutral-700 px-2 py-1 rounded text-neutral-600 dark:text-neutral-400">
                        {stage.count}
                      </span>
                    </div>
                    <span className="text-sm font-semibold text-neutral-900 dark:text-white">
                      {stage.conversion_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
                    <div
                      className="bg-primary-500 h-2 rounded-full transition-all"
                      style={{ width: `${stage.conversion_percent}%` }}
                    />
                  </div>
                </div>
              ))}
              <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700 mt-4">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  Overall Conversion: <span className="font-bold text-neutral-900 dark:text-white">{funnelData.overall_conversion_percent.toFixed(1)}%</span>
                </p>
              </div>
            </div>
          ) : null}
        </CardBody>
      </Card>

      {/* Financial Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>Financial Summary</CardHeader>
            <CardBody>
              {loading ? (
                <Skeleton className="h-64" />
              ) : financialData ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 dark:border-neutral-700">
                        <th className="text-left py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Month</th>
                        <th className="text-right py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Billed</th>
                        <th className="text-right py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Paid</th>
                        <th className="text-right py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Margin</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.monthly_trend.map((month) => (
                        <tr key={month.month} className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/50">
                          <td className="py-3 px-3 text-neutral-900 dark:text-white font-medium">{month.month}</td>
                          <td className="text-right py-3 px-3 text-neutral-600 dark:text-neutral-400">{formatCurrency(month.billed)}</td>
                          <td className="text-right py-3 px-3 text-neutral-600 dark:text-neutral-400">{formatCurrency(month.paid)}</td>
                          <td className="text-right py-3 px-3 text-green-600 dark:text-green-400 font-medium">{formatCurrency(month.margin)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}
            </CardBody>
          </Card>
        </div>

        <Card>
          <CardHeader>Totals</CardHeader>
          <CardBody className="space-y-4">
            {loading ? (
              <Skeleton className="h-40" />
            ) : financialData ? (
              <>
                <div>
                  <p className="text-xs font-medium text-neutral-600 dark:text-neutral-400">Total Billed</p>
                  <p className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                    {formatCurrency(financialData.total_billed)}
                  </p>
                </div>
                <div className="border-t border-neutral-200 dark:border-neutral-700 pt-4">
                  <p className="text-xs font-medium text-neutral-600 dark:text-neutral-400">Total Paid</p>
                  <p className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                    {formatCurrency(financialData.total_paid)}
                  </p>
                </div>
                <div className="border-t border-neutral-200 dark:border-neutral-700 pt-4">
                  <p className="text-xs font-medium text-neutral-600 dark:text-neutral-400">Gross Margin</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
                    {financialData.margin_percent.toFixed(1)}%
                  </p>
                </div>
              </>
            ) : null}
          </CardBody>
        </Card>
      </div>

      {/* Supplier Scorecard */}
      <Card>
        <CardHeader>Supplier Scorecard</CardHeader>
        <CardBody>
          {loading ? (
            <Skeleton className="h-80" />
          ) : scorecardData ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Rank</th>
                    <th className="text-left py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Supplier</th>
                    <th className="text-center py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Fill Rate</th>
                    <th className="text-center py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Avg TTF</th>
                    <th className="text-center py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Quality</th>
                    <th className="text-center py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Compliance</th>
                    <th className="text-center py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Active</th>
                    <th className="text-right py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {scorecardData.suppliers.map((supplier) => (
                    <tr key={supplier.name} className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/50">
                      <td className="py-3 px-3">
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-xs font-bold">
                          {supplier.rank}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-medium text-neutral-900 dark:text-white">{supplier.name}</td>
                      <td className="text-center py-3 px-3">
                        <span className={`font-semibold ${getStatusColor(supplier.fill_rate)}`}>
                          {supplier.fill_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="text-center py-3 px-3 text-neutral-600 dark:text-neutral-400">
                        {supplier.avg_time_to_fill_days.toFixed(1)}d
                      </td>
                      <td className="text-center py-3 px-3">
                        <span className={`font-semibold ${getStatusColor(supplier.quality_score)}`}>
                          {supplier.quality_score}
                        </span>
                      </td>
                      <td className="text-center py-3 px-3">
                        <span className={`font-semibold ${getStatusColor(supplier.compliance_score)}`}>
                          {supplier.compliance_score}
                        </span>
                      </td>
                      <td className="text-center py-3 px-3 text-neutral-600 dark:text-neutral-400">
                        {supplier.active_placements}
                      </td>
                      <td className="text-right py-3 px-3">
                        <span className={`inline-flex items-center gap-1 font-bold px-2 py-1 rounded ${getStatusBgColor(supplier.composite_score)}`}>
                          {supplier.composite_score.toFixed(1)}
                          {supplier.composite_score >= 90 && <ArrowTrendingUpIcon className="w-4 h-4 text-green-600 dark:text-green-400" />}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </CardBody>
      </Card>

      {/* Compliance & SLA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>Compliance Health</CardHeader>
          <CardBody>
            {loading ? (
              <Skeleton className="h-64" />
            ) : complianceData ? (
              <div className="space-y-4">
                <div className="text-center pb-4 border-b border-neutral-200 dark:border-neutral-700">
                  <p className="text-4xl font-bold text-neutral-900 dark:text-white">
                    {complianceData.overall_compliance_percent.toFixed(1)}%
                  </p>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-2">Overall Compliance</p>
                </div>
                <div className="space-y-3">
                  {complianceData.by_type.map((item) => (
                    <div key={item.type}>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-neutral-900 dark:text-white">{item.type}</span>
                        <span className="text-xs font-semibold text-neutral-600 dark:text-neutral-400">
                          {item.passed}/{item.count}
                        </span>
                      </div>
                      <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${item.percent >= 95 ? 'bg-green-500' : item.percent >= 80 ? 'bg-yellow-500' : 'bg-red-500'}`}
                          style={{ width: `${item.percent}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700 grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <p className="text-neutral-600 dark:text-neutral-400">Expiring Items</p>
                    <p className="text-lg font-bold text-orange-600 dark:text-orange-400 mt-1">
                      {complianceData.expiring_items_count}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-600 dark:text-neutral-400">High Risk Gaps</p>
                    <p className="text-lg font-bold text-red-600 dark:text-red-400 mt-1">
                      {complianceData.high_risk_gaps}
                    </p>
                  </div>
                </div>
              </div>
            ) : null}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>SLA Performance</CardHeader>
          <CardBody>
            {loading ? (
              <Skeleton className="h-64" />
            ) : slaData ? (
              <div className="space-y-4">
                <div className="text-center pb-4 border-b border-neutral-200 dark:border-neutral-700">
                  <p className="text-4xl font-bold text-neutral-900 dark:text-white">
                    {slaData.overall_sla_score.toFixed(1)}%
                  </p>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-2">Overall SLA Score</p>
                </div>
                <div className="space-y-3">
                  {slaData.metrics.map((metric) => (
                    <div key={metric.metric}>
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="text-sm font-medium text-neutral-900 dark:text-white">{metric.metric}</p>
                          <p className="text-xs text-neutral-500 dark:text-neutral-500">Target: {metric.target} | Actual: {metric.actual.toFixed(1)}</p>
                        </div>
                        <span className={`font-bold text-sm ${getStatusColor(metric.score)}`}>
                          {metric.score.toFixed(0)}%
                        </span>
                      </div>
                      <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${metric.score >= 90 ? 'bg-green-500' : metric.score >= 75 ? 'bg-yellow-500' : 'bg-red-500'}`}
                          style={{ width: `${Math.min(metric.score, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">Breaches MTD</p>
                    <p className="text-lg font-bold text-neutral-900 dark:text-white">{slaData.breach_count_mtd}</p>
                  </div>
                </div>
              </div>
            ) : null}
          </CardBody>
        </Card>
      </div>

      {/* By Client Financial Breakdown */}
      {financialData && !loading && (
        <Card>
          <CardHeader>Financial by Client</CardHeader>
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Client</th>
                    <th className="text-right py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Billed</th>
                    <th className="text-right py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Paid</th>
                    <th className="text-right py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Margin</th>
                    <th className="text-center py-3 px-3 font-semibold text-neutral-700 dark:text-neutral-300">Placements</th>
                  </tr>
                </thead>
                <tbody>
                  {financialData.by_client.map((client) => (
                    <tr key={client.client_name} className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/50">
                      <td className="py-3 px-3 font-medium text-neutral-900 dark:text-white">{client.client_name}</td>
                      <td className="text-right py-3 px-3 text-neutral-600 dark:text-neutral-400">{formatCurrency(client.billed)}</td>
                      <td className="text-right py-3 px-3 text-neutral-600 dark:text-neutral-400">{formatCurrency(client.paid)}</td>
                      <td className="text-right py-3 px-3 font-medium text-green-600 dark:text-green-400">{formatCurrency(client.margin)}</td>
                      <td className="text-center py-3 px-3 text-neutral-600 dark:text-neutral-400">{client.placements}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
};
