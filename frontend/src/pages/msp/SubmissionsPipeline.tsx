import React from 'react';

const pipelineColumns = [
  {
    title: 'New Submissions',
    color: 'border-blue-500',
    items: [
      { id: 1, candidate: 'John Smith', supplier: 'TechStaff Inc', req: 'Senior Java Dev', score: 82 },
      { id: 2, candidate: 'Jane Doe', supplier: 'ProStaffing', req: 'React Developer', score: 75 },
    ],
  },
  {
    title: 'MSP Review',
    color: 'border-amber-500',
    items: [
      { id: 3, candidate: 'Bob Wilson', supplier: 'GlobalRecruit', req: 'Data Engineer', score: 88 },
    ],
  },
  {
    title: 'Submitted to Client',
    color: 'border-indigo-500',
    items: [
      { id: 4, candidate: 'Alice Chen', supplier: 'TechStaff Inc', req: 'PM Lead', score: 91 },
      { id: 5, candidate: 'David Kim', supplier: 'ProStaffing', req: 'DevOps Engineer', score: 79 },
    ],
  },
  {
    title: 'Client Feedback',
    color: 'border-emerald-500',
    items: [
      { id: 6, candidate: 'Sarah Lee', supplier: 'GlobalRecruit', req: 'Senior Java Dev', score: 95 },
    ],
  },
  {
    title: 'Placed',
    color: 'border-purple-500',
    items: [
      { id: 7, candidate: 'Mike Brown', supplier: 'TechStaff Inc', req: 'Full Stack Dev', score: 90 },
    ],
  },
];

export const SubmissionsPipeline: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Submissions Pipeline</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Track candidate submissions through the VMS workflow</p>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-4">
        {pipelineColumns.map((col) => (
          <div key={col.title} className="flex-shrink-0 w-72">
            <div className={`border-t-2 ${col.color} bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700`}>
              <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-700">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-neutral-900 dark:text-white">{col.title}</h3>
                  <span className="text-xs bg-neutral-100 dark:bg-neutral-700 px-2 py-0.5 rounded-full text-neutral-600 dark:text-neutral-400">
                    {col.items.length}
                  </span>
                </div>
              </div>
              <div className="p-3 space-y-3">
                {col.items.map((item) => (
                  <div key={item.id} className="bg-neutral-50 dark:bg-neutral-750 rounded-lg p-3 cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors">
                    <p className="text-sm font-medium text-neutral-900 dark:text-white">{item.candidate}</p>
                    <p className="text-xs text-neutral-500 mt-1">{item.req}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-neutral-400">{item.supplier}</span>
                      <span className={`text-xs font-medium ${item.score >= 80 ? 'text-emerald-500' : item.score >= 60 ? 'text-amber-500' : 'text-red-500'}`}>
                        {item.score}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
