import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardBody, CardHeader } from '../common/Card';
import type { PipelineStage } from '@/types';

interface PipelineChartProps {
  data: PipelineStage[];
  loading?: boolean;
}

export const PipelineChart: React.FC<PipelineChartProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>Pipeline</CardHeader>
        <CardBody className="h-80 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary-500"></div>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>Candidates by Pipeline Stage</CardHeader>
      <CardBody className="p-0">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
            layout="vertical"
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis type="number" stroke="#6b7280" />
            <YAxis dataKey="name" type="category" stroke="#6b7280" width={100} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
              formatter={(value: any) => [value, 'Candidates']}
            />
            <Bar dataKey="count" fill="#0ea5e9" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  );
};
