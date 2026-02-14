import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardBody, CardHeader } from '../common/Card';
import type { SubmissionFunnel } from '@/types';

interface FunnelChartProps {
  data: SubmissionFunnel;
  loading?: boolean;
}

export const FunnelChart: React.FC<FunnelChartProps> = ({ data, loading }) => {
  const chartData = [
    { stage: 'Draft', count: data.draft },
    { stage: 'Pending', count: data.pending },
    { stage: 'Approved', count: data.approved },
    { stage: 'Submitted', count: data.submitted },
    { stage: 'Customer Review', count: data.customer_review },
    { stage: 'Placed', count: data.placed },
    { stage: 'Rejected', count: data.rejected },
  ];

  if (loading) {
    return (
      <Card>
        <CardHeader>Submission Funnel</CardHeader>
        <CardBody className="h-80 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary-500"></div>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>Submission Funnel</CardHeader>
      <CardBody className="p-0">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="stage" stroke="#6b7280" angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="#6b7280" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
              formatter={(value: any) => [value, 'Count']}
            />
            <Bar dataKey="count" fill="#10b981" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  );
};
