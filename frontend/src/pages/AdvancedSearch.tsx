import React, { useState } from 'react';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  StarIcon,
  XMarkIcon,
  BookmarkIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';

interface CandidateResult {
  id: string;
  name: string;
  title: string;
  matchScore: number;
  skills: string[];
  location: string;
  locationMatch: boolean;
  experience: string;
  availability: 'Immediate' | '2 Weeks' | '1 Month' | 'Not Available';
}

const mockCandidateResults: CandidateResult[] = [
  {
    id: '1',
    name: 'Sarah Johnson',
    title: 'Senior Frontend Engineer',
    matchScore: 95,
    skills: ['React', 'TypeScript', 'AWS', 'Node.js'],
    location: 'San Francisco, CA',
    locationMatch: true,
    experience: '10+ years',
    availability: 'Immediate',
  },
  {
    id: '2',
    name: 'Alex Chen',
    title: 'Full Stack Developer',
    matchScore: 89,
    skills: ['React', 'Node.js', 'MongoDB', 'AWS'],
    location: 'San Jose, CA',
    locationMatch: true,
    experience: '8 years',
    availability: '2 Weeks',
  },
  {
    id: '3',
    name: 'Emma Davis',
    title: 'DevOps Engineer',
    matchScore: 87,
    skills: ['Kubernetes', 'Docker', 'AWS', 'Terraform'],
    location: 'Remote',
    locationMatch: true,
    experience: '6 years',
    availability: '1 Month',
  },
  {
    id: '4',
    name: 'Mike Johnson',
    title: 'Senior Backend Engineer',
    matchScore: 85,
    skills: ['Node.js', 'Python', 'PostgreSQL', 'AWS'],
    location: 'New York, NY',
    locationMatch: false,
    experience: '9 years',
    availability: 'Immediate',
  },
  {
    id: '5',
    name: 'Jennifer Martinez',
    title: 'Frontend Engineer',
    matchScore: 82,
    skills: ['React', 'Vue.js', 'TypeScript', 'CSS'],
    location: 'Austin, TX',
    locationMatch: false,
    experience: '5 years',
    availability: '2 Weeks',
  },
  {
    id: '6',
    name: 'David Wong',
    title: 'Full Stack Developer',
    matchScore: 80,
    skills: ['React', 'Node.js', 'PostgreSQL'],
    location: 'Seattle, WA',
    locationMatch: false,
    experience: '7 years',
    availability: '1 Month',
  },
  {
    id: '7',
    name: 'Lisa Anderson',
    title: 'Senior DevOps Engineer',
    matchScore: 78,
    skills: ['Kubernetes', 'AWS', 'Terraform', 'Python'],
    location: 'Remote',
    locationMatch: true,
    experience: '11 years',
    availability: '1 Month',
  },
  {
    id: '8',
    name: 'James Wilson',
    title: 'Backend Engineer',
    matchScore: 76,
    skills: ['Node.js', 'Go', 'PostgreSQL', 'Redis'],
    location: 'Boston, MA',
    locationMatch: false,
    experience: '6 years',
    availability: '2 Weeks',
  },
  {
    id: '9',
    name: 'Maria Garcia',
    title: 'Full Stack Engineer',
    matchScore: 75,
    skills: ['React', 'Python', 'Django', 'PostgreSQL'],
    location: 'Los Angeles, CA',
    locationMatch: false,
    experience: '4 years',
    availability: 'Immediate',
  },
  {
    id: '10',
    name: 'Robert Lee',
    title: 'Senior Frontend Engineer',
    matchScore: 72,
    skills: ['React', 'TypeScript', 'Vue.js', 'GraphQL'],
    location: 'Chicago, IL',
    locationMatch: false,
    experience: '8 years',
    availability: '1 Month',
  },
];

const getMatchScoreColor = (score: number) => {
  if (score >= 90) return 'text-emerald-600 dark:text-emerald-400';
  if (score >= 80) return 'text-green-600 dark:text-green-400';
  if (score >= 70) return 'text-amber-600 dark:text-amber-400';
  return 'text-red-600 dark:text-red-400';
};

