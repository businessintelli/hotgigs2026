import client from './client';
import type {
  CopilotMessage,
  CopilotConversation,
  PaginatedResponse,
} from '@/types';

export const getConversations = async (
  limit?: number
): Promise<CopilotConversation[]> => {
  const response = await client.get<CopilotConversation[]>(
    '/copilot/conversations',
    {
      params: { limit: limit || 20 },
    }
  );
  return response.data;
};

export const getConversation = async (id: string): Promise<CopilotConversation> => {
  const response = await client.get<CopilotConversation>(
    `/copilot/conversations/${id}`
  );
  return response.data;
};

export const createConversation = async (title?: string): Promise<CopilotConversation> => {
  const response = await client.post<CopilotConversation>(
    '/copilot/conversations',
    { title }
  );
  return response.data;
};

export const deleteConversation = async (id: string): Promise<void> => {
  await client.delete(`/copilot/conversations/${id}`);
};

export const renameConversation = async (
  id: string,
  title: string
): Promise<CopilotConversation> => {
  const response = await client.patch<CopilotConversation>(
    `/copilot/conversations/${id}`,
    { title }
  );
  return response.data;
};

export const sendMessage = async (
  conversationId: string,
  content: string,
  metadata?: Record<string, unknown>
): Promise<CopilotMessage> => {
  const response = await client.post<CopilotMessage>(
    `/copilot/conversations/${conversationId}/messages`,
    {
      content,
      metadata,
    }
  );
  return response.data;
};

export const streamMessage = async (
  conversationId: string,
  content: string,
  metadata?: Record<string, unknown>
): Promise<ReadableStream<Uint8Array> | null> => {
  const response = await client.post(
    `/copilot/conversations/${conversationId}/messages/stream`,
    {
      content,
      metadata,
    },
    {
      responseType: 'stream',
    }
  );
  return response.data;
};

export const deleteMessage = async (
  conversationId: string,
  messageId: string
): Promise<void> => {
  await client.delete(
    `/copilot/conversations/${conversationId}/messages/${messageId}`
  );
};

export const getSuggestedActions = async (conversationId?: string) => {
  const response = await client.get('/copilot/suggested-actions', {
    params: { conversation_id: conversationId },
  });
  return response.data;
};

export const analyzeRequirement = async (requirementId: string) => {
  const response = await client.post(`/copilot/analyze/requirement/${requirementId}`, {});
  return response.data;
};

export const compareTopCandidates = async (
  requirementId: string,
  limit?: number
) => {
  const response = await client.post(
    `/copilot/analyze/compare-candidates/${requirementId}`,
    { limit: limit || 5 }
  );
  return response.data;
};

export const generateJobDescription = async (data: {
  title: string;
  skills: string[];
  experience: number;
  location?: string;
}): Promise<string> => {
  const response = await client.post<{ description: string }>(
    '/copilot/generate/job-description',
    data
  );
  return response.data.description;
};

export const generateInterviewQuestions = async (
  requirementId: string,
  skillsToFocus?: string[]
): Promise<string[]> => {
  const response = await client.post<{ questions: string[] }>(
    `/copilot/generate/interview-questions/${requirementId}`,
    { skills: skillsToFocus }
  );
  return response.data.questions;
};

export const createMarketingContent = async (data: {
  requirementId: string;
  platform: 'linkedin' | 'twitter' | 'email' | 'website';
}): Promise<string> => {
  const response = await client.post<{ content: string }>(
    '/copilot/generate/marketing-content',
    data
  );
  return response.data.content;
};

export const predictFillRate = async (requirementId: string) => {
  const response = await client.post(
    `/copilot/predict/fill-rate/${requirementId}`,
    {}
  );
  return response.data;
};

export const predictPlacementSuccess = async (submissionId: string) => {
  const response = await client.post(
    `/copilot/predict/placement-success/${submissionId}`,
    {}
  );
  return response.data;
};
