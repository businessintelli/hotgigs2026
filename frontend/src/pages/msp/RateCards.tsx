import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import client from '@/api/client';

interface RateCard {
  id: string;
  jobCategory: string;
  location: string;
  skillLevel: string;
  billRateMin: number;
  billRateMax: number;
  payRateMin: number;
  payRateMax: number;
  status: 'DRAFT' | 'ACTIVE' | 'ARCHIVED' | 'EXPIRED';
}

const mockRateCards: RateCard[] = [
  {
    id: '1',
    jobCategory: 'Software Engineer',
    location: 'New York, NY',
    skillLevel: 'Senior',
    billRateMin: 150,
    billRateMax: 180,
    payRateMin: 110,
    payRateMax: 130,
    status: 'ACTIVE',
  },
  {
    id: '2',
    jobCategory: 'Project Manager',
    location: 'San Francisco, CA',
    skillLevel: 'Mid-Level',
    billRateMin: 120,
    billRateMax: 150,
    payRateMin: 80,
    payRateMax: 100,
    status: 'ACTIVE',
  },
  {
    id: '3',
    jobCategory: 'Data Engineer',
    location: 'Remote',
    skillLevel: 'Senior',
    billRateMin: 160,
    billRateMax: 190,
    payRateMin: 115,
    payRateMax: 135,
    status: 'DRAFT',
  },
  {
    id: '4',
    jobCategory: 'QA Engineer',
    location: 'Austin, TX',
    skillLevel: 'Junior',
    billRateMin: 85,
    billRateMax: 110,
    payRateMin: 55,
    payRateMax: 70,
    status: 'EXPIRED',
  },
  {
    id: '5',
    jobCategory: 'DevOps Engineer',
    location: 'Seattle, WA',
    skillLevel: 'Senior',
    billRateMin: 155,
    billRateMax: 185,
    payRateMin: 112,
    payRateMax: 132,
    status: 'ARCHIVED',
  },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'DRAFT':
      return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-400';
    case 'ACTIVE':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    case 'ARCHIVED':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'EXPIRED':
      return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const RateCards: React.FC = () => {
  const [rateCards, setRateCards] = useState<RateCard[]>(mockRateCards);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);
  const [formData, setFormData] = useState({
    jobCategory: '',
    location: '',
    skillLevel: '',
    status: 'DRAFT',
    billRateMin: '',
    billRateMax: '',
    payRateMin: '',
    payRateMax: '',
  });

  useEffect(() => {
    const fetchRateCards = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await client.get('/rate-cards');
        if (response.data && response.data.length > 0) {
          setRateCards(response.data);
        }
      } catch (err) {
        console.error('Failed to fetch rate cards, using mock data:', err);
        setError('Failed to load rate cards, using mock data');
      } finally {
        setLoading(false);
      }
    };

    fetchRateCards();
  }, []);

  const handleCreateRateCard = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newCard = {
        jobCategory: formData.jobCategory,
        location: formData.location,
        skillLevel: formData.skillLevel,
        status: formData.status,
        billRateMin: parseFloat(formData.billRateMin),
        billRateMax: parseFloat(formData.billRateMax),
        payRateMin: parseFloat(formData.payRateMin),
        payRateMax: parseFloat(formData.payRateMax),
      };

      const response = await client.post('/rate-cards', newCard);
      setRateCards([...rateCards, response.data]);
      console.log('Rate card created successfully:', response.data);
      setFormData({
        jobCategory: '',
        location: '',
        skillLevel: '',
        status: 'DRAFT',
        billRateMin: '',
        billRateMax: '',
        payRateMin: '',
        payRateMax: '',
      });
      setIsCreateFormOpen(false);
    } catch (err) {
      console.error('Failed to create rate card:', err);
      alert('Failed to create rate card');
    }
  };

  const handleDeleteRateCard = async (id: string) => {
    try {
      await client.delete(`/rate-cards/${id}`);
      setRateCards(rateCards.filter(card => card.id !== id));
      console.log('Rate card deleted successfully');
    } catch (err) {
      console.error('Failed to delete rate card:', err);
      alert('Failed to delete rate card');
    }
  };

  const filteredCards = filterStatus === 'ALL'
    ? rateCards
    : rateCards.filter(card => card.status === filterStatus);

  return (
    <div className="space-y-6">
      {/* Loading Spinner */}
      {loading && (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">{error}</p>
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Rate Cards</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Manage billing and pay rates for job categories and skill levels
        </p>
      </div>

      {/* Filters and Actions */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <FunnelIcon className="w-5 h-5 text-neutral-500" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="ACTIVE">Active</option>
            <option value="ARCHIVED">Archived</option>
            <option value="EXPIRED">Expired</option>
          </select>
        </div>
        <button
          onClick={() => setIsCreateFormOpen(!isCreateFormOpen)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium"
        >
          <PlusIcon className="w-5 h-5" />
          Create Rate Card
        </button>
      </div>

      {/* Create Form - Inline */}
      {isCreateFormOpen && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700 space-y-4">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">Create New Rate Card</h3>
          <form onSubmit={handleCreateRateCard}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <input
                type="text"
                placeholder="Job Category"
                value={formData.jobCategory}
                onChange={(e) => setFormData({ ...formData, jobCategory: e.target.value })}
                required
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="text"
                placeholder="Location"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                required
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <select
                value={formData.skillLevel}
                onChange={(e) => setFormData({ ...formData, skillLevel: e.target.value })}
                required
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select Skill Level</option>
                <option value="Junior">Junior</option>
                <option value="Mid-Level">Mid-Level</option>
                <option value="Senior">Senior</option>
              </select>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="DRAFT">DRAFT</option>
                <option value="ACTIVE">ACTIVE</option>
              </select>
              <input
                type="number"
                placeholder="Bill Rate Min ($)"
                value={formData.billRateMin}
                onChange={(e) => setFormData({ ...formData, billRateMin: e.target.value })}
                required
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="number"
                placeholder="Bill Rate Max ($)"
                value={formData.billRateMax}
                onChange={(e) => setFormData({ ...formData, billRateMax: e.target.value })}
                required
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="number"
                placeholder="Pay Rate Min ($)"
                value={formData.payRateMin}
                onChange={(e) => setFormData({ ...formData, payRateMin: e.target.value })}
                required
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="number"
                placeholder="Pay Rate Max ($)"
                value={formData.payRateMax}
                onChange={(e) => setFormData({ ...formData, payRateMax: e.target.value })}
                required
                className="px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium"
              >
                Save Rate Card
              </button>
              <button
                type="button"
                onClick={() => setIsCreateFormOpen(false)}
                className="px-4 py-2 bg-neutral-200 dark:bg-neutral-700 text-neutral-900 dark:text-white rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors text-sm font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Rate Cards Table */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Job Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Skill Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Bill Rate Range
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Pay Rate Range
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {filteredCards.map((card) => (
                <tr key={card.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                    {card.jobCategory}
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                    {card.location}
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                    {card.skillLevel}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                    ${card.billRateMin} - ${card.billRateMax}/hr
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                    ${card.payRateMin} - ${card.payRateMax}/hr
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(card.status)}`}>
                      {card.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex items-center gap-2">
                      <button className="p-1 text-neutral-400 hover:text-primary-500 transition-colors" title="Edit">
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteRateCard(card.id)}
                        className="p-1 text-neutral-400 hover:text-red-500 transition-colors"
                        title="Delete"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empty State */}
      {filteredCards.length === 0 && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-12 text-center border border-neutral-200 dark:border-neutral-700">
          <p className="text-neutral-500 dark:text-neutral-400">No rate cards found for the selected filter.</p>
        </div>
      )}
    </div>
  );
};

export default RateCards;