const getMatchScoreBg = (score: number) => {
  if (score >= 90) return 'bg-emerald-50 dark:bg-emerald-900/10';
  if (score >= 80) return 'bg-green-50 dark:bg-green-900/10';
  if (score >= 70) return 'bg-amber-50 dark:bg-amber-900/10';
  return 'bg-red-50 dark:bg-red-900/10';
};

const getAvailabilityColor = (availability: CandidateResult['availability']) => {
  switch (availability) {
    case 'Immediate':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    case '2 Weeks':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case '1 Month':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'Not Available':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

interface SearchFilters {
  searchType: 'candidates' | 'requirements';
  skills: string[];
  location: string;
  minExperience: number;
  maxExperience: number;
  minSalary: number;
  maxSalary: number;
  availability: string;
  tags: string[];
  minMatchScore: number;
}

export const AdvancedSearch: React.FC = () => {
  const [filters, setFilters] = useState<SearchFilters>({
    searchType: 'candidates',
    skills: ['React', 'TypeScript', 'AWS'],
    location: 'San Francisco, CA',
    minExperience: 5,
    maxExperience: 15,
    minSalary: 80000,
    maxSalary: 150000,
    availability: '',
    tags: ['Senior', 'Remote Friendly'],
    minMatchScore: 70,
  });

  const [savedSearches] = useState([
    'Senior Frontend Engineers',
    'DevOps Specialists',
    'Full Stack Developers',
  ]);

  const handleRemoveSkill = (skill: string) => {
    setFilters(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill),
    }));
  };

  const handleRemoveTag = (tag: string) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag),
    }));
  };

  const filteredResults = mockCandidateResults.filter(
    candidate => candidate.matchScore >= filters.minMatchScore
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Advanced Search</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Multi-criteria candidate and requirement search
        </p>
      </div>

      {/* Search Type Toggle */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Search Type:</span>
          <div className="flex gap-2">
            {(['candidates', 'requirements'] as const).map(type => (
              <button
                key={type}
                onClick={() => setFilters(prev => ({ ...prev, searchType: type }))}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filters.searchType === type
                    ? 'bg-primary-600 text-white'
                    : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-900 dark:text-white hover:bg-neutral-200 dark:hover:bg-neutral-600'
                }`}
              >
                {type === 'candidates' ? 'Candidates' : 'Requirements'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filter Panel */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700 h-fit">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Filters</h3>

          {/* Skills */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Skills
            </label>
            <input
              type="text"
              placeholder="Add skill..."
              className="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-500 mb-3"
            />
            <div className="flex flex-wrap gap-2">
              {filters.skills.map(skill => (
                <span
                  key={skill}
                  className="px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-full text-xs font-medium inline-flex items-center gap-1"
                >
                  {skill}
                  <button onClick={() => handleRemoveSkill(skill)}>
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Location */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Location
            </label>
            <input
              type="text"
              value={filters.location}
              onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
              placeholder="City, State"
              className="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-500"
            />
          </div>

          {/* Experience Range */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Experience Range
            </label>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={filters.minExperience}
                  onChange={(e) => setFilters(prev => ({ ...prev, minExperience: parseInt(e.target.value) }))}
                  className="w-full px-2 py-1 rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white text-sm"
                  min="0"
                />
                <span className="text-neutral-500">-</span>
                <input
                  type="number"
                  value={filters.maxExperience}
                  onChange={(e) => setFilters(prev => ({ ...prev, maxExperience: parseInt(e.target.value) }))}
                  className="w-full px-2 py-1 rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white text-sm"
                  min="0"
                />
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                {filters.minExperience} - {filters.maxExperience} years
              </p>
            </div>
          </div>

          {/* Salary Range */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Salary Range
            </label>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={filters.minSalary}
                  onChange={(e) => setFilters(prev => ({ ...prev, minSalary: parseInt(e.target.value) }))}
                  className="w-full px-2 py-1 rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white text-sm"
                  step="10000"
                />
                <span className="text-neutral-500">-</span>
                <input
                  type="number"
                  value={filters.maxSalary}
                  onChange={(e) => setFilters(prev => ({ ...prev, maxSalary: parseInt(e.target.value) }))}
                  className="w-full px-2 py-1 rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white text-sm"
                  step="10000"
                />
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                ${filters.minSalary.toLocaleString()} - ${filters.maxSalary.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Availability */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Availability
            </label>
            <select
              value={filters.availability}
              onChange={(e) => setFilters(prev => ({ ...prev, availability: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white"
            >
              <option value="">Any</option>
              <option value="Immediate">Immediate</option>
              <option value="2 Weeks">2 Weeks</option>
              <option value="1 Month">1 Month</option>
            </select>
          </div>

          {/* Tags */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Tags
            </label>
            <input
              type="text"
              placeholder="Add tag..."
              className="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-500 mb-3"
            />
            <div className="flex flex-wrap gap-2">
              {filters.tags.map(tag => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-full text-xs font-medium inline-flex items-center gap-1"
                >
                  {tag}
                  <button onClick={() => handleRemoveTag(tag)}>
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Min Match Score */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Min Match Score
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={filters.minMatchScore}
              onChange={(e) => setFilters(prev => ({ ...prev, minMatchScore: parseInt(e.target.value) }))}
              className="w-full"
            />
            <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2">{filters.minMatchScore}%</p>
          </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-3 space-y-6">
          {/* Saved Searches */}
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-neutral-900 dark:text-white">Saved Searches</h4>
              <button className="text-blue-600 dark:text-blue-400 text-sm font-medium hover:underline">
                Save Current
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {savedSearches.map(search => (
                <button
                  key={search}
                  className="px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 text-neutral-900 dark:text-white hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors text-sm font-medium flex items-center gap-1"
                >
                  <BookmarkIcon className="w-4 h-4" />
                  {search}
                </button>
              ))}
            </div>
          </div>

          {/* Search Results */}
          <div className="space-y-4">
            <h4 className="font-semibold text-neutral-900 dark:text-white">
              Results ({filteredResults.length})
            </h4>

            {filteredResults.map(candidate => (
              <div
                key={candidate.id}
                className={`rounded-lg p-6 border-2 transition-colors ${getMatchScoreBg(candidate.matchScore)} border-neutral-200 dark:border-neutral-700 hover:shadow-md transition-shadow`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h5 className="font-semibold text-neutral-900 dark:text-white text-base">
                      {candidate.name}
                    </h5>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">{candidate.title}</p>
                  </div>
                  <div className="text-right">
                    <div className={`text-3xl font-bold ${getMatchScoreColor(candidate.matchScore)}`}>
                      {candidate.matchScore}%
                    </div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Match</p>
                  </div>
                </div>

                {/* Skills */}
                <div className="mb-4">
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mb-2">Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills.map(skill => {
                      const isMatched = filters.skills.includes(skill);
                      return (
                        <span
                          key={skill}
                          className={`px-2.5 py-1 rounded text-xs font-medium ${
                            isMatched
                              ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                              : 'bg-neutral-200 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300'
                          }`}
                        >
                          {skill}
                        </span>
                      );
                    })}
                  </div>
                </div>

                {/* Details Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Location</p>
                    <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1 flex items-center gap-1">
                      <MapPinIcon className={`w-4 h-4 ${candidate.locationMatch ? 'text-green-500' : 'text-neutral-400'}`} />
                      {candidate.location}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Experience</p>
                    <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{candidate.experience}</p>
                  </div>
                  <div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Availability</p>
                    <span className={`inline-block mt-1 px-2.5 py-1 rounded-full text-xs font-semibold ${getAvailabilityColor(candidate.availability)}`}>
                      {candidate.availability}
                    </span>
                  </div>
                  <div className="flex justify-end">
                    <button className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white">
                      <BookmarkIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedSearch;
